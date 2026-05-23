"""Prefect task: periodic LAN integrity audit — random-sample checksum verification.

Samples random files from the manifest and verifies their checksums on the
LAN destination to catch silent bit-rot, partial writes, or filesystem
corruption that accumulates over time.

Only runs every N backups (configurable via lan_integrity.run_every_n_backups).
"""

from prefect import task
from prefect.logging import get_run_logger

from core.manifest_db import ManifestDB
from core.lan_integrity import audit_lan_integrity
from models.config_model import AppConfig


@task(
    name="lan_integrity_audit",
    tags=["verification", "maintenance"],
    retries=0,
    task_run_name="lan-integrity-audit",
    timeout_seconds=7200,
)
def lan_integrity_task(config: AppConfig) -> dict:
    """Periodic full-audit of LAN mirror integrity via checksum sampling.

    Args:
        config: Validated application configuration.

    Returns:
        Dict with audit results.
    """
    logger = get_run_logger()

    li = config.lan_integrity
    if not li.enabled:
        logger.info("LAN integrity audit disabled, skipping")
        return {"status": "SKIPPED", "reason": "lan_integrity.enabled = false"}

    if not config.lan_backup.enabled:
        logger.info("LAN backup disabled, skipping integrity audit")
        return {"status": "SKIPPED", "reason": "lan_backup disabled"}

    db = ManifestDB(config.paths.database_path)
    try:
        run_counter = db.get_run_counter()
        interval = li.run_every_n_backups
        if run_counter % interval != 0:
            logger.info(
                f"LAN integrity audit skipped (run #{run_counter}, "
                f"next in {interval - (run_counter % interval)} backups)"
            )
            return {"status": "SKIPPED", "run_number": run_counter}
    finally:
        db.close()

    logger.info(
        f"Starting LAN integrity audit at run #{run_counter} "
        f"(sample: {li.sample_count}, workers: {li.checksum_concurrency})"
    )

    result = audit_lan_integrity(
        database_path=config.paths.database_path,
        source_drive=config.paths.source_drive,
        lan_destination=config.paths.lan_destination,
        sample_count=li.sample_count,
        max_workers=li.checksum_concurrency,
    )

    if result.status == "MISMATCH_DETECTED":
        logger.warning(
            f"LAN integrity audit found {result.mismatches} mismatches, "
            f"{result.missing} missing files out of {result.sampled} sampled"
        )
    elif result.is_clean:
        logger.info(
            f"LAN integrity audit passed: {result.verified}/{result.sampled} verified "
            f"({result.duration_seconds}s)"
        )

    return {
        "status": result.status,
        "sampled": result.sampled,
        "verified": result.verified,
        "mismatches": result.mismatches,
        "missing": result.missing,
        "errors": result.errors,
        "duration_seconds": result.duration_seconds,
    }
