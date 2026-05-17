"""Prefect task: manage VSS shadow copy lifecycle."""

import platform
from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger

from core.vss import create_shadow_copy, delete_shadow_copy, check_vss_available


@task(
    name="create_vss_snapshot",
    tags=["vss"],
    retries=0,
    task_run_name="create-vss-snapshot",
)
def create_vss_snapshot_task(drive_letter: str, fallback: bool = True) -> dict:
    """Create a VSS shadow copy and return the source path to use.

    Args:
        drive_letter: Drive letter to snapshot (e.g., "D").
        fallback: If True, return original drive path if VSS fails.

    Returns:
        Dict with "source_path" (path to use), "vss_enabled" (whether VSS was used),
        "device_path" (VSS device path if created, None otherwise).
    """
    logger = get_run_logger()

    if platform.system().lower() != "windows":
        logger.debug("VSS not available on non-Windows, using direct path")
        return {
            "source_path": f"{drive_letter}:\\",
            "vss_enabled": False,
            "device_path": None,
        }

    if not check_vss_available():
        logger.warning("VSS not available on this system, using direct backup")
        return {
            "source_path": f"{drive_letter}:\\",
            "vss_enabled": False,
            "device_path": None,
        }

    logger.info(f"Creating VSS shadow copy of {drive_letter}:\\")
    device_path = create_shadow_copy(drive_letter)

    if device_path:
        logger.info(f"VSS shadow copy ready: {device_path}")
        return {
            "source_path": device_path,
            "vss_enabled": True,
            "device_path": device_path,
        }
    elif fallback:
        logger.warning("VSS creation failed, falling back to direct backup")
        return {
            "source_path": f"{drive_letter}:\\",
            "vss_enabled": False,
            "device_path": None,
        }
    else:
        raise RuntimeError(
            f"VSS shadow copy creation failed for {drive_letter}:\\ "
            f"and fallback is disabled"
        )


@task(
    name="delete_vss_snapshot",
    tags=["vss"],
    retries=0,
    task_run_name="delete-vss-snapshot",
)
def delete_vss_snapshot_task(device_path: str | None) -> dict:
    """Delete a VSS shadow copy by its device path.

    Args:
        device_path: VSS device path from create_vss_snapshot_task.

    Returns:
        Result dict with deletion status.
    """
    logger = get_run_logger()

    if not device_path:
        return {"status": "SKIPPED", "reason": "no device path"}

    if platform.system().lower() != "windows":
        return {"status": "SKIPPED", "reason": "non-Windows"}

    logger.info(f"Deleting VSS shadow copy: {device_path}")
    success = delete_shadow_copy(device_path)

    if success:
        return {"status": "SUCCESS"}
    else:
        logger.warning(f"Failed to delete VSS shadow copy: {device_path}")
        return {"status": "FAILED"}
