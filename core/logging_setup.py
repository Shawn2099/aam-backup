"""Loguru logging configuration with daily rotating files."""

import sys
from pathlib import Path

from loguru import logger

_handler_ids = []


def configure_logging(log_dir: str | Path, rotation: str = "1 day", retention: str = "30 days", enqueue: bool = True):
    """Configure Loguru with two sinks: rotating daily file + stderr WARNING.

    Args:
        log_dir: Directory for log files. Created if it doesn't exist.
        rotation: When to rotate the log file (default: daily).
        retention: How long to keep old log files (default: 30 days).
        enqueue: Whether to use a background thread for log writes.
            Set to False for testing to avoid file handle locks on Windows.
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Remove all previously configured handlers
    logger.remove()
    _handler_ids.clear()

    # File sink: rotating daily, 30-day retention, UTF-8, DEBUG+
    fid = logger.add(
        log_dir / "backup_{time:YYYY-MM-DD}.log",
        rotation=rotation,
        retention=retention,
        encoding="utf-8",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        enqueue=enqueue,
    )
    _handler_ids.append(fid)

    # Stderr sink: WARNING and above
    fid = logger.add(
        sys.stderr,
        level="WARNING",
        format="{time:HH:mm:ss} | {level: <8} | {message}",
    )
    _handler_ids.append(fid)

    return logger


def close_logging():
    """Remove all handlers and complete pending writes.

    Call this during test cleanup to release file handles on Windows.
    """
    for fid in _handler_ids:
        logger.remove(fid)
    _handler_ids.clear()
    logger.complete()
