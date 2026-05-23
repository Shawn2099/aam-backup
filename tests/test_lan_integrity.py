"""Tests for LAN integrity audit module (core/lan_integrity.py)."""

import random
import time
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import pytest

from core.lan_integrity import (
    LanAuditResult,
    audit_lan_integrity,
    _verify_single_file,
)
from core.hashing import compute_checksum
from models.manifest_model import FileManifest


def _new_entry(path: str, checksum: str = "abcd1234abcd1234",
               backed_up_lan: bool = True) -> FileManifest:
    """Create a FileManifest entry for testing."""
    return FileManifest(
        file_id=f"uuid-{path.replace('/', '-').replace('\\\\', '-')}",
        relative_path=path,
        file_size=1024,
        last_modified_timestamp=1700000000.0,
        checksum=checksum,
        last_seen_at="2025-01-15T23:00:00+00:00",
        last_backed_up_lan="2025-01-15T23:05:00+00:00",
        last_backed_up_cloud=None,
        backed_up_to_lan=1 if backed_up_lan else 0,
        backed_up_to_cloud=0,
    )


class TestAuditLanIntegrity:
    def test_no_database_returns_error(self, tmp_path):
        result = audit_lan_integrity(
            str(tmp_path / "nonexistent.db"),
            str(tmp_path), str(tmp_path),
        )
        assert result.status == "ERROR"

    def test_empty_manifest_returns_ok(self, tmp_path, db_dir):
        db_path = db_dir / "empty.db"
        from core.manifest_db import ManifestDB
        db = ManifestDB(db_path)
        db.close()

        result = audit_lan_integrity(str(db_path), str(tmp_path), str(tmp_path))
        assert result.status == "OK"

    def test_no_confirmed_backups_returns_ok(self, tmp_path, db_dir):
        db_path = db_dir / "nolan.db"
        from core.manifest_db import ManifestDB
        db = ManifestDB(db_path)
        db.upsert_entry("test/file.txt", file_size=1024,
                        last_modified_timestamp=1700000000.0,
                        checksum="abcd1234abcd1234")
        db.close()

        result = audit_lan_integrity(str(db_path), str(tmp_path), str(tmp_path))
        assert result.status == "OK"
        assert result.sampled == 0

    def test_all_files_match(self, tmp_path, db_dir):
        source = tmp_path / "source"
        lan = tmp_path / "lan"
        source.mkdir()
        lan.mkdir()

        db_path = db_dir / "allmatch.db"
        from core.manifest_db import ManifestDB
        db = ManifestDB(db_path)

        file_paths = []
        for i in range(5):
            name = f"file_{i}.txt"
            content = f"content_{i}".encode()
            (source / name).write_bytes(content)
            (lan / name).write_bytes(content)

            checksum = compute_checksum(source / name)
            db.upsert_entry(name, file_size=1024,
                            last_modified_timestamp=1700000000.0,
                            checksum=checksum)
            file_paths.append(name)

        db.batch_mark_lan_backed_up(file_paths)
        db.close()

        result = audit_lan_integrity(
            str(db_path),
            str(source),
            str(lan),
            sample_count=10,
        )

        assert result.status == "OK"
        assert result.verified == 5  # all 5 files in manifest
        assert result.mismatches == 0
        assert result.missing == 0

    def test_missing_file_detected(self, tmp_path, db_dir):
        source = tmp_path / "source"
        lan = tmp_path / "lan"
        source.mkdir()
        lan.mkdir()

        db_path = db_dir / "missing.db"
        from core.manifest_db import ManifestDB
        db = ManifestDB(db_path)

        (source / "present.txt").write_bytes(b"hello")
        (lan / "present.txt").write_bytes(b"hello")
        # "missing.txt" is in manifest but not on LAN

        checksum_present = compute_checksum(source / "present.txt")
        db.upsert_entry("present.txt", file_size=1024,
                        last_modified_timestamp=1700000000.0,
                        checksum=checksum_present)
        db.batch_mark_lan_backed_up(["present.txt"])
        db.upsert_entry("missing.txt", file_size=1024,
                        last_modified_timestamp=1700000000.0,
                        checksum="abcd1234abcd1234")
        db.batch_mark_lan_backed_up(["missing.txt"])
        db.close()

        result = audit_lan_integrity(
            str(db_path), str(source), str(lan), sample_count=10,
        )

        assert result.status == "MISMATCH_DETECTED"
        assert result.missing >= 1
        assert any("missing.txt" in str(d) for d in result.details)

    def test_corrupted_file_detected(self, tmp_path, db_dir):
        source = tmp_path / "source"
        lan = tmp_path / "lan"
        source.mkdir()
        lan.mkdir()

        db_path = db_dir / "corrupt.db"
        from core.manifest_db import ManifestDB
        db = ManifestDB(db_path)

        (source / "good.txt").write_bytes(b"original data")
        (lan / "good.txt").write_bytes(b"corrupted!!!!")  # different content

        checksum = compute_checksum(source / "good.txt")
        db.upsert_entry("good.txt", file_size=1024,
                        last_modified_timestamp=1700000000.0,
                        checksum=checksum)
        db.batch_mark_lan_backed_up(["good.txt"])
        db.close()

        result = audit_lan_integrity(
            str(db_path), str(source), str(lan), sample_count=10,
        )

        assert result.status == "MISMATCH_DETECTED"
        assert result.mismatches == 1

    def test_sample_count_respected(self, tmp_path, db_dir):
        source = tmp_path / "source"
        lan = tmp_path / "lan"
        source.mkdir()
        lan.mkdir()

        db_path = db_dir / "samplecount.db"
        from core.manifest_db import ManifestDB
        db = ManifestDB(db_path)

        file_paths = []
        for i in range(20):
            name = f"file_{i:03d}.txt"
            content = f"data_{i}".encode()
            (source / name).write_bytes(content)
            (lan / name).write_bytes(content)
            checksum = compute_checksum(source / name)
            db.upsert_entry(name, file_size=1024,
                            last_modified_timestamp=1700000000.0,
                            checksum=checksum)
            file_paths.append(name)

        db.batch_mark_lan_backed_up(file_paths)

        db.close()

        result = audit_lan_integrity(
            str(db_path), str(source), str(lan), sample_count=5,
        )

        assert result.sampled == 5
        assert result.verified == 5


