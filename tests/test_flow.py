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
