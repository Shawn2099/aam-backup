"""Tests for wol.py."""

from unittest.mock import MagicMock, patch

import pytest

from core.wol import WolTimeout, WolError, ensure_server_online, ping_host, send_magic_packet


def test_ping_host_success():
    """ping_host returns True for reachable host."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert ping_host("127.0.0.1") is True


def test_ping_host_failure():
    """ping_host returns False for unreachable host."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1)
        assert ping_host("192.168.10.99") is False


def test_ping_host_timeout():
    """ping_host returns False on timeout."""
    with patch("subprocess.run", side_effect=TimeoutError):
        assert ping_host("192.168.10.99") is False


def test_send_magic_packet():
    """send_magic_packet uses wakeonlan library."""
    with patch("core.wol.wol_send") as mock_wol:
        send_magic_packet("00:11:22:33:44:55", "192.168.1.255", 9)
        mock_wol.assert_called_once_with("00:11:22:33:44:55", ip_address="192.168.1.255", port=9)


def test_send_magic_packet_error():
    """send_magic_packet raises WolError on failure."""
    with patch("core.wol.wol_send", side_effect=Exception("network error")):
        with pytest.raises(WolError):
            send_magic_packet("00:11:22:33:44:55")


def test_ensure_server_online_already_up(temp_config):
    """Online server: SMB port open, WoL packet NOT sent."""
    temp_config.wol.enabled = True
    temp_config.wol.server_ip = "127.0.0.1"

    with patch("core.wol._smb_port_open", return_value=True):
        assert ensure_server_online(temp_config) is True


def test_ensure_server_online_wol_needed(temp_config):
    """Offline server: SMB port closed, WoL packet sent, then port opens."""
    temp_config.wol.enabled = True
    temp_config.wol.server_ip = "192.168.10.10"
    temp_config.wol.mac_address = "00:11:22:33:44:55"
    temp_config.wol.ping_interval_seconds = 1
    temp_config.wol.stability_wait_seconds = 0

    call_count = [0]

    def mock_smb(ip):
        call_count[0] += 1
        return call_count[0] >= 2  # Fail first, succeed second

    with patch("core.wol._smb_port_open", side_effect=mock_smb):
        with patch("core.wol.send_magic_packet") as mock_wol:
            assert ensure_server_online(temp_config) is True
            mock_wol.assert_called_once()


def test_ensure_server_online_timeout(temp_config):
    """Timeout: WolTimeout raised after wake_timeout_seconds."""
    temp_config.wol.enabled = True
    temp_config.wol.server_ip = "192.168.10.10"
    temp_config.wol.mac_address = "00:11:22:33:44:55"
    temp_config.wol.wake_timeout_seconds = 2
    temp_config.wol.ping_interval_seconds = 1

    with patch("core.wol._smb_port_open", return_value=False):
        with pytest.raises(WolTimeout):
            ensure_server_online(temp_config)


def test_ensure_server_online_wol_disabled(temp_config):
    """WoL disabled: returns True without checking."""
    temp_config.wol.enabled = False

    with patch("core.wol._smb_port_open") as mock_smb:
        assert ensure_server_online(temp_config) is True
        mock_smb.assert_not_called()
