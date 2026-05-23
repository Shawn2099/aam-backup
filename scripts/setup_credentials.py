"""Setup credentials in Windows Credential Manager.

Usage:
    uv run scripts/setup_credentials.py gcs --name BackupAgent_GCS
    uv run scripts/setup_credentials.py smtp --name BackupAgent_SMTP

Prompts for credentials interactively and stores them securely.
"""

import getpass
import subprocess
from pathlib import Path

import typer

app = typer.Typer(help="Setup credentials in Windows Credential Manager")


def store_credential(name: str, username: str, password: str) -> bool:
    """Store a credential in Windows Credential Manager using cmdkey."""
    try:
        cmd = ["cmdkey", f"/add:{name}", f"/user:{username}", f"/pass:{password}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            typer.echo(f"  Credential '{name}' stored successfully.")
            return True
        else:
            typer.echo(f"  Failed to store credential: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        typer.echo("  Error: 'cmdkey' not found. This script requires Windows.")
        return False
    except subprocess.TimeoutExpired:
        typer.echo("  Error: cmdkey timed out.")
        return False


@app.command()
def gcs(
    name: str = typer.Option(..., "--name", "-n", help="Credential name (must match config.yaml)"),
):
    """Setup GCS service account credentials."""
    typer.echo(f"\nSetting up GCS credential: {name}")
    typer.echo("Enter the full path to your GCS service account JSON key file:")
    key_path = input("> ").strip()

    path = Path(key_path)
    if not path.exists():
        typer.echo(f"  Error: File not found: {path}")
        raise typer.Exit(1)

    try:
        resolved = str(path.resolve())
        cmd = ["cmdkey", f"/add:{name}", "/user:service_account", f"/pass:{resolved}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            typer.echo(f"  GCS credential '{name}' stored successfully.")
            typer.echo(f"  Key file: {resolved}")
        else:
            typer.echo(f"  Failed: {result.stderr.strip()}")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"  Error: {e}")
        raise typer.Exit(1)


@app.command()
def smtp(
    name: str = typer.Option(..., "--name", "-n", help="Credential name (must match config.yaml)"),
):
    """Setup SMTP credentials."""
    typer.echo(f"\nSetting up SMTP credential: {name}")
    username = typer.prompt("SMTP username")
    password = getpass.getpass("SMTP password: ")

    if not username or not password:
        typer.echo("  Error: Username and password are required.")
        raise typer.Exit(1)

    if not store_credential(name, username, password):
        raise typer.Exit(1)


@app.command()
def lan(
    name: str = typer.Option(..., "--name", "-n", help="Credential name (must match config.yaml)"),
):
    """Setup LAN share credentials."""
    typer.echo(f"\nSetting up LAN credential: {name}")
    username = typer.prompt("LAN username")
    password = getpass.getpass("LAN password: ")

    if not username or not password:
        typer.echo("  Error: Username and password are required.")
        raise typer.Exit(1)

    if not store_credential(name, username, password):
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
