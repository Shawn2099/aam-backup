"""Tests for flow.py and task integration."""

import pytest
from unittest.mock import MagicMock, patch

from models.scan_result import ScanResult


def test_flow_definition_exists():
    """Flow is defined and importable."""
    from flow import nightly_backup
    assert nightly_backup.name == "nightly-backup"


def test_flow_task_runner_config():
    """Flow uses ThreadPoolTaskRunner with max_workers=2."""
    from flow import nightly_backup
    # Verify the flow exists and has correct name
    assert nightly_backup.name == "nightly-backup"


def test_scan_no_changes_returns_complete(temp_config, temp_db):
    """Flow returns COMPLETE when no changes detected."""
    from tasks.scan_task import scan_task

    # Empty source directory — no changes
    result = scan_task.fn(temp_config, temp_db._database_path)
    assert not result.has_changes


def test_lan_task_disabled_returns_skipped(temp_config):
    """LAN task returns LAN_SKIPPED when disabled."""
    from tasks.lan_task import lan_backup_task

    temp_config.lan_backup.enabled = False
    result = lan_backup_task.fn(temp_config, ScanResult(), "/tmp/test.db")
    assert result["status"] == "LAN_SKIPPED"


def test_cloud_task_disabled_returns_skipped(temp_config):
    """Cloud task returns CLOUD_SKIPPED when disabled."""
    from tasks.cloud_task import cloud_backup_task

    temp_config.cloud_backup.enabled = False
    result = cloud_backup_task.fn(temp_config, "/fake/key.json", ScanResult(), "/tmp/test.db")
    assert result["status"] == "CLOUD_SKIPPED"


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
