"""Seed GCS bucket with initial directory structure.

Usage:
    uv run scripts/seed_cloud.py [--config config.yaml] [--dry-run]

Creates the remote_path directory in the GCS bucket if it doesn't exist.
This is a one-time setup step for new deployments.
"""

import subprocess
from pathlib import Path

import typer
import yaml

app = typer.Typer(help="Seed GCS bucket with initial structure")


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
        typer.echo("ERROR: No bucket configured in cloud_backup.bucket")
        return False

    remote = f"{bucket}:{remote_path}"

    if dry_run:
        typer.echo(f"  Would create: {remote}")
        return True

    typer.echo(f"  Creating: {remote}")

    try:
        result = subprocess.run(
            ["rclone", "mkdir", remote],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            typer.echo(f"  Directory created: {remote}")
            return True
        else:
            if "exists" in result.stderr.lower():
                typer.echo(f"  Directory already exists: {remote}")
                return True
            typer.echo(f"  Failed: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        typer.echo("ERROR: rclone not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        typer.echo("ERROR: rclone mkdir timed out")
        return False


def verify_bucket(config: dict) -> bool:
    """Verify the bucket is accessible and has the expected structure."""
    cloud = config.get("cloud_backup", {})
    bucket = cloud.get("bucket", "")
    remote_path = cloud.get("remote_path", "D_Drive_Backup")

    remote = f"{bucket}:{remote_path}"

    typer.echo(f"  Verifying: {remote}")

    import tempfile
    from core.rclone import _write_temp_config
    from pathlib import Path
    temp_dir = Path(tempfile.gettempdir()) / "backup_agent_seed"
    temp_config = _write_temp_config(
        temp_dir, "seed", "/dev/null", cloud.get("gcs_location", "asia-south1")
    )

    try:
        result = subprocess.run(
            ["rclone", "lsd", remote, "--config", str(temp_config), "--max-depth", "1"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            typer.echo("  Bucket structure verified")
            return True
        else:
            typer.echo(f"  Verification failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        typer.echo(f"  Verification error: {e}")
        return False


@app.command()
def seed(
    config: Path = typer.Option(Path("config.yaml"), "--config", "-c", help="Path to config.yaml"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show what would be done"),
):
    """Seed GCS bucket with initial structure."""
    typer.echo("=" * 50)
    typer.echo("Backup Agent — Seed Cloud Bucket")
    typer.echo("=" * 50)

    loaded = load_config(config)

    typer.echo("\n[1/2] Creating bucket structure...")
    if not seed_bucket(loaded, dry_run=dry_run):
        raise typer.Exit(1)

    typer.echo("\n[2/2] Verifying bucket structure...")
    if not verify_bucket(loaded):
        raise typer.Exit(1)

    typer.echo("\nBucket seeded successfully")


if __name__ == "__main__":
    app()
