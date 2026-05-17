"""Rclone wrapper — executes sync to GCS with temp config and cleanup."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from core.manifest_db import ManifestDB
from models.config_model import AppConfig
from models.scan_result import ScanResult


@dataclass
class RcloneResult:
    """Result of an Rclone execution."""
    status: str  # CLOUD_COMPLETE, CLOUD_PARTIAL, CLOUD_FAILED, CLOUD_SKIPPED
    exit_code: int
    output: str = ""


def _classify_exit_code(code: int) -> str:
    """Classify Rclone exit code.

    Code 0: CLOUD_COMPLETE
    Code 1: CLOUD_FAILED (syntax error)
    Code 2: CLOUD_PARTIAL
    Code 3: CLOUD_FAILED (source/destination not found)
    Code 4: CLOUD_PARTIAL
    Code 5: CLOUD_FAILED (temporary network error — Prefect retries at task level)
    Code 6: CLOUD_PARTIAL
    Code 7: CLOUD_FAILED
    Code 8: CLOUD_PARTIAL
    Other: CLOUD_FAILED

    Args:
        code: Rclone exit code.

    Returns:
        CLOUD_COMPLETE, CLOUD_PARTIAL, or CLOUD_FAILED.
    """
    mapping = {
        0: "CLOUD_COMPLETE",
        1: "CLOUD_FAILED",
        2: "CLOUD_PARTIAL",
        3: "CLOUD_FAILED",
        4: "CLOUD_PARTIAL",
        5: "CLOUD_FAILED",
        6: "CLOUD_PARTIAL",
        7: "CLOUD_FAILED",
        8: "CLOUD_PARTIAL",
    }
    return mapping.get(code, "CLOUD_FAILED")


def _write_temp_config(temp_dir: Path, job_id: str, gcs_key_path: str) -> Path:
    """Write a temporary rclone.conf with restricted ACL.

    Args:
        temp_dir: Directory for temp files.
        job_id: Unique identifier for this run.
        gcs_key_path: Path to GCS service account JSON key.

    Returns:
        Path to the created temp config file.
    """
    temp_dir.mkdir(parents=True, exist_ok=True)
    config_path = temp_dir / f"rclone_{job_id}.conf"

    content = (
        "[gcs_backup]\n"
        "type = google cloud storage\n"
        f"service_account_file = {gcs_key_path}\n"
        "bucket_policy_only = true\n"
        "location = asia-south1\n"
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
        config_path = _write_temp_config(temp_dir, job_id, gcs_key_path)
        filter_path = _write_filter_file(
            temp_dir, job_id,
            scope_config.exclude_folders,
            scope_config.exclude_extensions,
            scope_config.exclude_patterns,
            paths_config.source_drive,
        )

        # Build command
        remote = f"gcs_backup:{cloud_config.bucket}/{cloud_config.remote_path}"
        cmd = [
            "rclone", "sync",
            paths_config.source_drive,
            remote,
            "--config", str(config_path),
            "--filter-from", str(filter_path),
            "--bwlimit", cloud_config.bandwidth_limit,
            "--gcs-chunk-size", cloud_config.chunk_size,
            "--transfers", "4",
            "--checkers", "8",
            "--retries", str(cloud_config.retry_count),
            "--retries-sleep", "30s",
            "--stats", "300s",
            "--stats-log-level", "INFO",
            "--log-level", "INFO",
            "--use-json-log",
            "--no-traverse",
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

        # Update manifest
        if status in ("CLOUD_COMPLETE", "CLOUD_PARTIAL"):
            changed_paths = [
                f.relative_path
                for f in scan_result.new_files + scan_result.modified_files
            ]
            if changed_paths:
                db.batch_mark_cloud_backed_up(changed_paths)

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
