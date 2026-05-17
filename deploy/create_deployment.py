"""Create Prefect deployment for the nightly backup flow.

Usage:
    uv run deploy/create_deployment.py [--config config.yaml] [--work-pool default]

Uses Prefect's native flow.deploy() method instead of subprocess CLI calls.
Creates a deployment named 'nightly-backup-production' with:
- Cron schedule at configured daily_time
- Work pool assignment
- Default parameters
"""

import sys
from pathlib import Path

import typer
import yaml

app = typer.Typer(help="Create Prefect deployment")


def load_config(config_path: Path) -> dict:
    """Load config.yaml."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def time_to_cron(time_str: str) -> str:
    """Convert HH:MM to cron expression."""
    parts = time_str.split(":")
    return f"{parts[1]} {parts[0]} * * *"


@app.command()
def create(
    config: Path = typer.Option(Path("config.yaml"), "--config", "-c", help="Path to config.yaml"),
    work_pool: str = typer.Option("default", "--work-pool", "-p", help="Prefect work pool name"),
):
    """Create the Prefect deployment using native flow.deploy()."""
    from flow import nightly_backup

    typer.echo("=" * 50)
    typer.echo("Backup Agent — Create Deployment")
    typer.echo("=" * 50)

    loaded = load_config(config)
    schedule = loaded.get("schedule", {})
    daily_time = schedule.get("daily_time", "23:00")
    cron = time_to_cron(daily_time)
    config_path = Path("config.yaml").resolve()

    typer.echo(f"\n  Schedule: {cron} (daily at {daily_time})")
    typer.echo(f"  Work pool: {work_pool}")
    typer.echo(f"  Config: {config_path}")

    try:
        deployment_id = nightly_backup.deploy(
            name="nightly-backup-production",
            work_pool_name=work_pool,
            cron=cron,
            parameters={"config_path": str(config_path)},
            tags=["production", "backup", "aam-associates"],
            description="Nightly backup of D:\\ drive to LAN and GCS",
        )
        typer.echo(f"\n  Deployment created: {deployment_id}")
        typer.echo("\nDeployment ready")
    except Exception as e:
        typer.echo(f"\n  Failed: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
