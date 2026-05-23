"""Rclone wrapper — executes sync to GCS with temp config and cleanup."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from core.manifest_db import ManifestDB
from core.hashing import compute_checksum
from models.config_model import AppConfig
from models.manifest_model import PENDING_CHECKSUM
from models.scan_result import ScanResult


@dataclass
class RcloneResult:
    """Result of an Rclone execution."""
    status: str  # CLOUD_COMPLETE, CLOUD_PARTIAL, CLOUD_FAILED, CLOUD_SKIPPED
    exit_code: int
    output: str = ""


def _classify_exit_code(code: int) -> str:
    """Classify Rclone exit code per official documentation.

    Official rclone exit codes:
        0 — Success
        1 — Syntax or usage error
        2 — Directory or file not found (source/destination error)
        3 — Source or destination does not exist
        4 — File not found (less serious, often transient)
        5 — Temporary network error (retryable — Prefect handles at task level)
        6 — Less serious error (e.g., partial transfer issues)
        7 — Fatal error (authentication failure, bucket not found, etc.)
        8 — Transfer limit exceeded (--max-transfer or --max-backlog)
        9 — No files transferred (--error-on-no-transfer was set)
       10 — Duration limit exceeded (--max-duration)

    Mapping for our backup flow:
        0 → CLOUD_COMPLETE (success)
        1 → CLOUD_FAILED (syntax/usage — config problem)
        2 → CLOUD_FAILED (source/dest error — needs investigation)
        3 → CLOUD_FAILED (source/dest missing — hard failure)
        4 → CLOUD_PARTIAL (file not found — may be transient)
        5 → CLOUD_PARTIAL (network error — Prefect retries at task level)
        6 → CLOUD_PARTIAL (less serious — some files transferred)
        7 → CLOUD_FAILED (fatal — auth, bucket, or critical error)
        8 → CLOUD_FAILED (transfer limit — should not happen in normal operation)
        9 → CLOUD_COMPLETE (no files to transfer — source already matches dest)
       10 → CLOUD_PARTIAL (duration limit hit — some files may have transferred)
    Other → CLOUD_FAILED
    """
    mapping = {
        0: "CLOUD_COMPLETE",
        1: "CLOUD_FAILED",
        2: "CLOUD_FAILED",
        3: "CLOUD_FAILED",
        4: "CLOUD_PARTIAL",
        5: "CLOUD_PARTIAL",
        6: "CLOUD_PARTIAL",
        7: "CLOUD_FAILED",
        8: "CLOUD_FAILED",
        9: "CLOUD_COMPLETE",
        10: "CLOUD_PARTIAL",
    }
    return mapping.get(code, "CLOUD_FAILED")


def _write_temp_config(temp_dir: Path, job_id: str, gcs_key_path: str, gcs_location: str = "asia-south1") -> Path:
    """Write a temporary rclone.conf with restricted ACL.

    Args:
        temp_dir: Directory for temp files.
        job_id: Unique identifier for this run.
        gcs_key_path: Path to GCS service account JSON key.
        gcs_location: GCS region (from config).

    Returns:
        Path to the created temp config file.
    """
    temp_dir.mkdir(parents=True, exist_ok=True)
    config_path = temp_dir / f"rclone_{job_id}.conf"

    content = (
        "[gcs_backup]\n"
        "type = google cloud storage\n"
        f"service_account_file = {gcs_key_path.replace(chr(92), '/')}\n"
        "bucket_policy_only = true\n"
        f"location = {gcs_location}\n"
    )

    config_path.write_text(content, encoding="utf-8")

    # Apply restricted ACL on Windows
    import platform
    if platform.system().lower() == "windows":
        try:
            subprocess.run(
                ["icacls", str(config_path), "/inheritance:r"],
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to set ACL on temp config: {e}")

    return config_path


def _write_filter_file(
    temp_dir: Path,
    job_id: str,
    exclude_folders: list[str],
    exclude_extensions: list[str],
    exclude_patterns: list[str],
    source_drive: str,
) -> Path:
    """Write a temporary rclone filter file.

    Converts Windows paths to rclone filter syntax with forward slashes.

    Args:
        temp_dir: Directory for temp files.
        job_id: Unique identifier for this run.
        exclude_folders: List of excluded folder paths.
        exclude_extensions: List of excluded extensions.
        exclude_patterns: List of excluded patterns.
        source_drive: Source drive path (e.g., "D:\\").

    Returns:
        Path to the created filter file.
    """
    temp_dir.mkdir(parents=True, exist_ok=True)
    filter_path = temp_dir / f"rclone_filter_{job_id}.txt"

    lines = []

    # Convert folder exclusions: D:\Folder\Name → - Folder/Name/**
    # Strip source drive prefix and convert backslashes to forward slashes
    source_prefix = source_drive.rstrip("\\").rstrip("/")
    for folder in exclude_folders:
        # Remove source prefix (case-insensitive)
        relative = folder
        if relative.lower().startswith(source_prefix.lower()):
            relative = relative[len(source_prefix):]
        # Strip leading separators and convert to forward slashes
        relative = relative.lstrip("\\/").replace("\\", "/")
        if relative:
            lines.append(f"- {relative}/**")

    # Extension exclusions: - *.ext
    for ext in exclude_extensions:
        lines.append(f"- *{ext}")

    # Pattern exclusions
    for pattern in exclude_patterns:
        lines.append(f"- {pattern}")

    filter_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return filter_path


def run_rclone_check(
    config: AppConfig,
    gcs_key_path: str,
) -> dict:
    """Run rclone check to verify source vs cloud destination integrity.

    Uses rclone's --differ, --missing-on-dst, --error flags to write
    mismatch details to temp files (one path per line). No stdout parsing.
    Compares source and destination files by size and GCS server-side MD5 hash.

    Args:
        config: Validated application configuration.
        gcs_key_path: Path to GCS service account JSON key.

    Returns:
        Dict with check results: {"status": str, "matches": int, "mismatches": int,
        "missing": int, "errors": int, "differ_paths": list, "missing_paths": list, "error_paths": list}
    """
    cloud_config = config.cloud_backup
    paths_config = config.paths
    temp_dir = Path(paths_config.rclone_temp_directory)
    job_id = "check"

    config_path = None
    filter_path = None
    differ_file = None
    missing_file = None
    error_file = None

    try:
        config_path = _write_temp_config(temp_dir, job_id, gcs_key_path, cloud_config.gcs_location)
        filter_path = _write_filter_file(
            temp_dir, job_id,
            config.backup_scope.exclude_folders,
            config.backup_scope.exclude_extensions,
            config.backup_scope.exclude_patterns,
            paths_config.source_drive,
        )

        # Temp files for rclone structured output (one path per line)
        differ_file = temp_dir / f"rclone_{job_id}_differ.txt"
        missing_file = temp_dir / f"rclone_{job_id}_missing.txt"
        error_file = temp_dir / f"rclone_{job_id}_errors.txt"

        remote = f"gcs_backup:{cloud_config.bucket}/{cloud_config.remote_path}"
        cmd = [
            "rclone", "check",
            paths_config.source_drive,
            remote,
            "--config", str(config_path),
            "--filter-from", str(filter_path),
            # Structured output to files — no stdout parsing needed
            "--differ", str(differ_file),
            "--missing-on-dst", str(missing_file),
            "--error", str(error_file),
            # GCS-specific optimizations
            "--fast-list",
            "--gcs-no-check-bucket",
            "--modify-window", "1s",
            # Progress and logging
            "--stats", "60s",
            "--log-level", "INFO",
            "--use-json-log",
            "--one-way",  # Only check source → destination (not destination → source)
        ]

        logger.info(f"Running Rclone check: {paths_config.source_drive} vs {remote}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=cloud_config.subprocess_timeout_seconds,
        )

        # Read structured output files (one path per line, no parsing needed)
        differ_paths = _read_path_file(differ_file)
        missing_paths = _read_path_file(missing_file)
        error_paths = _read_path_file(error_file)

        mismatches = len(differ_paths)
        missing = len(missing_paths)
        errors = len(error_paths)

        # rclone check returns 0 if all OK, 1 if differences found
        status = "OK" if result.returncode == 0 else "MISMATCH"

        logger.info(
            f"Rclone check {status}: "
            f"{mismatches} mismatches, "
            f"{missing} missing, "
            f"{errors} errors"
        )

        return {
            "status": status,
            "matches": 0,  # Not tracked by file-output mode
            "mismatches": mismatches,
            "missing": missing,
            "errors": errors,
            "differ_paths": differ_paths,
            "missing_paths": missing_paths,
            "error_paths": error_paths,
            "output": result.stdout,
        }

    except subprocess.TimeoutExpired:
        logger.critical(f"Rclone check timed out after {cloud_config.subprocess_timeout_seconds}s")
        return {"status": "TIMEOUT", "matches": 0, "mismatches": 0, "missing": 0, "errors": 0,
                "differ_paths": [], "missing_paths": [], "error_paths": [], "output": ""}

    except FileNotFoundError:
        logger.critical("rclone.exe not found — not installed?")
        return {"status": "ERROR", "matches": 0, "mismatches": 0, "missing": 0, "errors": 0,
                "differ_paths": [], "missing_paths": [], "error_paths": [], "output": ""}

    except OSError as e:
        logger.critical(f"Rclone check failed with OS error: {e}")
        return {"status": "ERROR", "matches": 0, "mismatches": 0, "missing": 0, "errors": 0,
                "differ_paths": [], "missing_paths": [], "error_paths": [], "output": ""}

    finally:
        for path in [config_path, filter_path, differ_file, missing_file, error_file]:
            if path and path.exists():
                try:
                    path.unlink()
                    logger.debug(f"Cleaned up temp file: {path}")
                except OSError as e:
                    logger.critical(f"Failed to delete temp file {path}: {e} — Manual deletion required")


def _read_path_file(file_path: Path) -> list[str]:
    """Read a file containing one path per line (from rclone --differ/--missing-on-dst/--error).

    Returns empty list if file doesn't exist or is empty.

    Args:
        file_path: Path to the file.

    Returns:
        List of paths, one per line, stripped of whitespace.
    """
    if not file_path or not file_path.exists():
        return []
    try:
        content = file_path.read_text(encoding="utf-8").strip()
        if not content:
            return []
        return [line.strip() for line in content.splitlines() if line.strip()]
    except OSError:
        return []


def run_rclone(
    config: AppConfig,
    gcs_key_path: str,
    scan_result: ScanResult,
    db: ManifestDB,
) -> RcloneResult:
    """Execute rclone sync to mirror source to GCS.

    Creates temp config and filter files, executes sync,
    cleans up temp files in finally block.

    Retry logic is handled at the Prefect task level via exponential_backoff.

    Args:
        config: Validated application configuration.
        gcs_key_path: Path to GCS service account JSON key.
        scan_result: ScanResult with new/modified files.
        db: ManifestDB instance for post-backup manifest updates.

    Returns:
        RcloneResult with status and output.
    """
    if not config.cloud_backup.enabled:
        logger.info("Cloud backup disabled, skipping Rclone")
        return RcloneResult(status="CLOUD_SKIPPED", exit_code=0)

    cloud_config = config.cloud_backup
    paths_config = config.paths
    scope_config = config.backup_scope
    temp_dir = Path(paths_config.rclone_temp_directory)
    job_id = "run"  # Simplified — in production use uuid4()[:8]

    config_path = None
    filter_path = None

    try:
        # Create temp files
        config_path = _write_temp_config(temp_dir, job_id, gcs_key_path, cloud_config.gcs_location)
        filter_path = _write_filter_file(
            temp_dir, job_id,
            scope_config.exclude_folders,
            scope_config.exclude_extensions,
            scope_config.exclude_patterns,
            paths_config.source_drive,
        )

        # Build command — GCS-optimized flags based on official rclone docs
        # and GCS backend best practices for large file syncs
        remote = f"gcs_backup:{cloud_config.bucket}/{cloud_config.remote_path}"
        cmd = [
            "rclone", "sync",
            paths_config.source_drive,
            remote,
            "--config", str(config_path),
            "--filter-from", str(filter_path),
            # Bandwidth and chunk size (from config)
            "--bwlimit", cloud_config.bandwidth_limit,
            "--gcs-chunk-size", cloud_config.chunk_size,
            # Parallelism — tuned for GCS with 200K+ files
            "--transfers", "4",       # Concurrent file transfers
            "--checkers", "16",       # Parallel directory listing (default 8, doubled for GCS)
            # GCS-specific optimizations
            "--fast-list",            # Use GCS recursive ListObjects API (fewer API calls)
            "--gcs-no-check-bucket",  # Skip bucket existence check (saves 1 transaction per run)
            "--gcs-storage-class", cloud_config.storage_class,  # Set object class on upload
            "--modify-window", "1s",  # Avoid unnecessary metadata updates (GCS has 1s precision)
            # Retry and reliability
            "--retries", str(cloud_config.retry_count),
            "--retries-sleep", "30s",
            # Progress visibility — 60s stats so march phase is observable
            "--stats", "60s",
            "--stats-log-level", "INFO",
            # Logging
            "--log-level", "INFO",
            "--use-json-log",
            # Sync behavior
            "--no-traverse",          # Don't list destination for transfers (only for deletions)
        ]

        logger.info(f"Running Rclone sync to {remote}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=cloud_config.subprocess_timeout_seconds,
        )

        status = _classify_exit_code(result.returncode)

        rclone_result = RcloneResult(
            status=status,
            exit_code=result.returncode,
            output=result.stdout,
        )

        logger.info(f"Rclone {status} (exit code {result.returncode})")

        # Compute checksums for new files that were successfully backed up
        if status in ("CLOUD_COMPLETE", "CLOUD_PARTIAL"):
            for file_info in scan_result.new_files:
                entry = db.get_entry(file_info.relative_path)
                if entry and entry.checksum == PENDING_CHECKSUM:
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

        return rclone_result

    except subprocess.TimeoutExpired:
        logger.critical(
            f"Rclone timed out after {cloud_config.subprocess_timeout_seconds}s"
        )
        return RcloneResult(status="CLOUD_FAILED", exit_code=-1)

    except FileNotFoundError:
        logger.critical("rclone.exe not found — not installed?")
        return RcloneResult(status="CLOUD_FAILED", exit_code=-1)

    except OSError as e:
        logger.critical(f"Rclone failed with OS error: {e}")
        return RcloneResult(status="CLOUD_FAILED", exit_code=-1)

    finally:
        # Clean up temp files
        for path in [config_path, filter_path]:
            if path and path.exists():
                try:
                    path.unlink()
                    logger.debug(f"Cleaned up temp file: {path}")
                except OSError as e:
                    logger.critical(f"Failed to delete temp file {path}: {e} — Manual deletion required")
