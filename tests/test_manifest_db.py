"""Tests for manifest_db.py."""

import threading




def test_wal_mode_active(temp_db):
    """WAL mode is active after initialization."""
    from sqlalchemy import text
    with temp_db._engine.connect() as conn:
        result = conn.execute(text("PRAGMA journal_mode"))
        mode = result.scalar()
        assert mode == "wal"


def test_upsert_creates_new_entry(temp_db, sample_file_info):
    """Upsert creates new entry for unknown path."""
    entry = temp_db.upsert_entry(
        relative_path=sample_file_info["relative_path"],
        file_size=sample_file_info["file_size"],
        last_modified_timestamp=sample_file_info["last_modified_timestamp"],
    )
    assert entry.relative_path == sample_file_info["relative_path"]
    assert entry.file_size == sample_file_info["file_size"]
    assert entry.checksum == "pending"
    assert entry.file_id is not None


def test_upsert_updates_existing_entry(temp_db, sample_file_info):
    """Upsert updates existing entry for known path."""
    # Create initial entry
    temp_db.upsert_entry(
        relative_path=sample_file_info["relative_path"],
        file_size=100,
        last_modified_timestamp=1700000000.0,
    )

    # Update it
    entry = temp_db.upsert_entry(
        relative_path=sample_file_info["relative_path"],
        file_size=200,
        last_modified_timestamp=1700000001.0,
        checksum="abc123",
    )
    assert entry.file_size == 200
    assert entry.checksum == "abc123"


def test_batch_mark_lan_backed_up(temp_db, sample_file_info):
    """batch_mark_lan_backed_up updates correct rows."""
    temp_db.upsert_entry(
        relative_path=sample_file_info["relative_path"],
        file_size=sample_file_info["file_size"],
        last_modified_timestamp=sample_file_info["last_modified_timestamp"],
    )

    count = temp_db.batch_mark_lan_backed_up([sample_file_info["relative_path"]])
    assert count == 1

    entry = temp_db.get_entry(sample_file_info["relative_path"])
    assert entry.backed_up_to_lan == 1
    assert entry.last_backed_up_lan is not None


def test_get_all_paths_returns_complete_set(temp_db):
    """get_all_paths returns complete set of paths."""
    paths = ["file1.txt", "file2.txt", "file3.txt"]
    for p in paths:
        temp_db.upsert_entry(relative_path=p, file_size=100, last_modified_timestamp=1700000000.0)

    result = temp_db.get_all_paths()
    assert result == set(paths)


def test_delete_entry(temp_db, sample_file_info):
    """delete_entry removes a manifest entry."""
    temp_db.upsert_entry(
        relative_path=sample_file_info["relative_path"],
        file_size=sample_file_info["file_size"],
        last_modified_timestamp=sample_file_info["last_modified_timestamp"],
    )

    assert temp_db.get_entry(sample_file_info["relative_path"]) is not None
    assert temp_db.delete_entry(sample_file_info["relative_path"]) is True
    assert temp_db.get_entry(sample_file_info["relative_path"]) is None


def test_update_last_seen(temp_db, sample_file_info):
    """update_last_seen updates the timestamp."""
    temp_db.upsert_entry(
        relative_path=sample_file_info["relative_path"],
        file_size=sample_file_info["file_size"],
        last_modified_timestamp=sample_file_info["last_modified_timestamp"],
    )

    assert temp_db.update_last_seen(sample_file_info["relative_path"]) is True
    entry = temp_db.get_entry(sample_file_info["relative_path"])
    assert entry.last_seen_at is not None


def test_thread_safety_concurrent_writes(temp_db):
    """Concurrent writes do not corrupt data."""
    results = []
    errors = []

    def write_entry(index):
        try:
            temp_db.upsert_entry(
                relative_path=f"thread_{index}.txt",
                file_size=index,
                last_modified_timestamp=1700000000.0 + index,
            )
            results.append(index)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=write_entry, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0
    assert len(results) == 10
    assert len(temp_db.get_all_paths()) == 10
