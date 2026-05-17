"""Prefect task: version config.yaml before each backup run."""

import shutil
from datetime import datetime, timezone
from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger


@task(
    name="version_config",
    tags=["maintenance"],
    retries=0,
    task_run_name="version-config",
)
def version_config_task(config_path: str, log_directory: str) -> dict:
    """Copy config.yaml with timestamp for versioning.

    Creates a timestamped backup of the config file before each run.
    Only copies if config has changed from the previous version.

    Args:
        config_path: Path to config.yaml.
        log_directory: Directory for config versions.

    Returns:
        Result dict with versioning status.
    """
    logger = get_run_logger()

    config_file = Path(config_path)
    if not config_file.exists():
        logger.warning(f"Config file not found at {config_path}, skipping versioning")
        return {"status": "SKIPPED", "reason": "config not found"}

    versions_dir = Path(log_directory) / "config_versions"
    versions_dir.mkdir(parents=True, exist_ok=True)

    # Find the latest version
    existing = sorted(versions_dir.glob("config_*.yaml"))
    if existing:
        latest = existing[-1]
        # Compare content — skip if unchanged
        if config_file.read_bytes() == latest.read_bytes():
            logger.debug("Config unchanged, skipping version copy")
            return {"status": "SKIPPED", "reason": "unchanged"}

    # Create timestamped copy
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = versions_dir / f"config_{timestamp}.yaml"
    shutil.copy2(config_file, dest)

    logger.info(f"Config versioned: {dest}")

    # Cleanup old versions (keep last 30)
    all_versions = sorted(versions_dir.glob("config_*.yaml"))
    if len(all_versions) > 30:
        for old in all_versions[:-30]:
            old.unlink()
            logger.debug(f"Removed old config version: {old}")

    return {"status": "SUCCESS", "path": str(dest)}
