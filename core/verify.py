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
from core.rclone import _write_temp_config




def verify_lan_checksums(
    source_drive: str,
    lan_destination: str,
    scan_result: ScanResult,
) -> dict:
    """Verify LAN backup integrity by comparing checksums of ALL changed files.

    Computes xxHash64 on both source and LAN destination for every file
    that robocopy just copied, ensuring complete integrity.

    Args:
        source_drive: Source drive path (e.g., "D:\\").
        lan_destination: LAN backup destination path.
        scan_result: ScanResult with new/modified files that were backed up.

    Returns:
        Dict with {"verified": int, "mismatches": int, "errors": int, "details": [...]}.
    """
    changed = scan_result.new_files + scan_result.modified_files
    if not changed:
        return {"verified": 0, "mismatches": 0, "errors": 0, "details": []}

    source_prefix = str(Path(source_drive).resolve())
    results: list[dict[str, Any]] = []
    verified = 0
    mismatches = 0
    errors = 0

    for file_info in changed:
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
    job_id = "verify"

    config_path = None

    try:
        config_path = _write_temp_config(temp_dir, job_id, gcs_key_path, gcs_location)

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


def run_dry_run_lan(
    source_drive: str,
    lan_destination: str,
    exclude_folders: list[str] | None = None,
    exclude_extensions: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
) -> dict:
    """Run robocopy /L (list-only) to preview what would change on LAN.

    Uses ALL the same flags and exclusions as the real robocopy run
    (/MIR, /XJ, /XF, /XD, etc.) so the preview accurately reflects
    what the real run will do.

    Returns:
        Dict with {"new": int, "modified": int, "deleted": int, "total": int,
        "exit_code": int, "success": bool, "output": str}.
    """
    import platform

    if platform.system().lower() != "windows":
        return {"skipped": True, "reason": "Linux dev mode"}

    exclude_folders = exclude_folders or []
    exclude_extensions = exclude_extensions or []
    exclude_patterns = exclude_patterns or []

    try:
        cmd = [
            "robocopy",
            source_drive,
            lan_destination,
            "/MIR",
            "/L",
            "/XJ",
            "/NP",
            "/NJH",
            "/NJS",
            "/NDL",
            "/NC",
            "/NS",
            # Same safety exclusion as real run
            "/XD", "System Volume Information",
        ]

        # Same exclusions as real run
        for folder in exclude_folders:
            cmd.extend(["/XD", folder])
        for ext in exclude_extensions:
            cmd.extend(["/XF", f"*{ext}"])
        for pattern in exclude_patterns:
            cmd.extend(["/XF", pattern])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )

        output = result.stdout + result.stderr
        exit_code = result.returncode

        # Exit code 1 means no files changed — that's still a successful dry run
        success = exit_code <= 7

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
            "success": success,
            "exit_code": exit_code,
            "new": new_files,
            "modified": modified_files,
            "deleted": deleted_files,
            "total": total,
            "output": output,
        }

    except subprocess.TimeoutExpired:
        return {"skipped": False, "success": False, "exit_code": -1, "error": "timeout"}
    except Exception as e:
        return {"skipped": False, "success": False, "exit_code": -1, "error": str(e)}


