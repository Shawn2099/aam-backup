"""Shared fixtures for tests."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from core.config_loader import load_config
from core.manifest_db import ManifestDB
from models.config_model import AppConfig


@pytest.fixture
def temp_dir():
    """Create a temporary directory that is cleaned up after the test."""
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture
def temp_config_path(temp_dir):
    """Create a valid config.yaml in a temp directory."""
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
    }
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    return config_path


@pytest.fixture
def temp_config(temp_config_path):
    """Load and return a valid AppConfig from temp config."""
    return load_config(temp_config_path)


@pytest.fixture
def temp_db(temp_dir):
    """Create a ManifestDB in a temp directory."""
    db_path = temp_dir / "manifest.db"
    db = ManifestDB(db_path)
    yield db
    db.close()


@pytest.fixture
def sample_file_info():
    """Return a sample FileInfo-like dict for testing."""
    return {
        "relative_path": "test/file.txt",
        "file_size": 1024,
        "last_modified_timestamp": 1700000000.0,
    }
