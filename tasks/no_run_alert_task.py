"""Prefect task: alert if backup hasn't run for configured number of days."""

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

from prefect import task
from prefect.logging import get_run_logger


@task(
    name="check_backup_not_run_alert",
    tags=["monitoring", "alerts"],
    retries=0,
    task_run_name="check-backup-not-run-alert",
)
def check_backup_not_run_alert_task(
    log_directory: str,
    warning_days: int = 2,
) -> dict:
    """Check if backup hasn't run for the configured number of days.

    GAP #3: Monitors for "backup didn't run" scenarios by checking the
    last successful backup timestamp from metrics logs.

    Args:
        log_directory: Directory containing metrics JSONL files.
        warning_days: Number of days without a backup before alerting.

    Returns:
        Dict with alert status and details.
    """
    logger = get_run_logger()
    log_dir = Path(log_directory)
    metrics_file = log_dir / "backup_metrics.jsonl"

    if not metrics_file.exists():
        logger.warning(f"Metrics file not found: {metrics_file}")
        return {
            "status": "UNKNOWN",
            "reason": "metrics file not found",
            "warning_days": warning_days,
        }

    # Find the most recent successful backup from metrics file
    last_success_time = _find_last_successful_backup(metrics_file)

    if last_success_time is None:
        logger.warning("No successful backup runs found in metrics history")
        return {
            "status": "ALERT",
            "message": "No backup runs have ever been recorded",
            "warning_days": warning_days,
        }

    # Check if we've exceeded the warning threshold
    now = datetime.now(timezone.utc)
    days_since_last_run = (now - last_success_time).total_seconds() / 86400

    if days_since_last_run > warning_days:
        alert_msg = (
            f"Backup has not run for {days_since_last_run:.1f} days "
            f"(threshold: {warning_days} days). "
            f"Last successful run: {last_success_time.isoformat()}"
        )
        logger.warning(alert_msg)
        return {
            "status": "ALERT",
            "message": alert_msg,
            "last_success_time": last_success_time.isoformat(),
            "days_since_last_run": round(days_since_last_run, 1),
            "warning_days": warning_days,
        }

    logger.info(
        f"Backup run check OK: last run {days_since_last_run:.1f} days ago "
        f"(threshold: {warning_days} days)"
    )
    return {
        "status": "OK",
        "last_success_time": last_success_time.isoformat(),
        "days_since_last_run": round(days_since_last_run, 1),
        "warning_days": warning_days,
    }


def _find_last_successful_backup(metrics_file: Path) -> datetime | None:
    """Find the timestamp of the last successful backup from metrics file.

    Args:
        metrics_file: Path to the backup_metrics.jsonl file.

    Returns:
        Datetime of last successful backup, or None if not found.
    """
    last_time = None

    if not metrics_file.exists():
        return None

    try:
        with open(metrics_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("overall_status") in ("COMPLETE", "PARTIAL_FAILURE"):
                        run_time = entry.get("timestamp")
                        if run_time:
                            run_dt = datetime.fromisoformat(run_time.replace("Z", "+00:00"))
                            if last_time is None or run_dt > last_time:
                                last_time = run_dt
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass

    return last_time
