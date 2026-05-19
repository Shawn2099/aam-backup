"""Prefect task: automated test restore — verify random files from LAN and GCS."""

import random
import subprocess
import tempfile
from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger

from core.manifest_db import ManifestDB
from core.rclone import _write_temp_config
from models.manifest_model import PENDING_CHECKSUM


@task(
    name="test_restore_verification",
    tags=["verification", "maintenance"],
    retries=0,
    task_run_name="test-restore-verification",
    timeout_seconds=3600,  # 1 hour max
)
def test_restore_task(
    database_path: str,
    source_drive: str,
    lan_destination: str,
    cloud_enabled: bool = False,
    gcs_key_path: str | None = None,
    cloud_bucket: str | None = None,
    cloud_remote_path: str | None = None,
    gcs_location: str | None = None,
    sample_count: int = 10,
) -> dict:
    """Pick random files from manifest and verify they exist on LAN and GCS.

    Uses rclone for individual file checks against GCS, and direct
    file existence + size check against LAN destination.

    Args:
        database_path: Path to manifest.db.
        source_drive: Source drive path (e.g., "D:\\").
        lan_destination: UNC path to LAN backup destination.
        cloud_enabled: Whether cloud backup is enabled.
        gcs_key_path: Path to GCS service account JSON key.
        cloud_bucket: GCS bucket name.
        cloud_remote_path: GCS remote path prefix.
        gcs_location: GCS region.
        sample_count: Number of random files to verify.

    Returns:
        Dict with verification results for LAN and cloud.
    """
    logger = get_run_logger()

    db_path = Path(database_path)
    if not db_path.exists():
        logger.warning(f"manifest.db not found at {db_path}, skipping test restore")
        return {"status": "SKIPPED", "reason": "database not found"}

    db = ManifestDB(database_path)
    try:
        all_entries = db.get_all_entries()
    finally:
        db.close()

    if not all_entries:
        logger.warning("Manifest is empty, skipping test restore")
        return {"status": "SKIPPED", "reason": "empty manifest"}

    # Filter to files with confirmed backups (not PENDING_CHECKSUM checksum)
    backed_up = {
        path: entry
        for path, entry in all_entries.items()
        if entry.checksum != PENDING_CHECKSUM
    }

    if not backed_up:
        logger.warning("No confirmed backup files in manifest, skipping test restore")
        return {"status": "SKIPPED", "reason": "no confirmed backups"}

    # Sample random files
    actual_count = min(sample_count, len(backed_up))
    sampled = random.sample(list(backed_up.items()), actual_count)

    logger.info(f"Test restore: sampling {actual_count} random files from {len(backed_up)} confirmed backups")

    lan_results = []
    cloud_results = []

    for relative_path, entry in sampled:
        # Verify on LAN
        lan_result = _verify_lan_file(lan_destination, relative_path, int(entry.file_size))  # type: ignore[arg-type]
        lan_results.append(lan_result)

        # Verify on cloud
        if cloud_enabled and gcs_key_path and cloud_bucket and cloud_remote_path and gcs_location:
            cloud_result = _verify_cloud_file(
                gcs_key_path, gcs_location, cloud_bucket, cloud_remote_path,
                relative_path, int(entry.file_size),  # type: ignore[arg-type]
            )
            cloud_results.append(cloud_result)

    # Summarize
    lan_ok = sum(1 for r in lan_results if r["status"] == "OK")
    lan_fail = sum(1 for r in lan_results if r["status"] != "OK")

    cloud_ok = sum(1 for r in cloud_results if r["status"] == "OK") if cloud_results else 0
    cloud_fail = sum(1 for r in cloud_results if r["status"] != "OK") if cloud_results else 0

    lan_status = "OK" if lan_fail == 0 else "PARTIAL" if lan_ok > 0 else "FAILED"
    cloud_status = None
    if cloud_results:
        cloud_status = "OK" if cloud_fail == 0 else "PARTIAL" if cloud_ok > 0 else "FAILED"

    logger.info(
        f"Test restore LAN: {lan_ok}/{len(lan_results)} OK ({lan_status})"
    )
    if cloud_status:
        logger.info(
            f"Test restore cloud: {cloud_ok}/{len(cloud_results)} OK ({cloud_status})"
        )

    return {
        "lan": {"status": lan_status, "ok": lan_ok, "failed": lan_fail, "details": lan_results},
        "cloud": {
            "status": cloud_status,
            "ok": cloud_ok,
            "failed": cloud_fail,
            "details": cloud_results,
        } if cloud_results else {"status": "SKIPPED"},
    }


def _verify_lan_file(lan_destination: str, relative_path: str, expected_size: int) -> dict:
    """Verify a single file exists on LAN with matching size."""
    try:
        lan_path = Path(lan_destination) / relative_path

        if not lan_path.exists():
            return {"path": relative_path, "status": "MISSING", "reason": "file not found on LAN"}

        actual_size = lan_path.stat().st_size
        if actual_size != expected_size:
            return {
                "path": relative_path,
                "status": "MISMATCH",
                "expected_size": expected_size,
                "actual_size": actual_size,
            }

        return {"path": relative_path, "status": "OK", "size": actual_size}

    except Exception as e:
        return {"path": relative_path, "status": "ERROR", "reason": str(e)}


def _verify_cloud_file(
    gcs_key_path: str,
    gcs_location: str,
    bucket: str,
    remote_path: str,
    relative_path: str,
    expected_size: int,
) -> dict:
    """Verify a single file exists on GCS with matching size using rclone."""
    temp_dir = Path(tempfile.gettempdir()) / "backup_agent_test_restore"
    temp_dir.mkdir(parents=True, exist_ok=True)
    job_id = "test_restore"

    config_path = None

    try:
        config_path = _write_temp_config(temp_dir, job_id, gcs_key_path, gcs_location)

        remote = f"gcs_backup:{bucket}/{remote_path}/{relative_path}"

        cmd = [
            "rclone", "ls",
            remote,
            "--config", str(config_path),
            "--log-level", "ERROR",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            return {"path": relative_path, "status": "MISSING", "reason": "file not found on GCS"}

        output = result.stdout.strip()
        if not output:
            return {"path": relative_path, "status": "MISSING", "reason": "empty rclone ls output"}

        parts = output.split(None, 1)
        if len(parts) < 1:
            return {"path": relative_path, "status": "ERROR", "reason": "unexpected rclone output"}

        actual_size = int(parts[0])
        if actual_size != expected_size:
            return {
                "path": relative_path,
                "status": "MISMATCH",
                "expected_size": expected_size,
                "actual_size": actual_size,
            }

        return {"path": relative_path, "status": "OK", "size": actual_size}

    except subprocess.TimeoutExpired:
        return {"path": relative_path, "status": "ERROR", "reason": "rclone timed out"}

    except FileNotFoundError:
        return {"path": relative_path, "status": "ERROR", "reason": "rclone not found"}

    except Exception as e:
        return {"path": relative_path, "status": "ERROR", "reason": str(e)}

    finally:
        if config_path and config_path.exists():
            try:
                config_path.unlink()
            except OSError:
                pass
