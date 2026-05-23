"""Scanner — walks source drive, classifies files as new/modified/unchanged/deleted.

Uses pathlib.Path.walk (Python 3.12+) for directory traversal with top-down
pruning, maintaining pathlib.Path objects throughout while retaining the
performance characteristics of os.walk's in-place dirnames mutation.
"""

from pathlib import Path
import uuid
from datetime import datetime, timezone

from core.hashing import compute_checksum
from core.manifest_db import ManifestDB
from models.config_model import AppConfig
from models.manifest_model import PENDING_CHECKSUM, FileManifest
from models.scan_result import FileInfo, ScanResult


def is_excluded_folder(folder_path: Path, exclude_folders: list[str]) -> bool:
    """Check if a folder path matches any excluded folder.

    Case-insensitive. Matches exact path or any subfolder.

    Args:
        folder_path: Full path to the folder.
        exclude_folders: List of excluded folder paths.

    Returns:
        True if the folder should be excluded.
    """
    folder_normalized = folder_path.resolve().as_posix().lower()
    for excluded in exclude_folders:
        excluded_normalized = Path(excluded).resolve().as_posix().lower()
        if folder_normalized == excluded_normalized or folder_normalized.startswith(excluded_normalized + "/"):
            return True
    return False


def is_excluded_extension(filename: str, exclude_extensions: list[str]) -> bool:
    """Check if a file extension is in the exclusion list.

    Args:
        filename: The file name (not full path).
        exclude_extensions: List of extensions (e.g., ['.lnk', '.tmp']).

    Returns:
        True if the extension should be excluded.
    """
    return Path(filename).suffix.lower() in exclude_extensions


def is_excluded_pattern(filename: str, exclude_patterns: list[str]) -> bool:
    """Check if a filename matches any exclusion pattern.

    Uses fnmatch for glob-style matching. Case-insensitive.

    Args:
        filename: The file name (not full path).
        exclude_patterns: List of glob patterns (e.g., ['~$*', 'desktop.ini']).

    Returns:
        True if the filename should be excluded.
    """
    import fnmatch
    filename_lower = filename.lower()
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(filename_lower, pattern.lower()):
            return True
    return False


