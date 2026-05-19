"""Post-backup verification: checksum comparison for LAN and cloud.

Provides functions to verify that files were copied correctly
after robocopy (LAN) and rclone (cloud) operations.
"""

import random
import subprocess
import tempfile
from pathlib import Path

from typing import Any
from models.scan_result import ScanResult
from core.hashing import compute_checksum




def verify_lan_checksums(
    source_drive: str,
    lan_destination: str,
    scan_result: ScanResult,
    sample_count: int = 5,
) -> dict:
    """Verify LAN backup integrity by comparing checksums of sampled files.

    Picks random files from the set that robocopy just copied,
    computes xxHash64 on both source and LAN destination, and compares.

    Args:
        source_drive: Source drive path (e.g., "D:\\").
        lan_destination: LAN backup destination path.
        scan_result: ScanResult with new/modified files that were backed up.
        sample_count: Number of files to verify (default 5).

    Returns:
        Dict with {"verified": int, "mismatches": int, "errors": int, "details": [...]}.
    """
    changed = scan_result.new_files + scan_result.modified_files
    if not changed:
        return {"verified": 0, "mismatches": 0, "errors": 0, "details": []}

    actual_count = min(sample_count, len(changed))
    sampled = random.sample(changed, actual_count)

    source_prefix = str(Path(source_drive).resolve())
    results: list[dict[str, Any]] = []
    verified = 0
    mismatches = 0
    errors = 0

    for file_info in sampled:
        source_path = Path(source_prefix) / file_info.relative_path
        lan_path = Path(lan_destination) / file_info.relative_path

        try:
            if not lan_path.exists():
                results.append({"path": file_info.relative_path, "status": "MISSING"})
                errors += 1
                continue

            source_hash = compute_checksum(source_path)
            lan_hash = compute_checksum(lan_path)

            if source_hash == lan_hash:
                results.append({"path": file_info.relative_path, "status": "OK", "checksum": source_hash})
                verified += 1
            else:
                results.append({
                    "path": file_info.relative_path,
                    "status": "MISMATCH",
                    "source_checksum": source_hash,
                    "lan_checksum": lan_hash,
                })
                mismatches += 1

        except Exception as e:
            results.append({"path": file_info.relative_path, "status": "ERROR", "reason": str(e)})
            errors += 1

    return {"verified": verified, "mismatches": mismatches, "errors": errors, "details": results}


def verify_cloud_checksums(
    gcs_key_path: str,
    gcs_location: str,
    bucket: str,
    remote_path: str,
    scan_result: ScanResult,
    sample_count: int = 5,
) -> dict:
    """Verify cloud backup integrity by checking sampled files exist on GCS with matching size.

    Uses rclone ls to check each sampled file's size matches the manifest.

    Args:
        gcs_key_path: Path to GCS service account JSON key.
        gcs_location: GCS region.
        bucket: GCS bucket name.
        remote_path: GCS remote path prefix.
        scan_result: ScanResult with new/modified files that were backed up.
        sample_count: Number of files to verify (default 5).

    Returns:
        Dict with {"verified": int, "mismatches": int, "errors": int, "details": [...]}.
    """
    changed = scan_result.new_files + scan_result.modified_files
    if not changed:
        return {"verified": 0, "mismatches": 0, "errors": 0, "details": []}

    actual_count = min(sample_count, len(changed))
    sampled = random.sample(changed, actual_count)

    temp_dir = Path(tempfile.gettempdir()) / "backup_agent_verify"
    temp_dir.mkdir(parents=True, exist_ok=True)
    job_id = "verify"

    config_path = None

    try:
        # Write temp rclone config
        config_path = temp_dir / f"rclone_{job_id}.conf"
        config_path.write_text(
            "[gcs_backup]\n"
            "type = google cloud storage\n"
            f"service_account_file = {gcs_key_path}\n"
            "bucket_policy_only = true\n"
            f"location = {gcs_location}\n",
            encoding="utf-8",
        )

        results: list[dict[str, Any]] = []
        verified = 0
        mismatches = 0
        errors = 0

        for file_info in sampled:
            remote = f"gcs_backup:{bucket}/{remote_path}/{file_info.relative_path}"

            try:
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
                    results.append({"path": file_info.relative_path, "status": "MISSING"})
                    errors += 1
                    continue

                output = result.stdout.strip()
                if not output:
                    results.append({"path": file_info.relative_path, "status": "MISSING"})
                    errors += 1
                    continue

                parts = output.split(None, 1)
                actual_size = int(parts[0])

                if actual_size == file_info.file_size:
                    results.append({"path": file_info.relative_path, "status": "OK", "size": actual_size})
                    verified += 1
                else:
                    results.append({
                        "path": file_info.relative_path,
                        "status": "MISMATCH",
                        "expected_size": file_info.file_size,
                        "actual_size": actual_size,
                    })
                    mismatches += 1

            except subprocess.TimeoutExpired:
                results.append({"path": file_info.relative_path, "status": "ERROR", "reason": "timeout"})
                errors += 1
            except Exception as e:
                results.append({"path": file_info.relative_path, "status": "ERROR", "reason": str(e)})
                errors += 1

        return {"verified": verified, "mismatches": mismatches, "errors": errors, "details": results}

    finally:
        if config_path and config_path.exists():
            try:
                config_path.unlink()
            except OSError:
                pass


