"""Tests for anomaly detection module (core/anomaly.py)."""

import json
from datetime import datetime, timedelta, timezone

import pytest

from core.anomaly import (
    AnomalyResult,
    RunMetrics,
    detect_anomalies,
    _load_metrics,
    _check_spike,
    _check_silence,
)


def _make_metric_line(ts: datetime, total_changed: int, deleted: int = 0,
                      overall_status: str = "COMPLETE") -> str:
    """Helper to create a valid JSONL metrics line."""
    return json.dumps({
        "timestamp": ts.isoformat(),
        "scan": {
            "total_changed": total_changed,
            "deleted": deleted,
        },
        "overall_status": overall_status,
    })


class TestRunMetrics:
    def test_from_dict_parses_complete(self):
        data = {
            "timestamp": "2025-01-15T23:00:00+00:00",
            "scan": {"total_changed": 150, "deleted": 5},
            "overall_status": "COMPLETE",
        }
        rm = RunMetrics.from_dict(data)
        assert rm.total_changed == 150
        assert rm.deleted == 5
        assert rm.overall_status == "COMPLETE"

    def test_from_dict_handles_missing_scan(self):
        data = {
            "timestamp": "2025-01-15T23:00:00+00:00",
            "overall_status": "COMPLETE",
        }
        rm = RunMetrics.from_dict(data)
        assert rm.total_changed == 0
        assert rm.deleted == 0

    def test_from_dict_fallback_timestamp(self):
        data = {"scan": {"total_changed": 5, "deleted": 0}}
        rm = RunMetrics.from_dict(data)
        assert isinstance(rm.timestamp, datetime)


