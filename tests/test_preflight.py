"""Tests for comprehensive pre-flight checks."""

import socket
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from core.preflight import (
    Severity,
    CheckResult,
    PreflightReport,
    check_disk_space,
    check_time_sync,
    check_system_memory,
    check_source_drive,
    check_lan_destination,
    check_temp_directory,
    check_dns_resolution,
    check_port_connectivity,
    check_ping,
    check_credential_manager,
    check_smtp_config,
    check_vss_service,
    check_prefect_worker,
    check_gcs_connectivity,
    check_gcs_versioning,
    check_rclone_version,
    check_config_completeness,
    check_database,
    check_log_directory,
    check_binaries,
    run_preflight_checks,
)


# --- CheckResult tests ---


def test_check_result_defaults():
    """CheckResult has correct defaults."""
    result = CheckResult(
        category="Test",
        name="Test",
        severity=Severity.PASS,
        message="OK",
    )
    assert result.passed is True
    assert result.is_warning is False
    assert result.is_failure is False
    assert result.details == ""
    assert result.metric is None
    assert result.threshold is None


def test_check_result_severity_levels():
    """CheckResult correctly identifies severity levels."""
    p = CheckResult(category="T", name="T", severity=Severity.PASS, message="")
    s = CheckResult(category="T", name="T", severity=Severity.SKIP, message="")
    w = CheckResult(category="T", name="T", severity=Severity.WARN, message="")
    f = CheckResult(category="T", name="T", severity=Severity.FAIL, message="")

    # PASS, SKIP, and WARN are considered "passed" (warnings don't block)
    assert p.passed is True
    assert s.passed is True
    assert w.passed is True
    assert f.passed is False

    # Severity identification
    assert w.is_warning is True
    assert f.is_failure is True
    assert p.is_warning is False
    assert p.is_failure is False


# --- PreflightReport tests ---


def test_preflight_report_all_passed():
    """PreflightReport.all_passed is True when no failures."""
    report = PreflightReport(
        checks=[
            CheckResult(category="A", name="A", severity=Severity.PASS, message="OK"),
            CheckResult(category="B", name="B", severity=Severity.WARN, message="Warn"),
        ]
    )
    assert report.all_passed is True
    assert report.has_warnings is True
    assert len(report.failures) == 0
    assert len(report.warnings) == 1


def test_preflight_report_with_failure():
    """PreflightReport.all_passed is False when any check fails."""
    report = PreflightReport(
        checks=[
            CheckResult(category="A", name="A", severity=Severity.PASS, message="OK"),
            CheckResult(category="B", name="B", severity=Severity.FAIL, message="Failed"),
        ]
    )
    assert report.all_passed is False
    assert len(report.failures) == 1
    assert report.failures[0].name == "B"


def test_preflight_report_skipped():
    """PreflightReport.skipped returns skipped checks."""
    report = PreflightReport(
        checks=[
            CheckResult(category="A", name="A", severity=Severity.SKIP, message="Skipped"),
            CheckResult(category="B", name="B", severity=Severity.PASS, message="OK"),
        ]
    )
    assert len(report.skipped) == 1
    assert report.skipped[0].name == "A"


def test_preflight_report_summary():
    """PreflightReport.summary generates readable output."""
    report = PreflightReport(
        checks=[
            CheckResult(category="Test", name="Test", severity=Severity.PASS, message="OK"),
        ]
    )
    summary = report.summary()
    assert "PASS" in summary
    assert "Test" in summary
    assert "Pre-Flight Check Report" in summary


def test_preflight_report_to_dict():
    """PreflightReport.to_dict returns serializable dict."""
    report = PreflightReport(
        checks=[
            CheckResult(category="Test", name="Test", severity=Severity.PASS, message="OK"),
        ]
    )
    d = report.to_dict()
    assert d["all_passed"] is True
    assert d["total_checks"] == 1
    assert d["passed"] == 1
    assert d["warnings"] == 0
    assert d["failures"] == 0
    assert len(d["checks"]) == 1


# --- System Health Checks ---


def test_check_disk_space_sufficient(tmp_path):
    """check_disk_space passes when enough space available."""
    result = check_disk_space(str(tmp_path), min_free_gb=0.001)
    assert result.severity == Severity.PASS
    assert result.metric is not None


def test_check_disk_space_insufficient(tmp_path):
    """check_disk_space fails when space is below threshold."""
    result = check_disk_space(str(tmp_path), min_free_gb=999999.0)
    assert result.severity == Severity.FAIL
    assert result.metric is not None
    assert result.threshold is not None


