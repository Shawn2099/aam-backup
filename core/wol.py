"""Wake-on-LAN module — ping check and magic packet sending."""

import platform
import socket
import struct
import subprocess
import time
from pathlib import Path

from loguru import logger

from models.config_model import AppConfig


class WolError(Exception):
    """Base exception for WoL operations."""
    pass


class WolTimeout(WolError):
    """Raised when the server does not respond within the timeout."""
    pass


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
    param = "-n" if platform.system().lower() == "windows" else "-c"
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
    """Send a Wake-on-LAN magic packet.

    Args:
        mac_address: MAC address in XX:XX:XX:XX:XX:XX format.
        server_ip: Broadcast IP address (default: 255.255.255.255).
        port: UDP port (default: 9, the discard port commonly used for WoL).
    """
    # Parse MAC address
    mac_bytes = bytes.fromhex(mac_address.replace(":", "").replace("-", ""))
    if len(mac_bytes) != 6:
        raise WolError(f"Invalid MAC address: {mac_address}")

    # Magic packet: 6 bytes of 0xFF + 16 repetitions of MAC address
    payload = b"\xff" * 6 + mac_bytes * 16

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        sock.sendto(payload, (server_ip, port))
        logger.info(f"WoL magic packet sent to {mac_address}")
    finally:
        sock.close()


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

    # Initial ping check
    if ping_host(wol_config.server_ip):
        logger.info(f"Backup server {wol_config.server_ip} is already online")
        return True

    logger.info(f"Backup server {wol_config.server_ip} is offline, sending WoL...")
    send_magic_packet(wol_config.mac_address, wol_config.server_ip)

    # Poll until server responds or timeout
    start_time = time.time()
    while time.time() - start_time < wol_config.wake_timeout_seconds:
        time.sleep(wol_config.ping_interval_seconds)
        if ping_host(wol_config.server_ip):
            logger.info(f"Backup server {wol_config.server_ip} responded to ping")
            # Stability buffer — wait for services to fully initialize
            logger.debug(f"Waiting {wol_config.stability_wait_seconds}s for stability")
            time.sleep(wol_config.stability_wait_seconds)
            return True

    raise WolTimeout(
        f"Backup server {wol_config.server_ip} did not respond within "
        f"{wol_config.wake_timeout_seconds}s after WoL"
    )
