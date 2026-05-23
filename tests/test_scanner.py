"""Tests for scanner.py."""

from pathlib import Path


from core.scanner import (
    compute_checksum,
    is_excluded_extension,
    is_excluded_folder,
    is_excluded_pattern,
    scan_drive,
)
from models.config_model import AppConfig


def test_compute_checksum(temp_dir):
    """compute_checksum returns correct xxHash64."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("hello world", encoding="utf-8")
    checksum = compute_checksum(test_file)
    assert len(checksum) == 16
    assert all(c in "0123456789abcdef" for c in checksum)


def test_is_excluded_folder():
    """is_excluded_folder matches exact and subfolder paths."""
    excludes = ["D:\\BackupAgent", "D:\\Common Folder"]
    assert is_excluded_folder(Path("D:\\BackupAgent"), excludes) is True
    assert is_excluded_folder(Path("D:\\Common Folder"), excludes) is True
    assert is_excluded_folder(Path("D:\\AAM WORKS"), excludes) is False
    # Linux-style paths with forward slashes
    excludes_linux = ["/home/backup", "/tmp/excluded"]
    assert is_excluded_folder(Path("/home/backup"), excludes_linux) is True
    assert is_excluded_folder(Path("/home/backup/logs"), excludes_linux) is True
    assert is_excluded_folder(Path("/home/data"), excludes_linux) is False


def test_is_excluded_extension():
    """is_excluded_extension matches file extensions."""
    excludes = [".lnk", ".tmp", ".temp"]
    assert is_excluded_extension("file.lnk", excludes) is True
    assert is_excluded_extension("file.TMP", excludes) is True
    assert is_excluded_extension("file.txt", excludes) is False


def test_is_excluded_pattern():
    """is_excluded_pattern matches glob patterns."""
    excludes = ["~$*", "desktop.ini", "thumbs.db"]
    assert is_excluded_pattern("~$document.docx", excludes) is True
    assert is_excluded_pattern("desktop.ini", excludes) is True
    assert is_excluded_pattern("Thumbs.db", excludes) is True
    assert is_excluded_pattern("normal.txt", excludes) is False


def test_scan_new_file(source_dir, temp_db):
    """New file correctly classified as new."""
    test_file = source_dir / "new_file.txt"
    test_file.write_text("new content", encoding="utf-8")

    config = AppConfig(
        firm={"name": "Test"},
        paths={
            "source_drive": str(source_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(source_dir / "logs"),
            "database_path": str(source_dir / "manifest.db"),
        },
        wol={"enabled": False},
        cloud_backup={"enabled": False},
    )

    result = scan_drive(config, temp_db)
    assert len(result.new_files) == 1
    assert result.new_files[0].relative_path == "new_file.txt"


def test_scan_modified_file(source_dir, temp_db):
    """Modified file (size change) correctly classified as modified."""
    test_file = source_dir / "file.txt"
    test_file.write_text("original", encoding="utf-8")

    # First scan — file is new
    config = AppConfig(
        firm={"name": "Test"},
        paths={
            "source_drive": str(source_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(source_dir / "logs"),
            "database_path": str(source_dir / "manifest.db"),
        },
        wol={"enabled": False},
        cloud_backup={"enabled": False},
    )
    scan_drive(config, temp_db)

    # Modify file
    test_file.write_text("modified content is longer", encoding="utf-8")

    # Second scan — file is modified
    result = scan_drive(config, temp_db)
    assert len(result.modified_files) == 1
    assert result.modified_files[0].relative_path == "file.txt"


def test_scan_deleted_file(source_dir, temp_db):
    """Deleted file correctly identified."""
    test_file = source_dir / "to_delete.txt"
    test_file.write_text("delete me", encoding="utf-8")

    config = AppConfig(
        firm={"name": "Test"},
        paths={
            "source_drive": str(source_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(source_dir / "logs"),
            "database_path": str(source_dir / "manifest.db"),
        },
        wol={"enabled": False},
        cloud_backup={"enabled": False},
    )

    # First scan
    scan_drive(config, temp_db)

    # Delete file
    test_file.unlink()

    # Second scan — file is deleted
    result = scan_drive(config, temp_db)
    assert len(result.deleted_files) == 1
    assert "to_delete.txt" in result.deleted_files


def test_scan_excluded_folder_not_walked(source_dir, temp_db):
    """Excluded folder not walked."""
    excluded_dir = source_dir / "excluded"
    excluded_dir.mkdir()
    (excluded_dir / "secret.txt").write_text("hidden", encoding="utf-8")

    config = AppConfig(
        firm={"name": "Test"},
        paths={
            "source_drive": str(source_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(source_dir / "logs"),
            "database_path": str(source_dir / "manifest.db"),
        },
        backup_scope={"exclude_folders": [str(excluded_dir)]},
        wol={"enabled": False},
        cloud_backup={"enabled": False},
    )

    result = scan_drive(config, temp_db)
    assert len(result.new_files) == 0
    assert len(result.cannot_read) == 0


def test_scan_excluded_extension_not_included(source_dir, temp_db):
    """Excluded extension not included."""
    (source_dir / "shortcut.lnk").write_text("lnk", encoding="utf-8")
    (source_dir / "data.txt").write_text("data", encoding="utf-8")

    config = AppConfig(
        firm={"name": "Test"},
        paths={
            "source_drive": str(source_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(source_dir / "logs"),
            "database_path": str(source_dir / "manifest.db"),
        },
        wol={"enabled": False},
        cloud_backup={"enabled": False},
    )

    result = scan_drive(config, temp_db)
    assert len(result.new_files) == 1
    assert result.new_files[0].relative_path == "data.txt"


def test_scan_excluded_pattern_not_included(source_dir, temp_db):
    """Excluded pattern not included."""
    (source_dir / "~$temp.docx").write_text("temp", encoding="utf-8")
    (source_dir / "normal.docx").write_text("normal", encoding="utf-8")

    config = AppConfig(
        firm={"name": "Test"},
        paths={
            "source_drive": str(source_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(source_dir / "logs"),
            "database_path": str(source_dir / "manifest.db"),
        },
        wol={"enabled": False},
        cloud_backup={"enabled": False},
    )

    result = scan_drive(config, temp_db)
    assert len(result.new_files) == 1
    assert result.new_files[0].relative_path == "normal.docx"


def test_scan_unreadable_file_added_to_cannot_read(source_dir, temp_db):
    """Unreadable file added to cannot_read list.

    Note: os.stat() succeeds on files owned by the current user regardless
    of permissions. This test verifies the cannot_read list is populated
    when stat actually fails (e.g., file on inaccessible mount).
    """
    # Create a path that will fail stat (symlink to nonexistent target)
    broken_link = source_dir / "broken_link.txt"
    broken_link.symlink_to("/nonexistent/target/file.txt")

    config = AppConfig(
        firm={"name": "Test"},
        paths={
            "source_drive": str(source_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(source_dir / "logs"),
            "database_path": str(source_dir / "manifest.db"),
        },
        wol={"enabled": False},
        cloud_backup={"enabled": False},
    )

    result = scan_drive(config, temp_db)
    assert len(result.cannot_read) == 1
    assert "broken_link.txt" in result.cannot_read[0]


def test_scan_empty_directory_handled(source_dir, temp_db):
    """Empty directory handled without error."""
    empty_dir = source_dir / "empty"
    empty_dir.mkdir()

    config = AppConfig(
        firm={"name": "Test"},
        paths={
            "source_drive": str(source_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(source_dir / "logs"),
            "database_path": str(source_dir / "manifest.db"),
        },
        wol={"enabled": False},
        cloud_backup={"enabled": False},
    )

    result = scan_drive(config, temp_db)
    assert len(result.new_files) == 0
    assert len(result.cannot_read) == 0


def test_scan_full_rescan_checksums_all_files(source_dir, temp_db):
    """Full re-scan computes checksums for ALL files, not just changed ones."""
    test_file = source_dir / "file.txt"
    test_file.write_text("original", encoding="utf-8")

    config = AppConfig(
        firm={"name": "Test"},
        paths={
            "source_drive": str(source_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(source_dir / "logs"),
            "database_path": str(source_dir / "manifest.db"),
        },
        wol={"enabled": False},
        cloud_backup={"enabled": False},
    )

    # First scan — file is new
    scan_drive(config, temp_db)

    # Second scan with full rescan — unchanged file gets checksum recomputed
    result = scan_drive(config, temp_db, is_full_rescan=True)
    # File content hasn't changed, so it should be counted as unchanged
    assert len(result.modified_files) == 0
    assert result.unchanged_count == 1


def test_scan_full_rescan_detects_content_change(source_dir, temp_db):
    """Full re-scan detects content changes even when size/mtime appear unchanged."""
    import time
    test_file = source_dir / "file.txt"
    test_file.write_text("original content!!", encoding="utf-8")  # 18 bytes

    config = AppConfig(
        firm={"name": "Test"},
        paths={
            "source_drive": str(source_dir),
            "lan_destination": "\\\\192.168.10.10\\test$",
            "log_directory": str(source_dir / "logs"),
            "database_path": str(source_dir / "manifest.db"),
        },
        wol={"enabled": False},
        cloud_backup={"enabled": False},
    )

    # First scan
    result1 = scan_drive(config, temp_db)
    assert len(result1.new_files) == 1

    # Wait for mtime to settle, then modify with same size
    time.sleep(1.1)
    test_file.write_text("modified content!!", encoding="utf-8")  # Also 18 bytes

    # Full rescan — detects the content change via checksum
    result_full = scan_drive(config, temp_db, is_full_rescan=True)
    assert len(result_full.modified_files) == 1
    assert result_full.unchanged_count == 0
