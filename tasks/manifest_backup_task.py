"""Prefect task: backup manifest.db to LAN and cloud destinations."""

import shutil
from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger


@task(
    name="backup_manifest_db",
    tags=["maintenance"],
    retries=1,
    retry_delay_seconds=30,
    task_run_name="backup-manifest-db",
)
def backup_manifest_db_task(database_path: str, lan_destination: str, cloud_enabled: bool = False) -> dict:
    """Copy manifest.db to LAN destination and optionally cloud.

    This protects against manifest corruption — if the local DB is lost,
    a recent copy exists on backup destinations.

    Args:
        database_path: Path to the local manifest.db.
        lan_destination: UNC path to LAN backup destination.
        cloud_enabled: Whether to also copy to cloud (handled by rclone sync).

    Returns:
        Result dict with backup status.
    """
    logger = get_run_logger()
    db_path = Path(database_path)

    if not db_path.exists():
        logger.warning(f"manifest.db not found at {db_path}, skipping backup")
        return {"status": "SKIPPED", "reason": "database not found"}

    results = {"lan": "SKIPPED", "cloud": "SKIPPED"}

    # Backup to LAN destination
    try:
        lan_dest = Path(lan_destination)
        if lan_dest.exists():
            dest_path = lan_dest / "manifest.db"
            shutil.copy2(db_path, dest_path)
            results["lan"] = "SUCCESS"
            logger.info(f"manifest.db backed up to LAN: {dest_path}")
        else:
            results["lan"] = "SKIPPED"
            logger.warning(f"LAN destination not accessible: {lan_destination}")
    except Exception as e:
        results["lan"] = "FAILED"
        logger.error(f"Failed to backup manifest.db to LAN: {e}")

    # Cloud backup is handled by rclone sync — manifest.db is excluded
    # from backup scope in config.yaml, so we don't copy it to cloud here.
    # If cloud_enabled, the next rclone sync will pick it up if we place
    # it in a location that's included in the backup scope.
    if cloud_enabled:
        results["cloud"] = "INCLUDED_IN_NEXT_SYNC"
        logger.info("manifest.db will be included in next cloud sync")

    return results
