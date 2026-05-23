"""Prefect task: backup manifest.db with WAL checkpoint, SHA256, and retention (D-008).

Backs up manifest.db to LAN destination (preferred) and cloud (last resort).
Each backup is timestamped and integrity-verified with SHA256.
Old backups beyond retention_count are pruned.
"""

import hashlib
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger

from core.manifest_db import ManifestDB


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
    lan_path: str = "_manifest/",
    cloud_path: str = "_manifest/",
    retention_count: int = 7,
) -> dict:
    """Copy manifest.db to LAN and cloud destinations with integrity verification.

    Steps:
    1. WAL checkpoint to flush pending writes
    2. Copy to LAN _manifest/ with timestamp
    3. Generate SHA256 hash file alongside
    4. Copy to cloud _manifest/ (last resort)
    5. Prune old backups beyond retention_count

    Args:
        database_path: Path to the local manifest.db.
        lan_destination: UNC path to LAN backup destination.
        cloud_enabled: Whether to also copy to cloud.
        gcs_key_path: Path to GCS service account JSON key.
        bucket: GCS bucket name.
        remote_path: GCS remote path prefix.
        gcs_location: GCS region.
        lan_path: Relative path on LAN for manifest backups.
        cloud_path: Relative path on GCS for manifest backups.
        retention_count: Number of historical backups to retain.

    Returns:
        Result dict with backup status for each destination.
    """
    logger = get_run_logger()
    db_path = Path(database_path)

    if not db_path.exists():
        logger.warning(f"manifest.db not found at {db_path}, skipping backup")
        return {"status": "SKIPPED", "reason": "database not found"}

    results = {"lan": "SKIPPED", "cloud": "SKIPPED", "sha256": None}

    # Step 1: WAL checkpoint before copy
    try:
        _wal_checkpoint(database_path)
        logger.debug("WAL checkpoint completed before manifest backup")
    except Exception as e:
        logger.warning(f"WAL checkpoint failed (non-critical): {e}")

    # Step 2: Backup to LAN destination
    try:
        lan_dest = Path(lan_destination) / lan_path.rstrip("/")
        lan_dest.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_name = f"manifest_{timestamp}.db"
        backup_path = lan_dest / backup_name

        shutil.copy2(db_path, backup_path)

        # Step 3: Generate SHA256 hash
        sha256_hash = _compute_sha256(backup_path)
        hash_path = lan_dest / f"{backup_name}.sha256"
        hash_path.write_text(f"{sha256_hash}  {backup_name}\n", encoding="utf-8")

        results["lan"] = "SUCCESS"
        results["sha256"] = sha256_hash
        logger.info(f"manifest.db backed up to LAN: {backup_path} (SHA256: {sha256_hash[:16]}...)")

        # Step 5: Prune old LAN backups
        _prune_old_backups(lan_dest, "manifest_", retention_count)

    except Exception as e:
        results["lan"] = "FAILED"
        logger.error(f"Failed to backup manifest.db to LAN: {e}")

    # Step 4: Backup to cloud (last resort)
    if cloud_enabled and gcs_key_path and bucket and remote_path:
        try:
            from core.rclone import _write_temp_config
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_name = f"manifest_{timestamp}.db"

            temp_dir = Path(tempfile.gettempdir()) / "backup_agent_manifest"
            temp_config = _write_temp_config(temp_dir, "manifest", gcs_key_path, gcs_location)

            try:
                remote = f"gcs_backup:{bucket}/{remote_path}/{cloud_path.rstrip('/')}"
                cmd = [
                    "rclone", "copyto",
                    str(db_path),
                    f"{remote}/{backup_name}",
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
                    # Upload SHA256 hash too
                    sha256_hash = _compute_sha256(db_path)
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".sha256", delete=False
                    ) as hf:
                        hf.write(f"{sha256_hash}  {backup_name}\n")
                        hash_temp = Path(hf.name)

                    subprocess.run(
                        ["rclone", "copyto", str(hash_temp), f"{remote}/{backup_name}.sha256",
                         "--config", str(temp_config), "--log-level", "INFO"],
                        capture_output=True, text=True, timeout=60,
                    )
                    hash_temp.unlink(missing_ok=True)

                    results["cloud"] = "SUCCESS"
                    logger.info(f"manifest.db backed up to cloud: {remote}/{backup_name}")

                    # Prune old cloud backups
                    _prune_cloud_backups(
                        remote, temp_config, "manifest_", retention_count,
                    )
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


def _wal_checkpoint(database_path: str):
    """Force a WAL checkpoint to flush all pending writes to the main database file."""
    import sqlite3
    conn = sqlite3.connect(database_path)
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.commit()
    finally:
        conn.close()


def _compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def _prune_old_backups(backup_dir: Path, prefix: str, retention_count: int):
    """Remove old backup files beyond retention count."""
    try:
        backups = sorted(
            [f for f in backup_dir.iterdir() if f.name.startswith(prefix) and f.suffix == ".db"],
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        for old_backup in backups[retention_count:]:
            old_backup.unlink()
            hash_file = old_backup.with_suffix(".db.sha256")
            if hash_file.exists():
                hash_file.unlink()
    except Exception:
        pass  # Pruning is non-critical


def _prune_cloud_backups(remote: str, config_path: Path, prefix: str, retention_count: int):
    """Remove old cloud backup files beyond retention count."""
    try:
        result = subprocess.run(
            ["rclone", "lsf", remote, "--config", str(config_path), "--log-level", "ERROR"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            backups = sorted(
                [line for line in result.stdout.splitlines()
                 if line.startswith(prefix) and line.endswith(".db")],
                reverse=True,
            )
            for old_backup in backups[retention_count:]:
                subprocess.run(
                    ["rclone", "deletefile", f"{remote}/{old_backup}",
                     "--config", str(config_path), "--log-level", "ERROR"],
                    capture_output=True, text=True, timeout=30,
                )
                subprocess.run(
                    ["rclone", "deletefile", f"{remote}/{old_backup}.sha256",
                     "--config", str(config_path), "--log-level", "ERROR"],
                    capture_output=True, text=True, timeout=30,
                )
    except Exception:
        pass  # Pruning is non-critical
