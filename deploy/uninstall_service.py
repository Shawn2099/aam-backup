"""Uninstall the backup agent Windows service.

Usage:
    uv run deploy/uninstall_service.py [--service-name BackupAgent] [--servy-path servy.exe]

Stops and removes the Windows service. Does NOT delete:
- config.yaml
- manifest.db
- log files
- Servy binary
"""

import subprocess
import sys
from pathlib import Path

import typer

app = typer.Typer(help="Uninstall backup agent Windows service")


def find_servy(configured_path: str | None = None) -> Path | None:
    """Find the Servy executable."""
    if configured_path:
        p = Path(configured_path)
        if p.exists():
            return p
        return None

    candidates = [
        Path("C:\\servy\\servy.exe"),
        Path("C:\\Program Files\\servy\\servy.exe"),
        Path("C:\\Program Files (x86)\\servy\\servy.exe"),
    ]
    for p in candidates:
        if p.exists():
            return p

    import shutil
    servy_in_path = shutil.which("servy")
    if servy_in_path:
        return Path(servy_in_path)

    return None


def stop_service(servy: Path, service_name: str) -> bool:
    """Stop the Windows service."""
    cmd = [str(servy), "stop", service_name]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            typer.echo(f"  Service '{service_name}' stopped")
            return True
        else:
            if "not started" in result.stderr.lower():
                typer.echo(f"  Service '{service_name}' was not running")
                return True
            typer.echo(f"  Stop failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        typer.echo(f"  Stop error: {e}")
        return False


def remove_service(servy: Path, service_name: str) -> bool:
    """Remove the Windows service."""
    cmd = [str(servy), "delete", service_name]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            typer.echo(f"  Service '{service_name}' removed")
            return True
        else:
            typer.echo(f"  Remove failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        typer.echo(f"  Remove error: {e}")
        return False


@app.command()
def uninstall(
    service_name: str = typer.Option("BackupAgent", "--service-name", help="Service name to uninstall"),
    servy_path: str | None = typer.Option(None, "--servy-path", help="Path to servy.exe"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show what would be done"),
):
    """Uninstall backup agent Windows service."""
    typer.echo("=" * 50)
    typer.echo("Backup Agent — Uninstall Service")
    typer.echo("=" * 50)

    servy = find_servy(servy_path)
    if not servy:
        typer.echo("\nERROR: Servy not found.")
        typer.echo("Specify path with --servy-path")
        raise typer.Exit(1)

    typer.echo(f"\nFound Servy: {servy}")

    if dry_run:
        typer.echo(f"\n  Would stop service: {service_name}")
        typer.echo(f"  Would remove service: {service_name}")
        typer.echo("\n  Note: The following will NOT be deleted:")
        typer.echo("    - config.yaml")
        typer.echo("    - manifest.db")
        typer.echo("    - Log files")
        return

    if sys.platform != "win32":
        typer.echo("\nERROR: This script requires Windows.")
        raise typer.Exit(1)

    typer.echo(f"\n[1/2] Stopping service '{service_name}'...")
    if not stop_service(servy, service_name):
        typer.echo("\n  Warning: Service may not have been running")

    typer.echo(f"\n[2/2] Removing service '{service_name}'...")
    if not remove_service(servy, service_name):
        raise typer.Exit(1)

    typer.echo("\nService uninstalled successfully")
    typer.echo("\nNote: The following were NOT deleted:")
    typer.echo("  - config.yaml")
    typer.echo("  - manifest.db")
    typer.echo("  - Log files")
    typer.echo("  - Servy binary")


if __name__ == "__main__":
    app()
