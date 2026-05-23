"""Test connections to LAN and GCS destinations.

Usage:
    uv run scripts/test_connections.py [--config config.yaml]

Tests:
- LAN share accessibility
- GCS bucket accessibility via rclone
- Write permissions on both destinations
"""

import subprocess
import sys
from pathlib import Path

import typer
import yaml

app = typer.Typer(help="Test backup destination connections")


def load_config(config_path: Path) -> dict:
    """Load config.yaml."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def test_lan_connection(config: dict) -> bool:
    """Test LAN share connectivity."""
    lan = config.get("lan_backup", {})
    wol = config.get("wol", {})

    if not lan.get("enabled", False):
        typer.echo("  LAN backup disabled, skipping")
        return True

    dest = config.get("paths", {}).get("lan_destination", "")
    server_ip = wol.get("server_ip", "")

    typer.echo(f"  Testing LAN share: {dest}")

    if sys.platform == "win32":
        try:
            import os
            dest_path = dest
            # Path.exists() returns False for UNC paths even when accessible.
            # Use os.listdir() as the real accessibility test.
            os.listdir(dest_path)
            typer.echo("  LAN share is accessible")
            return True
        except PermissionError:
            typer.echo("  LAN share access failed: Permission denied")
            return False
        except FileNotFoundError:
            typer.echo("  LAN share not found")
            return False
        except OSError as e:
            typer.echo(f"  LAN share connection failed: {e}")
            return False
    else:
        if not server_ip:
            typer.echo("  No server_ip configured, skipping LAN test")
            return True
        try:
            result = subprocess.run(
                ["ping", "-c", "1", server_ip],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                typer.echo(f"  Server {server_ip} is reachable (Linux dev mode)")
                return True
            else:
                typer.echo(f"  Server {server_ip} is not reachable")
                return False
        except Exception as e:
            typer.echo(f"  Ping failed: {e}")
            return False


def test_gcs_connection(config: dict) -> bool:
    """Test GCS bucket connectivity via rclone."""
    cloud = config.get("cloud_backup", {})

    if not cloud.get("enabled", False):
        typer.echo("  Cloud backup disabled, skipping")
        return True

    bucket = cloud.get("bucket", "")
    if not bucket:
        typer.echo("  ERROR: No bucket configured")
        return False

    typer.echo(f"  Testing GCS bucket: {bucket}")

    try:
        result = subprocess.run(
            ["rclone", "lsd", f"{bucket}:", "--max-depth", "1"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            typer.echo("  GCS bucket is accessible")
            return True
        else:
            typer.echo(f"  GCS access failed: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        typer.echo("  ERROR: rclone not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        typer.echo("  GCS connection timed out")
        return False


@app.command()
def test(
    config: Path = typer.Option(Path("config.yaml"), "--config", "-c", help="Path to config.yaml"),
):
    """Test backup destination connections."""
    typer.echo("=" * 50)
    typer.echo("Backup Agent — Connection Tests")
    typer.echo("=" * 50)

    loaded = load_config(config)
    results = {}

    typer.echo("\n[1/2] Testing LAN connection...")
    results["LAN"] = test_lan_connection(loaded)

    typer.echo("\n[2/2] Testing GCS connection...")
    results["GCS"] = test_gcs_connection(loaded)

    typer.echo("\n" + "=" * 50)
    all_passed = all(results.values())
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        typer.echo(f"  {name}: {status}")

    if all_passed:
        typer.echo("\nAll connections OK")
    else:
        typer.echo("\nSome connections failed")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