def test_check_disk_space_invalid_path():
    """check_disk_space fails for invalid path."""
    result = check_disk_space("/nonexistent/path/that/does/not/exist", min_free_gb=1.0)
    assert result.severity == Severity.FAIL


def test_check_time_sync_no_ntplib():
    """check_time_sync warns when ntplib not installed."""
    with patch("core.preflight.ntplib", None):
        result = check_time_sync()
        assert result.severity == Severity.WARN


def test_check_system_memory_no_psutil():
    """check_system_memory skips when psutil not installed."""
    with patch("core.preflight.psutil", None):
        result = check_system_memory()
        assert result.severity == Severity.SKIP


def test_check_system_memory_with_psutil():
    """check_system_memory works when psutil is available."""
    mock_mem = MagicMock()
    mock_mem.available = 1024 * 1024 * 1024  # 1GB
    mock_mem.total = 16 * 1024 * 1024 * 1024  # 16GB
    mock_mem.percent = 50

    mock_psutil = MagicMock()
    mock_psutil.virtual_memory.return_value = mock_mem

    with patch("core.preflight.psutil", mock_psutil):
        result = check_system_memory()
        assert result.severity == Severity.PASS
        assert result.metric is not None


# --- Storage Checks ---


def test_check_source_drive_valid(tmp_path):
    """check_source_drive passes for valid directory."""
    result = check_source_drive(str(tmp_path))
    assert result.severity == Severity.PASS


def test_check_source_drive_invalid():
    """check_source_drive fails for non-existent path."""
    result = check_source_drive("/nonexistent/path/that/does/not/exist")
    assert result.severity == Severity.FAIL
    assert "not found" in result.message.lower()


def test_check_lan_linux_ping_success():
    """check_lan_destination uses ping on Linux."""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = check_lan_destination("\\\\server\\share", "192.168.1.1")
            assert result.severity == Severity.PASS
            assert "reachable" in result.message


def test_check_lan_linux_ping_failure():
    """check_lan_destination fails when ping fails."""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            result = check_lan_destination("\\\\server\\share", "192.168.1.1")
            assert result.severity == Severity.FAIL


def test_check_lan_dns_failure():
    """check_lan_destination fails when DNS resolution fails."""
    with patch("socket.gethostbyname", side_effect=socket.gaierror):
        result = check_lan_destination("\\\\server\\share", "invalid-hostname")
        assert result.severity == Severity.FAIL
        assert "Cannot resolve" in result.message


def test_check_temp_directory_valid(tmp_path):
    """check_temp_directory passes for writable directory."""
    temp_path = str(tmp_path / "temp")
    result = check_temp_directory(temp_path)
    assert result.severity == Severity.PASS


# --- Network Checks ---


def test_check_dns_resolution_success():
    """check_dns_resolution passes for valid hostname."""
    with patch("socket.gethostbyname", return_value="127.0.0.1"):
        result = check_dns_resolution("localhost")
        assert result.severity == Severity.PASS
        assert "127.0.0.1" in result.message


def test_check_dns_resolution_failure():
    """check_dns_resolution fails for invalid hostname."""
    with patch("socket.gethostbyname", side_effect=socket.gaierror):
        result = check_dns_resolution("invalid.host.that.does.not.exist")
        assert result.severity == Severity.FAIL


def test_check_port_connectivity_success():
    """check_port_connectivity passes for open port."""
    with patch("socket.create_connection"):
        result = check_port_connectivity("localhost", 80)
        assert result.severity == Severity.PASS


def test_check_port_connectivity_failure():
    """check_port_connectivity fails for closed port."""
    with patch("socket.create_connection", side_effect=ConnectionRefusedError):
        result = check_port_connectivity("localhost", 99999)
        assert result.severity == Severity.FAIL


def test_check_ping_success():
    """check_ping passes when ping succeeds."""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="rtt min/avg/max/mdev = 1.0/2.5/4.0/1.0 ms",
            )
            result = check_ping("127.0.0.1", count=1)
            assert result.severity == Severity.PASS
            assert "packets received" in result.message


def test_check_ping_failure():
    """check_ping fails when ping fails."""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="")
            result = check_ping("192.0.2.1", count=1)
            assert result.severity == Severity.FAIL


