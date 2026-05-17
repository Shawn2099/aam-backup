"""Prefect task for pre-flight checks."""

from prefect import task

from core.preflight import run_preflight_checks


@task(name="preflight-checks", retries=0)
def preflight_task(config: dict) -> dict:
    """Run pre-flight checks before backup starts.

    Returns the config if all checks pass, raises if any fail.
    """
    report = run_preflight_checks(config)

    if not report.all_passed:
        failures = [f"{c.name}: {c.message}" for c in report.failures]
        raise RuntimeError(
            f"Pre-flight checks failed:\n" + "\n".join(f"  - {f}" for f in failures)
        )

    return config
