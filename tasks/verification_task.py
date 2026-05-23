"""Prefect task: post-backup integrity verification."""

from prefect import task
from prefect.logging import get_run_logger

from core.manifest_db import ManifestDB
from core.rclone import run_rclone_check
from models.config_model import AppConfig
from models.scan_result import ScanResult


@task(
    name="verify_cloud_integrity",
    tags=["verification"],
    retries=1,
    retry_delay_seconds=60,
    task_run_name="verify-cloud-integrity",
    timeout_seconds=21600,
)
def verify_cloud_integrity_task(
    config: AppConfig,
    gcs_key_path: str,
    scan_result: ScanResult | None = None,
    database_path: str | None = None,
) -> dict:
    """Run rclone check to verify cloud backup integrity.

    Compares source drive against GCS bucket to detect missing or mismatched
    files. If verification passes and scan_result + database_path are provided,
    marks files as cloud-backed in the manifest.

    Args:
        config: Validated application configuration.
        gcs_key_path: Path to GCS service account JSON key.
        scan_result: ScanResult with new/modified files (for mark-after-verify).
        database_path: Path to manifest database (for mark-after-verify).

    Returns:
        Result dict with verification status.
    """
    logger = get_run_logger()

    if not config.cloud_backup.enabled:
        logger.info("Cloud backup disabled, skipping integrity verification")
        return {"status": "SKIPPED", "reason": "cloud backup disabled"}

    logger.info(f"Starting cloud integrity verification: {config.paths.source_drive} vs GCS")

    result = run_rclone_check(config, gcs_key_path)

    logger.info(
        f"Cloud integrity check {result['status']}: "
        f"{result['matches']} matches, "
        f"{result['mismatches']} mismatches, "
        f"{result['missing']} missing"
    )

    # Mark cloud-backed only after successful verification
    if result.get("status") == "MATCH" and scan_result and database_path:
        all_changed = [f.relative_path for f in scan_result.new_files + scan_result.modified_files]
        if all_changed:
            db = ManifestDB(database_path)
            try:
                count = db.batch_mark_cloud_backed_up(all_changed)
                logger.info(f"Marked {count} files as cloud-backed after verification")
            finally:
                db.close()

    return result