class TestVerifySingleFile:
    def test_matching_file_returns_ok(self, tmp_path):
        sp = tmp_path / "src.txt"
        lp = tmp_path / "lan.txt"
        sp.write_bytes(b"hello world")
        lp.write_bytes(b"hello world")
        expected = compute_checksum(sp)

        result = _verify_single_file("src.txt", str(sp), str(lp), expected)
        assert result["status"] == "OK"

    def test_mismatch_returns_mismatch(self, tmp_path):
        sp = tmp_path / "src.txt"
        lp = tmp_path / "lan.txt"
        sp.write_bytes(b"hello world")
        lp.write_bytes(b"different!")
        expected = compute_checksum(sp)

        result = _verify_single_file("src.txt", str(sp), str(lp), expected)
        assert result["status"] == "MISMATCH"

    def test_missing_lan_file_returns_missing(self, tmp_path):
        sp = tmp_path / "src.txt"
        sp.write_bytes(b"hello")
        expected = compute_checksum(sp)

        result = _verify_single_file(
            "src.txt", str(sp), str(tmp_path / "nonexistent.txt"), expected
        )
        assert result["status"] == "MISSING"

    def test_checksum_error_returns_error(self, tmp_path):
        sp = tmp_path / "src.txt"
        lp = tmp_path / "lan.txt"
        sp.write_bytes(b"hello")

        # Make LAN file unreadable
        lp.touch(mode=0o000)

        result = _verify_single_file("src.txt", str(sp), str(lp), "abcd")
        assert result["status"] == "ERROR"


class TestLanAuditResult:
    def test_is_clean_when_ok(self):
        r = LanAuditResult(status="OK", verified=10, sampled=10)
        assert r.is_clean

    def test_not_clean_when_mismatch(self):
        r = LanAuditResult(status="MISMATCH_DETECTED", verified=9,
                          mismatches=1, sampled=10)
        assert not r.is_clean
