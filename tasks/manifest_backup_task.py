"""Prefect task: backup manifest.db to LAN and cloud destinations."""

import shutil
import subprocess
from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger


@task(
    name="backup_manifest_db",
    tags=["maintenance"],
    retries=1,
    retry_delay_seconds=30,
    task_run_name="backup-manifest-db",
)
def backup_manifest_db_task(
    database_path: str,
    lan_destination: str,
    cloud_enabled: bool = False,
    gcs_key_path: str | None = None,
    bucket: str | None = None,
    remote_path: str | None = None,
    gcs_location: str | None = None,
) -> dict:
    """Copy manifest.db to LAN and cloud destinations.

    BUG FIX #5: Actually backs up manifest.db to cloud via rclone,
    not just relying on next sync (which excludes BackupAgent folder).

    Args:
        database_path: Path to the local manifest.db.
        lan_destination: UNC path to LAN backup destination.
        cloud_enabled: Whether to also copy to cloud.
        gcs_key_path: Path to GCS service account JSON key.
        bucket: GCS bucket name.
        remote_path: GCS remote path prefix.
        gcs_location: GCS region.

    Returns:
        Result dict with backup status for each destination.
    """
    logger = get_run_logger()
    db_path = Path(database_path)

    if not db_path.exists():
        logger.warning(f"manifest.db not found at {db_path}, skipping backup")
        return {"status": "SKIPPED", "reason": "database not found"}

    results = {"lan": "SKIPPED", "cloud": "SKIPPED"}

    # Backup to LAN destination
    try:
        lan_dest = Path(lan_destination)
        if lan_dest.exists():
            dest_path = lan_dest / "manifest.db"
            shutil.copy2(db_path, dest_path)
            results["lan"] = "SUCCESS"
            logger.info(f"manifest.db backed up to LAN: {dest_path}")
        else:
            results["lan"] = "SKIPPED"
            logger.warning(f"LAN destination not accessible: {lan_destination}")
    except Exception as e:
        results["lan"] = "FAILED"
        logger.error(f"Failed to backup manifest.db to LAN: {e}")

    # BUG FIX #5: Actually copy manifest.db to cloud via rclone
    if cloud_enabled and gcs_key_path and bucket and remote_path:
        try:
            import tempfile
            import platform

            # Write temp rclone config
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".conf", delete=False
            ) as f:
                f.write(
                    "[gcs_backup]\n"
                    "type = google cloud storage\n"
                    f"service_account_file = {gcs_key_path}\n"
                    "bucket_policy_only = true\n"
                    f"location = {gcs_location}\n"
                )
                temp_config = Path(f.name)

            try:
                # Set restricted ACL on Windows
                if platform.system().lower() == "windows":
                    try:
                        subprocess.run(
                            ["icacls", str(temp_config), "/inheritance:r"],
                            capture_output=True,
                            check=True,
                        )
                    except subprocess.CalledProcessError:
                        pass

                remote = f"gcs_backup:{bucket}/{remote_path}"
                cmd = [
                    "rclone", "copyto",
                    str(db_path),
                    f"{remote}/manifest.db",
                    "--config", str(temp_config),
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
                    logger.info(f"manifest.db backed up to cloud: {remote}/manifest.db")
                else:
                    results["cloud"] = "FAILED"
                    logger.error(f"Rclone copy failed: {result.stderr.strip()}")

            finally:
                if temp_config.exists():
                    try:
                        temp_config.unlink()
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
            logger.error(f"Failed to backup manifest.db to cloud: {e}")

    return results
