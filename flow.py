"""Prefect flow: nightly backup orchestration."""

import os
from pathlib import Path

from loguru import logger
from prefect import flow
from prefect.task_runners import ThreadPoolTaskRunner

from core.logging_setup import configure_logging
from tasks.cloud_task import cloud_backup_task
from tasks.config_task import load_config_task
from tasks.lan_task import lan_backup_task
from tasks.preflight_task import preflight_task
from tasks.scan_task import scan_task


@flow(
    name="nightly-backup",
    task_runner=ThreadPoolTaskRunner(max_workers=2),
    log_prints=True,
    version="1.0.0",
)
def nightly_backup(config_path: str = "config.yaml") -> str:
    """Execute the nightly backup flow.

    Flow:
    1. Load and validate configuration
    2. Run pre-flight checks
    3. Scan source drive for changes
    4. If changes detected: run LAN and cloud backup concurrently
    5. Compute overall status

    Args:
        config_path: Path to config.yaml. Defaults to "config.yaml".

    Returns:
        Overall status: COMPLETE, PARTIAL_FAILURE, or FAILED.
    """
    # Configure logging
    log_dir = Path(os.environ.get("BACKUP_LOG_DIR", "logs"))
    configure_logging(log_dir)

    # Task 1: Load configuration
    config, gcs_key_path = load_config_task(config_path)

    # Task 2: Pre-flight checks
    config = preflight_task(config.model_dump())

    # Task 3: Scan drive
    scan_result = scan_task(config, config.paths.database_path)

    logger.info(
        f"Scan complete: {len(scan_result.new_files)} new, "
        f"{len(scan_result.modified_files)} modified, "
        f"{len(scan_result.deleted_files)} deleted, "
        f"{scan_result.unchanged_count} unchanged"
    )

    if not scan_result.has_changes:
        logger.info("No changes detected — backup complete")
        return "COMPLETE"

    # Tasks 4 & 5: Concurrent LAN and cloud backup
    lan_future = lan_backup_task.submit(config, scan_result, config.paths.database_path)
    cloud_future = cloud_backup_task.submit(
        config, gcs_key_path, scan_result, config.paths.database_path
    )

    lan_result = lan_future.result()
    cloud_result = cloud_future.result()

    # Compute overall status
    lan_status = lan_result.get("status", "LAN_FAILED")
    cloud_status = cloud_result.get("status", "CLOUD_FAILED")

    if lan_status in ("LAN_COMPLETE", "LAN_PARTIAL") and cloud_status in (
        "CLOUD_COMPLETE",
        "CLOUD_PARTIAL",
    ):
        overall = "COMPLETE"
    elif lan_status == "LAN_SKIPPED" and cloud_status in ("CLOUD_COMPLETE", "CLOUD_PARTIAL"):
        overall = "COMPLETE"
    elif cloud_status == "CLOUD_SKIPPED" and lan_status in ("LAN_COMPLETE", "LAN_PARTIAL"):
        overall = "COMPLETE"
    elif lan_status in ("LAN_COMPLETE", "LAN_PARTIAL", "LAN_SKIPPED") or cloud_status in (
        "CLOUD_COMPLETE",
        "CLOUD_PARTIAL",
        "CLOUD_SKIPPED",
    ):
        overall = "PARTIAL_FAILURE"
    else:
        overall = "FAILED"

    logger.info(
        f"Backup complete — LAN: {lan_status}, Cloud: {cloud_status}, Overall: {overall}"
    )

    if overall == "FAILED":
        raise RuntimeError(f"Both backup destinations failed: LAN={lan_status}, Cloud={cloud_status}")

    return overall


if __name__ == "__main__":
    nightly_backup()
