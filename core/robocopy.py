"""Robocopy wrapper — executes /MIR backup with exit code parsing."""

import subprocess
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

from core.manifest_db import ManifestDB
from models.config_model import AppConfig
from models.scan_result import ScanResult


@dataclass
class RobocopyResult:
    """Result of a Robocopy execution."""
    status: str  # LAN_COMPLETE, LAN_PARTIAL, LAN_FAILED, LAN_SKIPPED
    exit_code: int
    files_copied: int = 0
    bytes_copied: int = 0
    files_failed: int = 0
    output: str = ""


def _classify_exit_code(code: int) -> str:
    """Classify Robocopy exit code using bitmask rules.

    Bit 0 (1): Files copied successfully
    Bit 1 (2): Extra files/directories in destination
    Bit 2 (4): Mismatched files detected
    Bit 3 (8): Some files could not be copied — COPY ERROR
    Bit 4 (16): Fatal error — Robocopy did not run properly

    Args:
        code: Robocopy exit code.

    Returns:
        LAN_COMPLETE, LAN_PARTIAL, or LAN_FAILED.
    """
    if code & 16:
        return "LAN_FAILED"
    elif code & 8:
        return "LAN_PARTIAL"
    elif code <= 7:
        return "LAN_COMPLETE"
    else:
        return "LAN_FAILED"


def _parse_robocopy_output(output: str) -> dict[str, int]:
    """Parse Robocopy summary output for file/byte counts.

    Args:
        output: Full Robocopy output text.

    Returns:
        Dict with 'files_copied', 'bytes_copied', 'files_failed'.
    """
    result = {"files_copied": 0, "bytes_copied": 0, "files_failed": 0}

    # Robocopy summary lines (English locale):
    #   Files :  ...  N  ...  N
    #   Bytes :  ...  N  ...  N
    #   Failed : ...  N  ...  N
    lines = output.splitlines()
    for line in lines:
        line = line.strip()
        # Match "Files : <total> <copied> <skipped> <mismatched> <failed> <extra>"
        files_match = re.match(r"Files\s*:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", line)
        if files_match:
            result["files_copied"] = int(files_match.group(2))
            result["files_failed"] = int(files_match.group(5))
            continue

        # Match "Bytes : <total> <copied> <skipped> <mismatched> <failed> <extra>"
        bytes_match = re.match(r"Bytes\s*:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", line)
        if bytes_match:
            result["bytes_copied"] = int(bytes_match.group(2))
            continue

    return result


def run_robocopy(config: AppConfig, scan_result: ScanResult, db: ManifestDB) -> RobocopyResult:
    """Execute Robocopy /MIR to mirror source to LAN destination.

    Args:
        config: Validated application configuration.
        scan_result: ScanResult with new/modified files.
        db: ManifestDB instance for post-backup manifest updates.

    Returns:
        RobocopyResult with status and statistics.
    """
    if not config.lan_backup.enabled:
        logger.info("LAN backup disabled, skipping Robocopy")
        return RobocopyResult(status="LAN_SKIPPED", exit_code=0)

    lan_config = config.lan_backup
    paths_config = config.paths
    scope_config = config.backup_scope

    # Build command as argument list (no shell=True)
    cmd = [
        "robocopy",
        paths_config.source_drive,
        paths_config.lan_destination,
        "/MIR",
        "/Z",
        f"/R:{lan_config.retry_count}",
        f"/W:{lan_config.retry_wait_seconds}",
        "/NP",
        "/BYTES",
        "/TEE",
    ]

    # Add exclusions
    for folder in scope_config.exclude_folders:
        cmd.extend(["/XD", folder])

    for ext in scope_config.exclude_extensions:
        cmd.extend(["/XF", f"*{ext}"])

    for pattern in scope_config.exclude_patterns:
        cmd.extend(["/XF", pattern])

    logger.info(f"Running Robocopy: {' '.join(cmd[:4])}...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=lan_config.subprocess_timeout_seconds,
        )

        exit_code = result.returncode
        status = _classify_exit_code(exit_code)
        stats = _parse_robocopy_output(result.stdout)

        robocopy_result = RobocopyResult(
            status=status,
            exit_code=exit_code,
            files_copied=stats["files_copied"],
            bytes_copied=stats["bytes_copied"],
            files_failed=stats["files_failed"],
            output=result.stdout,
        )

        logger.info(
            f"Robocopy {status}: {stats['files_copied']} files copied, "
            f"{stats['bytes_copied']} bytes, {stats['files_failed']} failed"
        )

        # Update manifest for backed up files
        if status in ("LAN_COMPLETE", "LAN_PARTIAL"):
            changed_paths = [f.relative_path for f in scan_result.new_files + scan_result.modified_files]
            if changed_paths:
                db.batch_mark_lan_backed_up(changed_paths)
                # Compute checksums for new files that were pending
                for file_info in scan_result.new_files:
                    entry = db.get_entry(file_info.relative_path)
                    if entry and entry.checksum == "pending":
                        try:
                            full_path = Path(paths_config.source_drive) / file_info.relative_path
                            checksum = _compute_file_checksum(full_path)
                            db.upsert_entry(
                                relative_path=file_info.relative_path,
                                file_size=file_info.file_size,
                                last_modified_timestamp=file_info.last_modified_timestamp,
                                checksum=checksum,
                            )
                        except Exception as e:
                            logger.warning(f"Could not compute checksum for {file_info.relative_path}: {e}")

        return robocopy_result

    except subprocess.TimeoutExpired:
        logger.critical(f"Robocopy timed out after {lan_config.subprocess_timeout_seconds}s")
        return RobocopyResult(status="LAN_FAILED", exit_code=-1)
    except FileNotFoundError:
        logger.critical("robocopy.exe not found — not running on Windows?")
        return RobocopyResult(status="LAN_FAILED", exit_code=-1)
    except OSError as e:
        logger.critical(f"Robocopy failed with OS error: {e}")
        return RobocopyResult(status="LAN_FAILED", exit_code=-1)


def _compute_file_checksum(file_path: Path) -> str:
    """Compute xxHash64 for a single file.

    Args:
        file_path: Path to the file.

    Returns:
        16-character hex string.
    """
    import xxhash
    h = xxhash.xxh64()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8 * 1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