def test_check_ping_timeout():
    """check_ping handles timeout."""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("ping", 10)):
            result = check_ping("192.0.2.1", count=1)
            assert result.severity == Severity.FAIL
            assert "timed out" in result.message


# --- Credential Checks ---


def test_check_credential_manager_non_windows():
    """check_credential_manager warns on non-Windows."""
    with patch("platform.system", return_value="Linux"):
        result = check_credential_manager("TestCred")
        assert result.severity == Severity.WARN


def test_check_credential_manager_found():
    """check_credential_manager passes when credential exists."""
    with patch("platform.system", return_value="Windows"):
        with patch("keyring.get_password", return_value="secret"):
            result = check_credential_manager("TestCred")
            assert result.severity == Severity.PASS


def test_check_credential_manager_missing():
    """check_credential_manager fails when credential missing."""
    with patch("platform.system", return_value="Windows"):
        with patch("keyring.get_password", return_value=None):
            result = check_credential_manager("TestCred")
            assert result.severity == Severity.FAIL


def test_check_smtp_config_incomplete():
    """check_smtp_config warns when config is incomplete."""
    config = {"smtp_host": "", "smtp_port": 587, "smtp_username": "", "sender": "", "recipients": []}
    result = check_smtp_config(config)
    assert result.severity == Severity.WARN
    assert "not fully configured" in result.message


def test_check_smtp_config_reachable():
    """check_smtp_config passes when SMTP server is reachable."""
    config = {
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "smtp_username": "user",
        "sender": "user@example.com",
        "recipients": ["admin@example.com"],
    }
    mock_server = MagicMock()
    with patch("smtplib.SMTP", return_value=mock_server):
        result = check_smtp_config(config)
        assert result.severity == Severity.PASS


def test_check_smtp_config_unreachable():
    """check_smtp_config warns when SMTP server is unreachable."""
    config = {
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "smtp_username": "user",
        "sender": "user@example.com",
        "recipients": ["admin@example.com"],
    }
    with patch("smtplib.SMTP", side_effect=ConnectionRefusedError):
        result = check_smtp_config(config)
        assert result.severity == Severity.WARN


# --- Service Checks ---


def test_check_vss_service_non_windows():
    """check_vss_service skips on non-Windows."""
    with patch("platform.system", return_value="Linux"):
        result = check_vss_service()
        assert result.severity == Severity.SKIP


def test_check_vss_service_running():
    """check_vss_service passes when VSS is running."""
    with patch("platform.system", return_value="Windows"):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="STATE: 4 RUNNING")
            result = check_vss_service()
            assert result.severity == Severity.PASS


def test_check_vss_service_not_running():
    """check_vss_service warns when VSS is not running."""
    with patch("platform.system", return_value="Windows"):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="STATE: 1 STOPPED")
            result = check_vss_service()
            assert result.severity == Severity.WARN


def test_check_prefect_worker_reachable():
    """check_prefect_worker passes when API is reachable."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_response):
        result = check_prefect_worker("http://127.0.0.1:4200/api")
        assert result.severity == Severity.PASS


def test_check_prefect_worker_unreachable_fallback():
    """check_prefect_worker falls back to port check."""
    with patch("urllib.request.urlopen", side_effect=Exception):
        with patch("socket.create_connection"):
            result = check_prefect_worker("http://127.0.0.1:4200/api")
            assert result.severity == Severity.PASS


def test_check_prefect_worker_unreachable():
    """check_prefect_worker warns when API is unreachable."""
    with patch("urllib.request.urlopen", side_effect=Exception):
        with patch("socket.create_connection", side_effect=ConnectionRefusedError):
            result = check_prefect_worker("http://127.0.0.1:4200/api")
            assert result.severity == Severity.WARN


# --- GCS Checks ---


def test_check_gcs_no_bucket():
    """check_gcs_connectivity fails when no bucket configured."""
    result = check_gcs_connectivity("")
    assert result.severity == Severity.FAIL
    assert "No bucket" in result.message


def test_check_gcs_success():
    """check_gcs_connectivity passes when bucket accessible (read + write)."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")
        with patch("tempfile.NamedTemporaryFile") as mock_tmp:
            mock_tmp.return_value.__enter__ = MagicMock(
                return_value=MagicMock(write=MagicMock(), close=MagicMock(), name="/tmp/test.preflight")
            )
            mock_tmp.return_value.__exit__ = MagicMock(return_value=False)
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.unlink"):
                    result = check_gcs_connectivity("my-bucket")
                    assert result.severity == Severity.PASS
                    assert "accessible" in result.message


