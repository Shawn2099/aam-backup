"""Loguru logging configuration with daily rotating files."""

import sys
from pathlib import Path

from loguru import logger


def configure_logging(log_dir: str | Path, rotation: str = "1 day", retention: str = "30 days"):
    """Configure Loguru with two sinks: rotating daily file + stderr WARNING.

    Args:
        log_dir: Directory for log files. Created if it doesn't exist.
        rotation: When to rotate the log file (default: daily).
        retention: How long to keep old log files (default: 30 days).
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Remove default handler
    logger.remove()

    # File sink: rotating daily, 30-day retention, UTF-8, DEBUG+
    logger.add(
        log_dir / "backup_{time:YYYY-MM-DD}.log",
        rotation=rotation,
        retention=retention,
        encoding="utf-8",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        enqueue=True,
    )

    # Stderr sink: WARNING and above
    logger.add(
        sys.stderr,
        level="WARNING",
        format="{time:HH:mm:ss} | {level: <8} | {message}",
    )

    return logger
