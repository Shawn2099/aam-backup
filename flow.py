"""Prefect flow: nightly backup orchestration."""

import os
import smtplib
import keyring
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from prefect import flow
from prefect.logging import get_run_logger
from prefect.tasks import exponential_backoff
from prefect.task_runners import ThreadPoolTaskRunner

from core.config_loader import load_config
from core.logging_setup import configure_logging
from tasks.cloud_task import cloud_backup_task
from tasks.config_task import load_config_task
from tasks.lan_task import lan_backup_task
from tasks.manifest_backup_task import backup_manifest_db_task
from tasks.preflight_task import preflight_task
from tasks.scan_task import scan_task
from tasks.verification_task import verify_cloud_integrity_task


def _send_failure_email(config_path: str, flow_run_id: str, error_message: str):
    """Send failure notification email using SMTP config from config.yaml."""
    try:
        config = load_config(config_path)
        notif = config.notifications

        if not notif.smtp_host or not notif.sender or not notif.recipients:
            return  # Email not configured

        # Retrieve SMTP password from Credential Manager
        smtp_password = keyring.get_password("BackupAgent", notif.smtp_password_credential)
        if not smtp_password:
            return  # Credential not found

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"❌ Backup Failed — {config.firm.name}"
        msg["From"] = notif.sender
        msg["To"] = ", ".join(notif.recipients)

        body_text = (
            f"Backup Failure Notification\n"
            f"{'=' * 40}\n\n"
            f"Firm: {config.firm.name}\n"
            f"Flow Run ID: {flow_run_id}\n"
            f"Error: {error_message}\n\n"
            f"Check Prefect UI for full details.\n"
        )

        body_html = f"""
        <html><body>
        <h2 style="color: red;">Backup Failure Notification</h2>
        <table>
            <tr><td><strong>Firm:</strong></td><td>{config.firm.name}</td></tr>
            <tr><td><strong>Flow Run ID:</strong></td><td>{flow_run_id}</td></tr>
            <tr><td><strong>Error:</strong></td><td><code>{error_message}</code></td></tr>
        </table>
        <p>Check Prefect UI for full details.</p>
        </body></html>
        """

        msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(notif.smtp_host, notif.smtp_port) as server:
            server.starttls()
            server.login(notif.smtp_username, smtp_password)
            server.sendmail(notif.sender, notif.recipients, msg.as_string())

    except Exception as e:
        # Log but don't fail the hook — email is best-effort
        try:
            logger = get_run_logger()
            logger.error(f"Failed to send failure email: {e}")
        except Exception:
            pass


def _on_backup_failure(flow_obj, flow_run, state):
    """Hook called when the backup flow fails."""
    logger = get_run_logger()
    logger.critical(
        f"Backup flow FAILED: {state.message}. "
        f"Run ID: {flow_run.id}. "
        f"Check Prefect UI for details."
    )

    # Send email notification (best-effort)
    config_path = flow_run.parameters.get("config_path", "config.yaml")
    _send_failure_email(config_path, str(flow_run.id), state.message or "Unknown error")


def _on_backup_completion(flow_obj, flow_run, state):
    """Hook called when the backup flow completes successfully."""
    logger = get_run_logger()
    logger.info(f"Backup flow completed successfully. Run ID: {flow_run.id}")


