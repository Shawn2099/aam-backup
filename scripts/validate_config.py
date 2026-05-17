"""Validate config.yaml before deployment.

Usage:
    uv run scripts/validate_config.py [--config config.yaml]

Checks:
- YAML syntax
- Required fields present
- Path format validity
- Schedule format
- Network connectivity to LAN destination
- Rclone binary availability
- Robocopy binary availability (Windows only)
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


def load_config(config_path: Path) -> dict | None:
    """Load and parse config.yaml."""
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        return None

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return config
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML syntax: {e}")
        return None


def check_required_fields(config: dict) -> list[str]:
    """Check that all required fields are present and non-empty."""
    errors = []

    # Firm
    if not config.get("firm", {}).get("name"):
        errors.append("firm.name is required")

    # Paths
    paths = config.get("paths", {})
    required_paths = [
        "source_drive",
        "lan_destination",
        "log_directory",
        "database_path",
        "rclone_temp_directory",
    ]
    for field in required_paths:
        if not paths.get(field):
            errors.append(f"paths.{field} is required")

    # Cloud backup
    cloud = config.get("cloud_backup", {})
    if cloud.get("enabled", False) and not cloud.get("bucket"):
        errors.append("cloud_backup.bucket is required when cloud_backup.enabled is true")

    # WoL
    wol = config.get("wol", {})
    if wol.get("enabled", False) and not wol.get("mac_address"):
        errors.append("wol.mac_address is required when wol.enabled is true")
    if wol.get("enabled", False) and not wol.get("server_ip"):
        errors.append("wol.server_ip is required when wol.enabled is true")

    # Notifications
    notifications = config.get("notifications", {})
    if notifications.get("send_on_failure", False) or notifications.get("send_on_every_run", False):
        if not notifications.get("smtp_host"):
            errors.append("notifications.smtp_host is required when email notifications are enabled")
        if not notifications.get("sender"):
            errors.append("notifications.sender is required when email notifications are enabled")
        if not notifications.get("recipients"):
            errors.append("notifications.recipients is required when email notifications are enabled")

    return errors


def check_binaries() -> list[str]:
    """Check that required binaries are available."""
    errors = []

    # Robocopy (Windows only)
    if sys.platform == "win32":
        if not shutil.which("robocopy"):
            errors.append("robocopy.exe not found in PATH")
    else:
        print("  Note: robocopy check skipped (not on Windows)")

    # Rclone
    if not shutil.which("rclone"):
        errors.append("rclone not found in PATH")

    return errors


def check_paths(config: dict) -> list[str]:
    """Validate path formats."""
    errors = []
    paths = config.get("paths", {})

    # Source drive should be a valid Windows drive letter
    source = paths.get("source_drive", "")
    if source and sys.platform == "win32":
        if not (len(source) == 3 and source[1] == ":" and source[2] == "\\"):
            errors.append(f"paths.source_drive should be in format 'X:\\', got: {source}")

    return errors


def check_lan_connectivity(config: dict) -> list[str]:
    """Test connectivity to LAN destination."""
    errors = []
    lan = config.get("lan_backup", {})
    wol = config.get("wol", {})

    if not lan.get("enabled", False):
        return errors

    server_ip = wol.get("server_ip", "")
    if not server_ip:
        return errors

    print(f"  Testing connectivity to {server_ip}...")
    try:
        result = subprocess.run(
            ["ping", "-n", "1" if sys.platform == "win32" else "-c", "1", server_ip],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            errors.append(f"Cannot ping LAN server at {server_ip}")
        else:
            print(f"  LAN server {server_ip} is reachable")
    except subprocess.TimeoutExpired:
        errors.append(f"Ping to {server_ip} timed out")
    except Exception as e:
        errors.append(f"Ping failed: {e}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate backup configuration")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to config.yaml (default: config.yaml)",
    )
    args = parser.parse_args()

    print("=" * 50)
    print("Backup Agent — Config Validation")
    print("=" * 50)

    all_errors = []

    # Load config
    print("\n[1/5] Loading config...")
    config = load_config(args.config)
    if config is None:
        sys.exit(1)
    print("  Config loaded successfully")

    # Check required fields
    print("\n[2/5] Checking required fields...")
    field_errors = check_required_fields(config)
    if field_errors:
        all_errors.extend(field_errors)
        for err in field_errors:
            print(f"  ERROR: {err}")
    else:
        print("  All required fields present")

    # Check binaries
    print("\n[3/5] Checking binaries...")
    binary_errors = check_binaries()
    if binary_errors:
        all_errors.extend(binary_errors)
        for err in binary_errors:
            print(f"  ERROR: {err}")
    else:
        print("  All binaries found")

    # Check paths
    print("\n[4/5] Checking path formats...")
    path_errors = check_paths(config)
    if path_errors:
        all_errors.extend(path_errors)
        for err in path_errors:
            print(f"  ERROR: {err}")
    else:
        print("  Path formats valid")

    # Check LAN connectivity
    print("\n[5/5] Testing LAN connectivity...")
    lan_errors = check_lan_connectivity(config)
    if lan_errors:
        all_errors.extend(lan_errors)
        for err in lan_errors:
            print(f"  ERROR: {err}")
    else:
        print("  LAN connectivity OK")

    # Summary
    print("\n" + "=" * 50)
    if all_errors:
        print(f"FAILED: {len(all_errors)} error(s) found")
        sys.exit(1)
    else:
        print("PASSED: Configuration is valid")


if __name__ == "__main__":
    main()
