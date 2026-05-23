"""Anomaly detection for backup scan patterns.

Detects suspicious file count spikes (possible ransomware/corruption, misconfiguration)
and extended silence (possible scanner failure, network outage).
Analyzes JSONL metrics history to establish baselines.
"""

import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from loguru import logger


@dataclass
class AnomalyResult:
    """Result of anomaly detection analysis."""

    status: str = "OK"
    """OK, SPIKE_DETECTED, SILENCE_DETECTED, or ERROR."""

    spike_details: list[str] = field(default_factory=list)
    """Human-readable descriptions of detected spikes."""

    silence_details: list[str] = field(default_factory=list)
    """Human-readable descriptions of detected silence."""

    baseline_info: dict = field(default_factory=dict)
    """Baseline statistics used for detection."""

    @property
    def has_anomalies(self) -> bool:
        return self.status in ("SPIKE_DETECTED", "SILENCE_DETECTED")


@dataclass
class RunMetrics:
    """Parsed metrics from a single JSONL line."""

    timestamp: datetime
    total_changed: int
    deleted: int
    overall_status: str

    @classmethod
    def from_dict(cls, data: dict) -> "RunMetrics":
        ts_str = data.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str)
        except (ValueError, TypeError):
            ts = datetime.now(timezone.utc)

        return cls(
            timestamp=ts,
            total_changed=data.get("scan", {}).get("total_changed", 0),
            deleted=data.get("scan", {}).get("deleted", 0),
            overall_status=data.get("overall_status", "UNKNOWN"),
        )


def detect_anomalies(
    log_directory: str,
    max_spike_ratio: float = 5.0,
    max_deletion_ratio: float = 10.0,
    silence_days: int = 7,
    lookback_days: int = 14,
) -> AnomalyResult:
    """Analyze backup metrics JSONL to detect anomalous scan patterns.

    Two anomaly types:
    1. File count SPIKE: current run's changed/created count exceeds
       the lookback period average by max_spike_ratio.
    2. File SILENCE: consecutive days with zero changes exceed silence_days.

    Args:
        log_directory: Directory containing backup_metrics.jsonl.
        max_spike_ratio: Max ratio of changed files vs baseline before warning.
        max_deletion_ratio: Max ratio of deleted files vs baseline before warning.
        silence_days: Consecutive zero-change days triggering a silence alert.
        lookback_days: Days of history to use for baseline calculation.

    Returns:
        AnomalyResult with status and details.
    """
    metrics_file = Path(log_directory) / "backup_metrics.jsonl"

    if not metrics_file.exists():
        return AnomalyResult(
            status="OK",
            baseline_info={
                "reason": "No metrics history available — skipping anomaly detection"
            },
        )

    try:
        metrics = _load_metrics(metrics_file, lookback_days)
    except Exception as e:
        logger.warning(f"Failed to load metrics for anomaly detection: {e}")
        return AnomalyResult(
            status="ERROR",
            spike_details=[f"Failed to load metrics: {e}"],
        )

    if len(metrics) < 2:
        return AnomalyResult(
            status="OK",
            baseline_info={
                "reason": f"Only {len(metrics)} run(s) in lookback window — need at least 2 for baseline"
            },
        )

    # Separate current run from history
    current = metrics[-1]
    history = metrics[:-1]

    # Check for spike
    spike_details = _check_spike(
        current, history, max_spike_ratio, max_deletion_ratio
    )

    # Check for silence
    silence_details = _check_silence(metrics, silence_days)

    # Build baseline info
    changed_counts = [m.total_changed for m in history]
    deleted_counts = [m.deleted for m in history]
    baseline_info = {
        "history_runs": len(history),
        "avg_changed_per_run": round(statistics.mean(changed_counts), 1) if changed_counts else 0,
        "median_changed_per_run": round(statistics.median(changed_counts), 1) if changed_counts else 0,
        "max_changed_in_history": max(changed_counts) if changed_counts else 0,
        "avg_deleted_per_run": round(statistics.mean(deleted_counts), 1) if deleted_counts else 0,
        "current_changed": current.total_changed,
        "current_deleted": current.deleted,
        "window_days": lookback_days,
    }

    if spike_details and silence_details:
        return AnomalyResult(
            status="SPIKE_DETECTED",
            spike_details=spike_details,
            silence_details=silence_details,
            baseline_info=baseline_info,
        )
    elif spike_details:
        return AnomalyResult(
            status="SPIKE_DETECTED",
            spike_details=spike_details,
            baseline_info=baseline_info,
        )
    elif silence_details:
        return AnomalyResult(
            status="SILENCE_DETECTED",
            silence_details=silence_details,
            baseline_info=baseline_info,
        )

    return AnomalyResult(status="OK", baseline_info=baseline_info)


