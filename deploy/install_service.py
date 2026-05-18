"""Install the backup agent as a Windows service using Servy.

Usage:
    uv run deploy/install_service.py [--config config.yaml] [--servy-path servy.exe]

Creates a Windows service named 'BackupAgent' that:
- Runs the Prefect worker
- Starts automatically on boot
- Restarts on failure
- Logs to C:\\BackupAgent\\logs\\ with rotation
"""

import subprocess
import sys
from pathlib import Path

import typer
import yaml

app = typer.Typer(help="Install backup agent as Windows service")


def load_config(config_path: Path) -> dict:
    """Load config.yaml."""
    with open(config_path) as f:
        return yaml.safe_load(f)


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


def install_service(
    servy: Path,
    service_name: str,
    python_exe: Path,
    work_dir: Path,
    config_path: Path,
    log_dir: Path,
) -> bool:
    """Install the Windows service using Servy."""
    log_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(servy),
        "create",
        service_name,
        "--command", str(python_exe),
        "--args", "-m prefect worker start --pool default --type process",
        "--working-directory", str(work_dir),
        "--log-file", str(log_dir / "backup_agent.log"),
        "--log-rotate",
        "--log-max-size-mb", "50",
        "--log-max-files", "5",
        "--restart-on-failure",
        "--restart-delay-seconds", "5",
        "--start-mode", "automatic",
        "--env", f"BACKUP_CONFIG_PATH={config_path}",
    ]

    typer.echo(f"  Installing service: {service_name}")
    typer.echo(f"  Servy: {servy}")
    typer.echo(f"  Python: {python_exe}")
    typer.echo(f"  Working directory: {work_dir}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            typer.echo(f"  Install failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        typer.echo(f"  Install error: {e}")
        return False

    typer.echo(f"  Service '{service_name}' installed successfully")
    return True


def start_service(servy: Path, service_name: str) -> bool:
    """Start the Windows service."""
    cmd = [str(servy), "start", service_name]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            typer.echo(f"  Service '{service_name}' started")
            return True
        else:
            typer.echo(f"  Start failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        typer.echo(f"  Start error: {e}")
        return False


@app.command()
def install(
    config: Path = typer.Option(Path("config.yaml"), "--config", "-c", help="Path to config.yaml"),
    servy_path: str | None = typer.Option(None, "--servy-path", help="Path to servy.exe"),
    service_name: str = typer.Option("BackupAgent", "--service-name", help="Service name"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show what would be done"),
):
    """Install backup agent as Windows service."""
    typer.echo("=" * 50)
    typer.echo("Backup Agent — Install Service")
    typer.echo("=" * 50)

    loaded = load_config(config)
    log_dir = Path(loaded.get("paths", {}).get("log_directory", "C:\\BackupAgent\\logs"))

    servy = find_servy(servy_path)
    if not servy:
        typer.echo("\nERROR: Servy not found.")
        typer.echo("Download from: https://github.com/aliostad/Servy/releases")
        raise typer.Exit(1)

    typer.echo(f"\nFound Servy: {servy}")

    python_exe = Path(sys.executable)
    work_dir = Path(__file__).parent.parent.resolve()

    if dry_run:
        typer.echo(f"\n  Would install service: {service_name}")
        typer.echo(f"  Python: {python_exe}")
        typer.echo(f"  Working directory: {work_dir}")
        typer.echo(f"  Log directory: {log_dir}")
        return

    if sys.platform != "win32":
        typer.echo("\nERROR: This script requires Windows.")
        raise typer.Exit(1)

    typer.echo("\n[1/2] Installing service...")
    if not install_service(servy, service_name, python_exe, work_dir, config, log_dir):
        raise typer.Exit(1)

    typer.echo("\n[2/2] Starting service...")
    if not start_service(servy, service_name):
        raise typer.Exit(1)

    typer.echo("\nService installed and running")


if __name__ == "__main__":
    app()
