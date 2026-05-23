"""Prefect task to shutdown the backup server after LAN backup."""

from prefect import task
from prefect.logging import get_run_logger
import subprocess


@task(
    name="shutdown-backup-server",
    tags=["post-backup"],
    task_run_name="shutdown-backup-server",
)
def shutdown_server_task(config: dict) -> dict:
    """Shutdown the remote backup server after successful LAN backup.

    Only runs if lan_backup.shutdown_after_backup is enabled.
    Sends shutdown /s /t 300 /f to the backup server, giving staff
    5 minutes to cancel with shutdown /a before power-off.

    Args:
        config: AppConfig model_dump() dict.

    Returns:
        dict with result status.
    """
    logger = get_run_logger()
    lan = config.get("lan_backup", {})
    wol = config.get("wol", {})
    server_ip = wol.get("server_ip", "")

    if not lan.get("shutdown_after_backup", False):
        logger.info("Server shutdown disabled in config, skipping")
        return {"shutdown_initiated": False, "server_ip": server_ip}

    if not server_ip:
        logger.warning("No server_ip configured, cannot send shutdown")
        return {"shutdown_initiated": False, "server_ip": "", "error": "No server_ip configured"}

    try:
        cmd = [
            "shutdown", "/s",
            "/m", f"\\\\{server_ip}",
            "/t", "300",
            "/f",
            "/c", "Backup complete — server shutting down in 5 minutes",
        ]
        logger.info(f"Initiating shutdown of {server_ip}: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            logger.info(f"Shutdown command sent to {server_ip} (5-minute delay)")
            return {"shutdown_initiated": True, "server_ip": server_ip}
        else:
            logger.warning(
                f"Shutdown command failed (exit {result.returncode}): {result.stderr.strip()}"
            )
            return {
                "shutdown_initiated": False,
                "server_ip": server_ip,
                "exit_code": result.returncode,
                "error": result.stderr.strip(),
            }

    except subprocess.TimeoutExpired:
        logger.error(f"Shutdown command timed out for {server_ip}")
        return {"shutdown_initiated": False, "server_ip": server_ip, "error": "Timeout"}
    except FileNotFoundError:
        logger.error("shutdown.exe not found — not a Windows system?")
        return {"shutdown_initiated": False, "server_ip": server_ip, "error": "shutdown.exe not found"}
    except Exception as e:
        logger.error(f"Unexpected error during shutdown: {e}")
        return {"shutdown_initiated": False, "server_ip": server_ip, "error": str(e)}
