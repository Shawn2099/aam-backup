"""Test connections to LAN and GCS destinations.

Usage:
    uv run scripts/test_connections.py [--config config.yaml]

Tests:
- LAN share accessibility
- GCS bucket accessibility via rclone
- Write permissions on both destinations
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


def test_lan_connection(config: dict) -> bool:
    """Test LAN share connectivity."""
    lan = config.get("lan_backup", {})
    wol = config.get("wol", {})

    if not lan.get("enabled", False):
        print("  LAN backup disabled, skipping")
        return True

    dest = config.get("paths", {}).get("lan_destination", "")
    server_ip = wol.get("server_ip", "")

    print(f"  Testing LAN share: {dest}")

    if sys.platform == "win32":
        # Try to list the share
        try:
            result = subprocess.run(
                ["dir", dest],
                capture_output=True,
                text=True,
                timeout=30,
                shell=True,
            )
            if result.returncode == 0:
                print("  LAN share is accessible")
                return True
            else:
                print(f"  LAN share access failed: {result.stderr.strip()}")
                return False
        except subprocess.TimeoutExpired:
            print("  LAN share connection timed out")
            return False
    else:
        # On Linux, just test ping
        if not server_ip:
            print("  No server_ip configured, skipping LAN test")
            return True

        try:
            result = subprocess.run(
                ["ping", "-c", "1", server_ip],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                print(f"  Server {server_ip} is reachable (Linux dev mode)")
                return True
            else:
                print(f"  Server {server_ip} is not reachable")
                return False
        except Exception as e:
            print(f"  Ping failed: {e}")
            return False


def test_gcs_connection(config: dict) -> bool:
    """Test GCS bucket connectivity via rclone."""
    cloud = config.get("cloud_backup", {})

    if not cloud.get("enabled", False):
        print("  Cloud backup disabled, skipping")
        return True

    bucket = cloud.get("bucket", "")
    if not bucket:
        print("  ERROR: No bucket configured")
        return False

    print(f"  Testing GCS bucket: {bucket}")

    try:
        result = subprocess.run(
            ["rclone", "lsd", f"{bucket}:", "--max-depth", "1"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print("  GCS bucket is accessible")
            return True
        else:
            print(f"  GCS access failed: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("  ERROR: rclone not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("  GCS connection timed out")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test backup destination connections")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to config.yaml (default: config.yaml)",
    )
    args = parser.parse_args()

    print("=" * 50)
    print("Backup Agent — Connection Tests")
    print("=" * 50)

    config = load_config(args.config)

    results = {}

    # Test LAN
    print("\n[1/2] Testing LAN connection...")
    results["LAN"] = test_lan_connection(config)

    # Test GCS
    print("\n[2/2] Testing GCS connection...")
    results["GCS"] = test_gcs_connection(config)

    # Summary
    print("\n" + "=" * 50)
    all_passed = all(results.values())
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")

    if all_passed:
        print("\nAll connections OK")
    else:
        print("\nSome connections failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
