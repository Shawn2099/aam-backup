"""Prefect task: periodic destination reconciliation (D-003).

Runs every N backup runs to audit both destinations against the source manifest.
If ANY drift is found, runs full robocopy /MIR and rclone sync to auto-correct.
Reuses existing core modules — no duplicated logic.
"""

from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger

from core.manifest_db import ManifestDB
from core.robocopy import run_robocopy
from core.rclone import run_rclone, run_rclone_check
from core.verify import verify_lan_checksums
from models.config_model import AppConfig
from models.scan_result import ScanResult


@task(
    name="reconciliation_task",
    tags=["reconciliation"],
    retries=1,
    retry_delay_seconds=60,
    task_run_name="destination-reconciliation",
    timeout_seconds=28800,
)
def reconciliation_task(
    config: AppConfig,
    database_path: str,
    gcs_key_path: str | None = None,
) -> dict:
    """Audit both destinations against source manifest and auto-correct drift."""
    logger = get_run_logger()

    if not config.reconciliation.enabled:
        logger.info("Reconciliation disabled, skipping")
        return {"status": "SKIPPED", "reason": "reconciliation.disabled = false"}

    # Read run counter WITHOUT incrementing (scan_task already incremented)
    db = ManifestDB(database_path)
    try:
        run_number = db.get_run_counter()
        interval = config.reconciliation.run_every_n_backups
        if run_number % interval != 0:
            logger.info(
                f"Reconciliation skipped (run #{run_number}, "
                f"next in {interval - (run_number % interval)} backups)"
            )
            return {"status": "SKIPPED", "run_number": run_number}
    finally:
        db.close()

    logger.info(
        f"Running destination reconciliation (run #{run_number}, "
        f"every {interval} backups)"
    )

    result = {"lan": {}, "cloud": {}, "auto_correct": False, "drift_found": False}

    if config.lan_backup.enabled:
        result["lan"] = _audit_lan(config, logger)
        if result["lan"].get("drift"):
            result["drift_found"] = True
            logger.warning(
                f"LAN drift detected: {result['lan']['drift_summary']}"
            )

    if config.cloud_backup.enabled and gcs_key_path:
        result["cloud"] = _audit_cloud(config, gcs_key_path, logger)
        if result["cloud"].get("drift"):
            result["drift_found"] = True
            logger.warning(
                f"Cloud drift detected: {result['cloud']['drift_summary']}"
            )

    if result["drift_found"] and config.reconciliation.auto_correct:
        result["auto_correct"] = True
        logger.info("Running auto-correction sync for drifted destinations")

        if config.lan_backup.enabled and result["lan"].get("drift"):
            _correct_lan(config, logger)

        if config.cloud_backup.enabled and gcs_key_path and result["cloud"].get("drift"):
            _correct_cloud(config, gcs_key_path, logger)

    return result


def _audit_lan(config: AppConfig, logger) -> dict:
    """Audit LAN destination against source manifest."""
    result = {"drift": False, "drift_summary": "", "missing_on_lan": 0, "extra_on_lan": 0}

    try:
        db = ManifestDB(config.paths.database_path)
        try:
            manifest_paths = db.get_all_paths()
        finally:
            db.close()

        lan_dest = Path(config.paths.lan_destination)
        if not lan_dest.exists():
            result["drift"] = True
            result["drift_summary"] = "LAN destination not accessible"
            return result

        lan_paths: set[str] = set()
        for dirpath, _dirnames, filenames in lan_dest.walk(top_down=True):
            for filename in filenames:
                full_path = dirpath / filename
                try:
                    relative = str(full_path.relative_to(lan_dest))
                    lan_paths.add(relative)
                except ValueError:
                    pass

        missing_on_lan = manifest_paths - lan_paths
        extra_on_lan = lan_paths - manifest_paths

        result["missing_on_lan"] = len(missing_on_lan)
        result["extra_on_lan"] = len(extra_on_lan)

        if missing_on_lan or extra_on_lan:
            result["drift"] = True
            total_manifest = len(manifest_paths)
            drift_pct = (len(missing_on_lan) / total_manifest * 100) if total_manifest > 0 else 0
            result["drift_summary"] = (
                f"{len(missing_on_lan)} files missing on LAN, "
                f"{len(extra_on_lan)} extra files on LAN "
                f"({drift_pct:.1f}% of {total_manifest} files)"
            )

    except Exception as e:
        result["drift"] = True
        result["drift_summary"] = f"Audit error: {e}"

    return result


def _audit_cloud(config: AppConfig, gcs_key_path: str, logger) -> dict:
    """Audit GCS destination using rclone check. Reuses run_rclone_check."""
    result = {"drift": False, "drift_summary": "", "mismatches": 0, "missing": 0, "errors": 0}

    try:
        check_result = run_rclone_check(config, gcs_key_path)

        result["mismatches"] = check_result.get("mismatches", 0)
        result["missing"] = check_result.get("missing", 0)
        result["errors"] = check_result.get("errors", 0)

        total_issues = result["mismatches"] + result["missing"] + result["errors"]
        if total_issues > 0:
            result["drift"] = True
            result["drift_summary"] = (
                f"{result['mismatches']} mismatches, "
                f"{result['missing']} missing, "
                f"{result['errors']} errors"
            )

    except Exception as e:
        result["drift"] = True
        result["drift_summary"] = f"Audit error: {e}"

    return result


def _correct_lan(config: AppConfig, logger) -> dict:
    """Auto-correct LAN drift by running full robocopy /MIR. Reuses run_robocopy."""
    logger.info("Running LAN auto-correction: robocopy /MIR")

    scan_result = ScanResult()

    db = ManifestDB(config.paths.database_path)
    try:
        result = run_robocopy(config, scan_result, db)
        logger.info(f"LAN auto-correction: {result.status}")

        if result.status in ("LAN_COMPLETE", "LAN_PARTIAL"):
            verify_result = verify_lan_checksums(
                config.paths.source_drive,
                config.paths.lan_destination,
                scan_result,
            )
            logger.info(
                f"LAN post-correction verification: "
                f"{verify_result['verified']} verified, "
                f"{verify_result['mismatches']} mismatches"
            )
            if verify_result["mismatches"] == 0 and scan_result.has_changes:
                all_changed = [f.relative_path for f in scan_result.new_files + scan_result.modified_files]
                if all_changed:
                    db.batch_mark_lan_backed_up(all_changed)
                    logger.info(f"Marked {len(all_changed)} files as LAN-backed after correction")

        return {"status": result.status}
    finally:
        db.close()


def _correct_cloud(config: AppConfig, gcs_key_path: str, logger) -> dict:
    """Auto-correct cloud drift by running full rclone sync. Reuses run_rclone."""
    logger.info("Running cloud auto-correction: rclone sync")

    scan_result = ScanResult()

    db = ManifestDB(config.paths.database_path)
    try:
        result = run_rclone(config, gcs_key_path, scan_result, db)
        logger.info(f"Cloud auto-correction: {result.status}")

        if result.status in ("CLOUD_COMPLETE", "CLOUD_PARTIAL") and scan_result.has_changes:
            check_result = run_rclone_check(config, gcs_key_path)
            if check_result.get("status") == "MATCH":
                all_changed = [f.relative_path for f in scan_result.new_files + scan_result.modified_files]
                if all_changed:
                    db.batch_mark_cloud_backed_up(all_changed)
                    logger.info(f"Marked {len(all_changed)} files as cloud-backed after correction")

        return {"status": result.status}
    finally:
        db.close()
