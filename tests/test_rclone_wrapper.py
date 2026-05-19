"""Tests for rclone.py."""

from unittest.mock import MagicMock, patch


from core.rclone import (
    _classify_exit_code,
    _write_filter_file,
    _write_temp_config,
    run_rclone,
)
from models.scan_result import ScanResult


def test_classify_exit_code_0():
    """Exit code 0 → CLOUD_COMPLETE."""
    assert _classify_exit_code(0) == "CLOUD_COMPLETE"


def test_classify_exit_code_5_partial():
    """Exit code 5 → CLOUD_PARTIAL (temporary network error — Prefect retries at task level)."""
    assert _classify_exit_code(5) == "CLOUD_PARTIAL"


def test_classify_exit_code_7_failed():
    """Exit code 7 → CLOUD_FAILED."""
    assert _classify_exit_code(7) == "CLOUD_FAILED"


def test_classify_exit_code_2_failed():
    """Exit code 2 → CLOUD_FAILED (source/destination error — needs investigation)."""
    assert _classify_exit_code(2) == "CLOUD_FAILED"


def test_classify_exit_code_3_failed():
    """Exit code 3 → CLOUD_FAILED (source/destination missing — hard failure)."""
    assert _classify_exit_code(3) == "CLOUD_FAILED"


def test_classify_exit_code_4_partial():
    """Exit code 4 → CLOUD_PARTIAL (file not found — may be transient)."""
    assert _classify_exit_code(4) == "CLOUD_PARTIAL"


def test_classify_exit_code_6_partial():
    """Exit code 6 → CLOUD_PARTIAL (less serious error — some files transferred)."""
    assert _classify_exit_code(6) == "CLOUD_PARTIAL"


def test_classify_exit_code_8_failed():
    """Exit code 8 → CLOUD_FAILED (transfer limit exceeded — should not happen in normal operation)."""
    assert _classify_exit_code(8) == "CLOUD_FAILED"


def test_classify_exit_code_9_complete():
    """Exit code 9 → CLOUD_COMPLETE (no files to transfer — source already matches dest)."""
    assert _classify_exit_code(9) == "CLOUD_COMPLETE"


def test_classify_exit_code_10_partial():
    """Exit code 10 → CLOUD_PARTIAL (duration limit hit — some files may have transferred)."""
    assert _classify_exit_code(10) == "CLOUD_PARTIAL"


def test_classify_exit_code_unknown_failed():
    """Unknown exit code → CLOUD_FAILED."""
    assert _classify_exit_code(99) == "CLOUD_FAILED"


def test_temp_config_created_and_deleted(temp_dir):
    """Temp config created and deleted in finally."""
    config_path = _write_temp_config(temp_dir, "test123", "/fake/key.json")
    assert config_path.exists()
    assert "[gcs_backup]" in config_path.read_text()


def test_filter_file_created_and_deleted(temp_dir):
    """Temp filter file created and deleted in finally."""
    filter_path = _write_filter_file(
        temp_dir, "test123",
        exclude_folders=["D:\\BackupAgent"],
        exclude_extensions=[".lnk", ".tmp"],
        exclude_patterns=["~$*"],
        source_drive="D:\\",
    )
    assert filter_path.exists()
    content = filter_path.read_text()
    assert "- BackupAgent/**" in content
    assert "- *.lnk" in content
    assert "- *.tmp" in content
    assert "- ~$*" in content


def test_rclone_disabled(temp_config):
    """Disabled cloud backup returns CLOUD_SKIPPED."""
    temp_config.cloud_backup.enabled = False
    result = run_rclone(temp_config, "/fake/key.json", ScanResult(), MagicMock())
    assert result.status == "CLOUD_SKIPPED"


def test_rclone_file_not_found(temp_config, temp_dir):
    """FileNotFoundError handled → CLOUD_FAILED."""
    temp_config.cloud_backup.enabled = True
    temp_config.cloud_backup.retry_count = 0
    temp_config.paths.rclone_temp_directory = str(temp_dir)
    with patch("subprocess.run", side_effect=FileNotFoundError):
        result = run_rclone(temp_config, "/fake/key.json", ScanResult(), MagicMock())
        assert result.status == "CLOUD_FAILED"


def test_rclone_temp_files_cleaned_up_on_error(temp_config, temp_dir):
    """Temp config deleted even when rclone raises exception."""
    temp_config.cloud_backup.enabled = True
    temp_config.cloud_backup.retry_count = 0  # No retries for test
    temp_config.paths.rclone_temp_directory = str(temp_dir)

    fake_config = temp_dir / "rclone_test.conf"
    fake_filter = temp_dir / "rclone_filter_test.txt"
    fake_config.write_text("test")
    fake_filter.write_text("test")

    with patch("core.rclone._write_temp_config", return_value=fake_config):
        with patch("core.rclone._write_filter_file", return_value=fake_filter):
            with patch("subprocess.run", side_effect=FileNotFoundError):
                run_rclone(temp_config, "/fake/key.json", ScanResult(), MagicMock())

    # Temp files should be cleaned up
    assert not fake_config.exists()
    assert not fake_filter.exists()
