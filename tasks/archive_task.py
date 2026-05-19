"""Prefect task: yearly archive of active FY data to archive prefix in GCS.

Uses the GCS StorageControlClient.rename_folder() API for atomic,
instant folder moves within HNS-enabled buckets. This is a single
metadata operation — O(1), ~2 seconds, free — regardless of file count.
"""

from pathlib import Path
from datetime import datetime, timezone

from prefect import task
from prefect.logging import get_run_logger


@task(
    name="yearly_archive",
    tags=["archive", "cloud"],
    retries=1,
    retry_delay_seconds=60,
    task_run_name="yearly-archive",
)
def yearly_archive_task(
    bucket: str,
    gcs_key_path: str,
    active_path: str,
    archive_path: str,
    log_directory: str,
) -> dict:
    """Atomically rename the active FY folder to the archive prefix in GCS.

    Uses StorageControlClient.rename_folder() which is a native GCS API
    call for HNS-enabled buckets. This is a metadata-only operation —
    no object copies, no deletes, no API costs.

    The rename preserves object creation timestamps, so age-based
    lifecycle rules continue to apply correctly after the move.

    Args:
        bucket: GCS bucket name (must have hierarchical namespace enabled).
        gcs_key_path: Path to GCS service account JSON key.
        active_path: Source folder path within bucket (e.g., "D_Drive_Backup/active/").
        archive_path: Destination folder path within bucket (e.g., "D_Drive_Backup/archive/").
        log_directory: Directory for marker files.

    Returns:
        Dict with archive status and details.
    """
    logger = get_run_logger()

    # Check if already archived this year
    current_year = datetime.now(timezone.utc).year
    marker_file = Path(log_directory) / f"archive_done_{current_year}.txt"

    if marker_file.exists():
        logger.info(f"Archive already completed for {current_year} — skipping")
        return {
            "status": "SKIPPED",
            "reason": f"Already archived for {current_year}",
            "year": current_year,
        }

    try:
        from google.cloud.storage.control_v2 import StorageControlClient  # type: ignore[import-untyped]

        # Initialize client with service account credentials
        client = StorageControlClient.from_service_account_json(gcs_key_path)

        # Build folder resource names
        # HNS folders use the format: projects/_/buckets/{bucket}/folders/{folder_path}
        source_folder = f"projects/_/buckets/{bucket}/folders/{active_path.rstrip('/')}"
        dest_folder_id = archive_path.rstrip("/")

        logger.info(f"Renaming folder: {source_folder} → {dest_folder_id}")

        # Atomic rename — single API call, instant, free
        request = StorageControlClient.types.RenameFolderRequest(
            name=source_folder,
            destination_folder_id=dest_folder_id,
        )

        operation = client.rename_folder(request=request)
        result = operation.result(timeout=300)  # Wait up to 5 minutes

        # Create marker file to prevent double-archiving
        marker_file.write_text(
            f"Archive completed for {current_year} at {datetime.now(timezone.utc).isoformat()}\n"
            f"Source: {source_folder}\n"
            f"Destination: {dest_folder_id}\n"
        )

        logger.info(
            f"Archive completed for {current_year}: "
            f"{active_path.rstrip('/')} → {dest_folder_id}"
        )

        return {
            "status": "SUCCESS",
            "year": current_year,
            "source": active_path.rstrip("/"),
            "destination": dest_folder_id,
            "folder_name": result.name if result else dest_folder_id,
        }

    except ImportError:
        logger.critical("google-cloud-storage not installed — run: uv sync")
        return {"status": "ERROR", "year": current_year, "error": "google-cloud-storage not installed"}

    except Exception as e:
        error_type = type(e).__name__
        logger.critical(f"Archive failed ({error_type}): {e}")
        return {"status": "FAILED", "year": current_year, "error": f"{error_type}: {e}"}