class TestDetectAnomalies:
    def test_no_metrics_file_returns_ok(self, temp_dir):
        result = detect_anomalies(str(temp_dir))
        assert result.status == "OK"
        assert "No metrics history" in result.baseline_info.get("reason", "")

    def test_few_metrics_returns_ok(self, tmp_path):
        now = datetime.now(timezone.utc)
        metrics_file = tmp_path / "backup_metrics.jsonl"
        metrics_file.write_text(
            _make_metric_line(now - timedelta(days=1), 100) + "\n"
        )

        result = detect_anomalies(str(tmp_path), lookback_days=14)
        assert result.status == "OK"
        assert "Only 1 run" in result.baseline_info.get("reason", "")

    def test_normal_metrics_no_anomaly(self, tmp_path):
        now = datetime.now(timezone.utc)
        lines = []
        for i in range(10, 0, -1):
            lines.append(_make_metric_line(now - timedelta(days=i), 100 + i * 5))
        metrics_file = tmp_path / "backup_metrics.jsonl"
        metrics_file.write_text("\n".join(lines) + "\n")

        result = detect_anomalies(str(tmp_path), max_spike_ratio=5.0,
                                  lookback_days=14)
        assert result.status == "OK"
        assert not result.has_anomalies

    def test_spike_detection(self, tmp_path):
        now = datetime.now(timezone.utc)
        lines = []
        # Baseline: 9 runs averaging ~100 changes
        for i in range(9, 0, -1):
            lines.append(_make_metric_line(now - timedelta(days=i), 100))
        # Current run: 2000 changes = 20x baseline (threshold is 5x)
        lines.append(_make_metric_line(now, 2000))
        metrics_file = tmp_path / "backup_metrics.jsonl"
        metrics_file.write_text("\n".join(lines) + "\n")

        result = detect_anomalies(str(tmp_path), max_spike_ratio=5.0,
                                  lookback_days=14)
        assert result.status == "SPIKE_DETECTED"
        assert result.has_anomalies
        assert len(result.spike_details) == 1
        assert "SPIKE" in result.spike_details[0]

    def test_deletion_spike(self, tmp_path):
        now = datetime.now(timezone.utc)
        lines = []
        # Baseline: 9 runs averaging ~5 deletions
        for i in range(9, 0, -1):
            lines.append(_make_metric_line(now - timedelta(days=i), 100, deleted=5))
        # Current: 200 deletions = 40x baseline (threshold is 10x)
        lines.append(_make_metric_line(now, 100, deleted=200))
        metrics_file = tmp_path / "backup_metrics.jsonl"
        metrics_file.write_text("\n".join(lines) + "\n")

        result = detect_anomalies(str(tmp_path), max_deletion_ratio=10.0,
                                  lookback_days=14)
        assert result.status == "SPIKE_DETECTED"
        assert any("Deletion SPIKE" in d for d in result.spike_details)

    def test_silence_detection(self, tmp_path):
        now = datetime.now(timezone.utc)
        lines = []
        # 7 consecutive zero-change runs after one normal run
        lines.append(_make_metric_line(now - timedelta(days=8), 100))
        for i in range(7, 0, -1):
            lines.append(_make_metric_line(now - timedelta(days=i), 0, deleted=0))
        metrics_file = tmp_path / "backup_metrics.jsonl"
        metrics_file.write_text("\n".join(lines) + "\n")

        result = detect_anomalies(str(tmp_path), silence_days=5,
                                  lookback_days=14)
        assert result.status == "SILENCE_DETECTED"
        assert len(result.silence_details) >= 1
        assert "SILENCE" in result.silence_details[0]

    def test_silence_below_threshold_no_alert(self, tmp_path):
        now = datetime.now(timezone.utc)
        lines = []
        # 3 zero-change runs, threshold is 7
        lines.append(_make_metric_line(now - timedelta(days=4), 100))
        for i in range(3, 0, -1):
            lines.append(_make_metric_line(now - timedelta(days=i), 0, deleted=0))
        metrics_file = tmp_path / "backup_metrics.jsonl"
        metrics_file.write_text("\n".join(lines) + "\n")

        result = detect_anomalies(str(tmp_path), silence_days=7,
                                  lookback_days=14)
        assert result.status == "OK"

    def test_outside_lookback_ignored(self, tmp_path):
        now = datetime.now(timezone.utc)
        # All runs outside 3-day lookback window
        lines = []
        for i in range(10, 4, -1):
            lines.append(_make_metric_line(now - timedelta(days=i), 50))
        metrics_file = tmp_path / "backup_metrics.jsonl"
        metrics_file.write_text("\n".join(lines) + "\n")

        result = detect_anomalies(str(tmp_path), lookback_days=3)
        assert result.status == "OK"
        assert "Only" in result.baseline_info.get("reason", "")

    def test_both_spike_and_silence(self, tmp_path):
        now = datetime.now(timezone.utc)
        lines = []
        # 5 zero runs in history, then 1 spike run NOW (most recent)
        for i in range(5, 0, -1):
            lines.append(_make_metric_line(now - timedelta(days=i), 0))
        lines.append(_make_metric_line(now, 5000))  # spike IS current run
        metrics_file = tmp_path / "backup_metrics.jsonl"
        metrics_file.write_text("\n".join(lines) + "\n")

        result = detect_anomalies(str(tmp_path), max_spike_ratio=3.0,
                                  silence_days=3, lookback_days=14)
        assert result.status == "SPIKE_DETECTED"
        assert len(result.spike_details) == 1
        # Silence: consecutive zeros at END of list → current is 5000 (non-zero) → no silence
        assert len(result.silence_details) == 0


class TestCheckSpike:
    def test_no_history_returns_empty(self):
        current = RunMetrics(datetime.now(timezone.utc), 100, 5, "COMPLETE")
        result = _check_spike(current, [], 5.0, 10.0)
        assert result == []

    def test_normal_within_range(self):
        now = datetime.now(timezone.utc)
        history = [RunMetrics(now - timedelta(days=i), 100, 5, "COMPLETE")
                   for i in range(5, 0, -1)]
        current = RunMetrics(now, 120, 6, "COMPLETE")
        result = _check_spike(current, history, 5.0, 10.0)
        assert result == []

    def test_baseline_zero_avg_with_spike_detected(self):
        """Spike after all-zero history: effective avg=1, ratio=50/1=50 > threshold."""
        now = datetime.now(timezone.utc)
        history = [RunMetrics(now - timedelta(days=i), 0, 0, "COMPLETE")
                   for i in range(5, 0, -1)]
        current = RunMetrics(now, 50, 0, "COMPLETE")
        result = _check_spike(current, history, 5.0, 10.0)
        # 50 / effective_avg(1) = 50x > 5x threshold → SPIKE
        assert len(result) == 1
        assert "SPIKE" in result[0]
