"""Seed GCS bucket with initial directory structure.

Usage:
    uv run scripts/seed_cloud.py [--config config.yaml]

Creates the remote_path directory in the GCS bucket if it doesn't exist.
This is a one-time setup step for new deployments.
"""

import argparse
import subprocess
import sys
from pathlib import Path

import yaml


def load_config(config_path: Path) -> dict:
    """Load config.yaml."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def seed_bucket(config: dict, dry_run: bool = False) -> bool:
    """Create the backup root directory in GCS."""
    cloud = config.get("cloud_backup", {})
    bucket = cloud.get("bucket", "")
    remote_path = cloud.get("remote_path", "D_Drive_Backup")

    if not bucket:
        print("ERROR: No bucket configured in cloud_backup.bucket")
        return False

    remote = f"{bucket}:{remote_path}"

    if dry_run:
        print(f"  Would create: {remote}")
        return True

    print(f"  Creating: {remote}")

    try:
        result = subprocess.run(
            ["rclone", "mkdir", remote],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"  Directory created: {remote}")
            return True
        else:
            # mkdir may fail if directory already exists, which is fine
            if "exists" in result.stderr.lower():
                print(f"  Directory already exists: {remote}")
                return True
            print(f"  Failed: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("ERROR: rclone not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("ERROR: rclone mkdir timed out")
        return False


def verify_bucket(config: dict) -> bool:
    """Verify the bucket is accessible and has the expected structure."""
    cloud = config.get("cloud_backup", {})
    bucket = cloud.get("bucket", "")
    remote_path = cloud.get("remote_path", "D_Drive_Backup")

    remote = f"{bucket}:{remote_path}"

    print(f"  Verifying: {remote}")

    try:
        result = subprocess.run(
            ["rclone", "lsd", remote, "--max-depth", "1"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print("  Bucket structure verified")
            return True
        else:
            print(f"  Verification failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  Verification error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Seed GCS bucket with initial structure")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to config.yaml (default: config.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    print("=" * 50)
    print("Backup Agent — Seed Cloud Bucket")
    print("=" * 50)

    config = load_config(args.config)

    # Seed
    print("\n[1/2] Creating bucket structure...")
    if not seed_bucket(config, dry_run=args.dry_run):
        sys.exit(1)

    # Verify
    print("\n[2/2] Verifying bucket structure...")
    if not verify_bucket(config):
        sys.exit(1)

    print("\nBucket seeded successfully")


if __name__ == "__main__":
    main()
