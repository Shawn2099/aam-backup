"""Tests for config_loader.py."""

import pytest
import yaml

from core.config_loader import ConfigurationError, load_config


def test_valid_config_loads(temp_config_path, temp_config):
    """Valid config loads correctly."""
    assert temp_config.firm.name == "Test Firm"
    assert temp_config.paths.source_drive is not None
    assert temp_config.schedule.enabled is True
    assert temp_config.lan_backup.enabled is True


def test_missing_config_file_raises(temp_dir):
    """Missing config file raises ConfigurationError."""
    with pytest.raises(ConfigurationError, match="Config file not found"):
        load_config(temp_dir / "nonexistent.yaml")


def test_invalid_yaml_raises(temp_dir):
    """Invalid YAML raises ConfigurationError."""
    bad_path = temp_dir / "bad.yaml"
    with open(bad_path, "w") as f:
        f.write("{{invalid yaml:::")
    with pytest.raises(ConfigurationError, match="Invalid YAML"):
        load_config(bad_path)


def test_empty_firm_name_raises(temp_config_path, temp_dir):
    """Empty firm.name raises ConfigurationError."""
    config = {
        "firm": {"name": "   "},
        "paths": {
            "source_drive": str(temp_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(temp_dir / "logs"),
            "database_path": str(temp_dir / "manifest.db"),
        },
    }
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    with pytest.raises(ConfigurationError, match="firm.name cannot be empty"):
        load_config(config_path)


def test_invalid_mac_address_raises(temp_config_path, temp_dir):
    """Invalid MAC address format raises ConfigurationError."""
    config = {
        "firm": {"name": "Test Firm"},
        "paths": {
            "source_drive": str(temp_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(temp_dir / "logs"),
            "database_path": str(temp_dir / "manifest.db"),
        },
        "wol": {
            "enabled": True,
            "mac_address": "invalid-mac",
            "server_ip": "192.168.10.10",
        },
    }
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    with pytest.raises(ConfigurationError, match="wol.mac_address format"):
        load_config(config_path)


def test_invalid_bucket_name_raises(temp_config_path, temp_dir):
    """Invalid GCS bucket name raises ConfigurationError."""
    config = {
        "firm": {"name": "Test Firm"},
        "paths": {
            "source_drive": str(temp_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(temp_dir / "logs"),
            "database_path": str(temp_dir / "manifest.db"),
        },
        "cloud_backup": {
            "enabled": True,
            "bucket": "INVALID_BUCKET",
        },
    }
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    with pytest.raises(ConfigurationError, match="cloud_backup.bucket"):
        load_config(config_path)


def test_missing_gcs_credential_raises(temp_config_path, temp_dir, mocker):
    """Missing GCS credential raises ConfigurationError."""
    mocker.patch("keyring.get_password", return_value=None)

    from core.config_loader import get_gcs_key_path

    with pytest.raises(ConfigurationError, match="not found"):
        get_gcs_key_path("BackupAgent_GCS")
