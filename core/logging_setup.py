"""Loguru logging configuration with daily rotating files.

Designed to coexist with Prefect's APILogHandler. Never removes
handlers we don't own, so Prefect API logging is never disrupted.
"""

from pathlib import Path

from loguru import logger

_handler_ids = []


def configure_logging(log_dir: str | Path, rotation: str = "1 day", retention: str = "30 days", enqueue: bool = True):
    """Add a rotating file sink to Loguru for persistent backup logs.

    Does NOT remove existing handlers (including Prefect's APILogHandler).
    Only removes sinks previously added by this module to avoid duplicates
    if called multiple times.

    Args:
        log_dir: Directory for log files. Created if it doesn't exist.
        rotation: When to rotate the log file (default: daily).
        retention: How long to keep old log files (default: 30 days).
        enqueue: Whether to use a background thread for log writes.
            Set to False for testing to avoid file handle locks on Windows.
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Remove only sinks we previously added (prevents duplicates on re-entry)
    close_logging()

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

    return logger


def close_logging():
    """Remove only handlers added by this module and complete pending writes.

    Safe to call multiple times. Does not touch Prefect's APILogHandler
    or any other external handlers.
    """
    for fid in _handler_ids:
        logger.remove(fid)
    _handler_ids.clear()
    logger.complete()
