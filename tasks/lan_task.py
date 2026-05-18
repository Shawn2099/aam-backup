"""Prefect task: LAN backup via Robocopy."""

from prefect import task
from prefect.logging import get_run_logger
from prefect.tasks import exponential_backoff

from core.manifest_db import ManifestDB
from core.robocopy import run_robocopy
from core.verify import verify_lan_checksums
from core.wol import ensure_server_online, WolTimeout
from models.config_model import AppConfig
from models.scan_result import ScanResult


@task(
    name="lan_backup_task",
    tags=["lan"],
    retries=3,
    retry_delay_seconds=exponential_backoff(backoff_factor=60),
    task_run_name="lan-backup",
    timeout_seconds=14400,  # 4 hours max
)
def lan_backup_task(config: AppConfig, scan_result: ScanResult, database_path: str) -> dict:
    """Execute LAN backup: WoL → Robocopy → manifest update → checksum verification.

    Args:
        config: Validated application configuration.
        scan_result: ScanResult with new/modified files.
        database_path: Path to the manifest database.

    Returns:
        Result dict with status and details.
    """
    logger = get_run_logger()

    if not config.lan_backup.enabled:
        logger.info("LAN backup disabled, skipping")
        return {"status": "LAN_SKIPPED", "message": "LAN backup disabled"}

    logger.info(f"Starting LAN backup to {config.paths.lan_destination}")

    db = ManifestDB(database_path)
    try:
        # Ensure backup server is online
        try:
            ensure_server_online(config)
        except WolTimeout as e:
            logger.error(f"Wake-on-LAN failed: {e}")
            return {"status": "LAN_FAILED", "error": str(e)}

        # Run Robocopy
        result = run_robocopy(config, scan_result, db)

        logger.info(
            f"LAN backup {result.status}: "
            f"{result.files_copied} files, "
            f"{result.bytes_copied} bytes copied"
        )

        # Verify checksums on a sample of copied files
        lan_checksum = {"verified": 0, "mismatches": 0, "errors": 0}
        if result.status in ("LAN_COMPLETE", "LAN_PARTIAL") and scan_result.has_changes:
            logger.info("Running LAN checksum verification on sampled files...")
            lan_checksum = verify_lan_checksums(
                config.paths.source_drive,
                config.paths.lan_destination,
                scan_result,
                sample_count=5,
            )
            if lan_checksum["mismatches"] > 0:
                logger.warning(
                    f"LAN checksum verification found {lan_checksum['mismatches']} mismatches "
                    f"out of {lan_checksum['verified'] + lan_checksum['mismatches']} verified"
                )
            else:
                logger.info(
                    f"LAN checksum verification passed: "
                    f"{lan_checksum['verified']} files verified"
                )

        return {
            "status": result.status,
            "exit_code": result.exit_code,
            "files_copied": result.files_copied,
            "bytes_copied": result.bytes_copied,
            "files_failed": result.files_failed,
            "lan_checksum": lan_checksum,
        }
    finally:
        db.close()
