"""Prefect task: scan source drive for changes."""

from prefect import task

from core.manifest_db import ManifestDB
from core.scanner import scan_drive
from models.config_model import AppConfig
from models.scan_result import ScanResult


@task(name="scan_task", tags=["scan"], retries=0)
def scan_task(config: AppConfig, database_path: str) -> ScanResult:
    """Scan source drive and detect new/modified/deleted files.

    Args:
        config: Validated application configuration.
        database_path: Path to the manifest database.

    Returns:
        ScanResult with file classifications.
    """
    db = ManifestDB(database_path)
    try:
        result = scan_drive(config, db)
        return result
    finally:
        db.close()
