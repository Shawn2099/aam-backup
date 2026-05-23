"""Create Prefect deployment for the nightly backup flow.

Usage:
    uv run deploy/create_deployment.py [--config config.yaml]

Uses Prefect 3.x flow.serve() method for deployment creation.
Creates a deployment named 'nightly-backup-production' with:
- Cron schedule at configured daily_time
- Default parameters
"""

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
):
    """Create the Prefect deployment using flow.serve()."""
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
    typer.echo(f"  Config: {config_path}")

    nightly_backup.serve(
        name="nightly-backup-production",
        cron=cron,
        parameters={"config_path": str(config_path)},
        tags=["production", "backup", "aam-associates"],
        description="Nightly backup of D:\\ drive to LAN and GCS",
    )


if __name__ == "__main__":
    app()
