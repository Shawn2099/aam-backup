"""Prefect task for pre-flight checks."""

from prefect import task
from prefect.logging import get_run_logger

from core.preflight import run_preflight_checks


@task(
    name="preflight-checks",
    tags=["setup"],
    retries=1,
    retry_delay_seconds=60,
    task_run_name="preflight-checks",
)
def preflight_task(config: dict) -> dict:
    """Run pre-flight checks before backup starts.

    Returns the config if all checks pass, raises if any fail.
    """
    logger = get_run_logger()
    logger.info("Running pre-flight checks...")

    report = run_preflight_checks(config)

    if not report.all_passed:
        failures = [f"{c.name}: {c.message}" for c in report.failures]
        error_msg = "Pre-flight checks failed:\n" + "\n".join(f"  - {f}" for f in failures)
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    if report.has_warnings:
        warnings = [f"{c.name}: {c.message}" for c in report.checks if c.warning]
        for w in warnings:
            logger.warning(f"Pre-flight warning: {w}")

    logger.info("All pre-flight checks passed")
    return config
