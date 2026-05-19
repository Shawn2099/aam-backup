"""Tests for post-backup verification (core/verify.py)."""

from unittest.mock import MagicMock, patch


from core.verify import (
    verify_lan_checksums,
    verify_cloud_checksums,
    run_dry_run_lan,
    run_dry_run_cloud,
)
from core.hashing import compute_checksum
from models.scan_result import FileInfo, ScanResult


class TestComputeChecksum:
    def test_checksum_is_consistent(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"hello world")
        h1 = compute_checksum(f)
        h2 = compute_checksum(f)
        assert h1 == h2

    def test_checksum_differs_for_different_content(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_bytes(b"hello")
        f2.write_bytes(b"world")
        assert compute_checksum(f1) != compute_checksum(f2)

    def test_checksum_is_hex_string(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"test")
        h = compute_checksum(f)
        assert len(h) == 16
        int(h, 16)  # Valid hex


class TestVerifyLanChecksums:
    def test_empty_scan_returns_empty(self, tmp_path):
        result = verify_lan_checksums(
            str(tmp_path), str(tmp_path / "lan"),
            ScanResult(),
        )
        assert result["verified"] == 0
        assert result["mismatches"] == 0

    def test_all_files_match(self, tmp_path):
        source = tmp_path / "source"
        lan = tmp_path / "lan"
        source.mkdir()
        lan.mkdir()

        for name in ["file1.txt", "file2.txt", "file3.txt"]:
            (source / name).write_bytes(b"data")
            (lan / name).write_bytes(b"data")

        scan = ScanResult()
        for name in ["file1.txt", "file2.txt", "file3.txt"]:
            scan.new_files.append(FileInfo(name, 4, 1700000000.0, "abc"))

        result = verify_lan_checksums(str(source), str(lan), scan, sample_count=3)
        assert result["verified"] == 3
        assert result["mismatches"] == 0

    def test_detects_mismatch(self, tmp_path):
        source = tmp_path / "source"
        lan = tmp_path / "lan"
        source.mkdir()
        lan.mkdir()

        (source / "file.txt").write_bytes(b"correct")
        (lan / "file.txt").write_bytes(b"wrong!!")

        scan = ScanResult()
        scan.new_files.append(FileInfo("file.txt", 7, 1700000000.0, "abc"))

        result = verify_lan_checksums(str(source), str(lan), scan, sample_count=1)
        assert result["mismatches"] == 1

    def test_detects_missing_file(self, tmp_path):
        source = tmp_path / "source"
        lan = tmp_path / "lan"
        source.mkdir()
        lan.mkdir()

        (source / "file.txt").write_bytes(b"data")
        # file.txt missing from LAN

        scan = ScanResult()
        scan.new_files.append(FileInfo("file.txt", 4, 1700000000.0, "abc"))

        result = verify_lan_checksums(str(source), str(lan), scan, sample_count=1)
        assert result["errors"] >= 1

    def test_respects_sample_count(self, tmp_path):
        source = tmp_path / "source"
        lan = tmp_path / "lan"
        source.mkdir()
        lan.mkdir()

        for i in range(20):
            (source / f"f{i}.txt").write_bytes(b"x")
            (lan / f"f{i}.txt").write_bytes(b"x")

        scan = ScanResult()
        for i in range(20):
            scan.new_files.append(FileInfo(f"f{i}.txt", 1, 1700000000.0, "abc"))

        result = verify_lan_checksums(str(source), str(lan), scan, sample_count=3)
        assert len(result["details"]) == 3


class TestVerifyCloudChecksums:
    @patch("subprocess.run")
    def test_all_files_match(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=0, stdout="100 file.txt")

        scan = ScanResult()
        scan.new_files.append(FileInfo("file.txt", 100, 1700000000.0, "abc"))

        result = verify_cloud_checksums(
            "/key.json", "asia-south1", "bucket", "path", scan, sample_count=1,
        )
        assert result["verified"] == 1
        assert result["mismatches"] == 0

    @patch("subprocess.run")
    def test_detects_missing_file(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="not found")

        scan = ScanResult()
        scan.new_files.append(FileInfo("file.txt", 100, 1700000000.0, "abc"))

        result = verify_cloud_checksums(
            "/key.json", "asia-south1", "bucket", "path", scan, sample_count=1,
        )
        assert result["errors"] >= 1


class TestDryRunLan:
    @patch("subprocess.run")
    @patch("platform.system", return_value="Windows")
    def test_parses_robocopy_output(self, mock_platform, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="Files : 100 5 3 2 0 0\nBytes : 1000 50 30 20 0 0",
            stderr="",
        )

        result = run_dry_run_lan("D:\\", "\\\\server\\share")
        assert result["skipped"] is False
        assert result["new"] == 5
        assert result["modified"] == 3
        assert result["deleted"] == 2
        assert result["total"] == 10

    @patch("platform.system", return_value="Linux")
    def test_skips_on_linux(self, mock_platform):
        result = run_dry_run_lan("D:\\", "\\\\server\\share")
        assert result["skipped"] is True


class TestDryRunCloud:
    @patch("subprocess.run")
    def test_parses_rclone_output(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Transferred:    5 / 5 Files, 100 B / 100 B\nDeleted:    2 (files)",
            stderr="",
        )

        result = run_dry_run_cloud("D:\\", "bucket", "path", "/key.json", "asia-south1")
        assert result["transfers"] == 5
        assert result["total"] == 7
