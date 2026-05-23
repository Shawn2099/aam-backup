"""Wake-on-LAN module — SMB reachability check and magic packet sending."""

import platform
import subprocess
import time
import socket

import typer
from loguru import logger
from wakeonlan import send_magic_packet as wol_send

from models.config_model import AppConfig


class WolError(Exception):
    """Base exception for WoL operations."""
    pass


class WolTimeout(WolError):
    """Raised when the server does not respond within the timeout."""
    pass


def _smb_port_open(server_ip: str, port: int = 445, timeout: float = 5.0) -> bool:
    """Check SMB port via TCP connect.

    More reliable than ping — TCP SYN proves the host and service are alive.
    No proxy-ARP false positives, no auth needed.
    """
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((server_ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def ping_host(ip: str, timeout: int = 5) -> bool:
    """Ping a host and return True if reachable.

    Uses the system ping command with a timeout.
    Cross-platform compatible.

    Args:
        ip: IPv4 address to ping.
        timeout: Seconds to wait for response.

    Returns:
        True if host responds to ping.
    """
    is_windows = platform.system().lower() == "windows"
    param = "-n" if is_windows else "-c"
    
    # Windows ping timeout (-w) is in milliseconds, Linux (-W) is in seconds
    if is_windows:
        command = ["ping", param, "1", "-w", str(timeout * 1000), ip]
    else:
        command = ["ping", param, "1", "-W", str(timeout), ip]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=timeout + 5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def send_magic_packet(mac_address: str, server_ip: str = "255.255.255.255", port: int = 9) -> None:
    """Send a Wake-on-LAN magic packet using the wakeonlan library.

    Args:
        mac_address: MAC address in XX:XX:XX:XX:XX:XX format.
        server_ip: Broadcast IP address (default: 255.255.255.255).
        port: UDP port (default: 9).
    """
    try:
        wol_send(mac_address, ip_address=server_ip, port=port)
        logger.info(f"WoL magic packet sent to {mac_address}")
    except Exception as e:
        raise WolError(f"Failed to send WoL packet: {e}")


def _derive_broadcast(ip: str) -> str:
    """Always use global broadcast for WoL — most reliable across subnets."""
    return "255.255.255.255"


def ensure_server_online(config: AppConfig) -> bool:
    """Ensure the backup server is online, using WoL if needed.

    Flow:
    1. If WoL is disabled, assume server is online.
    2. Ping the server. If responsive, return True.
    3. If not responsive, send WoL magic packet.
    4. Poll with ping until server responds or timeout.
    5. Wait stability buffer after server responds.

    Args:
        config: Validated application configuration.

    Returns:
        True if server is online.

    Raises:
        WolTimeout: If server does not respond within timeout.
    """
    wol_config = config.wol

    if not wol_config.enabled:
        logger.debug("WoL disabled, assuming server is online")
        return True

    server_ip = wol_config.server_ip

    # SMB port check — confirms the actual server is up with file services ready
    if _smb_port_open(server_ip):
        logger.info(f"Backup server {server_ip} SMB port accessible")
        return True

    logger.info(f"Backup server {server_ip} offline, sending WoL...")
    send_magic_packet(wol_config.mac_address, "255.255.255.255")

    start_time = time.time()
    while time.time() - start_time < wol_config.wake_timeout_seconds:
        time.sleep(wol_config.ping_interval_seconds)
        if _smb_port_open(server_ip):
            logger.info(f"Backup server {server_ip} SMB port accessible after WoL")
            logger.debug(f"Waiting {wol_config.stability_wait_seconds}s for stability")
            time.sleep(wol_config.stability_wait_seconds)
            return True

    raise WolTimeout(
        f"Backup server {server_ip} SMB port not accessible within "
        f"{wol_config.wake_timeout_seconds}s after WoL"
    )


# --- CLI for testing WoL ---
app = typer.Typer(help="Wake-on-LAN utilities")


@app.command()
def ping(
    ip: str = typer.Argument(..., help="IP address to ping"),
    timeout: int = typer.Option(5, "--timeout", "-t", help="Timeout in seconds"),
):
    """Ping a host and report if it's reachable."""
    if ping_host(ip, timeout):
        typer.echo(f"[PASS] {ip} is reachable")
    else:
        typer.echo(f"[FAIL] {ip} is not reachable")
        raise typer.Exit(1)


@app.command()
def wol(
    mac: str = typer.Argument(..., help="MAC address (XX:XX:XX:XX:XX:XX)"),
    ip: str = typer.Option("255.255.255.255", "--ip", "-i", help="Broadcast IP"),
    port: int = typer.Option(9, "--port", "-p", help="UDP port"),
):
    """Send a Wake-on-LAN magic packet."""
    typer.echo(f"Sending WoL packet to {mac} via {ip}:{port}")
    send_magic_packet(mac, ip, port)
    typer.echo("[OK] Packet sent")


if __name__ == "__main__":
    app()
