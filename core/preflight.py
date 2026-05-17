"""Pre-flight checks before backup execution.

Runs before the backup flow starts to catch problems early.
All checks are independent — one failure doesn't stop others.
"""

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger


@dataclass
class CheckResult:
    """Result of a single pre-flight check."""
    name: str
    passed: bool
    message: str
    warning: bool = False


@dataclass
class PreflightReport:
    """Aggregated report from all pre-flight checks."""
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        """True if all critical checks passed (warnings allowed)."""
        return all(c.passed for c in self.checks)

    @property
    def has_warnings(self) -> bool:
        """True if any checks have warnings."""
        return any(c.warning for c in self.checks)

    @property
    def failures(self) -> list[CheckResult]:
        """List of failed checks."""
        return [c for c in self.checks if not c.passed]

    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = ["=" * 50, "Pre-Flight Check Results", "=" * 50]
        for check in self.checks:
            status = "PASS" if check.passed else "FAIL"
            if check.warning:
                status = "WARN"
            lines.append(f"  [{status}] {check.name}: {check.message}")

        lines.append("=" * 50)
        if self.all_passed:
            lines.append("All checks passed")
        else:
            lines.append(f"{len(self.failures)} check(s) failed")
        return "\n".join(lines)


def check_source_drive(path: str) -> CheckResult:
    """Check that the source drive exists and is readable."""
    try:
        source = Path(path)
        if not source.exists():
            return CheckResult(
                name="Source Drive",
                passed=False,
                message=f"Source drive not found: {path}",
            )

        # Get disk usage
        usage = shutil.disk_usage(str(source))
        free_gb = usage.free / (1024 ** 3)
        total_gb = usage.total / (1024 ** 3)
        used_pct = (usage.used / usage.total) * 100

        return CheckResult(
            name="Source Drive",
            passed=True,
            message=f"{total_gb:.1f}GB total, {free_gb:.1f}GB free ({used_pct:.0f}% used)",
        )
    except Exception as e:
        return CheckResult(
            name="Source Drive",
            passed=False,
            message=f"Error checking source drive: {e}",
        )


def check_lan_destination(path: str, server_ip: str) -> CheckResult:
    """Check LAN destination accessibility and disk space."""
    try:
        # On Windows, try to access the share
        import platform
        if platform.system() == "Windows":
            dest = Path(path)
            if not dest.exists():
                return CheckResult(
                    name="LAN Destination",
                    passed=False,
                    message=f"LAN share not accessible: {path}",
                )

            usage = shutil.disk_usage(str(dest))
            free_gb = usage.free / (1024 ** 3)
            return CheckResult(
                name="LAN Destination",
                passed=True,
                message=f"{free_gb:.1f}GB free on {path}",
            )
        else:
            # On Linux, just ping the server
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "3", server_ip],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return CheckResult(
                    name="LAN Destination",
                    passed=True,
                    message=f"Server {server_ip} reachable (Linux dev mode)",
                )
            else:
                return CheckResult(
                    name="LAN Destination",
                    passed=False,
                    message=f"Server {server_ip} not reachable",
                )
    except subprocess.TimeoutExpired:
        return CheckResult(
            name="LAN Destination",
            passed=False,
            message=f"Ping to {server_ip} timed out",
        )
    except Exception as e:
        return CheckResult(
            name="LAN Destination",
            passed=False,
            message=f"Error checking LAN destination: {e}",
        )