def run_dry_run_lan(source_drive: str, lan_destination: str) -> dict:
    """Run robocopy /L (list-only) to preview what would change on LAN.

    Does NOT copy any files. Reports count of new/changed/deleted files.

    Returns:
        Dict with {"new": int, "modified": int, "deleted": int, "total": int, "output": str}.
    """
    import platform

    if platform.system().lower() != "windows":
        return {"skipped": True, "reason": "Linux dev mode"}

    try:
        cmd = [
            "robocopy",
            source_drive,
            lan_destination,
            "/MIR",
            "/L",
            "/NJH",
            "/NJS",
            "/NDL",
            "/NC",
            "/NS",
            "/NP",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )

        output = result.stdout + result.stderr
        new_files = 0
        modified_files = 0
        deleted_files = 0

        import re
        for line in output.splitlines():
            line = line.strip()
            files_match = re.match(r"Files\s*:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", line)
            if files_match:
                new_files = int(files_match.group(2))
                modified_files = int(files_match.group(3))
                deleted_files = int(files_match.group(4))
                break

        total = new_files + modified_files + deleted_files

        return {
            "skipped": False,
            "new": new_files,
            "modified": modified_files,
            "deleted": deleted_files,
            "total": total,
            "output": output,
        }

    except subprocess.TimeoutExpired:
        return {"skipped": False, "error": "timeout"}
    except Exception as e:
        return {"skipped": False, "error": str(e)}


def run_dry_run_cloud(
    source_drive: str,
    bucket: str,
    remote_path: str,
    gcs_key_path: str,
    gcs_location: str,
) -> dict:
    """Run rclone sync --dry-run to preview what would change on GCS.

    Does NOT copy any files. Reports count of transfers and deletes.

    Returns:
        Dict with {"transfers": int, "deletes": int, "total": int, "output": str}.
    """
    temp_dir = Path(tempfile.gettempdir()) / "backup_agent_dryrun"
    temp_dir.mkdir(parents=True, exist_ok=True)
    config_path = None

    try:
        config_path = temp_dir / "rclone_dryrun.conf"
        config_path.write_text(
            "[gcs_backup]\n"
            "type = google cloud storage\n"
            f"service_account_file = {gcs_key_path}\n"
            "bucket_policy_only = true\n"
            f"location = {gcs_location}\n",
            encoding="utf-8",
        )

        remote = f"gcs_backup:{bucket}/{remote_path}"
        cmd = [
            "rclone", "sync",
            source_drive,
            remote,
            "--config", str(config_path),
            "--dry-run",
            "--stats", "0",
            "--log-level", "INFO",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
        )

        output = result.stdout + result.stderr
        transfers = 0
        deletes = 0

        import re
        for line in output.splitlines():
            if "Transferred:" in line:
                match = re.search(r"(\d+)\s+/", line)
                if match:
                    transfers = int(match.group(1))
            if "Deleted:" in line:
                match = re.search(r"Deleted:\s+(\d+)", line)
                if match:
                    deletes = int(match.group(1))

        total = transfers + deletes

        return {
            "transfers": transfers,
            "deletes": deletes,
            "total": total,
            "output": output,
        }

    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    except FileNotFoundError:
        return {"error": "rclone not found"}
    except Exception as e:
        return {"error": str(e)}

    finally:
        if config_path and config_path.exists():
            try:
                config_path.unlink()
            except OSError:
                pass
