"""Volume Shadow Copy (VSS) support for backing up locked files.

Creates a point-in-time snapshot of the source drive so Robocopy and Rclone
can read consistent data even if applications (Tally, Winman) have files locked.

Shadow copy is created before scanning, used as the source for backup,
and deleted after backup completes.
"""

import platform
import re
import subprocess
from contextlib import contextmanager
from pathlib import Path

from loguru import logger


class VssError(Exception):
    """Raised when VSS operations fail."""
    pass


def _run_vssadmin(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    """Run vssadmin command and return result."""
    cmd = ["vssadmin"] + args
    logger.debug(f"Running: {' '.join(cmd)}")
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _run_powershell(script: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run PowerShell command and return result."""
    cmd = ["powershell", "-NoProfile", "-Command", script]
    logger.debug(f"Running PowerShell: {script[:100]}...")
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def create_shadow_copy(drive_letter: str = "D") -> str | None:
    """Create a VSS shadow copy of the specified drive.

    Uses PowerShell's Get-CimInstance to create the shadow copy,
    which is more reliable than vssadmin on Windows Server 2016.

    Args:
        drive_letter: Drive letter to snapshot (e.g., "D").

    Returns:
        Shadow copy device path (e.g., \\\\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy123\\)
        or None if creation failed.
    """
    if platform.system().lower() != "windows":
        logger.debug("VSS not available on non-Windows systems")
        return None

    drive = f"{drive_letter}:\\"

    # Use WMI to create shadow copy
    script = f"""
    $class = Get-CimClass -ClassName Win32_ShadowCopy
    $result = Invoke-CimMethod -CimClass $class -MethodName Create -Arguments @{{Volume = "{drive}"}}
    if ($result.ReturnValue -eq 0) {{
        $shadow = Get-CimInstance -ClassName Win32_ShadowCopy | Where-Object {{ $_.ID -eq $result.ShadowID }}
        Write-Output $shadow.DeviceObject
    }} else {{
        Write-Error "VSS creation failed with return code: $($result.ReturnValue)"
        exit 1
    }}
    """

    try:
        result = _run_powershell(script, timeout=120)
        if result.returncode == 0 and result.stdout.strip():
            device_path = result.stdout.strip()
            logger.info(f"VSS shadow copy created: {device_path}")
            return device_path
        else:
            logger.error(f"VSS creation failed: {result.stderr.strip()}")
            return None
    except subprocess.TimeoutExpired:
        logger.error("VSS creation timed out after 120s")
        return None
    except Exception as e:
        logger.error(f"VSS creation error: {e}")
        return None


def delete_shadow_copy(device_path: str) -> bool:
    """Delete a VSS shadow copy by its device path.

    Args:
        device_path: Shadow copy device path from create_shadow_copy().

    Returns:
        True if deletion succeeded, False otherwise.
    """
    if platform.system().lower() != "windows":
        return True  # Nothing to delete on non-Windows

    try:
        # Use vssadmin to delete by ID
        # First, find the ID from the device path
        result = _run_vssadmin(["List", "ShadowCopies"])
        if result.returncode != 0:
            logger.warning(f"Failed to list shadow copies: {result.stderr.strip()}")
            return False

        # Parse the output to find matching ID
        # Format: "Shadow Copy ID: {guid}" followed by "Original Volume: D:\"
        lines = result.stdout.splitlines()
        current_id = None
        for line in lines:
            id_match = re.search(r"Shadow Copy ID:\s*(\{[^}]+\})", line)
            if id_match:
                current_id = id_match.group(1)

            if current_id and device_path.lower() in line.lower():
                # Found the matching shadow copy, delete it
                del_result = _run_vssadmin(["Delete", "Shadow", f"/ID={current_id}", "/Quiet"])
                if del_result.returncode == 0:
                    logger.info(f"VSS shadow copy deleted: {device_path}")
                    return True
                else:
                    logger.warning(f"Failed to delete VSS: {del_result.stderr.strip()}")
                    return False

        logger.warning(f"Could not find shadow copy with device path: {device_path}")
        return False

    except Exception as e:
        logger.error(f"VSS deletion error: {e}")
        return False


def check_vss_available() -> bool:
    """Check if VSS is available and working on this system."""
    if platform.system().lower() != "windows":
        return False

    try:
        result = _run_vssadmin(["List", "ShadowStorage"])
        return result.returncode == 0
    except Exception:
        return False


@contextmanager
def vss_snapshot(drive_letter: str = "D", fallback: bool = True):
    """Context manager for VSS shadow copy lifecycle.

    Creates a shadow copy on entry, yields the source path to use,
    and deletes the shadow copy on exit (even if an error occurs).

    Args:
        drive_letter: Drive letter to snapshot.
        fallback: If True, yield the original drive path if VSS fails.
                  If False, raise VssError on failure.

    Yields:
        Path to use as source for backup (shadow copy path or original drive).

    Raises:
        VssError: If VSS creation fails and fallback is False.
    """
    if platform.system().lower() != "windows":
        # On non-Windows, just yield the original drive
        yield Path(f"{drive_letter}:\\")
        return

    device_path = create_shadow_copy(drive_letter)

    if device_path:
        # Convert device path to usable path format
        # DeviceObject looks like: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy123\
        # We need to use it as-is for Robocopy and Rclone
        try:
            yield Path(device_path)
        finally:
            delete_shadow_copy(device_path)
    elif fallback:
        logger.warning("VSS creation failed, falling back to direct backup")
        yield Path(f"{drive_letter}:\\")
    else:
        raise VssError(
            f"VSS shadow copy creation failed for {drive_letter}:\\ "
            f"and fallback is disabled"
        )
