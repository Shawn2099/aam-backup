"""Robocopy wrapper — executes /MIR backup with exit code parsing."""

import subprocess
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from core.manifest_db import ManifestDB
from core.hashing import compute_checksum
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

    Captures all 6 columns from the summary table:
    Total, Copied, Skipped, Mismatch, FAILED, Extras

    Args:
        output: Full Robocopy output text.

    Returns:
        Dict with 'files_copied', 'bytes_copied', 'files_failed'.
    """
    result = {"files_copied": 0, "bytes_copied": 0, "files_failed": 0}

    lines = output.splitlines()
    for line in lines:
        line = line.strip()
        files_match = re.match(r"Files\s*:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", line)
        if files_match:
            result["files_copied"] = int(files_match.group(2))
            result["files_failed"] = int(files_match.group(5))
            continue

        bytes_match = re.match(r"Bytes\s*:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", line)
        if bytes_match:
            result["bytes_copied"] = int(bytes_match.group(2))
            continue

    return result


def _parse_failed_files(output: str, source_drive: str) -> set[str]:
    """Parse Robocopy output for failed file paths.

    Catches all 4 error action types used by Robocopy
    (per ConvertFrom-RobocopLog):

        ERROR 5 (0x00000005) Copying File D:\\path\\to\\file.txt
        ERROR 32 (0x00000020) Accessing Source File D:\\path\\to\\file.txt
        ERROR 32 (0x00000020) Deleting File D:\\path\\to\\file.txt
        ERROR 5 (0x00000005) Deleting Extra File D:\\path\\to\\file.txt

    Args:
        output: Full Robocopy output text.
        source_drive: Source drive path (e.g., "D:\\").

    Returns:
        Set of relative paths that failed to copy.
    """
    failed = set()
    source_prefix = Path(source_drive).resolve().as_posix()

    # Industry-standard pattern from ConvertFrom-RobocopLog:
    # Catches Copying File, Accessing Source File, Deleting File, Deleting Extra File
    pattern = re.compile(
        r"ERROR\s+\d+\s+\(0x[0-9A-Fa-f]+\)\s+"
        r"(?:Copying|Accessing\s+Source|Deleting\s+(?:Extra\s+)?)\s+File\s+"
        r"(.+)$",
        re.IGNORECASE,
    )

    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            full_path = match.group(1).strip()
            # Convert to relative path
            try:
                full_path_normalized = Path(full_path).resolve().as_posix()
                if full_path_normalized.startswith(source_prefix):
                    relative = full_path_normalized[len(source_prefix):].lstrip("/")
                    # Normalize separators for Windows
                    relative = relative.replace("/", "\\")
                    failed.add(relative)
            except Exception:
                pass

    return failed


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
        "/XJ",
        "/MT:8",
        f"/R:{lan_config.retry_count}",
        f"/W:{lan_config.retry_wait_seconds}",
        "/NP",
        "/BYTES",
        "/TEE",
        # Safety: prevent /MIR from deleting System Volume Information
        # on destination (known issue on Windows Server 2012/2016)
        "/XD", "System Volume Information",
    ]

    # Add exclusions
    for folder in scope_config.exclude_folders:
        cmd.extend(["/XD", folder])

    for ext in scope_config.exclude_extensions:
        cmd.extend(["/XF", f"*{ext}"])

    for pattern in scope_config.exclude_patterns:
        cmd.extend(["/XF", pattern])

    logger.info(f"Running Robocopy: {' '.join(cmd[:4])}...")

    log_path = None
    try:
        # Microsoft recommends /log with /MT to avoid stdout buffering bottleneck
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".log", prefix="robocopy_", delete=False
        ) as log_file:
            log_path = Path(log_file.name)

        cmd.extend([f"/log:{log_path}"])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=lan_config.subprocess_timeout_seconds,
        )

        # Read log file for parsing (more reliable than stdout with /MT)
        output_text = log_path.read_text(encoding="utf-8")

        exit_code = result.returncode
        status = _classify_exit_code(exit_code)
        stats = _parse_robocopy_output(output_text)

        robocopy_result = RobocopyResult(
            status=status,
            exit_code=exit_code,
            files_copied=stats["files_copied"],
            bytes_copied=stats["bytes_copied"],
            files_failed=stats["files_failed"],
            output=output_text,
        )

        logger.info(
            f"Robocopy {status}: {stats['files_copied']} files copied, "
            f"{stats['bytes_copied']} bytes, {stats['files_failed']} failed"
        )

        # Update manifest for backed up files
        # On partial failure, only mark files that actually succeeded
        if status in ("LAN_COMPLETE", "LAN_PARTIAL"):
            all_changed = [f.relative_path for f in scan_result.new_files + scan_result.modified_files]
            failed_paths = _parse_failed_files(output_text, paths_config.source_drive)

            # Only mark files that were NOT in the failed list
            successful_paths = [p for p in all_changed if p not in failed_paths]

            if failed_paths:
                logger.warning(f"Robocopy failed on {len(failed_paths)} files: {list(failed_paths)[:10]}")

            if successful_paths:
                db.batch_mark_lan_backed_up(successful_paths)

            # Compute checksums for new files that were successfully backed up
            for file_info in scan_result.new_files:
                if file_info.relative_path in failed_paths:
                    continue
                entry = db.get_entry(file_info.relative_path)
                if entry and entry.checksum == "pending":
                    try:
                        full_path = Path(paths_config.source_drive) / file_info.relative_path
                        checksum = compute_checksum(full_path)
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
    finally:
        if log_path and log_path.exists():
            try:
                log_path.unlink()
            except OSError:
                pass


