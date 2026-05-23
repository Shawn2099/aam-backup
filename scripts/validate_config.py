"""Validate config.yaml before deployment.

Usage:
    uv run scripts/validate_config.py [--config config.yaml]

Checks:
- YAML syntax and Pydantic validation (all model-level validators)
- Required binaries (robocopy, rclone)
- Network connectivity to LAN destination
"""

import shutil
import subprocess
import sys
from pathlib import Path

import typer
from pydantic import ValidationError

from core.config_loader import load_config as pydantic_load_config, ConfigurationError

app = typer.Typer(help="Validate backup configuration")


def check_binaries() -> list[str]:
    """Check that required binaries are available."""
    errors = []
    if sys.platform == "win32":
        if not shutil.which("robocopy"):
            errors.append("robocopy.exe not found in PATH")
    else:
        typer.echo("  Note: robocopy check skipped (not on Windows)")
    if not shutil.which("rclone"):
        errors.append("rclone not found in PATH")
    return errors


def check_lan_connectivity(server_ip: str) -> list[str]:
    """Test connectivity to LAN destination."""
    errors: list[str] = []
    if not server_ip:
        return errors

    typer.echo(f"  Testing connectivity to {server_ip}...")
    try:
        flag = "-n" if sys.platform == "win32" else "-c"
        result = subprocess.run(
            ["ping", flag, "1", server_ip],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            errors.append(f"Cannot ping LAN server at {server_ip}")
        else:
            typer.echo(f"  LAN server {server_ip} is reachable")
    except subprocess.TimeoutExpired:
        errors.append(f"Ping to {server_ip} timed out")
    except Exception as e:
        errors.append(f"Ping failed: {e}")

    return errors


@app.command()
def validate(
    config: Path = typer.Option(Path("config.yaml"), "--config", "-c", help="Path to config.yaml"),
):
    """Validate backup configuration using Pydantic + connectivity checks."""
    typer.echo("=" * 50)
    typer.echo("Backup Agent — Config Validation")
    typer.echo("=" * 50)

    all_errors = []

    typer.echo("\n[1/4] Validating config.yaml with Pydantic...")
    try:
        appconfig = pydantic_load_config(config)
        typer.echo(f"  Config loaded and validated for firm: {appconfig.firm.name}")
    except (ConfigurationError, ValidationError) as e:
        typer.echo(f"  FAILED: {e}")
        raise typer.Exit(1)

    typer.echo("\n[2/4] Checking binaries...")
    binary_errors = check_binaries()
    if binary_errors:
        all_errors.extend(binary_errors)
        for err in binary_errors:
            typer.echo(f"  ERROR: {err}")
    else:
        typer.echo("  All binaries found")

    typer.echo("\n[3/4] Checking backup destinations...")
    dest_issues = appconfig.validate_backup_destinations()
    if dest_issues:
        for issue in dest_issues:
            all_errors.append(issue)
            typer.echo(f"  ERROR: {issue}")
    else:
        typer.echo("  At least one backup destination enabled")

    typer.echo("\n[4/4] Testing LAN connectivity...")
    if appconfig.lan_backup.enabled:
        lan_errors = check_lan_connectivity(appconfig.wol.server_ip)
        if lan_errors:
            all_errors.extend(lan_errors)
            for err in lan_errors:
                typer.echo(f"  ERROR: {err}")
        else:
            typer.echo("  LAN connectivity OK")
    else:
        typer.echo("  LAN backup disabled, skipping")

    typer.echo("\n" + "=" * 50)
    if all_errors:
        typer.echo(f"FAILED: {len(all_errors)} error(s) found")
        raise typer.Exit(1)
    else:
        typer.echo("PASSED: Configuration is valid")
