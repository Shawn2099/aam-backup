"""Prefect task: LAN backup via Robocopy."""

from prefect import task

from core.manifest_db import ManifestDB
from core.robocopy import run_robocopy
from core.wol import ensure_server_online, WolTimeout
from models.config_model import AppConfig
from models.scan_result import ScanResult


@task(name="lan_backup_task", tags=["lan"], retries=0)
def lan_backup_task(config: AppConfig, scan_result: ScanResult, database_path: str) -> dict:
    """Execute LAN backup: WoL → Robocopy → manifest update.

    Args:
        config: Validated application configuration.
        scan_result: ScanResult with new/modified files.
        database_path: Path to the manifest database.

    Returns:
        Result dict with status and details.
    """
    if not config.lan_backup.enabled:
        return {"status": "LAN_SKIPPED", "message": "LAN backup disabled"}

    db = ManifestDB(database_path)
    try:
        # Ensure backup server is online
        try:
            ensure_server_online(config)
        except WolTimeout as e:
            return {"status": "LAN_FAILED", "error": str(e)}

        # Run Robocopy
        result = run_robocopy(config, scan_result, db)

        return {
            "status": result.status,
            "exit_code": result.exit_code,
            "files_copied": result.files_copied,
            "bytes_copied": result.bytes_copied,
            "files_failed": result.files_failed,
        }
    finally:
        db.close()
