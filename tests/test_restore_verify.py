"""Tests for automated test restore verification task."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from core.manifest_db import ManifestDB
from tasks.restore_verify_task import (
    restore_verify_task as restore_task,
    _verify_lan_file_with_checksum,
    _verify_cloud_file_download,
    _verify_cloud_file_md5,
)


class TestVerifyLanFileWithChecksum:
    """Tests for LAN file verification via checksum."""

    def test_checksum_matches(self, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()

        test_file = source / "file.txt"
        test_file.write_bytes(b"hello world")

        lan_file = lan_dest / "file.txt"
        lan_file.write_bytes(b"hello world")

        from core.hashing import compute_checksum
        expected = compute_checksum(test_file)

        result = _verify_lan_file_with_checksum(str(source), str(lan_dest), "file.txt", expected)
        assert result["status"] == "OK"
        assert result["checksum"] == expected

    def test_file_missing(self, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()

        result = _verify_lan_file_with_checksum(str(source), str(lan_dest), "missing.txt", "abc123")
        assert result["status"] == "MISSING"

    def test_checksum_mismatch(self, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()

        source_file = source / "file.txt"
        source_file.write_bytes(b"original content")

        lan_file = lan_dest / "file.txt"
        lan_file.write_bytes(b"corrupted content")

        from core.hashing import compute_checksum
        expected = compute_checksum(source_file)

        result = _verify_lan_file_with_checksum(str(source), str(lan_dest), "file.txt", expected)
        assert result["status"] == "CORRUPTED"


class TestVerifyCloudFileDownload:
    """Tests for cloud file verification via actual download."""

    @patch("tasks.restore_verify_task._write_temp_config")
    @patch("subprocess.run")
    def test_download_and_verify(self, mock_run, mock_write_config, tmp_path):
        mock_config = tmp_path / "rclone.conf"
        mock_config.write_text("[gcs_backup]")
        mock_write_config.return_value = mock_config

        downloaded = tmp_path / "test_restore_file.txt"
        downloaded.write_bytes(b"hello world")

        def side_effect(cmd, **kwargs):
            if isinstance(cmd, list) and "copyto" in cmd:
                import shutil
                dest_path = [c for c in cmd if not c.startswith("--") and c not in ("rclone", "copyto")]
                if len(dest_path) >= 2:
                    dest = dest_path[1]
                    import os
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    shutil.copy2(str(downloaded), dest)
            return MagicMock(returncode=0)

        mock_run.side_effect = side_effect

        from core.hashing import compute_checksum
        expected = compute_checksum(downloaded)

        result = _verify_cloud_file_download(
            "/fake/key.json", "asia-south1", "my-bucket", "D_Drive_Backup",
            "file.txt", expected,
        )
        assert result["status"] == "OK"
        assert result["method"] == "download"

    @patch("tasks.restore_verify_task._write_temp_config")
    @patch("subprocess.run")
    def test_download_fails(self, mock_run, mock_write_config, tmp_path):
        mock_config = tmp_path / "rclone.conf"
        mock_config.write_text("[gcs_backup]")
        mock_write_config.return_value = mock_config

        mock_run.return_value = MagicMock(returncode=1, stderr="not found")

        result = _verify_cloud_file_download(
            "/fake/key.json", "asia-south1", "my-bucket", "D_Drive_Backup",
            "missing.txt", "abc123",
        )
        assert result["status"] == "MISSING"


class TestVerifyCloudFileMD5:
    """Tests for cloud file verification via server-side MD5."""

    @patch("tasks.restore_verify_task._write_temp_config")
    @patch("subprocess.run")
    def test_md5_match(self, mock_run, mock_write_config, tmp_path):
        mock_config = tmp_path / "rclone.conf"
        mock_config.write_text("[gcs_backup]")
        mock_write_config.return_value = mock_config

        mock_run.return_value = MagicMock(returncode=0, stdout="")

        result = _verify_cloud_file_md5(
            "/fake/key.json", "asia-south1", "my-bucket", "D_Drive_Backup",
            "file.txt", "abc123",
        )
        assert result["status"] == "OK"
        assert result["method"] == "md5"

    @patch("tasks.restore_verify_task._write_temp_config")
    @patch("subprocess.run")
    def test_md5_mismatch(self, mock_run, mock_write_config, tmp_path):
        mock_config = tmp_path / "rclone.conf"
        mock_config.write_text("[gcs_backup]")
        mock_write_config.return_value = mock_config

        temp_dir = Path(tempfile.gettempdir()) / "backup_agent_test_restore"
        temp_dir.mkdir(parents=True, exist_ok=True)
        differ_file = temp_dir / "differ.txt"
        differ_file.write_text("file.txt\n")

        mock_run.return_value = MagicMock(returncode=1, stdout="")

        result = _verify_cloud_file_md5(
            "/fake/key.json", "asia-south1", "my-bucket", "D_Drive_Backup",
            "file.txt", "abc123",
        )
        assert result["status"] == "MISMATCH"

        differ_file.unlink(missing_ok=True)


class TestRestoreTask:
    """Tests for the full test restore task."""

    def test_skips_when_db_missing(self, tmp_path):
        result = restore_task.fn(
            database_path=str(tmp_path / "nonexistent.db"),
            source_drive="D:\\",
            lan_destination="\\\\192.168.10.10\\test$",
        )
        assert result["status"] == "SKIPPED"

    def test_skips_when_manifest_empty(self, tmp_path):
        db_path = tmp_path / "manifest.db"
        db = ManifestDB(db_path)
        db.close()

        result = restore_task.fn(
            database_path=str(db_path),
            source_drive="D:\\",
            lan_destination="\\\\192.168.10.10\\test$",
        )
        assert result["status"] == "SKIPPED"

    def test_skips_when_all_pending(self, tmp_path):
        db_path = tmp_path / "manifest.db"
        db = ManifestDB(db_path)
        db.upsert_entry("file1.txt", 100, 1700000000.0)
        db.upsert_entry("file2.txt", 200, 1700000001.0)
        db.close()

        result = restore_task.fn(
            database_path=str(db_path),
            source_drive="D:\\",
            lan_destination="\\\\192.168.10.10\\test$",
        )
        assert result["status"] == "SKIPPED"

    def test_samples_and_verifies_lan(self, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()

        from core.hashing import compute_checksum
        for name, content in [("file1.txt", b"a" * 100), ("file2.txt", b"b" * 200), ("file3.txt", b"c" * 300)]:
            (source / name).write_bytes(content)
            (lan_dest / name).write_bytes(content)

        db_path = tmp_path / "manifest.db"
        db = ManifestDB(db_path)
        for name, content in [("file1.txt", b"a" * 100), ("file2.txt", b"b" * 200), ("file3.txt", b"c" * 300)]:
            checksum = compute_checksum(source / name)
            db.upsert_entry(name, len(content), 1700000000.0, checksum=checksum)
        db.close()

        result = restore_task.fn(
            database_path=str(db_path),
            source_drive=str(source),
            lan_destination=str(lan_dest),
            cloud_enabled=False,
            sample_count=3,
        )

        assert result["lan"]["status"] == "OK"
        assert result["lan"]["ok"] == 3
        assert result["lan"]["failed"] == 0
        assert result["cloud"]["status"] == "SKIPPED"

    def test_detects_missing_lan_file(self, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()

        from core.hashing import compute_checksum
        (source / "file1.txt").write_bytes(b"a" * 100)
        (lan_dest / "file1.txt").write_bytes(b"a" * 100)
        # file2.txt missing from LAN

        db_path = tmp_path / "manifest.db"
        db = ManifestDB(db_path)
        db.upsert_entry("file1.txt", 100, 1700000000.0, checksum=compute_checksum(source / "file1.txt"))
        db.upsert_entry("file2.txt", 200, 1700000001.0, checksum="def456")
        db.close()

        result = restore_task.fn(
            database_path=str(db_path),
            source_drive=str(source),
            lan_destination=str(lan_dest),
            cloud_enabled=False,
            sample_count=2,
        )

        assert result["lan"]["status"] == "PARTIAL"
        assert result["lan"]["failed"] >= 1

    @patch("tasks.restore_verify_task._verify_cloud_file_download")
    @patch("tasks.restore_verify_task._verify_cloud_file_md5")
    def test_verifies_cloud_when_enabled(self, mock_md5, mock_download, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()

        from core.hashing import compute_checksum
        (source / "file1.txt").write_bytes(b"a" * 100)
        (lan_dest / "file1.txt").write_bytes(b"a" * 100)

        db_path = tmp_path / "manifest.db"
        db = ManifestDB(db_path)
        db.upsert_entry("file1.txt", 100, 1700000000.0, checksum="abc123")
        db.close()

        mock_download.return_value = {"path": "file1.txt", "status": "OK", "method": "download"}
        mock_md5.return_value = {"path": "file1.txt", "status": "OK", "method": "md5"}

        result = restore_task.fn(
            database_path=str(db_path),
            source_drive=str(source),
            lan_destination=str(lan_dest),
            cloud_enabled=True,
            gcs_key_path="/fake/key.json",
            cloud_bucket="my-bucket",
            cloud_remote_path="D_Drive_Backup",
            gcs_location="asia-south1",
            sample_count=1,
        )

        assert result["cloud"]["status"] == "OK"
        mock_download.assert_called_once()

    def test_respects_sample_count(self, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()

        from core.hashing import compute_checksum
        for i in range(20):
            content = b"x" * 100
            (source / f"file{i}.txt").write_bytes(content)
            (lan_dest / f"file{i}.txt").write_bytes(content)

        db_path = tmp_path / "manifest.db"
        db = ManifestDB(db_path)
        for i in range(20):
            checksum = compute_checksum(source / f"file{i}.txt")
            db.upsert_entry(f"file{i}.txt", 100, 1700000000.0 + i, checksum=checksum)
        db.close()

        result = restore_task.fn(
            database_path=str(db_path),
            source_drive=str(source),
            lan_destination=str(lan_dest),
            cloud_enabled=False,
            sample_count=3,
        )

        assert result["lan"]["ok"] == 3
        assert len(result["lan"]["details"]) == 3