def test_check_gcs_write_failure():
    """check_gcs_connectivity fails when bucket is readable but not writable."""
    call_count = [0]
    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return MagicMock(returncode=0, stderr="", stdout="")  # lsd succeeds
        else:
            return MagicMock(returncode=1, stderr="permission denied")  # copyto fails

    with patch("subprocess.run", side_effect=side_effect):
        with patch("tempfile.NamedTemporaryFile") as mock_tmp:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.preflight"
            mock_tmp.return_value.__enter__ = MagicMock(return_value=mock_file)
            mock_tmp.return_value.__exit__ = MagicMock(return_value=False)
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.unlink"):
                    result = check_gcs_connectivity("my-bucket")
                    assert result.severity == Severity.FAIL
                    assert "not writable" in result.message


def test_check_gcs_failure():
    """check_gcs_connectivity fails when bucket inaccessible."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr="access denied")
        result = check_gcs_connectivity("my-bucket")
        assert result.severity == Severity.FAIL


def test_check_gcs_rclone_not_found():
    """check_gcs_connectivity fails when rclone not installed."""
    with patch("subprocess.run", side_effect=FileNotFoundError):
        result = check_gcs_connectivity("my-bucket")
        assert result.severity == Severity.FAIL
        assert "rclone" in result.message.lower()


def test_check_gcs_timeout():
    """check_gcs_connectivity fails on timeout."""
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("rclone", 30)):
        result = check_gcs_connectivity("my-bucket")
        assert result.severity == Severity.FAIL
        assert "timed out" in result.message


def test_check_gcs_versioning_enabled():
    """check_gcs_versioning passes when versioning enabled."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="Versioning: Enabled")
        result = check_gcs_versioning("my-bucket")
        assert result.severity == Severity.PASS


def test_check_gcs_versioning_disabled():
    """check_gcs_versioning warns when versioning not enabled."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="Versioning: Disabled")
        result = check_gcs_versioning("my-bucket")
        assert result.severity == Severity.WARN


def test_check_rclone_version_found():
    """check_rclone_version passes when rclone is installed."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="rclone v1.65.0\n- os/version: linux",
        )
        result = check_rclone_version()
        assert result.severity == Severity.PASS
        assert "rclone" in result.message.lower()


def test_check_rclone_version_not_found():
    """check_rclone_version fails when rclone not installed."""
    with patch("subprocess.run", side_effect=FileNotFoundError):
        result = check_rclone_version()
        assert result.severity == Severity.FAIL


# --- Configuration Checks ---


def test_check_config_completeness_all_set():
    """check_config_completeness passes when all values set."""
    config = {
        "wol": {"mac_address": "00:11:22:33:44:55"},
        "cloud_backup": {"bucket": "my-bucket"},
        "notifications": {
            "smtp_host": "smtp.example.com",
            "smtp_username": "user",
            "sender": "user@example.com",
        },
        "backup_scope": {"exclude_folders": []},
    }
    results = check_config_completeness(config)
    # No warnings for empty values
    assert len(results) == 0


def test_check_config_completeness_missing_values():
    """check_config_completeness warns when values are missing."""
    config = {
        "wol": {"mac_address": ""},
        "cloud_backup": {"bucket": ""},
        "notifications": {
            "smtp_host": "",
            "smtp_username": "",
            "sender": "",
        },
        "backup_scope": {"exclude_folders": []},
    }
    results = check_config_completeness(config)
    assert len(results) >= 4  # At least 4 missing values
    assert all(r.severity == Severity.WARN for r in results)


# --- Database Checks ---


def test_check_database_writable(tmp_path):
    """check_database passes when directory is writable."""
    db_path = str(tmp_path / "test.db")
    result = check_database(db_path)
    assert result.severity == Severity.PASS
    assert "writable" in result.message.lower() or "will be created" in result.message.lower()


def test_check_database_existing_db(tmp_path):
    """check_database checks schema when database exists."""
    import sqlite3

    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE manifest (id INTEGER PRIMARY KEY, path TEXT)")
    cursor.execute("INSERT INTO manifest (path) VALUES ('test.txt')")
    conn.commit()
    conn.close()

    result = check_database(str(db_path))
    assert result.severity == Severity.PASS
    assert result.metric == 1.0  # One file tracked


