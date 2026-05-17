"""Create Prefect deployment for the nightly backup flow.

Usage:
    uv run deploy/create_deployment.py [--config config.yaml]

Creates a deployment named 'nightly-backup-production' with:
- Cron schedule at configured daily_time
- Work pool assignment
- Environment variables for config path
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


def time_to_cron(time_str: str) -> str:
    """Convert HH:MM to cron expression."""
    parts = time_str.split(":")
    hour = parts[0]
    minute = parts[1]
    return f"{minute} {hour} * * *"


def create_deployment(config: dict, work_pool: str = "default") -> bool:
    """Create the Prefect deployment."""
    schedule = config.get("schedule", {})
    daily_time = schedule.get("daily_time", "23:00")
    cron = time_to_cron(daily_time)

    # Build the deployment command
    cmd = [
        "prefect",
        "deploy",
        "flow.py:nightly_backup",
        "--name",
        "nightly-backup-production",
        "--cron",
        cron,
        "--work-pool",
        work_pool,
        "--param",
        f"config_path={Path('config.yaml').resolve()}",
    ]

    print(f"  Schedule: {cron} (daily at {daily_time})")
    print(f"  Work pool: {work_pool}")
    print(f"  Config: {Path('config.yaml').resolve()}")
    print(f"\n  Running: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            print("  Deployment created successfully")
            print(result.stdout)
            return True
        else:
            print(f"  Failed: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("ERROR: prefect CLI not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("ERROR: Deployment creation timed out")
        return False


def main():
    parser = argparse.ArgumentParser(description="Create Prefect deployment")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to config.yaml (default: config.yaml)",
    )
    parser.add_argument(
        "--work-pool",
        default="default",
        help="Prefect work pool name (default: default)",
    )
    args = parser.parse_args()

    print("=" * 50)
    print("Backup Agent — Create Deployment")
    print("=" * 50)

    config = load_config(args.config)

    print("\nCreating deployment...")
    if not create_deployment(config, work_pool=args.work_pool):
        sys.exit(1)

    print("\nDeployment ready")


if __name__ == "__main__":
    main()