@flow(
    name="nightly-backup",
    flow_run_name="backup-{config_path}",
    task_runner=ThreadPoolTaskRunner(max_workers=2),
    log_prints=True,
    version="1.1.0",
    timeout_seconds=28800,  # 8 hours max
    retries=1,
    retry_delay_seconds=300,  # 5 minutes
    on_failure=[_on_backup_failure],
    on_completion=[_on_backup_completion],
)
def nightly_backup(config_path: str = "config.yaml") -> str:
    """Execute the nightly backup flow.

    Flow:
    1. Load and validate configuration
    2. Run pre-flight checks
    3. Scan source drive for changes
    4. If changes detected: run LAN and cloud backup concurrently
    5. Compute overall status

    Args:
        config_path: Path to config.yaml. Defaults to "config.yaml".

    Returns:
        Overall status: COMPLETE, PARTIAL_FAILURE, or FAILED.
    """
    logger = get_run_logger()

    # Configure logging
    log_dir = Path(os.environ.get("BACKUP_LOG_DIR", "logs"))
    configure_logging(log_dir)

    # Task 1: Load configuration
    config, gcs_key_path = load_config_task(config_path)

    # Task 2: Pre-flight checks
    config = preflight_task(config.model_dump())

    # Task 3: Scan drive
    scan_result = scan_task(config, config.paths.database_path)

    logger.info(
        f"Scan complete: {len(scan_result.new_files)} new, "
        f"{len(scan_result.modified_files)} modified, "
        f"{len(scan_result.deleted_files)} deleted, "
        f"{scan_result.unchanged_count} unchanged"
    )

    if not scan_result.has_changes:
        logger.info("No changes detected — backup complete")
        return "COMPLETE"

    # Tasks 4 & 5: Concurrent LAN and cloud backup
    lan_future = lan_backup_task.submit(config, scan_result, config.paths.database_path)
    cloud_future = cloud_backup_task.submit(
        config, gcs_key_path, scan_result, config.paths.database_path
    )

    lan_result = lan_future.result()
    cloud_result = cloud_future.result()

    # Compute overall status
    lan_status = lan_result.get("status", "LAN_FAILED")
    cloud_status = cloud_result.get("status", "CLOUD_FAILED")

    if lan_status in ("LAN_COMPLETE", "LAN_PARTIAL") and cloud_status in (
        "CLOUD_COMPLETE",
        "CLOUD_PARTIAL",
    ):
        overall = "COMPLETE"
    elif lan_status == "LAN_SKIPPED" and cloud_status in ("CLOUD_COMPLETE", "CLOUD_PARTIAL"):
        overall = "COMPLETE"
    elif cloud_status == "CLOUD_SKIPPED" and lan_status in ("LAN_COMPLETE", "LAN_PARTIAL"):
        overall = "COMPLETE"
    elif lan_status in ("LAN_COMPLETE", "LAN_PARTIAL", "LAN_SKIPPED") or cloud_status in (
        "CLOUD_COMPLETE",
        "CLOUD_PARTIAL",
        "CLOUD_SKIPPED",
    ):
        overall = "PARTIAL_FAILURE"
    else:
        overall = "FAILED"

    logger.info(
        f"Backup complete — LAN: {lan_status}, Cloud: {cloud_status}, Overall: {overall}"
    )

    if overall == "FAILED":
        raise RuntimeError(f"Both backup destinations failed: LAN={lan_status}, Cloud={cloud_status}")

    # Backup manifest.db after successful backup
    try:
        backup_manifest_db_task(
            config.paths.database_path,
            config.paths.lan_destination,
            config.cloud_backup.enabled,
        )
    except Exception as e:
        logger.warning(f"manifest.db backup failed (non-critical): {e}")

    # Verify cloud integrity after successful cloud backup
    if cloud_status in ("CLOUD_COMPLETE", "CLOUD_PARTIAL"):
        try:
            verify_result = verify_cloud_integrity_task(config, gcs_key_path)
            if verify_result.get("status") == "MISMATCH":
                logger.warning(
                    f"Cloud integrity check found mismatches: "
                    f"{verify_result.get('mismatches', 0)} mismatches, "
                    f"{verify_result.get('missing', 0)} missing"
                )
            else:
                logger.info(f"Cloud integrity check passed: {verify_result.get('matches', 0)} files verified")
        except Exception as e:
            logger.warning(f"Cloud integrity verification failed (non-critical): {e}")

    return overall


if __name__ == "__main__":
    nightly_backup.deploy(
        name="nightly-backup-production",
        work_pool_name="default",
        cron="0 23 * * *",
        parameters={"config_path": "config.yaml"},
        tags=["production", "backup", "aam-associates"],
        description="Nightly backup of D:\\ drive to LAN and GCS",
    )
