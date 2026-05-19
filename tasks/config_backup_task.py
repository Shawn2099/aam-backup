"""Prefect task: backup config.yaml to LAN and cloud destinations."""

import subprocess
import tempfile
from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger


@task(
    name="backup_config",
    tags=["maintenance"],
    retries=1,
    retry_delay_seconds=30,
    task_run_name="backup-config",
)
def backup_config_task(
    config_path: str,
    lan_destination: str,
    cloud_enabled: bool = False,
    gcs_key_path: str | None = None,
    cloud_bucket: str | None = None,
    cloud_remote_path: str | None = None,
    gcs_location: str | None = None,
) -> dict:
    """Copy config.yaml to LAN and cloud destinations for DR recovery.

    Args:
        config_path: Path to config.yaml.
        lan_destination: UNC path to LAN backup destination.
        cloud_enabled: Whether cloud backup is enabled.
        gcs_key_path: Path to GCS service account JSON key.
        cloud_bucket: GCS bucket name.
        cloud_remote_path: GCS remote path prefix.
        gcs_location: GCS region.

    Returns:
        Result dict with backup status for each destination.
    """
    logger = get_run_logger()

    config_file = Path(config_path)
    if not config_file.exists():
        logger.warning(f"Config file not found at {config_path}, skipping backup")
        return {"status": "SKIPPED", "reason": "config not found"}

    results = {"lan": "SKIPPED", "cloud": "SKIPPED"}

    # Backup to LAN
    try:
        lan_dest = Path(lan_destination)
        if lan_dest.exists():
            dest_path = lan_dest / "config.yaml"
            import shutil
            shutil.copy2(config_file, dest_path)
            results["lan"] = "SUCCESS"
            logger.info(f"config.yaml backed up to LAN: {dest_path}")
        else:
            logger.warning(f"LAN destination not accessible: {lan_destination}")
    except Exception as e:
        results["lan"] = "FAILED"
        logger.error(f"Failed to backup config.yaml to LAN: {e}")

    # Backup to cloud via rclone
    if cloud_enabled and gcs_key_path and cloud_bucket and cloud_remote_path:
        try:
            temp_dir = Path(tempfile.gettempdir()) / "backup_agent_config"
            temp_dir.mkdir(parents=True, exist_ok=True)
            config_path_temp = None

            try:
                config_path_temp = temp_dir / "rclone_config.conf"
                config_path_temp.write_text(
                    "[gcs_backup]\n"
                    "type = google cloud storage\n"
                    f"service_account_file = {gcs_key_path}\n"
                    "bucket_policy_only = true\n"
                    f"location = {gcs_location}\n",
                    encoding="utf-8",
                )

                remote = f"gcs_backup:{cloud_bucket}/{cloud_remote_path}"
                cmd = [
                    "rclone", "copyto",
                    str(config_file),
                    f"{remote}/config.yaml",
                    "--config", str(config_path_temp),
                    "--log-level", "INFO",
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if result.returncode == 0:
                    results["cloud"] = "SUCCESS"
                    logger.info(f"config.yaml backed up to cloud: {remote}/config.yaml")
                else:
                    results["cloud"] = "FAILED"
                    logger.error(f"Rclone copy failed: {result.stderr.strip()}")

            finally:
                if config_path_temp and config_path_temp.exists():
                    try:
                        config_path_temp.unlink()
                    except OSError:
                        pass

        except subprocess.TimeoutExpired:
            results["cloud"] = "FAILED"
            logger.error("Rclone copy timed out")
        except FileNotFoundError:
            results["cloud"] = "FAILED"
            logger.error("rclone not found in PATH")
        except Exception as e:
            results["cloud"] = "FAILED"
            logger.error(f"Failed to backup config.yaml to cloud: {e}")

    return results
