"""Tests for automated test restore verification task."""

import subprocess
from unittest.mock import MagicMock, patch


from core.manifest_db import ManifestDB
from tasks.restore_verify_task import test_restore_task as restore_task, _verify_lan_file, _verify_cloud_file


class TestVerifyLanFile:
    """Tests for LAN file verification."""

    def test_file_exists_and_matches_size(self, tmp_path):
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()
        test_file = lan_dest / "docs" / "report.pdf"
        test_file.parent.mkdir()
        test_file.write_bytes(b"x" * 5000)

        result = _verify_lan_file(str(lan_dest), "docs/report.pdf", 5000)
        assert result["status"] == "OK"
        assert result["size"] == 5000

    def test_file_missing(self, tmp_path):
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()

        result = _verify_lan_file(str(lan_dest), "docs/missing.pdf", 1000)
        assert result["status"] == "MISSING"

    def test_file_size_mismatch(self, tmp_path):
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()
        test_file = lan_dest / "file.txt"
        test_file.write_bytes(b"hello")

        result = _verify_lan_file(str(lan_dest), "file.txt", 9999)
        assert result["status"] == "MISMATCH"
        assert result["expected_size"] == 9999
        assert result["actual_size"] == 5


class TestVerifyCloudFile:
    """Tests for cloud file verification."""

    @patch("tasks.restore_verify_task._write_temp_config")
    @patch("subprocess.run")
    def test_file_exists_and_matches_size(self, mock_run, mock_write_config, tmp_path):
        mock_config = tmp_path / "rclone.conf"
        mock_config.write_text("[gcs_backup]")
        mock_write_config.return_value = mock_config

        mock_run.return_value = MagicMock(returncode=0, stdout="5000 docs/report.pdf")

        result = _verify_cloud_file(
            "/fake/key.json", "asia-south1", "my-bucket", "D_Drive_Backup",
            "docs/report.pdf", 5000,
        )
        assert result["status"] == "OK"
        assert result["size"] == 5000

    @patch("tasks.restore_verify_task._write_temp_config")
    @patch("subprocess.run")
    def test_file_missing(self, mock_run, mock_write_config, tmp_path):
        mock_config = tmp_path / "rclone.conf"
        mock_config.write_text("[gcs_backup]")
        mock_write_config.return_value = mock_config

        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="not found")

        result = _verify_cloud_file(
            "/fake/key.json", "asia-south1", "my-bucket", "D_Drive_Backup",
            "docs/missing.pdf", 1000,
        )
        assert result["status"] == "MISSING"

    @patch("tasks.restore_verify_task._write_temp_config")
    @patch("subprocess.run")
    def test_file_size_mismatch(self, mock_run, mock_write_config, tmp_path):
        mock_config = tmp_path / "rclone.conf"
        mock_config.write_text("[gcs_backup]")
        mock_write_config.return_value = mock_config

        mock_run.return_value = MagicMock(returncode=0, stdout="9999 file.txt")

        result = _verify_cloud_file(
            "/fake/key.json", "asia-south1", "my-bucket", "D_Drive_Backup",
            "file.txt", 5000,
        )
        assert result["status"] == "MISMATCH"

    @patch("tasks.restore_verify_task._write_temp_config")
    @patch("subprocess.run")
    def test_rclone_timeout(self, mock_run, mock_write_config, tmp_path):
        mock_config = tmp_path / "rclone.conf"
        mock_config.write_text("[gcs_backup]")
        mock_write_config.return_value = mock_config

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="rclone", timeout=120)

        result = _verify_cloud_file(
            "/fake/key.json", "asia-south1", "my-bucket", "D_Drive_Backup",
            "file.txt", 5000,
        )
        assert result["status"] == "ERROR"
        assert "timed out" in result["reason"]

    @patch("tasks.restore_verify_task._write_temp_config")
    @patch("subprocess.run")
    def test_rclone_not_found(self, mock_run, mock_write_config, tmp_path):
        mock_config = tmp_path / "rclone.conf"
        mock_config.write_text("[gcs_backup]")
        mock_write_config.return_value = mock_config

        mock_run.side_effect = FileNotFoundError()

        result = _verify_cloud_file(
            "/fake/key.json", "asia-south1", "my-bucket", "D_Drive_Backup",
            "file.txt", 5000,
        )
        assert result["status"] == "ERROR"
        assert "not found" in result["reason"]


