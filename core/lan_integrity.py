"""Periodic full LAN integrity audit via random-sample checksum verification.

Unlike post-backup verify_lan_checksums() which checks only the files that
changed in the current run, this performs a broader audit by randomly sampling
files from the manifest and verifying their integrity on the LAN destination.
This catches silent bit-rot, partial writes, or filesystem corruption that
accumulates over time.

Uses ProcessPoolExecutor for parallel checksum computation to keep audit
duration reasonable for large sample sizes.
"""

import random
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from loguru import logger

from core.hashing import compute_checksum
from core.manifest_db import ManifestDB
from models.manifest_model import PENDING_CHECKSUM


@dataclass
class LanAuditResult:
    """Result of a LAN integrity audit."""

    status: str = "OK"
    """OK, MISMATCH_DETECTED, or ERROR."""

    sampled: int = 0
    verified: int = 0
    mismatches: int = 0
    missing: int = 0
    errors: int = 0

    details: list[dict] = field(default_factory=list)
    """Per-file details for any mismatches or errors."""

    duration_seconds: float = 0.0

    @property
    def is_clean(self) -> bool:
        return self.status == "OK"


def audit_lan_integrity(
    database_path: str,
    source_drive: str,
    lan_destination: str,
    sample_count: int = 500,
    max_workers: int = 4,
) -> LanAuditResult:
    """Audit LAN mirror integrity by randomly sampling files and verifying checksums.

    Randomly selects N files from the manifest (excluding pending-checksum entries),
    computes xxHash64 on both the source and LAN copy for each, and reports mismatches.

    Args:
        database_path: Path to manifest.db.
        source_drive: Source drive path (e.g., "D:\\").
        lan_destination: UNC path to LAN backup destination.
        sample_count: Number of random files to verify.
        max_workers: Number of parallel checksum workers.

    Returns:
        LanAuditResult with verification statistics.
    """
    import time
    start = time.time()

    db_path = Path(database_path)
    if not db_path.exists():
        return LanAuditResult(status="ERROR", details=[{"reason": "manifest.db not found"}])

    db = ManifestDB(database_path)
    try:
        all_entries = db.get_all_entries()
    finally:
        db.close()

    if not all_entries:
        return LanAuditResult(status="OK", details=[{"reason": "manifest is empty"}])

    confirmed = {
        path: entry
        for path, entry in all_entries.items()
        if entry.checksum != PENDING_CHECKSUM and entry.backed_up_to_lan
    }

    if not confirmed:
        return LanAuditResult(
            status="OK",
            details=[{"reason": "no files with confirmed LAN backup in manifest"}],
        )

    actual_count = min(sample_count, len(confirmed))
    sampled = random.sample(list(confirmed.keys()), actual_count)

    logger.info(
        f"LAN integrity audit: verifying {actual_count} random files "
        f"out of {len(confirmed)} confirmed LAN backups "
        f"(using {max_workers} workers)"
    )

    source_prefix = Path(source_drive)
    lan_prefix = Path(lan_destination)

    tasks = []
    for path in sampled:
        entry = confirmed[path]
        source_path = source_prefix / path
        lan_path = lan_prefix / path
        tasks.append((path, str(source_path), str(lan_path), entry.checksum))

    result = LanAuditResult(sampled=actual_count)
    mismatch_details: list[dict] = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(_verify_single_file, path, src, lan, expected_chk): path
            for path, src, lan, expected_chk in tasks
        }

        for future in as_completed(future_map):
            path = future_map[future]
            try:
                file_result = future.result()
            except Exception as e:
                file_result = {"path": path, "status": "ERROR", "reason": str(e)}

            status = file_result.get("status", "ERROR")
            if status == "OK":
                result.verified += 1
            elif status == "MISMATCH":
                result.mismatches += 1
                mismatch_details.append(file_result)
            elif status == "MISSING":
                result.missing += 1
                mismatch_details.append(file_result)
            else:
                result.errors += 1
                mismatch_details.append(file_result)

    result.details = mismatch_details
    if result.mismatches > 0 or result.missing > 0 or result.errors > 0:
        result.status = "MISMATCH_DETECTED"

    result.duration_seconds = round(time.time() - start, 1)

    logger.info(
        f"LAN audit complete: {result.verified}/{result.sampled} verified, "
        f"{result.mismatches} mismatches, {result.missing} missing, "
        f"{result.errors} errors ({result.duration_seconds}s)"
    )

    return result


def _verify_single_file(
    relative_path: str,
    source_path: str,
    lan_path: str,
    expected_checksum: str,
) -> dict:
    """Verify a single file's checksum match on LAN (worker function).

    This runs in a ProcessPoolExecutor worker — no shared state.
    """
    sp = Path(source_path)
    lp = Path(lan_path)

    if not lp.exists():
        return {"path": relative_path, "status": "MISSING", "reason": "file not found on LAN"}

    try:
        lan_checksum = compute_checksum(lp)
    except Exception as e:
        return {"path": relative_path, "status": "ERROR", "reason": f"checksum failed: {e}"}

    if lan_checksum == expected_checksum:
        return {"path": relative_path, "status": "OK", "checksum": lan_checksum}

    # Verify source checksum to distinguish source-change vs LAN corruption
    try:
        if sp.exists():
            source_checksum = compute_checksum(sp)
            if source_checksum == expected_checksum:
                return {
                    "path": relative_path,
                    "status": "MISMATCH",
                    "reason": "LAN copy corrupted",
                    "expected_checksum": expected_checksum,
                    "lan_checksum": lan_checksum,
                }
            else:
                return {
                    "path": relative_path,
                    "status": "MISMATCH",
                    "reason": "source changed since backup",
                    "expected_checksum": expected_checksum,
                    "lan_checksum": lan_checksum,
                    "source_checksum": source_checksum,
                }
    except Exception:
        pass

    return {
        "path": relative_path,
        "status": "MISMATCH",
        "reason": "checksum mismatch (source verification failed)",
        "expected_checksum": expected_checksum,
        "lan_checksum": lan_checksum,
    }