def test_check_database_missing_table(tmp_path):
    """check_database warns when manifest table is missing."""
    import sqlite3

    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE other_table (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

    result = check_database(str(db_path))
    assert result.severity == Severity.WARN
    assert "manifest table missing" in result.message.lower()


def test_check_log_directory_writable(tmp_path):
    """check_log_directory passes when directory is writable."""
    log_path = str(tmp_path / "logs")
    result = check_log_directory(log_path)
    assert result.severity == Severity.PASS


# --- Binary Checks ---


def test_check_binaries_linux():
    """check_binaries skips robocopy on Linux."""
    with patch("platform.system", return_value="Linux"):
        with patch("shutil.which", return_value="/usr/bin/rclone"):
            results = check_binaries()
            robocopy_check = next(r for r in results if r.name == "Robocopy")
            assert robocopy_check.severity == Severity.SKIP

            rclone_check = next(r for r in results if r.name == "Rclone")
            assert rclone_check.severity == Severity.PASS


def test_check_binaries_rclone_missing():
    """check_binaries fails when rclone not found."""
    with patch("platform.system", return_value="Linux"):
        with patch("shutil.which", return_value=None):
            results = check_binaries()
            rclone_check = next(r for r in results if r.name == "Rclone")
            assert rclone_check.severity == Severity.FAIL


def test_check_binaries_python_version():
    """check_binaries includes Python version."""
    with patch("platform.system", return_value="Linux"):
        with patch("shutil.which", return_value="/usr/bin/rclone"):
            results = check_binaries()
            python_check = next(r for r in results if r.name == "Python")
            assert python_check.severity == Severity.PASS


# --- Main Runner ---


def test_run_preflight_checks_minimal_config(tmp_path):
    """run_preflight_checks works with minimal config."""
    config = {
        "paths": {
            "source_drive": str(tmp_path),
            "lan_destination": "\\\\server\\share",
            "database_path": str(tmp_path / "manifest.db"),
            "log_directory": str(tmp_path / "logs"),
            "rclone_temp_directory": str(tmp_path / "temp"),
        },
        "lan_backup": {"enabled": False},
        "cloud_backup": {"enabled": False},
        "wol": {"server_ip": "127.0.0.1"},
        "vss": {"enabled": False},
        "ui": {"prefect_api_url": "http://127.0.0.1:4200/api"},
        "notifications": {
            "smtp_host": "",
            "smtp_port": 587,
            "smtp_username": "",
            "sender": "",
            "recipients": [],
        },
        "cloud_credentials": {"credential_name": "TestCred"},
        "backup_scope": {"exclude_folders": []},
    }

    with patch("shutil.which", return_value="/usr/bin/rclone"):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        with patch("socket.create_connection"):
            with patch("socket.gethostbyname", return_value="127.0.0.1"):
                with patch("core.preflight.psutil", None):
                    report = run_preflight_checks(config)

    assert isinstance(report, PreflightReport)
    assert report.duration_seconds > 0
    assert report.completed_at is not None
    assert len(report.checks) >= 5


def test_run_preflight_checks_all_enabled(tmp_path):
    """run_preflight_checks runs all checks when everything enabled."""
    config = {
        "paths": {
            "source_drive": str(tmp_path),
            "lan_destination": "\\\\server\\share",
            "database_path": str(tmp_path / "manifest.db"),
            "log_directory": str(tmp_path / "logs"),
            "rclone_temp_directory": str(tmp_path / "temp"),
        },
        "lan_backup": {"enabled": True},
        "cloud_backup": {"enabled": True, "bucket": "test-bucket"},
        "wol": {"server_ip": "127.0.0.1"},
        "vss": {"enabled": False},
        "ui": {"prefect_api_url": "http://127.0.0.1:4200/api"},
        "notifications": {
            "smtp_host": "",
            "smtp_port": 587,
            "smtp_username": "",
            "sender": "",
            "recipients": [],
        },
        "cloud_credentials": {"credential_name": "TestCred"},
        "backup_scope": {"exclude_folders": []},
    }

    with patch("shutil.which", return_value="/usr/bin/rclone"):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        with patch("socket.create_connection"):
            with patch("socket.gethostbyname", return_value="127.0.0.1"):
                with patch("core.preflight.psutil", None):
                    report = run_preflight_checks(config)

    # Should have more checks than minimal config
    assert len(report.checks) > 5
    # Should include GCS checks
    gcs_checks = [c for c in report.checks if "GCS" in c.name or "gcs" in c.name.lower()]
    assert len(gcs_checks) >= 2
