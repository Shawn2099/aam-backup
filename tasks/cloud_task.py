"""Prefect task: cloud backup via Rclone."""

from prefect import task
from prefect.logging import get_run_logger
from prefect.tasks import exponential_backoff

from core.manifest_db import ManifestDB
from core.rclone import run_rclone
from models.config_model import AppConfig
from models.scan_result import ScanResult


@task(
    name="cloud_backup_task",
    tags=["cloud"],
    retries=3,
    retry_delay_seconds=exponential_backoff(backoff_factor=60),
    task_run_name="cloud-backup",
    timeout_seconds=21600,  # 6 hours max
)
def cloud_backup_task(
    config: AppConfig,
    gcs_key_path: str,
    scan_result: ScanResult,
    database_path: str,
) -> dict:
    """Execute cloud backup: Rclone sync → manifest update.

    Args:
        config: Validated application configuration.
        gcs_key_path: Path to GCS service account JSON key.
        scan_result: ScanResult with new/modified files.
        database_path: Path to the manifest database.

    Returns:
        Result dict with status and details.
    """
    logger = get_run_logger()

    if not config.cloud_backup.enabled:
        logger.info("Cloud backup disabled, skipping")
        return {"status": "CLOUD_SKIPPED", "message": "Cloud backup disabled"}

    logger.info(f"Starting cloud backup to {config.cloud_backup.bucket}")

    db = ManifestDB(database_path)
    try:
        result = run_rclone(config, gcs_key_path, scan_result, db)

        logger.info(f"Cloud backup {result.status} (exit code {result.exit_code})")

        return {
            "status": result.status,
            "exit_code": result.exit_code,
            "output_length": len(result.output),
        }
    finally:
        db.close()
