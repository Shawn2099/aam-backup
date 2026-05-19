"""Prefect task: check for stale backup (no recent changes detected)."""

from datetime import datetime, timezone, timedelta

from prefect import task
from prefect.logging import get_run_logger

from core.manifest_db import ManifestDB


@task(
    name="check_stale_backup",
    tags=["monitoring"],
    retries=0,
    task_run_name="check-stale-backup",
)
def check_stale_backup_task(database_path: str, warning_days: int) -> dict:
    """Check if no files have been backed up within the warning threshold.

    Warns when the scanner may be misconfigured or the source drive
    has genuinely had no changes for an extended period.

    Args:
        database_path: Path to manifest.db.
        warning_days: Number of days without a backup before warning.

    Returns:
        Dict with status and details.
    """
    logger = get_run_logger()
    db_path = database_path

    db = ManifestDB(db_path)
    try:
        all_entries = db.get_all_entries()
    finally:
        db.close()

    if not all_entries:
        return {"status": "OK", "reason": "manifest is empty"}

    cutoff = datetime.now(timezone.utc) - timedelta(days=warning_days)
    cutoff_iso = cutoff.isoformat()

    recent_backup = any(
        (e.last_backed_up_lan or "") > cutoff_iso or
        (e.last_backed_up_cloud or "") > cutoff_iso
        for e in all_entries.values()
    )

    if not recent_backup:
        msg = (
            f"No file changes detected in {warning_days}+ days. "
            f"Scanner may be misconfigured or source drive unchanged. "
            f"Total files in manifest: {len(all_entries)}"
        )
        logger.warning(msg)
        return {"status": "WARNING", "message": msg, "file_count": len(all_entries)}

    return {"status": "OK", "file_count": len(all_entries)}
