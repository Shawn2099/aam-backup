"""Scanner — walks source drive, classifies files as new/modified/unchanged/deleted."""

import os
import fnmatch
from pathlib import Path
from typing import Callable

import xxhash

from core.manifest_db import ManifestDB
from models.config_model import AppConfig
from models.scan_result import FileInfo, ScanResult


def compute_checksum(file_path: Path) -> str:
    """Compute xxHash64 checksum for a file.

    Reads in 8MB chunks to avoid loading large files into memory.

    Args:
        file_path: Path to the file.

    Returns:
        16-character hex string.
    """
    h = xxhash.xxh64()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8 * 1024 * 1024)  # 8MB
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def is_excluded_folder(folder_path: str, exclude_folders: list[str]) -> bool:
    """Check if a folder path matches any excluded folder.

    Case-insensitive. Matches exact path or any subfolder.
    Normalizes separators for cross-platform compatibility.

    Args:
        folder_path: Full path to the folder.
        exclude_folders: List of excluded folder paths.

    Returns:
        True if the folder should be excluded.
    """
    folder_normalized = os.path.normpath(folder_path).lower()
    for excluded in exclude_folders:
        excluded_normalized = os.path.normpath(excluded).lower()
        if folder_normalized == excluded_normalized or folder_normalized.startswith(excluded_normalized + os.sep):
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
    _, ext = os.path.splitext(filename)
    return ext.lower() in exclude_extensions


def is_excluded_pattern(filename: str, exclude_patterns: list[str]) -> bool:
    """Check if a filename matches any exclusion pattern.

    Uses fnmatch for glob-style matching. Case-insensitive.

    Args:
        filename: The file name (not full path).
        exclude_patterns: List of glob patterns (e.g., ['~$*', 'desktop.ini']).

    Returns:
        True if the filename should be excluded.
    """
    filename_lower = filename.lower()
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(filename_lower, pattern.lower()):
            return True
    return False


def scan_drive(config: AppConfig, db: ManifestDB) -> ScanResult:
    """Walk the source drive and classify files.

    Algorithm:
    1. os.walk with topdown=True for in-place dirnames pruning.
    2. For each file: extension check → pattern check → stat → manifest lookup.
    3. Classify as new, modified, or unchanged.
    4. After walk: detect deleted files (in manifest but not on disk).

    Args:
        config: Validated application configuration.
        db: ManifestDB instance for lookups and updates.

    Returns:
        ScanResult with new_files, modified_files, deleted_files, unchanged_count.
    """
    source = Path(config.paths.source_drive)
    exclude_folders = config.backup_scope.exclude_folders
    exclude_extensions = config.backup_scope.exclude_extensions
    exclude_patterns = config.backup_scope.exclude_patterns

    result = ScanResult()
    current_paths: set[str] = set()

    for dirpath, dirnames, filenames in os.walk(source, topdown=True):
        # Prune excluded folders in-place (critical for os.walk descent)
        dirnames[:] = [
            d for d in dirnames
            if not is_excluded_folder(os.path.join(dirpath, d), exclude_folders)
        ]

        for filename in filenames:
            # Step 1: Extension check
            if is_excluded_extension(filename, exclude_extensions):
                continue

            # Step 2: Pattern check
            if is_excluded_pattern(filename, exclude_patterns):
                continue

            full_path = os.path.join(dirpath, filename)

            # Step 3: stat
            try:
                stat_result = os.stat(full_path)
            except OSError:
                result.cannot_read.append(full_path)
                continue

            # Step 4: Compute relative path
            relative_path = os.path.relpath(full_path, source)

            # Step 5: Add to current paths
            current_paths.add(relative_path)

            # Step 6: Manifest lookup
            existing = db.get_entry(relative_path)

            if existing is None:
                # Step 7a: NEW FILE
                file_info = FileInfo(
                    relative_path=relative_path,
                    file_size=stat_result.st_size,
                    last_modified_timestamp=stat_result.st_mtime,
                    checksum="",
                )
                result.new_files.append(file_info)
                db.upsert_entry(
                    relative_path=relative_path,
                    file_size=stat_result.st_size,
                    last_modified_timestamp=stat_result.st_mtime,
                    checksum="pending",
                )

            else:
                # Step 7b/7c: Check size and mtime (1.0 second tolerance)
                size_match = existing.file_size == stat_result.st_size
                mtime_match = abs(existing.last_modified_timestamp - stat_result.st_mtime) < 1.0

                if size_match and mtime_match:
                    # UNCHANGED
                    db.update_last_seen(relative_path)
                    result.unchanged_count += 1
                else:
                    # Size or mtime differs — compute checksum
                    checksum = compute_checksum(Path(full_path))

                    if checksum == existing.checksum:
                        # METADATA CHANGE ONLY
                        db.upsert_entry(
                            relative_path=relative_path,
                            file_size=stat_result.st_size,
                            last_modified_timestamp=stat_result.st_mtime,
                            checksum=checksum,
                        )
                    else:
                        # MODIFIED FILE
                        file_info = FileInfo(
                            relative_path=relative_path,
                            file_size=stat_result.st_size,
                            last_modified_timestamp=stat_result.st_mtime,
                            checksum=checksum,
                        )
                        result.modified_files.append(file_info)
                        db.upsert_entry(
                            relative_path=relative_path,
                            file_size=stat_result.st_size,
                            last_modified_timestamp=stat_result.st_mtime,
                            checksum=checksum,
                        )

    # Deleted file detection
    all_manifest_paths = db.get_all_paths()
    deleted = all_manifest_paths - current_paths
    for deleted_path in deleted:
        result.deleted_files.append(deleted_path)
        db.delete_entry(deleted_path)

    return result
