"""Install the backup agent as a Windows service using NSSM.

Usage:
    uv run deploy/install_service.py [--config config.yaml] [--nssm-path nssm.exe]

Creates a Windows service named 'BackupAgent' that:
- Runs the Prefect worker
- Starts automatically on boot
- Restarts on failure
- Logs to C:\\BackupAgent\\logs\\service.log
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


def find_nssm(configured_path: str | None = None) -> Path | None:
    """Find the NSSM executable."""
    if configured_path:
        p = Path(configured_path)
        if p.exists():
            return p
        return None

    # Search common locations
    candidates = [
        Path("C:\\nssm\\nssm.exe"),
        Path("C:\\Program Files\\nssm\\nssm.exe"),
        Path("C:\\Program Files (x86)\\nssm\\nssm.exe"),
    ]
    for p in candidates:
        if p.exists():
            return p

    # Check PATH
    import shutil
    nssm_in_path = shutil.which("nssm")
    if nssm_in_path:
        return Path(nssm_in_path)

    return None


def install_service(
    nssm: Path,
    service_name: str,
    python_exe: Path,
    work_dir: Path,
    config_path: Path,
    log_dir: Path,
) -> bool:
    """Install the Windows service using NSSM."""
    # Create log directory
    log_dir.mkdir(parents=True, exist_ok=True)

    # NSSM install command
    # We run the Prefect worker which will pick up the deployment
    cmd = [
        str(nssm),
        "install",
        service_name,
        str(python_exe),
        "-m",
        "prefect",
        "worker",
        "start",
        "--pool",
        "default",
        "--type",
        "process",
    ]

    print(f"  Installing service: {service_name}")
    print(f"  NSSM: {nssm}")
    print(f"  Python: {python_exe}")
    print(f"  Working directory: {work_dir}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"  Install failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  Install error: {e}")
        return False

    # Configure service settings
    settings = [
        # Working directory
        ("AppDirectory", str(work_dir)),
        # Environment variables
        ("AppEnvironmentExtra", f"BACKUP_CONFIG_PATH={config_path}"),
        # Logging
        ("Stdout", str(log_dir / "service.log")),
        ("Stderr", str(log_dir / "service_error.log")),
        # Auto-start
        ("Start", "SERVICE_AUTO_START"),
        # Restart on failure
        ("AppRestartDelay", "5000"),
        ("AppExit", "Default", "Restart"),
        ("AppExit", "0", "Exit"),
        ("AppExit", "1", "Restart"),
    ]

    for setting in settings:
        set_cmd = [str(nssm), "set", service_name] + list(setting)
        try:
            subprocess.run(set_cmd, capture_output=True, text=True, timeout=10)
        except Exception as e:
            print(f"  Warning: Failed to set {setting[0]}: {e}")

    print(f"  Service '{service_name}' installed successfully")
    return True


def start_service(nssm: Path, service_name: str) -> bool:
    """Start the Windows service."""
    cmd = [str(nssm), "start", service_name]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"  Service '{service_name}' started")
            return True
        else:
            print(f"  Start failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  Start error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Install backup agent as Windows service")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to config.yaml (default: config.yaml)",
    )
    parser.add_argument(
        "--nssm-path",
        type=str,
        default=None,
        help="Path to nssm.exe (auto-detected if not specified)",
    )
    parser.add_argument(
        "--service-name",
        default="BackupAgent",
        help="Service name (default: BackupAgent)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    print("=" * 50)
    print("Backup Agent — Install Service")
    print("=" * 50)

    config = load_config(args.config)
    log_dir = Path(config.get("paths", {}).get("log_directory", "C:\\BackupAgent\\logs"))

    # Find NSSM
    nssm = find_nssm(args.nssm_path)
    if not nssm:
        print("\nERROR: NSSM not found.")
        print("Download from: https://nssm.cc/download")
        print("Or specify path with --nssm-path")
        sys.exit(1)

    print(f"\nFound NSSM: {nssm}")

    # Find Python executable
    python_exe = Path(sys.executable)
    work_dir = Path(__file__).parent.parent.resolve()

    if args.dry_run:
        print(f"\n  Would install service: {args.service_name}")
        print(f"  Python: {python_exe}")
        print(f"  Working directory: {work_dir}")
        print(f"  Log directory: {log_dir}")
        return

    if sys.platform != "win32":
        print("\nERROR: This script requires Windows.")
        sys.exit(1)

    # Install
    print("\n[1/2] Installing service...")
    if not install_service(nssm, args.service_name, python_exe, work_dir, args.config, log_dir):
        sys.exit(1)

    # Start
    print("\n[2/2] Starting service...")
    if not start_service(nssm, args.service_name):
        sys.exit(1)

    print("\nService installed and running")


if __name__ == "__main__":
    main()
