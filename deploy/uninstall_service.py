"""Uninstall the backup agent Windows service.

Usage:
    uv run deploy/uninstall_service.py [--service-name BackupAgent] [--nssm-path nssm.exe]

Stops and removes the Windows service. Does NOT delete:
- config.yaml
- manifest.db
- log files
- NSSM binary
"""

import argparse
import subprocess
import sys
from pathlib import Path


def find_nssm(configured_path: str | None = None) -> Path | None:
    """Find the NSSM executable."""
    if configured_path:
        p = Path(configured_path)
        if p.exists():
            return p
        return None

    candidates = [
        Path("C:\\nssm\\nssm.exe"),
        Path("C:\\Program Files\\nssm\\nssm.exe"),
        Path("C:\\Program Files (x86)\\nssm\\nssm.exe"),
    ]
    for p in candidates:
        if p.exists():
            return p

    import shutil
    nssm_in_path = shutil.which("nssm")
    if nssm_in_path:
        return Path(nssm_in_path)

    return None


def stop_service(nssm: Path, service_name: str) -> bool:
    """Stop the Windows service."""
    cmd = [str(nssm), "stop", service_name]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"  Service '{service_name}' stopped")
            return True
        else:
            # Service might already be stopped
            if "not started" in result.stderr.lower():
                print(f"  Service '{service_name}' was not running")
                return True
            print(f"  Stop failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  Stop error: {e}")
        return False


def remove_service(nssm: Path, service_name: str) -> bool:
    """Remove the Windows service."""
    cmd = [str(nssm), "remove", service_name, "confirm"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"  Service '{service_name}' removed")
            return True
        else:
            print(f"  Remove failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  Remove error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Uninstall backup agent Windows service")
    parser.add_argument(
        "--service-name",
        default="BackupAgent",
        help="Service name to uninstall (default: BackupAgent)",
    )
    parser.add_argument(
        "--nssm-path",
        type=str,
        default=None,
        help="Path to nssm.exe (auto-detected if not specified)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    print("=" * 50)
    print("Backup Agent — Uninstall Service")
    print("=" * 50)

    # Find NSSM
    nssm = find_nssm(args.nssm_path)
    if not nssm:
        print("\nERROR: NSSM not found.")
        print("Specify path with --nssm-path")
        sys.exit(1)

    print(f"\nFound NSSM: {nssm}")

    if args.dry_run:
        print(f"\n  Would stop service: {args.service_name}")
        print(f"  Would remove service: {args.service_name}")
        print("\n  Note: The following will NOT be deleted:")
        print("    - config.yaml")
        print("    - manifest.db")
        print("    - Log files")
        return

    if sys.platform != "win32":
        print("\nERROR: This script requires Windows.")
        sys.exit(1)

    # Stop
    print(f"\n[1/2] Stopping service '{args.service_name}'...")
    if not stop_service(nssm, args.service_name):
        print("\n  Warning: Service may not have been running")

    # Remove
    print(f"\n[2/2] Removing service '{args.service_name}'...")
    if not remove_service(nssm, args.service_name):
        sys.exit(1)

    print("\nService uninstalled successfully")
    print("\nNote: The following were NOT deleted:")
    print("  - config.yaml")
    print("  - manifest.db")
    print("  - Log files")
    print("  - NSSM binary")


if __name__ == "__main__":
    main()
