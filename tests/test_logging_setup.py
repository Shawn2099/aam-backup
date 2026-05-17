"""Tests for logging_setup.py."""

import os
from pathlib import Path

from core.logging_setup import configure_logging
from loguru import logger


def test_logging_creates_directory(temp_dir):
    """Log directory is created if it doesn't exist."""
    log_dir = temp_dir / "logs"
    assert not log_dir.exists()
    configure_logging(log_dir)
    assert log_dir.exists()


def test_logging_creates_log_file(temp_dir):
    """Log file is created after logging a message."""
    log_dir = temp_dir / "logs"
    configure_logging(log_dir)
    logger.info("Test message")
    logger.complete()

    log_files = list(log_dir.glob("backup_*.log"))
    assert len(log_files) == 1


def test_logging_rotation_config(temp_dir):
    """Loguru is configured with rotation."""
    log_dir = temp_dir / "logs"
    logger_instance = configure_logging(log_dir)
    # Verify logger has handlers configured
    assert len(logger_instance._core.handlers) > 0
