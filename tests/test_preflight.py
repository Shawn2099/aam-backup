"""Tests for pre-flight checks."""

import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from core.preflight import (
    CheckResult,
    PreflightReport,
    check_source_drive,
    check_lan_destination,
    check_gcs_connectivity,
    check_binaries,
    check_database,
    check_log_directory,
    run_preflight_checks,
)


# --- CheckResult tests ---


def test_check_result_defaults():
    """CheckResult has correct defaults."""
    result = CheckResult(name="Test", passed=True, message="OK")
    assert result.warning is False


# --- PreflightReport tests ---


def test_preflight_report_all_passed():
    """PreflightReport.all_passed is True when all checks pass."""
    report = PreflightReport(
        checks=[
            CheckResult(name="A", passed=True, message="OK"),
            CheckResult(name="B", passed=True, message="OK"),
        ]
    )
    assert report.all_passed is True
    assert report.has_warnings is False
    assert len(report.failures) == 0


def test_preflight_report_with_failure():
    """PreflightReport.all_passed is False when any check fails."""
    report = PreflightReport(
        checks=[
            CheckResult(name="A", passed=True, message="OK"),
            CheckResult(name="B", passed=False, message="Failed"),
        ]
    )
    assert report.all_passed is False
    assert len(report.failures) == 1
    assert report.failures[0].name == "B"


def test_preflight_report_with_warning():
    """PreflightReport.has_warnings is True when any check has warnings."""
    report = PreflightReport(
        checks=[
            CheckResult(name="A", passed=True, message="OK", warning=True),
        ]
    )
    assert report.has_warnings is True
    assert report.all_passed is True


def test_preflight_report_summary():
    """PreflightReport.summary generates readable output."""
    report = PreflightReport(
        checks=[
            CheckResult(name="Test", passed=True, message="OK"),
        ]
    )
    summary = report.summary()
    assert "PASS" in summary
    assert "Test" in summary


# --- check_source_drive tests ---


def test_check_source_drive_valid(tmp_path):
    """check_source_drive passes for valid directory."""
    result = check_source_drive(str(tmp_path))
    assert result.passed is True
    assert "GB" in result.message


def test_check_source_drive_invalid():
    """check_source_drive fails for non-existent path."""
    result = check_source_drive("/nonexistent/path/that/does/not/exist")
    assert result.passed is False
    assert "not found" in result.message.lower()


# --- check_lan_destination tests ---


def test_check_lan_linux_ping_success():
    """check_lan_destination uses ping on Linux."""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = check_lan_destination("\\\\server\\share", "192.168.1.1")
            assert result.passed is True
            assert "reachable" in result.message


def test_check_lan_linux_ping_failure():
    """check_lan_destination fails when ping fails."""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            result = check_lan_destination("\\\\server\\share", "192.168.1.1")
            assert result.passed is False
            assert "not reachable" in result.message


def test_check_lan_timeout():
    """check_lan_destination handles ping timeout."""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("ping", 10)):
            result = check_lan_destination("\\\\server\\share", "192.168.1.1")
            assert result.passed is False
            assert "timed out" in result.message


# --- check_gcs_connectivity tests ---


def test_check_gcs_no_bucket():
    """check_gcs_connectivity fails when no bucket configured."""
    result = check_gcs_connectivity("")
    assert result.passed is False
    assert "No bucket" in result.message


def test_check_gcs_success():
    """check_gcs_connectivity passes when bucket accessible."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = check_gcs_connectivity("my-bucket")
        assert result.passed is True
        assert "accessible" in result.message


def test_check_gcs_failure():
    """check_gcs_connectivity fails when bucket inaccessible."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr="access denied")
        result = check_gcs_connectivity("my-bucket")
        assert result.passed is False


def test_check_gcs_rclone_not_found():
    """check_gcs_connectivity fails when rclone not installed."""
    with patch("subprocess.run", side_effect=FileNotFoundError):
        result = check_gcs_connectivity("my-bucket")
        assert result.passed is False
        assert "rclone" in result.message.lower()


# --- check_binaries tests ---


def test_check_binaries_linux():
    """check_binaries skips robocopy on Linux."""
    with patch("platform.system", return_value="Linux"):
        with patch("shutil.which", return_value="/usr/bin/rclone"):
            results = check_binaries()
            robocopy_check = next(r for r in results if r.name == "Robocopy")
            assert robocopy_check.passed is True
            assert robocopy_check.warning is True


def test_check_binaries_rclone_missing():
    """check_binaries fails when rclone not found."""
    with patch("platform.system", return_value="Linux"):
        with patch("shutil.which", return_value=None):
            results = check_binaries()
            rclone_check = next(r for r in results if r.name == "Rclone")
            assert rclone_check.passed is False


# --- check_database tests ---


def test_check_database_writable(tmp_path):
    """check_database passes when directory is writable."""
    db_path = str(tmp_path / "test.db")
    result = check_database(db_path)
    assert result.passed is True
    assert "writable" in result.message


def test_check_database_readonly(tmp_path):
    """check_database fails when directory is not writable."""
    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()
    readonly_dir.chmod(0o000)

    db_path = str(readonly_dir / "test.db")
    result = check_database(db_path)

    # Restore permissions so cleanup works
    readonly_dir.chmod(0o755)

    assert result.passed is False


# --- check_log_directory tests ---


def test_check_log_directory_writable(tmp_path):
    """check_log_directory passes when directory is writable."""
    log_path = str(tmp_path / "logs")
    result = check_log_directory(log_path)
    assert result.passed is True


# --- run_preflight_checks tests ---


def test_run_preflight_checks_minimal_config(tmp_path):
    """run_preflight_checks works with minimal config."""
    config = {
        "paths": {
            "source_drive": str(tmp_path),
            "lan_destination": "\\\\server\\share",
            "database_path": str(tmp_path / "manifest.db"),
            "log_directory": str(tmp_path / "logs"),
        },
        "lan_backup": {"enabled": False},
        "cloud_backup": {"enabled": False},
        "wol": {"server_ip": "192.168.1.1"},
    }

    with patch("shutil.which", return_value="/usr/bin/rclone"):
        report = run_preflight_checks(config)

    assert isinstance(report, PreflightReport)
    # Source, database, log dir should pass; LAN/GCS skipped; rclone found
    assert len(report.checks) >= 3


def test_run_preflight_checks_all_enabled(tmp_path):
    """run_preflight_checks runs all checks when everything enabled."""
    config = {
        "paths": {
            "source_drive": str(tmp_path),
            "lan_destination": "\\\\server\\share",
            "database_path": str(tmp_path / "manifest.db"),
            "log_directory": str(tmp_path / "logs"),
        },
        "lan_backup": {"enabled": True},
        "cloud_backup": {"enabled": True, "bucket": "test-bucket"},
        "wol": {"server_ip": "192.168.1.1"},
    }

    with patch("shutil.which", return_value="/usr/bin/rclone"):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            report = run_preflight_checks(config)

    # Should have more checks than minimal config
    assert len(report.checks) > 3
