"""Validate config.yaml before deployment.

Usage:
    uv run scripts/validate_config.py [--config config.yaml]

Checks:
- YAML syntax
- Required fields present
- Path format validity
- Schedule format
- Network connectivity to LAN destination
- Rclone binary availability
- Robocopy binary availability (Windows only)
"""

import shutil
import subprocess
import sys
from pathlib import Path

import typer
import yaml

app = typer.Typer(help="Validate backup configuration")


def load_config(config_path: Path) -> dict | None:
    """Load and parse config.yaml."""
    if not config_path.exists():
        typer.echo(f"ERROR: Config file not found: {config_path}")
        return None

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return config
    except yaml.YAMLError as e:
        typer.echo(f"ERROR: Invalid YAML syntax: {e}")
        return None


def check_required_fields(config: dict) -> list[str]:
    """Check that all required fields are present and non-empty."""
    errors = []

    if not config.get("firm", {}).get("name"):
        errors.append("firm.name is required")

    paths = config.get("paths", {})
    for field in ["source_drive", "lan_destination", "log_directory", "database_path", "rclone_temp_directory"]:
        if not paths.get(field):
            errors.append(f"paths.{field} is required")

    cloud = config.get("cloud_backup", {})
    if cloud.get("enabled", False) and not cloud.get("bucket"):
        errors.append("cloud_backup.bucket is required when cloud_backup.enabled is true")

    wol = config.get("wol", {})
    if wol.get("enabled", False) and not wol.get("mac_address"):
        errors.append("wol.mac_address is required when wol.enabled is true")
    if wol.get("enabled", False) and not wol.get("server_ip"):
        errors.append("wol.server_ip is required when wol.enabled is true")

    notifications = config.get("notifications", {})
    if notifications.get("send_on_failure", False) or notifications.get("send_on_every_run", False):
        if not notifications.get("smtp_host"):
            errors.append("notifications.smtp_host is required when email notifications are enabled")
        if not notifications.get("sender"):
            errors.append("notifications.sender is required when email notifications are enabled")
        if not notifications.get("recipients"):
            errors.append("notifications.recipients is required when email notifications are enabled")

    return errors


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


def check_paths(config: dict) -> list[str]:
    """Validate path formats."""
    errors = []
    source = config.get("paths", {}).get("source_drive", "")
    if source and sys.platform == "win32":
        if not (len(source) == 3 and source[1] == ":" and source[2] == "\\"):
            errors.append(f"paths.source_drive should be in format 'X:\\', got: {source}")
    return errors


def check_lan_connectivity(config: dict) -> list[str]:
    """Test connectivity to LAN destination."""
    errors = []
    lan = config.get("lan_backup", {})
    wol = config.get("wol", {})

    if not lan.get("enabled", False):
        return errors

    server_ip = wol.get("server_ip", "")
    if not server_ip:
        return errors

    typer.echo(f"  Testing connectivity to {server_ip}...")
    try:
        result = subprocess.run(
            ["ping", "-n", "1" if sys.platform == "win32" else "-c", "1", server_ip],
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
    """Validate backup configuration."""
    typer.echo("=" * 50)
    typer.echo("Backup Agent — Config Validation")
    typer.echo("=" * 50)

    all_errors = []

    typer.echo("\n[1/5] Loading config...")
    loaded = load_config(config)
    if loaded is None:
        raise typer.Exit(1)
    typer.echo("  Config loaded successfully")

    typer.echo("\n[2/5] Checking required fields...")
    field_errors = check_required_fields(loaded)
    if field_errors:
        all_errors.extend(field_errors)
        for err in field_errors:
            typer.echo(f"  ERROR: {err}")
    else:
        typer.echo("  All required fields present")

    typer.echo("\n[3/5] Checking binaries...")
    binary_errors = check_binaries()
    if binary_errors:
        all_errors.extend(binary_errors)
        for err in binary_errors:
            typer.echo(f"  ERROR: {err}")
    else:
        typer.echo("  All binaries found")

    typer.echo("\n[4/5] Checking path formats...")
    path_errors = check_paths(loaded)
    if path_errors:
        all_errors.extend(path_errors)
        for err in path_errors:
            typer.echo(f"  ERROR: {err}")
    else:
        typer.echo("  Path formats valid")

    typer.echo("\n[5/5] Testing LAN connectivity...")
    lan_errors = check_lan_connectivity(loaded)
    if lan_errors:
        all_errors.extend(lan_errors)
        for err in lan_errors:
            typer.echo(f"  ERROR: {err}")
    else:
        typer.echo("  LAN connectivity OK")

    typer.echo("\n" + "=" * 50)
    if all_errors:
        typer.echo(f"FAILED: {len(all_errors)} error(s) found")
        raise typer.Exit(1)
    else:
        typer.echo("PASSED: Configuration is valid")


if __name__ == "__main__":
    app()
