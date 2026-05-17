"""Prefect task: post-backup integrity verification."""

from prefect import task
from prefect.logging import get_run_logger

from core.rclone import run_rclone_check
from models.config_model import AppConfig


@task(
    name="verify_cloud_integrity",
    tags=["verification"],
    retries=1,
    retry_delay_seconds=60,
    task_run_name="verify-cloud-integrity",
    timeout_seconds=21600,  # 6 hours max
)
def verify_cloud_integrity_task(config: AppConfig, gcs_key_path: str) -> dict:
    """Run rclone check to verify cloud backup integrity.

    Compares source drive against GCS bucket to detect:
    - Missing files (on source but not in cloud)
    - Mismatched files (different size or hash)

    Args:
        config: Validated application configuration.
        gcs_key_path: Path to GCS service account JSON key.

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

    return result
