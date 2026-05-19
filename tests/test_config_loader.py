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


def test_backup_destinations_both_enabled(temp_config):
    """backup_destinations shows both enabled when defaults are used."""
    dest = temp_config.backup_destinations
    assert dest["lan"]["enabled"] is True
    assert dest["cloud"]["enabled"] is False
    assert dest["any_enabled"] is True
    assert dest["all_disabled"] is False
    assert dest["warning"] is None


def test_backup_destinations_both_disabled(temp_config_path, temp_dir):
    """backup_destinations warns when both LAN and cloud are disabled."""
    config = {
        "firm": {"name": "Test Firm"},
        "paths": {
            "source_drive": str(temp_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(temp_dir / "logs"),
            "database_path": str(temp_dir / "manifest.db"),
        },
        "lan_backup": {"enabled": False},
        "cloud_backup": {"enabled": False},
    }
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    loaded = load_config(config_path)
    dest = loaded.backup_destinations
    assert dest["lan"]["enabled"] is False
    assert dest["cloud"]["enabled"] is False
    assert dest["any_enabled"] is False
    assert dest["all_disabled"] is True
    assert "Both LAN and Cloud backup are disabled" in dest["warning"]


def test_validate_backup_destinations_both_disabled(temp_config_path, temp_dir):
    """validate_backup_destinations returns error when both disabled."""
    config = {
        "firm": {"name": "Test Firm"},
        "paths": {
            "source_drive": str(temp_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(temp_dir / "logs"),
            "database_path": str(temp_dir / "manifest.db"),
        },
        "lan_backup": {"enabled": False},
        "cloud_backup": {"enabled": False},
    }
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    loaded = load_config(config_path)
    issues = loaded.validate_backup_destinations()
    assert len(issues) == 1
    assert "CRITICAL" in issues[0]


def test_validate_backup_destinations_lan_only(temp_config_path, temp_dir):
    """validate_backup_destinations OK when only LAN is enabled."""
    config = {
        "firm": {"name": "Test Firm"},
        "paths": {
            "source_drive": str(temp_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(temp_dir / "logs"),
            "database_path": str(temp_dir / "manifest.db"),
        },
        "lan_backup": {"enabled": True},
        "cloud_backup": {"enabled": False},
    }
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    loaded = load_config(config_path)
    issues = loaded.validate_backup_destinations()
    assert len(issues) == 0


def test_validate_backup_destinations_cloud_only(temp_config_path, temp_dir):
    """validate_backup_destinations OK when only cloud is enabled."""
    config = {
        "firm": {"name": "Test Firm"},
        "paths": {
            "source_drive": str(temp_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(temp_dir / "logs"),
            "database_path": str(temp_dir / "manifest.db"),
        },
        "lan_backup": {"enabled": False},
        "cloud_backup": {"enabled": True, "bucket": "my-bucket"},
    }
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    loaded = load_config(config_path)
    issues = loaded.validate_backup_destinations()
    assert len(issues) == 0