def check_gcs_connectivity(bucket: str) -> CheckResult:
    """Check GCS bucket connectivity via rclone."""
    if not bucket:
        return CheckResult(
            name="GCS Bucket",
            passed=False,
            message="No bucket configured",
        )

    try:
        result = subprocess.run(
            ["rclone", "lsd", f"{bucket}:", "--max-depth", "1"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return CheckResult(
                name="GCS Bucket",
                passed=True,
                message=f"Bucket {bucket} accessible",
            )
        else:
            return CheckResult(
                name="GCS Bucket",
                passed=False,
                message=f"Bucket access failed: {result.stderr.strip()}",
            )
    except FileNotFoundError:
        return CheckResult(
            name="GCS Bucket",
            passed=False,
            message="rclone not found in PATH",
        )
    except subprocess.TimeoutExpired:
        return CheckResult(
            name="GCS Bucket",
            passed=False,
            message="Connection timed out",
        )
    except Exception as e:
        return CheckResult(
            name="GCS Bucket",
            passed=False,
            message=f"Error checking GCS: {e}",
        )


def check_binaries() -> list[CheckResult]:
    """Check that required binaries are available."""
    results = []

    # Robocopy (Windows only)
    import platform
    if platform.system() == "Windows":
        if shutil.which("robocopy"):
            results.append(CheckResult(
                name="Robocopy",
                passed=True,
                message="Found in PATH",
            ))
        else:
            results.append(CheckResult(
                name="Robocopy",
                passed=False,
                message="Not found in PATH",
            ))
    else:
        results.append(CheckResult(
            name="Robocopy",
            passed=True,
            message="Skipped (Linux dev mode)",
            warning=True,
        ))

    # Rclone
    if shutil.which("rclone"):
        results.append(CheckResult(
            name="Rclone",
            passed=True,
            message="Found in PATH",
        ))
    else:
        results.append(CheckResult(
            name="Rclone",
            passed=False,
            message="Not found in PATH",
        ))

    return results


def check_database(db_path: str) -> CheckResult:
    """Check that the database directory is writable."""
    try:
        db = Path(db_path)
        db.parent.mkdir(parents=True, exist_ok=True)

        # Check if we can write to the directory
        test_file = db.parent / ".preflight_test"
        test_file.touch()
        test_file.unlink()

        return CheckResult(
            name="Database",
            passed=True,
            message=f"Directory writable: {db.parent}",
        )
    except Exception as e:
        return CheckResult(
            name="Database",
            passed=False,
            message=f"Database directory not writable: {e}",
        )


def check_log_directory(log_path: str) -> CheckResult:
    """Check that the log directory is writable."""
    try:
        log_dir = Path(log_path)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Check if we can write to the directory
        test_file = log_dir / ".preflight_test"
        test_file.touch()
        test_file.unlink()

        return CheckResult(
            name="Log Directory",
            passed=True,
            message=f"Directory writable: {log_dir}",
        )
    except Exception as e:
        return CheckResult(
            name="Log Directory",
            passed=False,
            message=f"Log directory not writable: {e}",
        )


def run_preflight_checks(config: dict) -> PreflightReport:
    """Run all pre-flight checks and return a report."""
    logger.info("Running pre-flight checks...")

    report = PreflightReport()
    paths = config.get("paths", {})
    wol = config.get("wol", {})
    cloud = config.get("cloud_backup", {})

    # Source drive
    report.checks.append(check_source_drive(paths.get("source_drive", "")))

    # LAN destination
    if config.get("lan_backup", {}).get("enabled", False):
        report.checks.append(
            check_lan_destination(
                paths.get("lan_destination", ""),
                wol.get("server_ip", ""),
            )
        )

    # GCS bucket
    if cloud.get("enabled", False):
        report.checks.append(check_gcs_connectivity(cloud.get("bucket", "")))

    # Binaries
    report.checks.extend(check_binaries())

    # Database
    report.checks.append(check_database(paths.get("database_path", "")))

    # Log directory
    report.checks.append(check_log_directory(paths.get("log_directory", "")))

    # Log results
    logger.info(report.summary())

    if not report.all_passed:
        logger.error(f"Pre-flight checks failed: {[f.name for f in report.failures]}")
    elif report.has_warnings:
        logger.warning("Pre-flight checks passed with warnings")
    else:
        logger.info("All pre-flight checks passed")

    return report
