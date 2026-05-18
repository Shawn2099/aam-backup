"""Tests for robocopy.py."""

from unittest.mock import MagicMock, patch

import pytest

from core.robocopy import (
    RobocopyResult,
    _classify_exit_code,
    _parse_robocopy_output,
    run_robocopy,
)
from models.scan_result import ScanResult


def test_classify_exit_code_0():
    """Exit code 0 → LAN_COMPLETE (already in sync)."""
    assert _classify_exit_code(0) == "LAN_COMPLETE"


def test_classify_exit_code_1():
    """Exit code 1 → LAN_COMPLETE (files copied)."""
    assert _classify_exit_code(1) == "LAN_COMPLETE"


def test_classify_exit_code_7():
    """Exit code 7 → LAN_COMPLETE (bits 0+1+2: copied + extra + mismatched)."""
    assert _classify_exit_code(7) == "LAN_COMPLETE"


def test_classify_exit_code_8():
    """Exit code 8 → LAN_PARTIAL (bit 3: copy errors)."""
    assert _classify_exit_code(8) == "LAN_PARTIAL"


def test_classify_exit_code_16():
    """Exit code 16 → LAN_FAILED (bit 4: fatal error)."""
    assert _classify_exit_code(16) == "LAN_FAILED"


def test_classify_exit_code_bitmask():
    """Exit codes are evaluated with bitwise AND."""
    # 1 + 8 = 9 (files copied + some failed) → LAN_PARTIAL
    assert _classify_exit_code(9) == "LAN_PARTIAL"
    # 1 + 16 = 17 (files copied + fatal) → LAN_FAILED
    assert _classify_exit_code(17) == "LAN_FAILED"


def test_parse_robocopy_output():
    """Parse Robocopy summary output correctly."""
    output = """
-------------------------------------------------------------------------------
   Total    Copied   Skipped  Mismatch    FAILED    Extras
    Dirs :         5         5         0         0         0         0
   Files :        10         8         1         0         1         0
   Bytes :   1000000    800000    100000         0    100000         0
-------------------------------------------------------------------------------
"""
    stats = _parse_robocopy_output(output)
    assert stats["files_copied"] == 8
    assert stats["bytes_copied"] == 800000
    assert stats["files_failed"] == 1


def test_robocopy_disabled(temp_config):
    """Disabled LAN backup returns LAN_SKIPPED."""
    temp_config.lan_backup.enabled = False
    result = run_robocopy(temp_config, ScanResult(), MagicMock())
    assert result.status == "LAN_SKIPPED"


def test_robocopy_timeout(temp_config):
    """Timeout raises handled → LAN_FAILED."""
    temp_config.lan_backup.subprocess_timeout_seconds = 1
    with patch("subprocess.run", side_effect=TimeoutError):
        result = run_robocopy(temp_config, ScanResult(), MagicMock())
        assert result.status == "LAN_FAILED"


def test_robocopy_file_not_found(temp_config):
    """FileNotFoundError handled → LAN_FAILED."""
    with patch("subprocess.run", side_effect=FileNotFoundError):
        result = run_robocopy(temp_config, ScanResult(), MagicMock())
        assert result.status == "LAN_FAILED"


def test_robocopy_includes_system_volume_exclusion(temp_config):
    """Robocopy command includes /XD 'System Volume Information' for safety."""
    temp_config.lan_backup.enabled = True
    temp_config.lan_backup.retry_count = 0

    captured_cmd = None

    def capture_run(cmd, *args, **kwargs):
        nonlocal captured_cmd
        captured_cmd = cmd
        raise FileNotFoundError("robocopy not found")

    with patch("subprocess.run", side_effect=capture_run):
        run_robocopy(temp_config, ScanResult(), MagicMock())

    assert captured_cmd is not None
    assert "/XD" in captured_cmd
    assert "System Volume Information" in captured_cmd
