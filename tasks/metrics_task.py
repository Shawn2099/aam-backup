"""Prefect task: collect and persist backup run metrics."""

import json
from datetime import datetime, timezone
from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger


@task(
    name="collect_backup_metrics",
    tags=["metrics"],
    retries=0,
    task_run_name="collect-metrics",
)
def collect_metrics_task(
    log_directory: str,
    flow_run_id: str,
    overall_status: str,
    lan_status: str,
    cloud_status: str,
    scan_new: int,
    scan_modified: int,
    scan_deleted: int,
    scan_unchanged: int,
    lan_files_copied: int = 0,
    lan_bytes_copied: int = 0,
    lan_files_failed: int = 0,
    cloud_mismatches: int = 0,
    cloud_missing: int = 0,
    duration_seconds: float = 0,
    total_source_bytes: int = 0,
    total_file_count: int = 0,
    lan_destination: str = "",
    lan_checksum_verified: int = 0,
    lan_checksum_mismatches: int = 0,
    lan_retry_count: int = 0,
    manifest_db_size_mb: float = 0.0,
) -> dict:
    """Append backup run metrics to a JSONL file for trend analysis.

    Each run produces one line in a JSON Lines file.
    File is never overwritten — only appended.

    Args:
        log_directory: Directory for metrics file.
        flow_run_id: Prefect flow run ID.
        overall_status: COMPLETE, PARTIAL_FAILURE, or FAILED.
        lan_status: LAN_COMPLETE, LAN_PARTIAL, LAN_FAILED, or LAN_SKIPPED.
        cloud_status: CLOUD_COMPLETE, CLOUD_PARTIAL, CLOUD_FAILED, or CLOUD_SKIPPED.
        scan_new: Number of new files detected.
        scan_modified: Number of modified files detected.
        scan_deleted: Number of deleted files detected.
        scan_unchanged: Number of unchanged files.
        lan_files_copied: Files copied to LAN.
        lan_bytes_copied: Bytes copied to LAN.
        lan_files_failed: Files that failed LAN copy.
        cloud_mismatches: Files with checksum mismatches in cloud.
        cloud_missing: Files missing from cloud.
        duration_seconds: Total flow run duration.

    Returns:
        Metrics dict that was written.
    """
    logger = get_run_logger()

    metrics_dir = Path(log_directory)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    metrics_file = metrics_dir / "backup_metrics.jsonl"

    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "flow_run_id": flow_run_id,
        "overall_status": overall_status,
        "lan_status": lan_status,
        "cloud_status": cloud_status,
        "scan": {
            "new": scan_new,
            "modified": scan_modified,
            "deleted": scan_deleted,
            "unchanged": scan_unchanged,
            "total_changed": scan_new + scan_modified + scan_deleted,
        },
        "lan": {
            "files_copied": lan_files_copied,
            "bytes_copied": lan_bytes_copied,
            "files_failed": lan_files_failed,
            "checksum_verified": lan_checksum_verified,
            "checksum_mismatches": lan_checksum_mismatches,
            "retry_count": lan_retry_count,
        },
        "cloud": {
            "mismatches": cloud_mismatches,
            "missing": cloud_missing,
        },
        "duration_seconds": duration_seconds,
        "throughput_mbps": round(lan_bytes_copied / (1024 * 1024) / max(duration_seconds, 1), 2),
        "manifest_db_size_mb": manifest_db_size_mb,
        "capacity": {
            "total_source_bytes": total_source_bytes,
            "total_file_count": total_file_count,
            "lan_free_bytes": _get_disk_free_bytes(lan_destination),
        },
    }

    try:
        with open(metrics_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(metrics) + "\n")
        logger.info(f"Backup metrics written to {metrics_file}")
    except Exception as e:
        logger.warning(f"Failed to write metrics (non-critical): {e}")

    return metrics


def _get_disk_free_bytes(path: str) -> int:
    """Get free disk space in bytes for a given path.

    Returns 0 if path is empty or inaccessible.
    Cross-platform: uses shutil.disk_usage on Linux, works with UNC on Windows.
    """
    if not path:
        return 0
    try:
        import shutil
        usage = shutil.disk_usage(path)
        return usage.free
    except Exception:
        return 0
