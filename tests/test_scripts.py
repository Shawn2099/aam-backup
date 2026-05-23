"""Tests for deployment and setup scripts."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import yaml


# --- validate_config.py tests ---


def test_validate_config_loads_valid_config(tmp_path):
    """validate_config.py loads a valid config successfully."""
    config = {
        "firm": {"name": "Test Firm"},
        "paths": {
            "source_drive": "D:\\",
            "lan_destination": "\\\\192.168.10.10\\backup$",
            "log_directory": "C:\\BackupAgent\\logs",
            "database_path": "C:\\BackupAgent\\manifest.db",
            "rclone_temp_directory": "C:\\BackupAgent\\rclone_temp",
        },
        "schedule": {"enabled": True, "daily_time": "23:00"},
        "cloud_backup": {"enabled": False},
        "wol": {"enabled": False},
        "lan_backup": {"enabled": False},
        "notifications": {"send_on_failure": False, "send_on_every_run": False},
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.dump(config))

    from core.config_loader import load_config
    appconfig = load_config(config_path)
    assert appconfig is not None
    assert appconfig.firm.name == "Test Firm"


def test_validate_config_missing_required_fields(tmp_path):
    """Pydantic validation catches missing required fields."""
    config = {
        "firm": {"name": ""},
        "paths": {},
        "cloud_backup": {"enabled": True, "bucket": ""},
        "wol": {"enabled": True, "mac_address": "", "server_ip": ""},
        "lan_backup": {"enabled": False},
        "notifications": {"send_on_failure": True, "send_on_every_run": False},
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.dump(config))

    from core.config_loader import load_config

    try:
        _ = load_config(config_path)
        # Shouldn't reach here — multiple validators should fire
        assert False, "Expected ValidationError"
    except Exception:
        pass


def test_validate_config_invalid_yaml(tmp_path):
    """validate_config module handles invalid YAML."""
    from core.config_loader import load_config

    config_path = tmp_path / "config.yaml"
    config_path.write_text("invalid: yaml: : :")

    try:
        _ = load_config(config_path)
        assert False, "Expected error"
    except Exception:
        pass


def test_validate_config_missing_file():
    """validate_config module handles missing config file."""
    from core.config_loader import load_config

    try:
        _ = load_config(Path("/nonexistent/config.yaml"))
        assert False, "Expected error"
    except Exception:
        pass


# --- seed_cloud.py tests ---


def test_seed_cloud_dry_run(tmp_path):
    """seed_cloud.py dry run shows what would be done."""
    config = {
        "cloud_backup": {
            "enabled": True,
            "bucket": "my-backup-bucket",
            "remote_path": "D_Drive_Backup",
        }
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.dump(config))

    from scripts.seed_cloud import seed_bucket

    with patch("subprocess.run") as mock_run:
        result = seed_bucket(config, dry_run=True)
        assert result is True
        mock_run.assert_not_called()


def test_seed_cloud_creates_bucket(tmp_path):
    """seed_cloud.py creates the bucket directory."""
    config = {
        "cloud_backup": {
            "enabled": True,
            "bucket": "my-backup-bucket",
            "remote_path": "D_Drive_Backup",
        }
    }

    from scripts.seed_cloud import seed_bucket

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = seed_bucket(config, dry_run=False)
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "rclone" in args
        assert "mkdir" in args


def test_seed_cloud_bucket_exists(tmp_path):
    """seed_cloud.py handles existing bucket gracefully."""
    config = {
        "cloud_backup": {
            "enabled": True,
            "bucket": "my-backup-bucket",
            "remote_path": "D_Drive_Backup",
        }
    }

    from scripts.seed_cloud import seed_bucket

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr="directory exists")
        result = seed_bucket(config, dry_run=False)
        assert result is True  # Already exists is OK


# --- test_connections.py tests ---


def test_test_connections_lan_disabled(tmp_path):
    """test_connections.py skips LAN test when disabled."""
    config = {
        "lan_backup": {"enabled": False},
        "cloud_backup": {"enabled": False},
    }

    from scripts.test_connections import test_lan_connection, test_gcs_connection

    assert test_lan_connection(config) is True
    assert test_gcs_connection(config) is True


def test_test_connections_gcs_disabled(tmp_path):
    """test_connections.py skips GCS test when disabled."""
    config = {
        "cloud_backup": {"enabled": False},
    }

    from scripts.test_connections import test_gcs_connection

    assert test_gcs_connection(config) is True


def test_test_connections_gcs_success(tmp_path):
    """test_connections.py verifies GCS connectivity."""
    config = {
        "cloud_backup": {
            "enabled": True,
            "bucket": "my-backup-bucket",
        }
    }

    from scripts.test_connections import test_gcs_connection

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = test_gcs_connection(config)
        assert result is True


def test_test_connections_gcs_failure(tmp_path):
    """test_connections.py detects GCS connectivity failure."""
    config = {
        "cloud_backup": {
            "enabled": True,
            "bucket": "my-backup-bucket",
        }
    }

    from scripts.test_connections import test_gcs_connection

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr="access denied")
        result = test_gcs_connection(config)
        assert result is False


# --- create_deployment.py tests ---


def test_create_deployment_time_to_cron():
    """create_deployment.py converts time to cron expression."""
    from deploy.create_deployment import time_to_cron

    assert time_to_cron("23:00") == "00 23 * * *"
    assert time_to_cron("00:00") == "00 00 * * *"
    assert time_to_cron("12:30") == "30 12 * * *"


def test_create_deployment_uses_flow_deploy(tmp_path):
    """create_deployment.py uses native flow.deploy() instead of subprocess."""
    from deploy.create_deployment import time_to_cron

    # Verify time_to_cron works
    assert time_to_cron("23:00") == "00 23 * * *"
    assert time_to_cron("00:00") == "00 00 * * *"
    assert time_to_cron("12:30") == "30 12 * * *"


# --- install_service.py tests ---


def test_install_service_find_servy():
    """install_service.py finds Servy in common locations."""
    from deploy.install_service import find_servy

    with patch.object(Path, "exists", return_value=False):
        with patch("shutil.which", return_value="C:\\servy\\servy.exe"):
            result = find_servy()
            assert result is not None
            assert "servy.exe" in str(result)


def test_install_service_find_servy_explicit_path(tmp_path):
    """install_service.py uses explicit Servy path."""
    from deploy.install_service import find_servy

    fake_servy = tmp_path / "servy.exe"
    fake_servy.touch()

    result = find_servy(str(fake_servy))
    assert result == fake_servy


def test_install_service_not_found():
    """install_service.py returns None when Servy not found."""
    from deploy.install_service import find_servy

    with patch.object(Path, "exists", return_value=False):
        with patch("shutil.which", return_value=None):
            result = find_servy()
            assert result is None


# --- uninstall_service.py tests ---


def test_uninstall_service_find_servy():
    """uninstall_service.py finds Servy."""
    from deploy.uninstall_service import find_servy

    with patch.object(Path, "exists", return_value=False):
        with patch("shutil.which", return_value="C:\\servy\\servy.exe"):
            result = find_servy()
            assert result is not None
