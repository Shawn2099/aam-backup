"""Comprehensive pre-flight checks before backup execution.

Covers system health, storage, network, credentials, services, VSS, GCS,
configuration, database, security, binaries, and previous run analysis.
All checks are independent — one failure doesn't stop others.
"""

import platform
import shutil
import socket
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore[assignment]

try:
    import ntplib  # type: ignore[import-not-found]
except ImportError:
    ntplib = None  # type: ignore[assignment]

from loguru import logger


class Severity(str, Enum):
    """Severity levels for pre-flight check results."""
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    SKIP = "SKIP"


@dataclass
class CheckResult:
    """Result of a single pre-flight check."""
    category: str
    name: str
    severity: Severity
    message: str
    details: str = ""
    metric: Optional[float] = None
    threshold: Optional[float] = None

    @property
    def passed(self) -> bool:
        return self.severity in (Severity.PASS, Severity.SKIP, Severity.WARN)

    @property
    def is_warning(self) -> bool:
        return self.severity == Severity.WARN

    @property
    def is_failure(self) -> bool:
        return self.severity == Severity.FAIL


@dataclass
class PreflightReport:
    """Aggregated report from all pre-flight checks."""
    checks: list[CheckResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0

    @property
    def all_passed(self) -> bool:
        """True if no critical checks failed (warnings allowed)."""
        return not any(c.is_failure for c in self.checks)

    @property
    def has_warnings(self) -> bool:
        return any(c.is_warning for c in self.checks)

    @property
    def failures(self) -> list[CheckResult]:
        return [c for c in self.checks if c.is_failure]

    @property
    def warnings(self) -> list[CheckResult]:
        return [c for c in self.checks if c.is_warning]

    @property
    def skipped(self) -> list[CheckResult]:
        return [c for c in self.checks if c.severity == Severity.SKIP]

    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            "=" * 60,
            "Pre-Flight Check Report",
            f"Started: {self.started_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Duration: {self.duration_seconds:.1f}s",
            "=" * 60,
        ]

        # Group by category
        categories: dict[str, list[CheckResult]] = {}
        for check in self.checks:
            categories.setdefault(check.category, []).append(check)

        for category, checks in sorted(categories.items()):
            lines.append(f"\n[{category}]")
            for check in checks:
                status = check.severity.value
                line = f"  [{status}] {check.name}: {check.message}"
                if check.details:
                    line += f"\n         {check.details}"
                if check.metric is not None and check.threshold is not None:
                    line += f" ({check.metric:.1f} / {check.threshold:.1f})"
                lines.append(line)

        lines.append("\n" + "=" * 60)
        passed = sum(1 for c in self.checks if c.severity == Severity.PASS)
        warned = len(self.warnings)
        failed = len(self.failures)
        skipped = len(self.skipped)
        lines.append(f"Results: {passed} passed, {warned} warnings, {failed} failed, {skipped} skipped")

        if self.all_passed:
            lines.append("Status: READY TO PROCEED")
        else:
            lines.append("Status: BLOCKED — fix failures before running backup")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Convert report to dictionary for logging/UI."""
        return {
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "all_passed": self.all_passed,
            "has_warnings": self.has_warnings,
            "total_checks": len(self.checks),
            "passed": sum(1 for c in self.checks if c.severity == Severity.PASS),
            "warnings": len(self.warnings),
            "failures": len(self.failures),
            "skipped": len(self.skipped),
            "checks": [
                {
                    "category": c.category,
                    "name": c.name,
                    "severity": c.severity.value,
                    "message": c.message,
                    "details": c.details,
                }
                for c in self.checks
            ],
        }


# ─── System Health Checks ───────────────────────────────────────────────

def check_disk_space(path: str, min_free_gb: float = 10.0) -> CheckResult:
    """Check available disk space on a path."""
    try:
        usage = shutil.disk_usage(str(path))
        free_gb = usage.free / (1024 ** 3)
        total_gb = usage.total / (1024 ** 3)
        used_pct = (usage.used / usage.total) * 100

        if free_gb < min_free_gb:
            return CheckResult(
                category="System",
                name=f"Disk Space ({path})",
                severity=Severity.FAIL,
                message=f"Only {free_gb:.1f}GB free (minimum: {min_free_gb:.1f}GB)",
                metric=free_gb,
                threshold=min_free_gb,
            )

        # Warn if less than 20% free
        if used_pct > 80:
            return CheckResult(
                category="System",
                name=f"Disk Space ({path})",
                severity=Severity.WARN,
                message=f"{free_gb:.1f}GB free ({used_pct:.0f}% used) — space running low",
                metric=free_gb,
                threshold=min_free_gb,
            )

        return CheckResult(
            category="System",
            name=f"Disk Space ({path})",
            severity=Severity.PASS,
            message=f"{free_gb:.1f}GB free of {total_gb:.1f}GB ({used_pct:.0f}% used)",
            metric=free_gb,
            threshold=min_free_gb,
        )
    except Exception as e:
        return CheckResult(
            category="System",
            name=f"Disk Space ({path})",
            severity=Severity.FAIL,
            message=f"Cannot check disk space: {e}",
        )


def check_time_sync(max_drift_seconds: float = 300.0) -> CheckResult:
    """Check if system clock is reasonably synchronized."""
    try:
        local_time = time.time()

        if ntplib is None:
            return CheckResult(
                category="System",
                name="Time Sync",
                severity=Severity.WARN,
                message="Cannot verify time sync (ntplib not installed)",
                details="Install ntplib: pip install ntplib",
            )

        try:
            client = ntplib.NTPClient()
            response = client.request("pool.ntp.org", version=3, timeout=5)
            drift = abs(local_time - response.tx_time)
        except Exception:
            return CheckResult(
                category="System",
                name="Time Sync",
                severity=Severity.WARN,
                message="Cannot verify time sync (NTP request failed)",
                details="Install ntplib: pip install ntplib",
            )

        if drift > max_drift_seconds:
            return CheckResult(
                category="System",
                name="Time Sync",
                severity=Severity.WARN,
                message=f"Clock drift: {drift:.0f}s (max: {max_drift_seconds:.0f}s)",
                metric=drift,
                threshold=max_drift_seconds,
            )

        return CheckResult(
            category="System",
            name="Time Sync",
            severity=Severity.PASS,
            message=f"Clock drift: {drift:.1f}s",
            metric=drift,
            threshold=max_drift_seconds,
        )
    except Exception as e:
        return CheckResult(
            category="System",
            name="Time Sync",
            severity=Severity.WARN,
            message=f"Cannot check time sync: {e}",
        )


def check_system_memory(min_free_mb: float = 256.0) -> CheckResult:
    """Check available system memory."""
    if psutil is None:
        return CheckResult(
            category="System",
            name="Memory",
            severity=Severity.SKIP,
            message="psutil not installed — skipping memory check",
        )

    try:
        mem = psutil.virtual_memory()
        free_mb = mem.available / (1024 ** 2)
        total_mb = mem.total / (1024 ** 2)
        used_pct = mem.percent

        if free_mb < min_free_mb:
            return CheckResult(
                category="System",
                name="Memory",
                severity=Severity.WARN,
                message=f"Only {free_mb:.0f}MB free of {total_mb:.0f}MB ({used_pct:.0f}% used)",
                metric=free_mb,
                threshold=min_free_mb,
            )

        return CheckResult(
            category="System",
            name="Memory",
            severity=Severity.PASS,
            message=f"{free_mb:.0f}MB free of {total_mb:.0f}MB ({used_pct:.0f}% used)",
            metric=free_mb,
            threshold=min_free_mb,
        )
    except Exception as e:
        return CheckResult(
            category="System",
            name="Memory",
            severity=Severity.WARN,
            message=f"Cannot check memory: {e}",
        )


# ─── Storage Checks ─────────────────────────────────────────────────────

def check_source_drive(path: str) -> CheckResult:
    """Check that the source drive exists and is readable."""
    try:
        source = Path(path)
        if not source.exists():
            return CheckResult(
                category="Storage",
                name="Source Drive",
                severity=Severity.FAIL,
                message=f"Source drive not found: {path}",
            )

        # Check readability — test a single file instead of loading entire directory
        try:
            _ = next(source.iterdir(), None)
        except PermissionError:
            return CheckResult(
                category="Storage",
                name="Source Drive",
                severity=Severity.FAIL,
                message=f"Source drive exists but not readable: {path}",
            )

        usage = shutil.disk_usage(str(source))
        total_gb = usage.total / (1024 ** 3)
        used_pct = (usage.used / usage.total) * 100

        return CheckResult(
            category="Storage",
            name="Source Drive",
            severity=Severity.PASS,
            message=f"{total_gb:.1f}GB total, {used_pct:.0f}% used",
        )
    except Exception as e:
        return CheckResult(
            category="Storage",
            name="Source Drive",
            severity=Severity.FAIL,
            message=f"Error checking source drive: {e}",
        )


def check_lan_destination(path: str, server_ip: str, min_free_gb: float = 50.0) -> CheckResult:
    """Check LAN destination accessibility and disk space."""
    try:
        # Check network connectivity first
        try:
            socket.gethostbyname(server_ip)
        except socket.gaierror:
            return CheckResult(
                category="Storage",
                name="LAN Destination",
                severity=Severity.FAIL,
                message=f"Cannot resolve hostname: {server_ip}",
            )

        if platform.system() == "Windows":
            dest = Path(path)
            if not dest.exists():
                return CheckResult(
                    category="Storage",
                    name="LAN Destination",
                    severity=Severity.FAIL,
                    message=f"LAN share not accessible: {path}",
                )

            usage = shutil.disk_usage(str(dest))
            free_gb = usage.free / (1024 ** 3)
            total_gb = usage.total / (1024 ** 3)

            if free_gb < min_free_gb:
                return CheckResult(
                    category="Storage",
                    name="LAN Destination",
                    severity=Severity.FAIL,
                    message=f"Only {free_gb:.1f}GB free (minimum: {min_free_gb:.1f}GB)",
                    metric=free_gb,
                    threshold=min_free_gb,
                )

            return CheckResult(
                category="Storage",
                name="LAN Destination",
                severity=Severity.PASS,
                message=f"{free_gb:.1f}GB free of {total_gb:.1f}GB on {path}",
                metric=free_gb,
                threshold=min_free_gb,
            )
        else:
            # Linux dev mode — ping only
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "3", server_ip],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return CheckResult(
                    category="Storage",
                    name="LAN Destination",
                    severity=Severity.PASS,
                    message=f"Server {server_ip} reachable (Linux dev mode)",
                )
            else:
                return CheckResult(
                    category="Storage",
                    name="LAN Destination",
                    severity=Severity.FAIL,
                    message=f"Server {server_ip} not reachable",
                )
    except subprocess.TimeoutExpired:
        return CheckResult(
            category="Storage",
            name="LAN Destination",
            severity=Severity.FAIL,
            message=f"Ping to {server_ip} timed out",
        )
    except Exception as e:
        return CheckResult(
            category="Storage",
            name="LAN Destination",
            severity=Severity.FAIL,
            message=f"Error checking LAN destination: {e}",
        )


def check_lan_destination_capacity(source_path: str, lan_path: str, min_free_gb: float = 50.0) -> CheckResult:
    """GAP #4: Check LAN destination has enough space for source data.

    Compares source drive total size against LAN destination free space
    to ensure there's room for the backup.

    Args:
        source_path: Source drive path.
        lan_path: LAN destination path.
        min_free_gb: Minimum free space to retain after backup.

    Returns:
        CheckResult with capacity assessment.
    """
    try:
        source = Path(source_path)
        lan_dest = Path(lan_path)

        if not source.exists():
            return CheckResult(
                category="Storage",
                name="LAN Capacity",
                severity=Severity.FAIL,
                message=f"Source path not found: {source_path}",
            )

        if not lan_dest.exists():
            return CheckResult(
                category="Storage",
                name="LAN Capacity",
                severity=Severity.FAIL,
                message=f"LAN destination not accessible: {lan_path}",
            )

        # Get source total size and LAN free space
        source_usage = shutil.disk_usage(str(source))
        lan_usage = shutil.disk_usage(str(lan_dest))

        _source_total_gb = source_usage.total / (1024 ** 3)
        source_used_gb = source_usage.used / (1024 ** 3)
        lan_free_gb = lan_usage.free / (1024 ** 3)

        # Check if LAN has enough space for source data plus minimum free space
        required_space_gb = source_used_gb + min_free_gb
        if lan_free_gb < required_space_gb:
            deficit_gb = required_space_gb - lan_free_gb
            return CheckResult(
                category="Storage",
                name="LAN Capacity",
                severity=Severity.FAIL,
                message=(
                    f"LAN destination insufficient space: {lan_free_gb:.1f}GB free, "
                    f"need {required_space_gb:.1f}GB ({source_used_gb:.1f}GB source + "
                    f"{min_free_gb:.1f}GB buffer). Deficit: {deficit_gb:.1f}GB"
                ),
                metric=lan_free_gb,
                threshold=required_space_gb,
            )

        # Warn if less than 20% free after backup
        projected_free_gb = lan_free_gb - source_used_gb
        lan_total_gb = lan_usage.total / (1024 ** 3)
        projected_free_pct = (projected_free_gb / lan_total_gb) * 100

        if projected_free_pct < 20:
            return CheckResult(
                category="Storage",
                name="LAN Capacity",
                severity=Severity.WARN,
                message=(
                    f"LAN destination will have only {projected_free_pct:.0f}% free "
                    f"after backup ({projected_free_gb:.1f}GB)"
                ),
                metric=projected_free_pct,
                threshold=20.0,
            )

        return CheckResult(
            category="Storage",
            name="LAN Capacity",
            severity=Severity.PASS,
            message=(
                f"LAN has sufficient space: {lan_free_gb:.1f}GB free, "
                f"source uses {source_used_gb:.1f}GB, "
                f"{projected_free_gb:.1f}GB will remain ({projected_free_pct:.0f}%)"
            ),
            metric=lan_free_gb,
            threshold=required_space_gb,
        )

    except Exception as e:
        return CheckResult(
            category="Storage",
            name="LAN Capacity",
            severity=Severity.WARN,
            message=f"Cannot check LAN capacity: {e}",
        )


def check_temp_directory(path: str) -> CheckResult:
    """Check that the temp directory exists and has space."""
    try:
        temp = Path(path)
        temp.mkdir(parents=True, exist_ok=True)

        usage = shutil.disk_usage(str(temp))
        free_gb = usage.free / (1024 ** 3)

        if free_gb < 1.0:
            return CheckResult(
                category="Storage",
                name="Temp Directory",
                severity=Severity.FAIL,
                message=f"Only {free_gb:.1f}GB free in temp directory",
            )

        return CheckResult(
            category="Storage",
            name="Temp Directory",
            severity=Severity.PASS,
            message=f"{free_gb:.1f}GB free",
        )
    except Exception as e:
        return CheckResult(
            category="Storage",
            name="Temp Directory",
            severity=Severity.FAIL,
            message=f"Temp directory not writable: {e}",
        )


# ─── Network Checks ─────────────────────────────────────────────────────

def check_dns_resolution(hostname: str) -> CheckResult:
    """Check that a hostname can be resolved."""
    try:
        ip = socket.gethostbyname(hostname)
        return CheckResult(
            category="Network",
            name=f"DNS ({hostname})",
            severity=Severity.PASS,
            message=f"Resolved to {ip}",
        )
    except socket.gaierror:
        return CheckResult(
            category="Network",
            name=f"DNS ({hostname})",
            severity=Severity.FAIL,
            message=f"Cannot resolve: {hostname}",
        )


def check_port_connectivity(host: str, port: int, timeout: float = 5.0) -> CheckResult:
    """Check that a port is open on a host."""
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return CheckResult(
            category="Network",
            name=f"Port ({host}:{port})",
            severity=Severity.PASS,
            message=f"Port {port} open",
        )
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        return CheckResult(
            category="Network",
            name=f"Port ({host}:{port})",
            severity=Severity.FAIL,
            message=f"Port {port} not reachable: {e}",
        )


def check_ping(host: str, count: int = 3, timeout: float = 10.0) -> CheckResult:
    """Check connectivity via ping."""
    try:
        if platform.system() == "Windows":
            cmd = ["ping", "-n", str(count), "-w", "3000", host]
        else:
            cmd = ["ping", "-c", str(count), "-W", "3", host]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            # Parse average latency if possible
            avg_ms = None
            for line in result.stdout.splitlines():
                if "avg" in line.lower() or "average" in line.lower():
                    try:
                        parts = line.split("=")[-1].split("/")
                        avg_ms = float(parts[1])
                    except (IndexError, ValueError):
                        pass
            msg = f"{count}/{count} packets received"
            if avg_ms is not None:
                msg += f", avg latency: {avg_ms:.1f}ms"
            return CheckResult(
                category="Network",
                name=f"Ping ({host})",
                severity=Severity.PASS,
                message=msg,
                metric=avg_ms,
            )
        else:
            return CheckResult(
                category="Network",
                name=f"Ping ({host})",
                severity=Severity.FAIL,
                message=f"Ping failed (exit code: {result.returncode})",
            )
    except subprocess.TimeoutExpired:
        return CheckResult(
            category="Network",
            name=f"Ping ({host})",
            severity=Severity.FAIL,
            message=f"Ping timed out after {timeout}s",
        )
    except Exception as e:
        return CheckResult(
            category="Network",
            name=f"Ping ({host})",
            severity=Severity.FAIL,
            message=f"Ping error: {e}",
        )


# ─── Credential Checks ──────────────────────────────────────────────────

def check_credential_manager(credential_name: str) -> CheckResult:
    """Check that a credential exists in Windows Credential Manager."""
    if platform.system() != "Windows":
        return CheckResult(
            category="Credentials",
            name=f"Credential ({credential_name})",
            severity=Severity.WARN,
            message="Windows Credential Manager not available (Linux dev mode)",
        )

    try:
        import keyring
        cred = keyring.get_password("BackupAgent", credential_name)
        if cred:
            return CheckResult(
                category="Credentials",
                name=f"Credential ({credential_name})",
                severity=Severity.PASS,
                message="Found in Credential Manager",
            )
        else:
            return CheckResult(
                category="Credentials",
                name=f"Credential ({credential_name})",
                severity=Severity.FAIL,
                message="Not found in Credential Manager",
            )
    except ImportError:
        return CheckResult(
            category="Credentials",
            name=f"Credential ({credential_name})",
            severity=Severity.FAIL,
            message="keyring package not installed",
        )
    except Exception as e:
        return CheckResult(
            category="Credentials",
            name=f"Credential ({credential_name})",
            severity=Severity.FAIL,
            message=f"Error accessing Credential Manager: {e}",
        )


def check_smtp_config(config: dict) -> CheckResult:
    """Check SMTP configuration completeness."""
    smtp_host = config.get("smtp_host", "")
    smtp_port = config.get("smtp_port", 587)
    smtp_username = config.get("smtp_username", "")
    sender = config.get("sender", "")
    recipients = config.get("recipients", [])

    missing = []
    if not smtp_host:
        missing.append("smtp_host")
    if not smtp_username:
        missing.append("smtp_username")
    if not sender:
        missing.append("sender")
    if not recipients:
        missing.append("recipients")

    if missing:
        return CheckResult(
            category="Credentials",
            name="SMTP Config",
            severity=Severity.WARN,
            message=f"SMTP not fully configured: {', '.join(missing)}",
            details="Email notifications will not work until configured",
        )

    # Test SMTP connectivity
    try:
        import smtplib
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        server.ehlo()
        if smtp_port == 587:
            server.starttls()
        server.quit()
        return CheckResult(
            category="Credentials",
            name="SMTP Config",
            severity=Severity.PASS,
            message=f"SMTP server reachable at {smtp_host}:{smtp_port}",
        )
    except Exception as e:
        return CheckResult(
            category="Credentials",
            name="SMTP Config",
            severity=Severity.WARN,
            message=f"SMTP server not reachable: {e}",
        )


# ─── Service Checks ─────────────────────────────────────────────────────

def check_vss_service() -> CheckResult:
    """Check that VSS service is running (Windows only)."""
    if platform.system() != "Windows":
        return CheckResult(
            category="Services",
            name="VSS Service",
            severity=Severity.SKIP,
            message="VSS not available on Linux",
        )

    try:
        result = subprocess.run(
            ["sc", "query", "vss"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if "RUNNING" in result.stdout:
            return CheckResult(
                category="Services",
                name="VSS Service",
                severity=Severity.PASS,
                message="VSS service running",
            )
        else:
            return CheckResult(
                category="Services",
                name="VSS Service",
                severity=Severity.WARN,
                message="VSS service not running",
                details="VSS shadow copies will not work until service is started",
            )
    except Exception as e:
        return CheckResult(
            category="Services",
            name="VSS Service",
            severity=Severity.WARN,
            message=f"Cannot check VSS service: {e}",
        )


def check_prefect_worker(prefect_api_url: str) -> CheckResult:
    """Check that Prefect API is reachable."""
    try:
        import urllib.request
        url = f"{prefect_api_url}/health"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return CheckResult(
                    category="Services",
                    name="Prefect API",
                    severity=Severity.PASS,
                    message=f"Prefect API healthy at {prefect_api_url}",
                )
    except Exception:
        pass

    # Fallback: check if port is open
    try:
        from urllib.parse import urlparse
        parsed = urlparse(prefect_api_url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 4200

        sock = socket.create_connection((host, port), timeout=5)
        sock.close()
        return CheckResult(
            category="Services",
            name="Prefect API",
            severity=Severity.PASS,
            message=f"Prefect port {port} open",
        )
    except Exception as e:
        return CheckResult(
            category="Services",
            name="Prefect API",
            severity=Severity.WARN,
            message=f"Prefect API not reachable: {e}",
        )


# ─── GCS Checks ─────────────────────────────────────────────────────────

def check_gcs_key_path(key_path: str) -> CheckResult:
    """Check that the GCS service account key file exists and is valid JSON."""
    if not key_path:
        return CheckResult(
            category="Cloud",
            name="GCS Key File",
            severity=Severity.FAIL,
            message="GCS key path not configured",
        )

    key_file = Path(key_path)
    if not key_file.exists():
        return CheckResult(
            category="Cloud",
            name="GCS Key File",
            severity=Severity.FAIL,
            message=f"Key file not found: {key_path}",
        )

    # Validate JSON structure
    try:
        import json
        with open(key_file) as f:
            data = json.load(f)
        if "type" not in data or data.get("type") != "service_account":
            return CheckResult(
                category="Cloud",
                name="GCS Key File",
                severity=Severity.FAIL,
                message="Key file is not a valid GCS service account JSON",
            )
        project_id = data.get("project_id", "unknown")
        return CheckResult(
            category="Cloud",
            name="GCS Key File",
            severity=Severity.PASS,
            message=f"Valid key for project: {project_id}",
        )
    except json.JSONDecodeError as e:
        return CheckResult(
            category="Cloud",
            name="GCS Key File",
            severity=Severity.FAIL,
            message=f"Key file is not valid JSON: {e}",
        )
    except Exception as e:
        return CheckResult(
            category="Cloud",
            name="GCS Key File",
            severity=Severity.FAIL,
            message=f"Error reading key file: {e}",
        )


def check_gcs_connectivity(bucket: str) -> CheckResult:
    """Check GCS bucket connectivity via rclone (read + write)."""
    if not bucket:
        return CheckResult(
            category="Cloud",
            name="GCS Bucket",
            severity=Severity.FAIL,
            message="No bucket configured",
        )

    try:
        # Check read access
        result = subprocess.run(
            ["rclone", "lsd", f"{bucket}:", "--max-depth", "1"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return CheckResult(
                category="Cloud",
                name="GCS Bucket",
                severity=Severity.FAIL,
                message=f"Bucket access failed: {result.stderr.strip()}",
            )

        # Check write access — create and delete a test file
        import tempfile
        test_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".preflight", delete=False
        )
        test_file.write("preflight check")
        test_file.close()
        test_path = Path(test_file.name)

        try:
            # Upload test file
            upload = subprocess.run(
                ["rclone", "copyto", str(test_path), f"{bucket}:_preflight_test.txt"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if upload.returncode != 0:
                return CheckResult(
                    category="Cloud",
                    name="GCS Bucket",
                    severity=Severity.FAIL,
                    message=f"Bucket not writable: {upload.stderr.strip()}",
                )

            # Delete test file
            subprocess.run(
                ["rclone", "deletefile", f"{bucket}:_preflight_test.txt"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            return CheckResult(
                category="Cloud",
                name="GCS Bucket",
                severity=Severity.PASS,
                message=f"Bucket {bucket} accessible (read + write verified)",
            )

        finally:
            if test_path.exists():
                test_path.unlink()

    except FileNotFoundError:
        return CheckResult(
            category="Cloud",
            name="GCS Bucket",
            severity=Severity.FAIL,
            message="rclone not found in PATH",
        )
    except subprocess.TimeoutExpired:
        return CheckResult(
            category="Cloud",
            name="GCS Bucket",
            severity=Severity.FAIL,
            message="Connection timed out",
        )
    except Exception as e:
        return CheckResult(
            category="Cloud",
            name="GCS Bucket",
            severity=Severity.FAIL,
            message=f"Error checking GCS: {e}",
        )


def check_gcs_versioning(bucket: str) -> CheckResult:
    """Check that GCS versioning is enabled on the bucket."""
    if not bucket:
        return CheckResult(
            category="Cloud",
            name="GCS Versioning",
            severity=Severity.SKIP,
            message="No bucket configured",
        )

    try:
        result = subprocess.run(
            ["rclone", "backend", "versioning", f"{bucket}:"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and "Enabled" in result.stdout:
            return CheckResult(
                category="Cloud",
                name="GCS Versioning",
                severity=Severity.PASS,
                message="Versioning enabled",
            )
        else:
            return CheckResult(
                category="Cloud",
                name="GCS Versioning",
                severity=Severity.WARN,
                message="Versioning not enabled or cannot be checked",
                details="Run: gsutil versioning set on gs://BUCKET",
            )
    except Exception:
        return CheckResult(
            category="Cloud",
            name="GCS Versioning",
            severity=Severity.WARN,
            message="Cannot check versioning status",
        )


def check_rclone_version() -> CheckResult:
    """Check rclone version is recent enough."""
    try:
        result = subprocess.run(
            ["rclone", "version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            # Parse version from output
            version_line = result.stdout.splitlines()[0] if result.stdout else ""
            return CheckResult(
                category="Cloud",
                name="Rclone Version",
                severity=Severity.PASS,
                message=version_line,
            )
        else:
            return CheckResult(
                category="Cloud",
                name="Rclone Version",
                severity=Severity.FAIL,
                message="rclone version command failed",
            )
    except FileNotFoundError:
        return CheckResult(
            category="Cloud",
            name="Rclone Version",
            severity=Severity.FAIL,
            message="rclone not found in PATH",
        )
    except Exception as e:
        return CheckResult(
            category="Cloud",
            name="Rclone Version",
            severity=Severity.FAIL,
            message=f"Error checking rclone version: {e}",
        )


# ─── Configuration Checks ───────────────────────────────────────────────

def check_config_completeness(config: dict) -> list[CheckResult]:
    """Check that all required config values are set."""
    results = []

    # Check for placeholder/empty values
    placeholders = {
        "wol.mac_address": config.get("wol", {}).get("mac_address", ""),
        "cloud_backup.bucket": config.get("cloud_backup", {}).get("bucket", ""),
        "notifications.smtp_host": config.get("notifications", {}).get("smtp_host", ""),
        "notifications.smtp_username": config.get("notifications", {}).get("smtp_username", ""),
        "notifications.sender": config.get("notifications", {}).get("sender", ""),
    }

    for key, value in placeholders.items():
        if not value:
            results.append(CheckResult(
                category="Configuration",
                name=f"Config: {key}",
                severity=Severity.WARN,
                message=f"Empty placeholder value for {key}",
            ))

    # Check exclude folders reference valid paths
    exclude_folders = config.get("backup_scope", {}).get("exclude_folders", [])
    for folder in exclude_folders:
        if not Path(folder).exists() and platform.system() == "Windows":
            results.append(CheckResult(
                category="Configuration",
                name=f"Exclude: {folder}",
                severity=Severity.WARN,
                message=f"Exclude folder does not exist: {folder}",
            ))

    return results


# ─── Database Checks ────────────────────────────────────────────────────

def check_database(db_path: str) -> CheckResult:
    """Check that the database directory is writable and schema is valid."""
    try:
        db = Path(db_path)
        db.parent.mkdir(parents=True, exist_ok=True)

        # Check write permission
        test_file = db.parent / ".preflight_test"
        test_file.touch()
        test_file.unlink()

        # If database exists, check schema
        if db.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(str(db))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                if "manifest" not in tables:
                    return CheckResult(
                        category="Database",
                        name="Manifest DB",
                        severity=Severity.WARN,
                        message="Database exists but manifest table missing",
                        details="Table will be created on first run",
                    )

                # Check row count
                cursor.execute("SELECT COUNT(*) FROM manifest")
                row_count = cursor.fetchone()[0]
                conn.close()

                return CheckResult(
                    category="Database",
                    name="Manifest DB",
                    severity=Severity.PASS,
                    message=f"{row_count} files tracked",
                    metric=float(row_count),
                )
            except Exception as e:
                return CheckResult(
                    category="Database",
                    name="Manifest DB",
                    severity=Severity.WARN,
                    message=f"Database schema check failed: {e}",
                )

        return CheckResult(
            category="Database",
            name="Manifest DB",
            severity=Severity.PASS,
            message="Directory writable, database will be created",
        )
    except Exception as e:
        return CheckResult(
            category="Database",
            name="Manifest DB",
            severity=Severity.FAIL,
            message=f"Database directory not writable: {e}",
        )


def check_log_directory(log_path: str) -> CheckResult:
    """Check that the log directory is writable."""
    try:
        log_dir = Path(log_path)
        log_dir.mkdir(parents=True, exist_ok=True)

        test_file = log_dir / ".preflight_test"
        test_file.touch()
        test_file.unlink()

        return CheckResult(
            category="Database",
            name="Log Directory",
            severity=Severity.PASS,
            message=f"Directory writable: {log_dir}",
        )
    except Exception as e:
        return CheckResult(
            category="Database",
            name="Log Directory",
            severity=Severity.FAIL,
            message=f"Log directory not writable: {e}",
        )


# ─── Binary Checks ──────────────────────────────────────────────────────

def check_binaries(cloud_enabled: bool = False) -> list[CheckResult]:
    """Check that required binaries are available with versions."""
    results = []

    # Robocopy (Windows only)
    if platform.system() == "Windows":
        robocopy_path = shutil.which("robocopy")
        if robocopy_path:
            results.append(CheckResult(
                category="Binaries",
                name="Robocopy",
                severity=Severity.PASS,
                message=f"Found at {robocopy_path}",
            ))
        else:
            results.append(CheckResult(
                category="Binaries",
                name="Robocopy",
                severity=Severity.FAIL,
                message="Not found in PATH",
            ))
    else:
        results.append(CheckResult(
            category="Binaries",
            name="Robocopy",
            severity=Severity.SKIP,
            message="Skipped (Linux dev mode)",
        ))

    # Rclone (only if cloud backup enabled)
    if cloud_enabled:
        rclone_path = shutil.which("rclone")
        if rclone_path:
            results.append(CheckResult(
                category="Binaries",
                name="Rclone",
                severity=Severity.PASS,
                message=f"Found at {rclone_path}",
            ))
        else:
            results.append(CheckResult(
                category="Binaries",
                name="Rclone",
                severity=Severity.FAIL,
                message="Not found in PATH",
            ))
    else:
        results.append(CheckResult(
            category="Binaries",
            name="Rclone",
            severity=Severity.SKIP,
            message="Skipped (cloud backup disabled)",
        ))

    # Python version
    import sys
    results.append(CheckResult(
        category="Binaries",
        name="Python",
        severity=Severity.PASS,
        message=f"{sys.version.split()[0]}",
    ))

    return results


def check_dry_run_lan(
    source_drive: str,
    lan_destination: str,
    exclude_folders: list[str] | None = None,
    exclude_extensions: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
) -> CheckResult:
    """Run robocopy /L (list-only) to preview what would change on LAN.

    Validates exit code — failure means the real run would also fail.
    """
    from core.verify import run_dry_run_lan

    result = run_dry_run_lan(
        source_drive, lan_destination,
        exclude_folders, exclude_extensions, exclude_patterns,
    )

    if result.get("skipped"):
        return CheckResult(
            category="Dry Run",
            name="LAN Preview",
            severity=Severity.SKIP,
            message=f"Skipped ({result.get('reason', 'unknown')})",
        )

    if not result.get("success"):
        return CheckResult(
            category="Dry Run",
            name="LAN Preview",
            severity=Severity.FAIL,
            message=f"Dry run failed (exit code {result.get('exit_code', -1)}): {result.get('error', 'unknown')}",
            details="Real LAN backup would also fail — check destination accessibility and permissions",
        )

    total = result["total"]
    message = (
        f"{total} files would change: "
        f"{result['new']} new, {result['modified']} modified, {result['deleted']} deleted"
    )

    return CheckResult(
        category="Dry Run",
        name="LAN Preview",
        severity=Severity.PASS,
        message=message,
        metric=total,
    )


def check_dry_run_cloud(
    source_drive: str,
    bucket: str,
    remote_path: str,
    gcs_key_path: str,
    gcs_location: str,
    exclude_folders: list[str] | None = None,
    exclude_extensions: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
    bandwidth_limit: str = "10M",
    chunk_size: str = "100M",
    retry_count: int = 3,
) -> CheckResult:
    """Run rclone sync --dry-run to preview what would change on GCS.

    Validates exit code — failure means the real run would also fail.
    """
    from core.verify import run_dry_run_cloud

    result = run_dry_run_cloud(
        source_drive, bucket, remote_path, gcs_key_path, gcs_location,
        exclude_folders, exclude_extensions, exclude_patterns,
        bandwidth_limit, chunk_size, retry_count,
    )

    if not result.get("success"):
        return CheckResult(
            category="Dry Run",
            name="Cloud Preview",
            severity=Severity.FAIL,
            message=f"Dry run failed (exit code {result.get('exit_code', -1)}): {result.get('error', 'unknown')}",
            details="Real cloud backup would also fail — check credentials, bucket, and network",
        )

    total = result["total"]
    message = (
        f"{total} files would change: "
        f"{result['transfers']} transfers, {result['deletes']} deletes"
    )

    return CheckResult(
        category="Dry Run",
        name="Cloud Preview",
        severity=Severity.PASS,
        message=message,
        metric=total,
    )


# ─── Main Runner ────────────────────────────────────────────────────────

def run_preflight_checks(config: dict) -> PreflightReport:
    """Run all pre-flight checks and return a comprehensive report."""
    start_time = time.time()
    logger.info("Running comprehensive pre-flight checks...")

    report = PreflightReport()
    paths = config.get("paths", {})
    wol = config.get("wol", {})
    cloud = config.get("cloud_backup", {})
    notifications = config.get("notifications", {})
    ui = config.get("ui", {})

    # System Health
    report.checks.append(check_system_memory())
    report.checks.append(check_time_sync())

    # Storage
    report.checks.append(check_source_drive(paths.get("source_drive", "")))
    if config.get("lan_backup", {}).get("enabled", False):
        report.checks.append(
            check_lan_destination(
                paths.get("lan_destination", ""),
                wol.get("server_ip", ""),
            )
        )
        # GAP #4: Check LAN destination has enough capacity for source data
        report.checks.append(
            check_lan_destination_capacity(
                paths.get("source_drive", ""),
                paths.get("lan_destination", ""),
                min_free_gb=50.0,
            )
        )
    report.checks.append(check_temp_directory(paths.get("rclone_temp_directory", "")))
    # Use configurable source free space threshold (D-005)
    source_free_gb = config.get("alerts", {}).get("source_free_space_warning_gb", 5.0)
    report.checks.append(check_disk_space(paths.get("source_drive", ""), min_free_gb=float(source_free_gb)))

    # Network
    report.checks.append(check_ping(wol.get("server_ip", "127.0.0.1"), count=2))
    if cloud.get("enabled", False):
        report.checks.append(check_dns_resolution("storage.googleapis.com"))

    # Binaries
    report.checks.extend(check_binaries(cloud.get("enabled", False)))
    if cloud.get("enabled", False):
        report.checks.append(check_rclone_version())

    # Credentials
    report.checks.append(check_credential_manager(config.get("cloud_credentials", {}).get("credential_name", "")))
    report.checks.append(check_smtp_config(notifications))

    # Services
    report.checks.append(check_prefect_worker(ui.get("prefect_api_url", "http://127.0.0.1:4200/api")))
    if config.get("vss", {}).get("enabled", False):
        report.checks.append(check_vss_service())

    # Cloud
    if cloud.get("enabled", False):
        # Validate GCS key file before connectivity check
        from core.config_loader import load_config
        try:
            _ = load_config(Path(__file__).parent.parent / "config.yaml")
            gcs_key_path = None
            # Try to get key path from credential manager
            try:
                import keyring
                cred_name = config.get("cloud_credentials", {}).get("credential_name", "BackupAgent_GCS")
                gcs_key_path = keyring.get_password("BackupAgent", cred_name)
            except Exception:
                pass
            if gcs_key_path:
                report.checks.append(check_gcs_key_path(gcs_key_path))
        except Exception:
            pass

        report.checks.append(check_gcs_connectivity(cloud.get("bucket", "")))
        report.checks.append(check_gcs_versioning(cloud.get("bucket", "")))

    # Configuration
    report.checks.extend(check_config_completeness(config))

    # Database
    report.checks.append(check_database(paths.get("database_path", "")))
    report.checks.append(check_log_directory(paths.get("log_directory", "")))

    # Dry Run Previews (D-006: same flags as real runs + exit code validation)
    scope = config.get("backup_scope", {})
    exclude_folders = scope.get("exclude_folders", [])
    exclude_extensions = scope.get("exclude_extensions", [])
    exclude_patterns = scope.get("exclude_patterns", [])

    if config.get("lan_backup", {}).get("enabled", False):
        report.checks.append(check_dry_run_lan(
            paths.get("source_drive", ""),
            paths.get("lan_destination", ""),
            exclude_folders,
            exclude_extensions,
            exclude_patterns,
        ))
    if cloud.get("enabled", False):
        gcs_key_path = None
        try:
            import keyring
            cred_name = config.get("cloud_credentials", {}).get("credential_name", "BackupAgent_GCS")
            gcs_key_path = keyring.get_password("BackupAgent", cred_name)
        except Exception:
            pass
        if gcs_key_path:
            report.checks.append(check_dry_run_cloud(
                paths.get("source_drive", ""),
                cloud.get("bucket", ""),
                cloud.get("remote_path", ""),
                gcs_key_path,
                cloud.get("gcs_location", "asia-south1"),
                exclude_folders,
                exclude_extensions,
                exclude_patterns,
                cloud.get("bandwidth_limit", "10M"),
                cloud.get("chunk_size", "100M"),
                cloud.get("retry_count", 3),
            ))

    # Finalize report
    report.completed_at = datetime.now(timezone.utc)
    report.duration_seconds = time.time() - start_time

    # Log results
    logger.info(report.summary())

    if not report.all_passed:
        logger.error(f"Pre-flight checks failed: {[f.name for f in report.failures]}")
    elif report.has_warnings:
        logger.warning("Pre-flight checks passed with warnings")
    else:
        logger.info("All pre-flight checks passed")

    return report
