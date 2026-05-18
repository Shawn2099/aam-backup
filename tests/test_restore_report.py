"""Tests for restore script and report task."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from tasks.report_task import generate_report_task


def test_generate_report_weekly(tmp_path):
    """Generate weekly report from metrics data."""
    metrics_file = tmp_path / "backup_metrics.jsonl"
    now = "2026-05-18T00:00:00+00:00"
    entries = [
        {
            "timestamp": now,
            "flow_run_id": "run-1",
            "overall_status": "COMPLETE",
            "lan_status": "LAN_COMPLETE",
            "cloud_status": "CLOUD_COMPLETE",
            "scan_new": 10,
            "scan_modified": 5,
            "scan_deleted": 2,
            "lan_files_copied": 100,
            "lan_bytes_copied": 1024 * 1024,
            "lan_files_failed": 0,
            "cloud_mismatches": 0,
            "cloud_missing": 0,
            "duration_seconds": 3600,
        },
        {
            "timestamp": now,
            "flow_run_id": "run-2",
            "overall_status": "COMPLETE",
            "lan_status": "LAN_COMPLETE",
            "cloud_status": "CLOUD_COMPLETE",
            "scan_new": 5,
            "scan_modified": 3,
            "scan_deleted": 0,
            "lan_files_copied": 50,
            "lan_bytes_copied": 512 * 1024,
            "lan_files_failed": 0,
            "cloud_mismatches": 0,
            "cloud_missing": 0,
            "duration_seconds": 1800,
        },
    ]
    with open(metrics_file, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    report = generate_report_task(str(tmp_path), report_type="weekly")

    assert report.get("status") != "SKIPPED"
    assert report["total_runs"] == 2
    assert report["successful"] == 2
    assert report["success_rate"] == 100.0
    assert report["total_new_files"] == 15
    assert report["total_modified_files"] == 8
    assert report["total_lan_files_copied"] == 150


def test_generate_report_monthly_with_failures(tmp_path):
    """Generate monthly report with mixed results."""
    metrics_file = tmp_path / "backup_metrics.jsonl"
    entries = [
        {"timestamp": "2026-05-18T00:00:00+00:00", "flow_run_id": "run-1", "overall_status": "COMPLETE", "lan_status": "LAN_COMPLETE", "cloud_status": "CLOUD_COMPLETE", "scan_new": 10, "scan_modified": 5, "scan_deleted": 0, "lan_files_copied": 100, "lan_bytes_copied": 1024, "lan_files_failed": 0, "cloud_mismatches": 0, "cloud_missing": 0, "duration_seconds": 3600},
        {"timestamp": "2026-05-17T00:00:00+00:00", "flow_run_id": "run-2", "overall_status": "FAILED", "lan_status": "LAN_FAILED", "cloud_status": "CLOUD_FAILED", "scan_new": 0, "scan_modified": 0, "scan_deleted": 0, "lan_files_copied": 0, "lan_bytes_copied": 0, "lan_files_failed": 0, "cloud_mismatches": 0, "cloud_missing": 0, "duration_seconds": 60},
        {"timestamp": "2026-05-16T00:00:00+00:00", "flow_run_id": "run-3", "overall_status": "PARTIAL_FAILURE", "lan_status": "LAN_COMPLETE", "cloud_status": "CLOUD_FAILED", "scan_new": 5, "scan_modified": 2, "scan_deleted": 0, "lan_files_copied": 50, "lan_bytes_copied": 512, "lan_files_failed": 0, "cloud_mismatches": 0, "cloud_missing": 0, "duration_seconds": 1800},
    ]
    with open(metrics_file, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    report = generate_report_task(str(tmp_path), report_type="monthly")

    assert report.get("status") != "SKIPPED"
    assert report["total_runs"] == 3
    assert report["successful"] == 1
    assert report["partial_failures"] == 1
    assert report["failures"] == 1
    assert report["success_rate"] == pytest.approx(33.3, abs=0.1)
    assert len(report["failed_run_details"]) == 1
    assert len(report["partial_run_details"]) == 1


def test_generate_report_no_metrics(tmp_path):
    """Generate report skips when no metrics file exists."""
    report = generate_report_task(str(tmp_path), report_type="weekly")
    assert report["status"] == "SKIPPED"


def test_generate_report_no_recent_runs(tmp_path):
    """Generate report skips when no runs in period."""
    metrics_file = tmp_path / "backup_metrics.jsonl"
    # Old entry (outside weekly window)
    with open(metrics_file, "w") as f:
        f.write(json.dumps({
            "timestamp": "2020-01-01T00:00:00+00:00",
            "flow_run_id": "old-run",
            "overall_status": "COMPLETE",
            "lan_status": "LAN_COMPLETE",
            "cloud_status": "CLOUD_COMPLETE",
            "scan_new": 0,
            "scan_modified": 0,
            "scan_deleted": 0,
            "lan_files_copied": 0,
            "lan_bytes_copied": 0,
            "lan_files_failed": 0,
            "cloud_mismatches": 0,
            "cloud_missing": 0,
            "duration_seconds": 0,
        }) + "\n")

    report = generate_report_task(str(tmp_path), report_type="weekly")
    assert report["status"] == "SKIPPED"
