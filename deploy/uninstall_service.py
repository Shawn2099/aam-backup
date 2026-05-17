"""Uninstall the backup agent Windows service.

Usage:
    uv run deploy/uninstall_service.py [--service-name BackupAgent] [--nssm-path nssm.exe]

Stops and removes the Windows service. Does NOT delete:
- config.yaml
- manifest.db
- log files
- NSSM binary
"""

import subprocess
import sys
from pathlib import Path

import typer

app = typer.Typer(help="Uninstall backup agent Windows service")


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


def remove_service(nssm: Path, service_name: str) -> bool:
    """Remove the Windows service."""
    cmd = [str(nssm), "remove", service_name, "confirm"]
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
    nssm_path: str | None = typer.Option(None, "--nssm-path", help="Path to nssm.exe"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show what would be done"),
):
    """Uninstall backup agent Windows service."""
    typer.echo("=" * 50)
    typer.echo("Backup Agent — Uninstall Service")
    typer.echo("=" * 50)

    nssm = find_nssm(nssm_path)
    if not nssm:
        typer.echo("\nERROR: NSSM not found.")
        typer.echo("Specify path with --nssm-path")
        raise typer.Exit(1)

    typer.echo(f"\nFound NSSM: {nssm}")

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
    if not stop_service(nssm, service_name):
        typer.echo("\n  Warning: Service may not have been running")

    typer.echo(f"\n[2/2] Removing service '{service_name}'...")
    if not remove_service(nssm, service_name):
        raise typer.Exit(1)

    typer.echo("\nService uninstalled successfully")
    typer.echo("\nNote: The following were NOT deleted:")
    typer.echo("  - config.yaml")
    typer.echo("  - manifest.db")
    typer.echo("  - Log files")
    typer.echo("  - NSSM binary")


if __name__ == "__main__":
    app()
