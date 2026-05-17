"""Tests for VSS module."""

import platform
from unittest.mock import MagicMock, patch

import pytest

from core.vss import (
    VssError,
    check_vss_available,
    create_shadow_copy,
    delete_shadow_copy,
    vss_snapshot,
)


def test_create_shadow_copy_non_windows():
    """create_shadow_copy returns None on non-Windows."""
    with patch("platform.system", return_value="Linux"):
        result = create_shadow_copy("D")
        assert result is None


def test_delete_shadow_copy_non_windows():
    """delete_shadow_copy returns True on non-Windows."""
    with patch("platform.system", return_value="Linux"):
        result = delete_shadow_copy("\\\\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy1\\")
        assert result is True


def test_check_vss_available_non_windows():
    """check_vss_available returns False on non-Windows."""
    with patch("platform.system", return_value="Linux"):
        result = check_vss_available()
        assert result is False


def test_vss_snapshot_context_non_windows():
    """vss_snapshot yields original drive on non-Windows."""
    with patch("platform.system", return_value="Linux"):
        with vss_snapshot("D") as source_path:
            assert str(source_path) == "D:\\"


def test_create_shadow_copy_success():
    """create_shadow_copy returns device path on success."""
    with patch("platform.system", return_value="Windows"):
        with patch("core.vss._run_powershell") as mock_ps:
            mock_ps.return_value = MagicMock(
                returncode=0,
                stdout="\\\\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy123\\",
                stderr="",
            )
            result = create_shadow_copy("D")
            assert result is not None
            assert "HarddiskVolumeShadowCopy123" in result


def test_create_shadow_copy_failure():
    """create_shadow_copy returns None on failure."""
    with patch("platform.system", return_value="Windows"):
        with patch("core.vss._run_powershell") as mock_ps:
            mock_ps.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="VSS creation failed",
            )
            result = create_shadow_copy("D")
            assert result is None


def test_delete_shadow_copy_success():
    """delete_shadow_copy returns True on success."""
    with patch("platform.system", return_value="Windows"):
        with patch("core.vss._run_vssadmin") as mock_admin:
            mock_admin.return_value = MagicMock(
                returncode=0,
                stdout="Shadow Copy ID: {12345}\nOriginal Volume: D:\\",
                stderr="",
            )
            result = delete_shadow_copy("D:\\")
            assert result is True


def test_vss_snapshot_with_fallback():
    """vss_snapshot falls back to original drive when VSS fails."""
    with patch("platform.system", return_value="Windows"):
        with patch("core.vss.check_vss_available", return_value=True):
            with patch("core.vss.create_shadow_copy", return_value=None):
                with vss_snapshot("D", fallback=True) as source_path:
                    assert str(source_path) == "D:\\"


def test_vss_snapshot_without_fallback_raises():
    """vss_snapshot raises VssError when VSS fails and fallback is False."""
    with patch("platform.system", return_value="Windows"):
        with patch("core.vss.check_vss_available", return_value=True):
            with patch("core.vss.create_shadow_copy", return_value=None):
                with pytest.raises(VssError):
                    with vss_snapshot("D", fallback=False):
                        pass
