"""Tests for flow.py and task integration."""

import pytest
from unittest.mock import patch



def test_flow_definition_exists():
    """Flow is defined and importable."""
    from flow import nightly_backup
    assert nightly_backup.name == "nightly-backup"


def test_flow_task_runner_config():
    """Flow uses ThreadPoolTaskRunner with max_workers=2."""
    from flow import nightly_backup
    assert nightly_backup.name == "nightly-backup"


def test_flow_run_name_template():
    """Flow has flow_run_name template configured."""
    from flow import nightly_backup
    assert nightly_backup.flow_run_name is not None


def test_flow_timeout_configured():
    """Flow has timeout_seconds configured."""
    from flow import nightly_backup
    assert nightly_backup.timeout_seconds == 28800


def test_flow_retries_disabled():
    """Flow has NO retries — task-level retries handle transient failures.

    Flow-level retries would restart the entire flow from the beginning,
    causing double-backup on non-idempotent operations (Robocopy /MIR,
    VSS snapshots, config versioning). Individual tasks have their own
    retries (LAN=3, Cloud=3, Config=2).
    """
    from flow import nightly_backup
    assert nightly_backup.retries == 0


def test_flow_on_failure_hook():
    """Flow has on_failure hook configured."""
    from flow import nightly_backup
    assert nightly_backup.on_failure_hooks is not None
    assert len(nightly_backup.on_failure_hooks) == 1
    assert callable(nightly_backup.on_failure_hooks[0])


def test_scan_task_retries_configured():
    """Scan task has retries configured."""
    from tasks.scan_task import scan_task
    assert scan_task.retries == 1
    assert scan_task.timeout_seconds == 3600


def test_lan_task_retries_configured():
    """LAN task has retries and exponential_backoff configured."""
    from tasks.lan_task import lan_backup_task
    assert lan_backup_task.retries == 3
    assert lan_backup_task.timeout_seconds == 14400


def test_cloud_task_retries_configured():
    """Cloud task has retries and exponential_backoff configured."""
    from tasks.cloud_task import cloud_backup_task
    assert cloud_backup_task.retries == 3
    assert cloud_backup_task.timeout_seconds == 21600


def test_preflight_task_retries_configured():
    """Preflight task has retries configured."""
    from tasks.preflight_task import preflight_task
    assert preflight_task.retries == 1


def test_config_task_retries_configured():
    """Config task has retries configured."""
    from tasks.config_task import load_config_task
    assert load_config_task.retries == 2


def test_config_task_loads_valid_config(temp_config_path):
    """Config task loads and returns config + key path."""
    from tasks.config_task import load_config_task

    # Mock keyring since we don't have Credential Manager on Linux
    with patch("keyring.get_password", return_value="/fake/key.json"):
        config, gcs_key_path = load_config_task.fn(str(temp_config_path))
        assert config.firm.name == "Test Firm"
        assert gcs_key_path == "/fake/key.json"


def test_config_task_raises_on_invalid_config(temp_dir):
    """Config task raises on invalid config."""
    from core.config_loader import ConfigurationError
    from tasks.config_task import load_config_task

    bad_path = temp_dir / "bad.yaml"
    bad_path.write_text("not: valid: yaml: {{{", encoding="utf-8")

    with pytest.raises(ConfigurationError):
        load_config_task.fn(str(bad_path))


def test_send_failure_email_fallback(temp_dir):
    """Test _send_failure_email fallback when block load fails."""
    # Write custom config with notifications
    config = {
        "firm": {"name": "Test Firm"},
        "paths": {
            "source_drive": str(temp_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(temp_dir / "logs"),
            "database_path": str(temp_dir / "manifest.db"),
        },
        "wol": {"enabled": False},
        "cloud_backup": {"enabled": False},
        "notifications": {
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "smtp_user",
            "smtp_password_credential": "smtp_password",
            "sender": "sender@example.com",
            "recipients": ["admin@example.com"],
        }
    }
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        import yaml
        yaml.dump(config, f)

    from flow import _send_failure_email
    
    with patch("keyring.get_password", return_value="dummy_pass"), \
         patch("prefect_email.EmailServerCredentials.load", side_effect=Exception("block not found")), \
         patch("prefect_email.email_send_message.fn") as mock_send_message:
        
        _send_failure_email(str(config_path), "test-flow-id", "test error message")
        
        # Verify call arguments
        mock_send_message.assert_called_once()
        kwargs = mock_send_message.call_args[1]
        assert "Backup Failed" in kwargs["subject"]
        assert kwargs["email_from"] == "sender@example.com"
        assert kwargs["email_to"] == ["admin@example.com"]
        assert "test error message" in kwargs["msg_plain"]
        
        # Verify dynamic block was instantiated correctly
        creds = kwargs["email_server_credentials"]
        assert creds.username == "smtp_user"
        assert creds.smtp_server == "smtp.example.com"
        assert creds.smtp_port == 587
        assert creds.smtp_type == "STARTTLS" or getattr(creds.smtp_type, "name", None) == "STARTTLS"


def test_send_success_email_block_success(temp_dir):
    """Test _send_success_email using Prefect block when it exists."""
    config = {
        "firm": {"name": "Test Firm"},
        "paths": {
            "source_drive": str(temp_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(temp_dir / "logs"),
            "database_path": str(temp_dir / "manifest.db"),
        },
        "wol": {"enabled": False},
        "cloud_backup": {"enabled": False},
        "notifications": {
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "smtp_user",
            "smtp_password_credential": "smtp_password",
            "sender": "sender@example.com",
            "recipients": ["admin@example.com"],
        }
    }
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        import yaml
        yaml.dump(config, f)

    from flow import _send_success_email
    from prefect_email import EmailServerCredentials
    
    mock_block = EmailServerCredentials(
        username="block_user",
        password="block_password",
        smtp_server="smtp.block.com",
        smtp_port=465,
        smtp_type="SSL",
    )
    
    with patch("keyring.get_password", return_value="dummy_pass"), \
         patch("prefect_email.EmailServerCredentials.load", return_value=mock_block), \
         patch("prefect_email.email_send_message.fn") as mock_send_message:
        
        _send_success_email(str(config_path), "test-flow-id", "COMPLETE", 3661.0)
        
        # Verify call arguments
        mock_send_message.assert_called_once()
        kwargs = mock_send_message.call_args[1]
        assert "Backup Complete" in kwargs["subject"]
        assert kwargs["email_from"] == "sender@example.com"
        assert kwargs["email_to"] == ["admin@example.com"]
        assert "1h 1m 1s" in kwargs["msg_plain"]
        
        # Verify block was loaded and passed
        assert kwargs["email_server_credentials"] is mock_block
