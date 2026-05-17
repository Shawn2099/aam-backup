"""Install the backup agent as a Windows service using NSSM.

Usage:
    uv run deploy/install_service.py [--config config.yaml] [--nssm-path nssm.exe]

Creates a Windows service named 'BackupAgent' that:
- Runs the Prefect worker
- Starts automatically on boot
- Restarts on failure
- Logs to C:\\BackupAgent\\logs\\service.log
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


def install_service(
    nssm: Path,
    service_name: str,
    python_exe: Path,
    work_dir: Path,
    config_path: Path,
    log_dir: Path,
) -> bool:
    """Install the Windows service using NSSM."""
    log_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(nssm),
        "install",
        service_name,
        str(python_exe),
        "-m",
        "prefect",
        "worker",
        "start",
        "--pool",
        "default",
        "--type",
        "process",
    ]

    typer.echo(f"  Installing service: {service_name}")
    typer.echo(f"  NSSM: {nssm}")
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

    settings = [
        ("AppDirectory", str(work_dir)),
        ("AppEnvironmentExtra", f"BACKUP_CONFIG_PATH={config_path}"),
        ("Stdout", str(log_dir / "service.log")),
        ("Stderr", str(log_dir / "service_error.log")),
        ("Start", "SERVICE_AUTO_START"),
        ("AppRestartDelay", "5000"),
        ("AppExit", "Default", "Restart"),
        ("AppExit", "0", "Exit"),
        ("AppExit", "1", "Restart"),
    ]

    for setting in settings:
        set_cmd = [str(nssm), "set", service_name] + list(setting)
        try:
            subprocess.run(set_cmd, capture_output=True, text=True, timeout=10)
        except Exception as e:
            typer.echo(f"  Warning: Failed to set {setting[0]}: {e}")

    typer.echo(f"  Service '{service_name}' installed successfully")
    return True


def start_service(nssm: Path, service_name: str) -> bool:
    """Start the Windows service."""
    cmd = [str(nssm), "start", service_name]
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
    nssm_path: str | None = typer.Option(None, "--nssm-path", help="Path to nssm.exe"),
    service_name: str = typer.Option("BackupAgent", "--service-name", help="Service name"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show what would be done"),
):
    """Install backup agent as Windows service."""
    typer.echo("=" * 50)
    typer.echo("Backup Agent — Install Service")
    typer.echo("=" * 50)

    loaded = load_config(config)
    log_dir = Path(loaded.get("paths", {}).get("log_directory", "C:\\BackupAgent\\logs"))

    nssm = find_nssm(nssm_path)
    if not nssm:
        typer.echo("\nERROR: NSSM not found.")
        typer.echo("Download from: https://nssm.cc/download")
        raise typer.Exit(1)

    typer.echo(f"\nFound NSSM: {nssm}")

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
    if not install_service(nssm, service_name, python_exe, work_dir, config, log_dir):
        raise typer.Exit(1)

    typer.echo("\n[2/2] Starting service...")
    if not start_service(nssm, service_name):
        raise typer.Exit(1)

    typer.echo("\nService installed and running")


if __name__ == "__main__":
    app()
