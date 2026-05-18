"""Prefect task: SQLite manifest database maintenance."""

from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger

from core.manifest_db import ManifestDB


@task(
    name="maintain_manifest_db",
    tags=["maintenance"],
    retries=0,
    task_run_name="maintain-manifest-db",
)
def maintain_manifest_db_task(database_path: str, max_size_mb: int = 500) -> dict:
    """Perform SQLite maintenance: VACUUM, WAL checkpoint, size monitoring.

    Prevents database bloat from 200K+ daily writes.
    Should be called after each successful backup run.

    Args:
        database_path: Path to the manifest.db file.
        max_size_mb: Alert threshold for database file size.

    Returns:
        Dict with maintenance results: {"vacuumed": bool, "checkpointed": bool,
        "size_mb": float, "size_warning": bool}.
    """
    logger = get_run_logger()
    db_path = Path(database_path)

    if not db_path.exists():
        logger.warning(f"manifest.db not found at {db_path}, skipping maintenance")
        return {"status": "SKIPPED", "reason": "database not found"}

    db = ManifestDB(database_path)
    try:
        result = db.maintenance(max_size_mb=max_size_mb)

        if result.get("vacuumed"):
            logger.info("Manifest DB VACUUM completed")
        if result.get("checkpointed"):
            logger.info("Manifest DB WAL checkpoint completed")

        size_mb = result.get("size_mb", 0)
        logger.info(f"Manifest DB size: {size_mb:.1f}MB")

        if result.get("size_warning"):
            logger.warning(
                f"Manifest DB size ({size_mb:.1f}MB) exceeds threshold ({max_size_mb}MB). "
                f"Consider investigating or archiving old entries."
            )

        return {
            "status": "SUCCESS",
            **result,
        }
    finally:
        db.close()