def scan_drive(
    config: AppConfig,
    db: ManifestDB,
    is_full_rescan: bool = False,
) -> ScanResult:
    """Walk the source drive and classify files.

    Algorithm:
    1. Load all manifest entries into memory once (bulk read).
    2. Path.walk with top_down=True for in-place dirnames pruning.
    3. For each file: extension check → pattern check → stat → in-memory manifest lookup.
    4. Classify as new, modified, or unchanged.
    5. After walk: detect deleted files (in manifest but not on disk).

    BUG FIX #2: Handles VSS device paths (\\?\GLOBALROOT\...) by computing
    relative paths manually instead of relying on Path.relative_to().

    Args:
        config: Validated application configuration.
        db: ManifestDB instance for lookups and updates.
        is_full_rescan: If True, compute checksums for ALL files (not just changed ones).

    Returns:
        ScanResult with new_files, modified_files, deleted_files, unchanged_count.
    """
    source = Path(config.paths.source_drive)
    exclude_folders = config.backup_scope.exclude_folders
    exclude_extensions = config.backup_scope.exclude_extensions
    exclude_patterns = config.backup_scope.exclude_patterns

    result = ScanResult()
    current_paths: set[str] = set()

    # Bulk load all manifest entries into memory — avoids 200K+ individual queries
    manifest_cache = db.get_all_entries()

    # Get now_iso timestamp once at the beginning to share across batch updates
    now_iso = datetime.now(timezone.utc).isoformat()

    to_upsert: list[dict] = []
    to_update_last_seen: list[str] = []

    # BUG FIX #2: For VSS paths, store the original drive letter for relative path computation
    # VSS paths look like: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy123\
    # We need to compute relative paths against the original drive (e.g., D:\)
    source_str = str(source)
    is_vss_path = source_str.startswith("\\\\?\\") or source_str.startswith("\\\\")

    for dirpath, dirnames, filenames in source.walk(top_down=True):
        # Prune excluded folders in-place (critical for top-down descent)
        dirnames[:] = [
            d for d in dirnames
            if not is_excluded_folder(dirpath / d, exclude_folders)
        ]

        for filename in filenames:
            # Step 1: Extension check
            if is_excluded_extension(filename, exclude_extensions):
                continue

            # Step 2: Pattern check
            if is_excluded_pattern(filename, exclude_patterns):
                continue

            full_path = dirpath / filename

            # Step 3: stat
            try:
                stat_result = full_path.stat()
            except OSError:
                result.cannot_read.append(str(full_path))
                continue

            # Step 4: Compute relative path
            # BUG FIX #2: Handle VSS device paths where Path.relative_to() fails
            full_path_str = str(full_path)
            if is_vss_path:
                # For VSS paths, strip the source prefix manually
                source_prefix = source_str.rstrip("\\").rstrip("/")
                if full_path_str.lower().startswith(source_prefix.lower()):
                    relative_path = full_path_str[len(source_prefix):].lstrip("\\").lstrip("/")
                    # Normalize separators
                    relative_path = relative_path.replace("/", "\\")
                else:
                    continue  # Skip files outside source
            else:
                relative_path = str(full_path.relative_to(source))

            # Step 5: Add to current paths
            current_paths.add(relative_path)

            # Step 6: In-memory manifest lookup (O(1) dict access)
            existing = manifest_cache.get(relative_path)

            if existing is None:
                # Step 7a: NEW FILE
                file_id = str(uuid.uuid4())
                file_info = FileInfo(
                    relative_path=relative_path,
                    file_size=stat_result.st_size,
                    last_modified_timestamp=stat_result.st_mtime,
                    checksum="",
                )
                result.new_files.append(file_info)

                to_upsert.append({
                    "file_id": file_id,
                    "relative_path": relative_path,
                    "file_size": stat_result.st_size,
                    "last_modified_timestamp": stat_result.st_mtime,
                    "checksum": PENDING_CHECKSUM,
                    "last_seen_at": now_iso,
                })

                # Update cache so subsequent calculations/scans see it
                new_entry = FileManifest(
                    file_id=file_id,
                    relative_path=relative_path,
                    file_size=stat_result.st_size,
                    last_modified_timestamp=stat_result.st_mtime,
                    checksum=PENDING_CHECKSUM,
                    last_seen_at=now_iso,
                    backed_up_to_lan=0,
                    backed_up_to_cloud=0,
                )
                manifest_cache[relative_path] = new_entry

            else:
                # Step 7b/7c: Check size and mtime (1.0 second tolerance)
                size_match = existing.file_size == stat_result.st_size
                mtime_match = abs(existing.last_modified_timestamp - stat_result.st_mtime) < 1.0

                if size_match and mtime_match and not is_full_rescan:
                    # UNCHANGED — skip checksum, add to batch last_seen update
                    to_update_last_seen.append(relative_path)
                    result.unchanged_count += 1
                    
                    # Update local cache for correctness
                    existing.last_seen_at = now_iso
                else:
                    # Size/mtime differs OR full rescan — compute checksum
                    checksum = compute_checksum(full_path)

                    # Check if content actually changed
                    # During full rescan with pending checksum, treat as unchanged only if size/mtime also match
                    # (meaning file hasn't been touched since first scan)
                    if existing.checksum == PENDING_CHECKSUM:
                        checksums_match = is_full_rescan and size_match and mtime_match
                    else:
                        checksums_match = checksum == existing.checksum

                    if checksums_match:
                        # CONTENT UNCHANGED
                        to_upsert.append({
                            "file_id": existing.file_id,
                            "relative_path": relative_path,
                            "file_size": stat_result.st_size,
                            "last_modified_timestamp": stat_result.st_mtime,
                            "checksum": checksum,
                            "last_seen_at": now_iso,
                        })
                        result.unchanged_count += 1
                        
                        # Update local cache
                        existing.file_size = stat_result.st_size
                        existing.last_modified_timestamp = stat_result.st_mtime
                        existing.checksum = checksum
                        existing.last_seen_at = now_iso
                    else:
                        # MODIFIED FILE
                        file_info = FileInfo(
                            relative_path=relative_path,
                            file_size=stat_result.st_size,
                            last_modified_timestamp=stat_result.st_mtime,
                            checksum=checksum,
                        )
                        result.modified_files.append(file_info)

                        to_upsert.append({
                            "file_id": existing.file_id,
                            "relative_path": relative_path,
                            "file_size": stat_result.st_size,
                            "last_modified_timestamp": stat_result.st_mtime,
                            "checksum": checksum,
                            "last_seen_at": now_iso,
                        })

                        # Update local cache
                        existing.file_size = stat_result.st_size
                        existing.last_modified_timestamp = stat_result.st_mtime
                        existing.checksum = checksum
                        existing.last_seen_at = now_iso

    # Deleted file detection — use cached manifest paths
    all_manifest_paths = set(manifest_cache.keys())
    deleted = all_manifest_paths - current_paths
    deleted_list = list(deleted) if deleted else []
    if deleted_list:
        for deleted_path in deleted_list:
            result.deleted_files.append(deleted_path)

    # Single atomic transaction: upsert + update last_seen + delete
    db.sync_manifest(
        to_upsert=to_upsert,
        to_update_last_seen=to_update_last_seen,
        to_delete=deleted_list,
    )

    # Compute totals for capacity tracking
    result.total_file_count = len(current_paths)
    result.total_source_bytes = sum(
        int(entry.file_size)  # type: ignore[misc, arg-type]
        for entry in manifest_cache.values()
        if entry.relative_path in current_paths
    )

    return result
