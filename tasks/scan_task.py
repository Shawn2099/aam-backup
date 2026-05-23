"""Prefect task: scan source drive for changes."""

from prefect import task
from prefect.logging import get_run_logger

from core.manifest_db import ManifestDB
from core.scanner import scan_drive
from models.config_model import AppConfig
from models.scan_result import ScanResult


@task(
    name="scan_task",
    tags=["scan"],
    retries=1,
    retry_delay_seconds=30,
    task_run_name="scan-drive",
    timeout_seconds=3600,  # 1 hour max for scanning
)
def scan_task(config: AppConfig, database_path: str) -> ScanResult:
    """Scan source drive and detect new/modified/deleted files.

    Args:
        config: Validated application configuration.
        database_path: Path to the manifest database.

    Returns:
        ScanResult with file classifications.
    """
    logger = get_run_logger()
    logger.info(f"Scanning drive: {config.paths.source_drive}")

    db = ManifestDB(database_path)
    try:
        run_number = db.get_and_increment_run_counter()
        full_rescan_interval = config.backup_scope.full_rescan_every_n_runs
        is_full_rescan = (run_number % full_rescan_interval == 0)

        if is_full_rescan:
            logger.info(
                f"Full re-scan triggered (run #{run_number}, every {full_rescan_interval} runs). "
                "Computing checksums for ALL files."
            )

        result = scan_drive(config, db, is_full_rescan=is_full_rescan)
        logger.info(
            f"Scan complete: {len(result.new_files)} new, "
            f"{len(result.modified_files)} modified, "
            f"{len(result.deleted_files)} deleted"
        )
        return result
    finally:
        db.close()
