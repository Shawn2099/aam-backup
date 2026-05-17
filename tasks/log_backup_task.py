"""Prefect task: sync log files to cloud backup."""

import subprocess
from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger

from core.rclone import _write_temp_config, _write_filter_file


@task(
    name="backup_logs_to_cloud",
    tags=["maintenance"],
    retries=1,
    retry_delay_seconds=60,
    task_run_name="backup-logs-cloud",
    timeout_seconds=3600,  # 1 hour max
)
def backup_logs_cloud_task(
    log_directory: str,
    gcs_key_path: str,
    cloud_enabled: bool,
    cloud_bucket: str,
    cloud_remote_path: str,
    gcs_location: str = "asia-south1",
) -> dict:
    """Sync log files to a separate GCS prefix for disaster recovery.

    Logs are stored under bucket/remote_path/_logs/ to keep them
    separate from backup data but still in the same bucket.

    Args:
        log_directory: Path to log directory.
        gcs_key_path: Path to GCS service account JSON key.
        cloud_enabled: Whether cloud backup is enabled.
        cloud_bucket: GCS bucket name.
        cloud_remote_path: Remote path prefix from config.
        gcs_location: GCS region.

    Returns:
        Result dict with sync status.
    """
    logger = get_run_logger()

    if not cloud_enabled:
        logger.info("Cloud backup disabled, skipping log sync")
        return {"status": "SKIPPED", "reason": "cloud disabled"}

    log_dir = Path(log_directory)
    if not log_dir.exists():
        logger.warning(f"Log directory not found: {log_directory}")
        return {"status": "SKIPPED", "reason": "log dir not found"}

    temp_dir = log_dir.parent / "rclone_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    job_id = "logs"

    config_path = None
    filter_path = None

    try:
        config_path = _write_temp_config(temp_dir, job_id, gcs_key_path, gcs_location)

        # Only sync log files, nothing else
        filter_path = temp_dir / f"rclone_filter_{job_id}.txt"
        filter_path.write_text("+ *.log\n- *\n", encoding="utf-8")

        remote = f"gcs_backup:{cloud_bucket}/{cloud_remote_path}/_logs"
        cmd = [
            "rclone", "sync",
            str(log_dir),
            remote,
            "--config", str(config_path),
            "--filter-from", str(filter_path),
            "--transfers", "2",
            "--retries", "2",
            "--log-level", "INFO",
            "--use-json-log",
        ]

        logger.info(f"Syncing logs to {remote}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,
        )

        status = "SUCCESS" if result.returncode == 0 else "PARTIAL"
        logger.info(f"Log sync {status} (exit code {result.returncode})")

        return {"status": status, "exit_code": result.returncode, "output": result.stdout}

    except subprocess.TimeoutExpired:
        logger.critical("Log sync timed out after 3600s")
        return {"status": "TIMEOUT", "exit_code": -1}

    except FileNotFoundError:
        logger.critical("rclone.exe not found")
        return {"status": "ERROR", "exit_code": -1}

    except OSError as e:
        logger.critical(f"Log sync failed: {e}")
        return {"status": "ERROR", "exit_code": -1}

    finally:
        for path in [config_path, filter_path]:
            if path and path.exists():
                try:
                    path.unlink()
                except OSError:
                    pass
