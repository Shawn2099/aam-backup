"""Restore files from backup destinations.

Supports restoring from LAN (Robocopy reverse) or GCS (Rclone).
Can restore specific files, folders, or entire drive.

Usage:
    uv run scripts/restore.py list --source lan
    uv run scripts/restore.py restore --source lan --path "WINMAN/data.mdb"
    uv run scripts/restore.py restore --source gcs --path "WINMAN/" --dest "D:\Restored"
    uv run scripts/restore.py restore --source lan --full --dest "D:\Restored"
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
import yaml

app = typer.Typer(help="Restore files from backup destinations")


def _load_config() -> dict:
    """Load config.yaml."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def _get_gcs_key_path(config: dict) -> Optional[str]:
    """Get GCS key path from Credential Manager or config."""
    try:
        import keyring
        cred_name = config.get("cloud_credentials", {}).get("credential_name", "BackupAgent_GCS")
        return keyring.get_password("BackupAgent", cred_name)
    except Exception:
        return None


@app.command()
def list(
    source: str = typer.Option("lan", "--source", help="Backup source: lan or gcs"),
    path: str = typer.Option("", "--path", help="List specific path (empty = root)"),
    depth: int = typer.Option(1, "--depth", help="Directory depth to list"),
):
    """List files available in backup destination."""
    config = _load_config()

    if source == "lan":
        lan_dest = config["paths"]["lan_destination"]
        target = Path(lan_dest) / path if path else Path(lan_dest)

        if not target.exists():
            typer.echo(f"Error: LAN destination not accessible: {target}")
            raise typer.Exit(1)

        typer.echo(f"Listing: {target}")
        for i, item in enumerate(target.rglob("*")):
            if item.is_file():
                rel = item.relative_to(target)
                if len(rel.parts) <= depth:
                    typer.echo(f"  FILE  {rel} ({item.stat().st_size:,} bytes)")
            elif item.is_dir():
                rel = item.relative_to(target)
                if len(rel.parts) <= depth:
                    typer.echo(f"  DIR   {rel}/")

    elif source == "gcs":
        bucket = config["cloud_backup"]["bucket"]
        remote_path = config["cloud_backup"]["remote_path"]
        gcs_key = _get_gcs_key_path(config)

        if not gcs_key:
            typer.echo("Error: GCS key not found in Credential Manager")
            raise typer.Exit(1)

        prefix = f"{remote_path}/{path}" if path else remote_path
        cmd = [
            "rclone", "ls",
            f"gcs_backup:{bucket}/{prefix}",
            "--config", "/dev/null",  # Will write temp config
            "--max-depth", str(depth),
        ]

        typer.echo(f"Listing: gs://{bucket}/{prefix}")
        typer.echo("(Requires GCS credentials — run on server with Credential Manager configured)")
        typer.echo(f"Command: {' '.join(cmd)}")

    else:
        typer.echo(f"Error: Unknown source '{source}'. Use 'lan' or 'gcs'.")
        raise typer.Exit(1)