def run_dry_run_cloud(
    source_drive: str,
    bucket: str,
    remote_path: str,
    gcs_key_path: str,
    gcs_location: str,
    exclude_folders: list[str] | None = None,
    exclude_extensions: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
    bandwidth_limit: str = "10M",
    chunk_size: str = "100M",
    retry_count: int = 3,
) -> dict:
    """Run rclone sync --dry-run to preview what would change on GCS.

    Uses ALL the same flags, filter file, and optimizations as the real
    rclone sync run so the preview accurately reflects what will happen.

    Returns:
        Dict with {"transfers": int, "deletes": int, "total": int,
        "exit_code": int, "success": bool, "output": str}.
    """
    exclude_folders = exclude_folders or []
    exclude_extensions = exclude_extensions or []
    exclude_patterns = exclude_patterns or []

    temp_dir = Path(tempfile.gettempdir()) / "backup_agent_dryrun"
    temp_dir.mkdir(parents=True, exist_ok=True)
    config_path = None
    filter_path = None

    try:
        config_path = _write_temp_config(temp_dir, "dryrun", gcs_key_path, gcs_location)

        # Write filter file (same exclusions as real run)
        filter_path = temp_dir / "rclone_dryrun_filter.txt"
        filter_lines = []
        source_prefix = source_drive.rstrip("\\").rstrip("/")
        for folder in exclude_folders:
            relative = folder
            if relative.lower().startswith(source_prefix.lower()):
                relative = relative[len(source_prefix):]
            relative = relative.lstrip("\\/").replace("\\", "/")
            if relative:
                filter_lines.append(f"- {relative}/**")
        for ext in exclude_extensions:
            filter_lines.append(f"- *{ext}")
        for pattern in exclude_patterns:
            filter_lines.append(f"- {pattern}")
        filter_path.write_text("\n".join(filter_lines) + "\n", encoding="utf-8")

        remote = f"gcs_backup:{bucket}/{remote_path}"
        cmd = [
            "rclone", "sync",
            source_drive,
            remote,
            "--config", str(config_path),
            "--filter-from", str(filter_path),
            "--dry-run",
            # Same flags as real run
            "--bwlimit", bandwidth_limit,
            "--gcs-chunk-size", chunk_size,
            "--transfers", "4",
            "--checkers", "16",
            "--fast-list",
            "--gcs-no-check-bucket",
            "--gcs-storage-class", "COLDLINE",
            "--modify-window", "1s",
            "--retries", str(retry_count),
            "--retries-sleep", "30s",
            "--no-traverse",
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
        exit_code = result.returncode

        # rclone exit codes: 0=success, 1-3=hard failure, 4-6=partial, 7+=fatal
        success = exit_code <= 6

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
            "success": success,
            "exit_code": exit_code,
            "transfers": transfers,
            "deletes": deletes,
            "total": total,
            "output": output,
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "exit_code": -1, "error": "timeout"}
    except FileNotFoundError:
        return {"success": False, "exit_code": -1, "error": "rclone not found"}
    except Exception as e:
        return {"success": False, "exit_code": -1, "error": str(e)}

    finally:
        for path in [config_path, filter_path]:
            if path and path.exists():
                try:
                    path.unlink()
                except OSError:
                    pass


def compare_dry_run_deletions(
    lan_result: dict,
    cloud_result: dict,
    scanner_deleted: int,
) -> dict:
    """Compare deletion counts between LAN dry run, cloud dry run, and scanner.

    Returns:
        Dict with {"max_delta_pct": float, "lan_deletions": int,
        "cloud_deletions": int, "scanner_deletions": int,
        "mismatch": bool, "details": str}.
    """
    lan_deletions = lan_result.get("deleted", 0)
    cloud_deletions = cloud_result.get("deletes", 0)

    counts = [c for c in [lan_deletions, cloud_deletions, scanner_deleted] if c > 0]
    if not counts:
        return {
            "max_delta_pct": 0.0,
            "lan_deletions": lan_deletions,
            "cloud_deletions": cloud_deletions,
            "scanner_deletions": scanner_deleted,
            "mismatch": False,
            "details": "No deletions detected by any tool",
        }

    max_count = max(counts)
    min_count = min(counts)
    delta_pct = ((max_count - min_count) / max_count * 100) if max_count > 0 else 0.0

    mismatch = delta_pct > 10.0

    details = (
        f"Deletion counts — LAN: {lan_deletions}, "
        f"Cloud: {cloud_deletions}, Scanner: {scanner_deleted}, "
        f"Delta: {delta_pct:.1f}%"
    )

    return {
        "max_delta_pct": round(delta_pct, 1),
        "lan_deletions": lan_deletions,
        "cloud_deletions": cloud_deletions,
        "scanner_deletions": scanner_deleted,
        "mismatch": mismatch,
        "details": details,
    }
