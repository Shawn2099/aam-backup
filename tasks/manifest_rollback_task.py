"""Prefect task: pre-run manifest.db backup for rollback protection."""

import shutil
from pathlib import Path
from datetime import datetime, timezone

from prefect import task
from prefect.logging import get_run_logger


@task(
    name="pre_run_manifest_backup",
    tags=["maintenance", "rollback"],
    retries=0,
    task_run_name="pre-run-manifest-backup",
)
def pre_run_manifest_backup_task(
    database_path: str,
    log_directory: str,
    max_backups: int = 3,
) -> dict:
    """Create a pre-run backup of manifest.db for rollback protection.

    GAP #2: Before any backup operations begin, create a snapshot of the
    current manifest.db. If the backup run corrupts the manifest, this
    snapshot can be used to restore the previous state.

    Args:
        database_path: Path to the local manifest.db.
        log_directory: Directory to store rollback backups.
        max_backups: Maximum number of rollback backups to retain.

    Returns:
        Dict with backup status and path to the rollback file.
    """
    logger = get_run_logger()
    db_path = Path(database_path)

    if not db_path.exists():
        logger.warning(f"manifest.db not found at {db_path}, skipping rollback backup")
        return {"status": "SKIPPED", "reason": "database not found"}

    # Create rollback directory
    rollback_dir = Path(log_directory) / "manifest_rollbacks"
    rollback_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamped backup filename
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_name = f"manifest_pre_run_{timestamp}.db"
    backup_path = rollback_dir / backup_name

    try:
        # Copy the database file (SQLite WAL mode requires copying -wal and -shm too)
        shutil.copy2(db_path, backup_path)

        # Copy WAL and SHM files if they exist
        for suffix in ["-wal", "-shm"]:
            source_file = db_path.with_name(db_path.name + suffix)
            if source_file.exists():
                dest_file = backup_path.with_name(backup_path.name + suffix)
                shutil.copy2(source_file, dest_file)

        logger.info(f"Pre-run manifest backup created: {backup_path}")

        # Clean up old backups beyond max_backups
        _cleanup_old_backups(rollback_dir, max_backups)

        return {
            "status": "SUCCESS",
            "backup_path": str(backup_path),
            "backup_size_bytes": backup_path.stat().st_size,
        }

    except Exception as e:
        logger.error(f"Failed to create pre-run manifest backup: {e}")
        return {"status": "FAILED", "error": str(e)}


def _cleanup_old_backups(rollback_dir: Path, max_backups: int):
    """Remove oldest rollback backups beyond the retention limit.

    Args:
        rollback_dir: Directory containing rollback backups.
        max_backups: Maximum number of backups to keep.
    """
    backups = sorted(
        rollback_dir.glob("manifest_pre_run_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    for old_backup in backups[max_backups:]:
        try:
            old_backup.unlink()
            # Also remove associated WAL/SHM files
            for suffix in ["-wal", "-shm"]:
                wal_file = old_backup.with_name(old_backup.name + suffix)
                if wal_file.exists():
                    wal_file.unlink()
        except OSError:
            pass