def _load_metrics(metrics_file: Path, lookback_days: int) -> list[RunMetrics]:
    """Load and parse metrics from JSONL within the lookback window."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    metrics: list[RunMetrics] = []

    with open(metrics_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                rm = RunMetrics.from_dict(data)
                if rm.timestamp >= cutoff:
                    metrics.append(rm)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue

    metrics.sort(key=lambda m: m.timestamp)
    return metrics


def _check_spike(
    current: RunMetrics,
    history: list[RunMetrics],
    max_spike_ratio: float,
    max_deletion_ratio: float,
) -> list[str]:
    """Check if current run has anomalous file count or deletion spikes."""
    details: list[str] = []

    if not history:
        return details

    changed_counts = [m.total_changed for m in history]
    deleted_counts = [m.deleted for m in history]

    # Use effective average: if history is all-zero, use floor of 1 so a burst
    # after silence still triggers. Requires at least 2 history runs.
    if len(history) < 2:
        return details

    avg_changed = statistics.mean(changed_counts) if changed_counts else 0
    effective_avg_changed = max(avg_changed, 1)
    avg_deleted = statistics.mean(deleted_counts) if deleted_counts else 0
    effective_avg_deleted = max(avg_deleted, 1)

    if current.total_changed > 0:
        ratio = current.total_changed / effective_avg_changed
        if ratio > max_spike_ratio:
            details.append(
                f"File count SPIKE: {current.total_changed} files changed "
                f"(vs baseline avg of {avg_changed:.0f} over {len(history)} runs). "
                f"Ratio: {ratio:.1f}x. Threshold: {max_spike_ratio:.1f}x. "
                f"This could indicate ransomware, mass corruption, or misconfiguration."
            )

    if current.deleted > 0:
        deletion_ratio = current.deleted / effective_avg_deleted
        if deletion_ratio > max_deletion_ratio:
            details.append(
                f"Deletion SPIKE: {current.deleted} files deleted "
                f"(vs baseline avg of {avg_deleted:.0f} over {len(history)} runs). "
                f"Ratio: {deletion_ratio:.1f}x. Threshold: {max_deletion_ratio:.1f}x. "
                f"This could indicate mass data loss or exclusion config drift."
            )

    return details


def _check_silence(
    metrics: list[RunMetrics],
    silence_days: int,
) -> list[str]:
    """Check for extended periods with zero file changes."""
    details: list[str] = []

    # Count zero-change runs in reverse chronological order
    consecutive_zeros = 0
    for m in reversed(metrics):
        if m.total_changed == 0:
            consecutive_zeros += 1
        else:
            break

    if consecutive_zeros >= silence_days:
        details.append(
            f"Extended SILENCE: {consecutive_zeros} consecutive backups "
            f"with zero file changes (threshold: {silence_days}). "
            f"Scanner may have failed silently, source drive may be unmounted, "
            f"or exclusions may be over-matching."
        )

        # Add detail about last changed run if available
        if consecutive_zeros < len(metrics):
            last_changed = metrics[-(consecutive_zeros + 1)]
            days_since = (datetime.now(timezone.utc) - last_changed.timestamp).days
            details.append(
                f"Last backup with changes was {days_since} days ago "
                f"({last_changed.total_changed} files changed)."
            )

    return details
