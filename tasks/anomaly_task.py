"""Prefect task: anomaly detection for backup scan patterns."""

from prefect import task
from prefect.logging import get_run_logger

from core.anomaly import detect_anomalies
from models.config_model import AppConfig


@task(
    name="anomaly_detection",
    tags=["monitoring", "anomaly"],
    retries=0,
    task_run_name="anomaly-detection",
)
def anomaly_detection_task(log_directory: str, config: AppConfig) -> dict:
    """Run anomaly detection against backup metrics history.

    Checks for:
    - File count spikes (>Nx the historical average)
    - Deletion spikes (>Nx the historical average)
    - Extended silence (consecutive zero-change runs)

    Args:
        log_directory: Directory containing backup_metrics.jsonl.
        config: Validated application configuration.

    Returns:
        Dict with anomaly detection results.
    """
    logger = get_run_logger()

    ad = config.anomaly_detection
    if not ad.enabled:
        logger.info("Anomaly detection disabled, skipping")
        return {"status": "SKIPPED", "reason": "anomaly_detection.enabled = false"}

    result = detect_anomalies(
        log_directory=log_directory,
        max_spike_ratio=ad.max_file_count_spike_ratio,
        max_deletion_ratio=ad.max_deletion_spike_ratio,
        silence_days=ad.silence_days_alert,
        lookback_days=ad.lookback_window_days,
    )

    if result.status == "OK":
        if result.baseline_info.get("reason"):
            logger.info(
                f"Anomaly detection OK: {result.baseline_info['reason']}"
            )
        else:
            logger.info(
                f"Anomaly detection OK — "
                f"{result.baseline_info.get('current_changed', 0)} changed "
                f"(avg: {result.baseline_info.get('avg_changed_per_run', 0)})"
            )
    elif result.has_anomalies:
        for detail in result.spike_details:
            logger.warning(f"ANOMALY: {detail}")
        for detail in result.silence_details:
            logger.warning(f"ANOMALY: {detail}")

    return {
        "status": result.status,
        "has_anomalies": result.has_anomalies,
        "spike_details": result.spike_details,
        "silence_details": result.silence_details,
        "baseline_info": result.baseline_info,
    }
