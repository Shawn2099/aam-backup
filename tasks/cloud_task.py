"""Prefect task: cloud backup via Rclone."""

from prefect import task

from core.manifest_db import ManifestDB
from core.rclone import run_rclone
from models.config_model import AppConfig
from models.scan_result import ScanResult


@task(name="cloud_backup_task", tags=["cloud"], retries=0)
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
    if not config.cloud_backup.enabled:
        return {"status": "CLOUD_SKIPPED", "message": "Cloud backup disabled"}

    db = ManifestDB(database_path)
    try:
        result = run_rclone(config, gcs_key_path, scan_result, db)

        return {
            "status": result.status,
            "exit_code": result.exit_code,
            "output_length": len(result.output),
        }
    finally:
        db.close()
