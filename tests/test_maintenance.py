"""Tests for manifest DB maintenance task."""

import sqlite3


from core.manifest_db import ManifestDB, SCHEMA_VERSION
from tasks.maintenance_task import maintain_manifest_db_task


def test_schema_version_table_created(tmp_path):
    """Schema version table is created on first init."""
    db_path = str(tmp_path / "test.db")
    db = ManifestDB(db_path)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
        assert cursor.fetchone() is not None

        cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == SCHEMA_VERSION
        conn.close()
    finally:
        db.close()


def test_maintenance_vacuum_and_checkpoint(tmp_path):
    """Maintenance performs VACUUM and WAL checkpoint."""
    db_path = str(tmp_path / "test.db")
    db = ManifestDB(db_path)
    try:
        result = db.maintenance()
        assert result["vacuumed"] is True
        assert result["checkpointed"] is True
        assert result["size_mb"] >= 0
        assert result["size_warning"] is False
    finally:
        db.close()


def test_maintenance_size_warning(tmp_path):
    """Maintenance warns when database exceeds threshold."""
    db_path = str(tmp_path / "test.db")
    db = ManifestDB(db_path)
    try:
        # Set threshold to 0 to trigger warning
        result = db.maintenance(max_size_mb=0)
        assert result["size_warning"] is True
    finally:
        db.close()


def test_maintenance_empty_db(tmp_path):
    """Maintenance works on empty database (no entries)."""
    db_path = str(tmp_path / "test.db")
    db = ManifestDB(db_path)
    try:
        result = db.maintenance()
        assert result["vacuumed"] is True
        assert result["checkpointed"] is True
        assert result["size_mb"] >= 0
    finally:
        db.close()


def test_maintain_task_skips_missing_db():
    """Maintenance task skips when database not found."""
    result = maintain_manifest_db_task("/nonexistent/path/test.db")
    assert result["status"] == "SKIPPED"


def test_maintain_task_success(tmp_path):
    """Maintenance task succeeds on valid database."""
    db_path = str(tmp_path / "test.db")
    ManifestDB(db_path).close()

    result = maintain_manifest_db_task(db_path)
    assert result["status"] == "SUCCESS"
    assert result["vacuumed"] is True
    assert result["checkpointed"] is True