class TestRestoreTask:
    """Tests for the full test restore task."""

    def test_skips_when_db_missing(self, tmp_path):
        result = restore_task(
            database_path=str(tmp_path / "nonexistent.db"),
            source_drive="D:\\",
            lan_destination="\\\\192.168.10.10\\test$",
        )
        assert result["status"] == "SKIPPED"

    def test_skips_when_manifest_empty(self, tmp_path):
        db_path = tmp_path / "manifest.db"
        db = ManifestDB(db_path)
        db.close()

        result = restore_task(
            database_path=str(db_path),
            source_drive="D:\\",
            lan_destination="\\\\192.168.10.10\\test$",
        )
        assert result["status"] == "SKIPPED"

    def test_skips_when_all_pending(self, tmp_path):
        db_path = tmp_path / "manifest.db"
        db = ManifestDB(db_path)
        db.upsert_entry("file1.txt", 100, 1700000000.0, checksum="pending")
        db.upsert_entry("file2.txt", 200, 1700000001.0, checksum="pending")
        db.close()

        result = restore_task(
            database_path=str(db_path),
            source_drive="D:\\",
            lan_destination="\\\\192.168.10.10\\test$",
        )
        assert result["status"] == "SKIPPED"

    def test_samples_and_verifies_lan(self, tmp_path):
        # Setup LAN destination with files
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()
        (lan_dest / "file1.txt").write_bytes(b"a" * 100)
        (lan_dest / "file2.txt").write_bytes(b"b" * 200)
        (lan_dest / "file3.txt").write_bytes(b"c" * 300)

        # Setup manifest with confirmed backups
        db_path = tmp_path / "manifest.db"
        db = ManifestDB(db_path)
        db.upsert_entry("file1.txt", 100, 1700000000.0, checksum="abc123")
        db.upsert_entry("file2.txt", 200, 1700000001.0, checksum="def456")
        db.upsert_entry("file3.txt", 300, 1700000002.0, checksum="ghi789")
        db.close()

        result = restore_task(
            database_path=str(db_path),
            source_drive="D:\\",
            lan_destination=str(lan_dest),
            cloud_enabled=False,
            sample_count=3,
        )

        assert result["lan"]["status"] == "OK"
        assert result["lan"]["ok"] == 3
        assert result["lan"]["failed"] == 0
        assert result["cloud"]["status"] == "SKIPPED"

    def test_detects_missing_lan_file(self, tmp_path):
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()
        (lan_dest / "file1.txt").write_bytes(b"a" * 100)
        # file2.txt is missing from LAN

        db_path = tmp_path / "manifest.db"
        db = ManifestDB(db_path)
        db.upsert_entry("file1.txt", 100, 1700000000.0, checksum="abc123")
        db.upsert_entry("file2.txt", 200, 1700000001.0, checksum="def456")
        db.close()

        result = restore_task(
            database_path=str(db_path),
            source_drive="D:\\",
            lan_destination=str(lan_dest),
            cloud_enabled=False,
            sample_count=2,
        )

        assert result["lan"]["status"] == "PARTIAL"
        assert result["lan"]["failed"] >= 1

    @patch("tasks.restore_verify_task._verify_cloud_file")
    def test_verifies_cloud_when_enabled(self, mock_cloud_verify, tmp_path):
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()
        (lan_dest / "file1.txt").write_bytes(b"a" * 100)

        db_path = tmp_path / "manifest.db"
        db = ManifestDB(db_path)
        db.upsert_entry("file1.txt", 100, 1700000000.0, checksum="abc123")
        db.close()

        mock_cloud_verify.return_value = {"path": "file1.txt", "status": "OK", "size": 100}

        result = restore_task(
            database_path=str(db_path),
            source_drive="D:\\",
            lan_destination=str(lan_dest),
            cloud_enabled=True,
            gcs_key_path="/fake/key.json",
            cloud_bucket="my-bucket",
            cloud_remote_path="D_Drive_Backup",
            gcs_location="asia-south1",
            sample_count=1,
        )

        assert result["cloud"]["status"] == "OK"
        mock_cloud_verify.assert_called_once()

    def test_respects_sample_count(self, tmp_path):
        lan_dest = tmp_path / "lan"
        lan_dest.mkdir()
        for i in range(20):
            (lan_dest / f"file{i}.txt").write_bytes(b"x" * 100)

        db_path = tmp_path / "manifest.db"
        db = ManifestDB(db_path)
        for i in range(20):
            db.upsert_entry(f"file{i}.txt", 100, 1700000000.0 + i, checksum=f"hash{i}")
        db.close()

        result = restore_task(
            database_path=str(db_path),
            source_drive="D:\\",
            lan_destination=str(lan_dest),
            cloud_enabled=False,
            sample_count=3,
        )

        assert result["lan"]["ok"] == 3
        assert len(result["lan"]["details"]) == 3