@app.command()
def restore(
    source: str = typer.Option("lan", "--source", help="Backup source: lan or gcs"),
    path: str = typer.Option("", "--path", help="Specific file/folder to restore (empty = full)"),
    dest: str = typer.Option("", "--dest", help="Destination path (default: original location)"),
    full: bool = typer.Option(False, "--full", help="Restore entire backup"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be restored"),
):
    """Restore files from backup destination."""
    config = _load_config()

    if full and path:
        typer.echo("Error: Use --full OR --path, not both")
        raise typer.Exit(1)

    if source == "lan":
        _restore_from_lan(config, path, dest, full, dry_run)
    elif source == "gcs":
        _restore_from_gcs(config, path, dest, full, dry_run)
    else:
        typer.echo(f"Error: Unknown source '{source}'. Use 'lan' or 'gcs'.")
        raise typer.Exit(1)


def _restore_from_lan(config: dict, path: str, dest: str, full: bool, dry_run: bool):
    """Restore from LAN backup using Robocopy."""
    lan_dest = config["paths"]["lan_destination"]
    source_drive = config["paths"]["source_drive"]

    if full:
        src = lan_dest
        dst = dest if dest else source_drive
    elif path:
        src = str(Path(lan_dest) / path)
        dst = dest if dest else str(Path(source_drive) / path)
    else:
        typer.echo("Error: Specify --path or --full")
        raise typer.Exit(1)

    if not Path(src).exists():
        typer.echo(f"Error: Source not found in LAN backup: {src}")
        raise typer.Exit(1)

    cmd = [
        "robocopy",
        src,
        dst,
        "/E",  # Copy subdirectories including empty
        "/Z",  # Restartable mode
        "/XJ",  # Exclude junction points
        "/R:3",  # 3 retries
        "/W:5",  # 5 second wait
        "/NP",  # No progress
        "/TEE",  # Output to console + log
    ]

    if dry_run:
        cmd.append("/L")  # List only
        typer.echo("[DRY RUN] Would restore:")

    typer.echo(f"Restoring: {src} → {dst}")
    typer.echo(f"Command: {' '.join(cmd[:4])}...")

    if not dry_run:
        result = subprocess.run(cmd, capture_output=True, text=True)
        typer.echo(result.stdout)
        if result.returncode > 7:
            typer.echo(f"Restore failed with exit code: {result.returncode}")
            raise typer.Exit(1)
        else:
            typer.echo("Restore complete")


def _restore_from_gcs(config: dict, path: str, dest: str, full: bool, dry_run: bool):
    """Restore from GCS backup using Rclone."""
    bucket = config["cloud_backup"]["bucket"]
    remote_path = config["cloud_backup"]["remote_path"]
    gcs_key = _get_gcs_key_path(config)

    if not gcs_key:
        typer.echo("Error: GCS key not found in Credential Manager")
        raise typer.Exit(1)

    if full:
        remote_prefix = remote_path
        dst = dest if dest else config["paths"]["source_drive"]
    elif path:
        remote_prefix = f"{remote_path}/{path}"
        dst = dest if dest else str(Path(config["paths"]["source_drive"]) / path)
    else:
        typer.echo("Error: Specify --path or --full")
        raise typer.Exit(1)

    # Write temp rclone config
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
        f.write(
            "[gcs_backup]\n"
            "type = google cloud storage\n"
            f"service_account_file = {gcs_key}\n"
            "bucket_policy_only = true\n"
            f"location = {config['cloud_backup']['gcs_location']}\n"
        )
        temp_config = f.name

    cmd = [
        "rclone", "sync",
        f"gcs_backup:{bucket}/{remote_prefix}",
        dst,
        "--config", temp_config,
        "--progress",
    ]

    if dry_run:
        cmd.append("--dry-run")
        typer.echo("[DRY RUN] Would restore:")

    typer.echo(f"Restoring: gs://{bucket}/{remote_prefix} → {dst}")

    if not dry_run:
        result = subprocess.run(cmd, capture_output=True, text=True)
        typer.echo(result.stdout)
        if result.returncode != 0:
            typer.echo(f"Restore failed: {result.stderr}")
            raise typer.Exit(1)
        else:
            typer.echo("Restore complete")

    Path(temp_config).unlink(missing_ok=True)


@app.command()
def verify(
    source: str = typer.Option("lan", "--source", help="Backup source: lan or gcs"),
):
    """Verify backup integrity before restore."""
    config = _load_config()

    if source == "lan":
        lan_dest = Path(config["paths"]["lan_destination"])
        if not lan_dest.exists():
            typer.echo(f"FAIL: LAN destination not accessible: {lan_dest}")
            raise typer.Exit(1)

        file_count = sum(1 for _ in lan_dest.rglob("*") if _.is_file())
        typer.echo(f"LAN backup verified: {file_count:,} files found")

    elif source == "gcs":
        bucket = config["cloud_backup"]["bucket"]
        gcs_key = _get_gcs_key_path(config)

        if not gcs_key:
            typer.echo("FAIL: GCS key not found")
            raise typer.Exit(1)

        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(
                "[gcs_backup]\n"
                "type = google cloud storage\n"
                f"service_account_file = {gcs_key}\n"
                "bucket_policy_only = true\n"
            )
            temp_config = f.name

        result = subprocess.run(
            ["rclone", "lsd", f"gcs_backup:{bucket}:", "--config", temp_config],
            capture_output=True, text=True,
        )
        Path(temp_config).unlink(missing_ok=True)

        if result.returncode == 0:
            typer.echo(f"GCS backup verified: bucket {bucket} accessible")
        else:
            typer.echo(f"FAIL: GCS bucket not accessible: {result.stderr}")
            raise typer.Exit(1)


if __name__ == "__main__":
    app()
