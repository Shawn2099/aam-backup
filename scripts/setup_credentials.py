"""Setup credentials in Windows Credential Manager.

Usage:
    uv run scripts/setup_credentials.py --type gcs --name BackupAgent_GCS
    uv run scripts/setup_credentials.py --type smtp --name BackupAgent_SMTP

Prompts for credentials interactively and stores them securely.
"""

import argparse
import getpass
import subprocess
import sys
from pathlib import Path


def store_credential(name: str, username: str, password: str) -> bool:
    """Store a credential in Windows Credential Manager using cmdkey."""
    try:
        # cmdkey /add:target /user:username /pass:password
        cmd = ["cmdkey", f"/add:{name}", f"/user:{username}", f"/pass:{password}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"  Credential '{name}' stored successfully.")
            return True
        else:
            print(f"  Failed to store credential: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("  Error: 'cmdkey' not found. This script requires Windows.")
        return False
    except subprocess.TimeoutExpired:
        print("  Error: cmdkey timed out.")
        return False


def setup_gcs_credential(name: str) -> bool:
    """Setup GCS service account credentials."""
    print(f"\nSetting up GCS credential: {name}")
    print("Enter the full path to your GCS service account JSON key file:")
    key_path = input("> ").strip()

    path = Path(key_path)
    if not path.exists():
        print(f"  Error: File not found: {path}")
        return False

    # Store the path as the credential value
    try:
        cmd = ["cmdkey", f"/add:{name}", f"/user:service_account", f"/pass:{path.resolve()}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"  GCS credential '{name}' stored successfully.")
            print(f"  Key file: {path.resolve()}")
            return True
        else:
            print(f"  Failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def setup_smtp_credential(name: str) -> bool:
    """Setup SMTP credentials."""
    print(f"\nSetting up SMTP credential: {name}")
    username = input("SMTP username: ").strip()
    password = getpass.getpass("SMTP password: ")

    if not username or not password:
        print("  Error: Username and password are required.")
        return False

    return store_credential(name, username, password)


def setup_lan_credential(name: str) -> bool:
    """Setup LAN share credentials."""
    print(f"\nSetting up LAN credential: {name}")
    username = input("LAN username: ").strip()
    password = getpass.getpass("LAN password: ")

    if not username or not password:
        print("  Error: Username and password are required.")
        return False

    return store_credential(name, username, password)


def main():
    parser = argparse.ArgumentParser(description="Setup credentials in Windows Credential Manager")
    parser.add_argument(
        "--type",
        choices=["gcs", "smtp", "lan"],
        required=True,
        help="Type of credential to setup",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Credential name (must match config.yaml)",
    )
    args = parser.parse_args()

    print("=" * 50)
    print("Backup Agent — Credential Setup")
    print("=" * 50)

    if sys.platform != "win32":
        print("\nWarning: This script is designed for Windows.")
        print("On Linux, credentials would be stored differently.")
        print("Continuing in dry-run mode...\n")
        print(f"  Would setup {args.type} credential: {args.name}")
        return

    if args.type == "gcs":
        success = setup_gcs_credential(args.name)
    elif args.type == "smtp":
        success = setup_smtp_credential(args.name)
    elif args.type == "lan":
        success = setup_lan_credential(args.name)
    else:
        print(f"Unknown credential type: {args.type}")
        success = False

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
