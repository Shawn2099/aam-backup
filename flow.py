"""Prefect flow: nightly backup orchestration."""

import os
import smtplib
import time
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
from core.manifest_db import ManifestDB
from tasks.cloud_task import cloud_backup_task
from tasks.config_task import load_config_task
from tasks.config_version_task import version_config_task
from tasks.lan_task import lan_backup_task
from tasks.log_backup_task import backup_logs_cloud_task
from tasks.maintenance_task import maintain_manifest_db_task
from tasks.manifest_backup_task import backup_manifest_db_task
from tasks.manifest_rollback_task import pre_run_manifest_backup_task
from tasks.metrics_task import collect_metrics_task
from tasks.no_run_alert_task import check_backup_not_run_alert_task
from tasks.preflight_task import preflight_task
from tasks.report_task import generate_report_task
from tasks.scan_task import scan_task
from tasks.restore_verify_task import test_restore_task
from tasks.verification_task import verify_cloud_integrity_task
from tasks.vss_task import create_vss_snapshot_task, delete_vss_snapshot_task
from tasks.archive_task import yearly_archive_task


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
        try:
            logger = get_run_logger()
            logger.error(f"Failed to send failure email: {e}")
        except Exception:
            pass


def _send_success_email(config_path: str, flow_run_id: str, status: str, duration: float):
    """Send success notification email using SMTP config from config.yaml."""
    try:
        config = load_config(config_path)
        notif = config.notifications

        if not notif.smtp_host or not notif.sender or not notif.recipients:
            return

        smtp_password = keyring.get_password("BackupAgent", notif.smtp_password_credential)
        if not smtp_password:
            return

        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        duration_str = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"✅ Backup Complete — {config.firm.name}"
        msg["From"] = notif.sender
        msg["To"] = ", ".join(notif.recipients)

        body_text = (
            f"Backup Success Notification\n"
            f"{'=' * 40}\n\n"
            f"Firm: {config.firm.name}\n"
            f"Flow Run ID: {flow_run_id}\n"
            f"Status: {status}\n"
            f"Duration: {duration_str}\n"
        )

        body_html = f"""
        <html><body>
        <h2 style="color: green;">Backup Success Notification</h2>
        <table>
            <tr><td><strong>Firm:</strong></td><td>{config.firm.name}</td></tr>
            <tr><td><strong>Flow Run ID:</strong></td><td>{flow_run_id}</td></tr>
            <tr><td><strong>Status:</strong></td><td>{status}</td></tr>
            <tr><td><strong>Duration:</strong></td><td>{duration_str}</td></tr>
        </table>
        </body></html>
        """

        msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(notif.smtp_host, notif.smtp_port) as server:
            server.starttls()
            server.login(notif.smtp_username, smtp_password)
            server.sendmail(notif.sender, notif.recipients, msg.as_string())

    except Exception as e:
        try:
            logger = get_run_logger()
            logger.error(f"Failed to send success email: {e}")
        except Exception:
            pass


def _get_and_increment_run_counter(log_directory: str) -> int:
    """Get and increment a persistent run counter from a file.

    Returns the current run number (1-based).
    File is created if it doesn't exist.
    """
    counter_file = Path(log_directory) / "run_counter.txt"
    counter_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        current = int(counter_file.read_text().strip())
    except (FileNotFoundError, ValueError):
        current = 0

    counter_file.write_text(str(current + 1))
    return current + 1


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

    config_path = flow_run.parameters.get("config_path", "config.yaml")
    config = load_config(config_path)

    if config.notifications.send_on_every_run:
        try:
            duration = flow_run.total_run_time or 0
            _send_success_email(config_path, str(flow_run.id), "COMPLETE", duration)
        except Exception as e:
            logger.error(f"Failed to send success email: {e}")


def _flow_run_name() -> str:
    """Generate a unique flow run name with timestamp."""
    from datetime import datetime
    return f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


@flow(
    name="nightly-backup",
    flow_run_name=_flow_run_name,
    task_runner=ThreadPoolTaskRunner(max_workers=2),
    log_prints=True,
    version="1.2.0",
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
    2. Create VSS snapshot if enabled
    3. Run pre-flight checks
    4. Scan source drive for changes
    5. If changes detected: run LAN and cloud backup concurrently
    6. Post-backup: manifest backup, integrity check, log sync, metrics
    7. Clean up VSS snapshot (always, even on failure)

    Args:
        config_path: Path to config.yaml. Defaults to "config.yaml".

    Returns:
        Overall status: COMPLETE, PARTIAL_FAILURE, or FAILED.
    """
    logger = get_run_logger()

    start_time = time.time()

    log_dir = Path(os.environ.get("BACKUP_LOG_DIR", "logs"))
    configure_logging(log_dir)

    try:
        # Track VSS state for cleanup (must survive exceptions)
        vss_enabled = False
        vss_device_path = None

        # Task 1: Load configuration
        config, gcs_key_path = load_config_task(config_path)

        # Task 1b: Version config before run
        try:
            version_config_task(config_path, config.paths.log_directory)
        except Exception as e:
            logger.warning(f"Config versioning failed (non-critical): {e}")

        # GAP #2: Pre-run manifest backup for rollback protection
        try:
            rollback_result = pre_run_manifest_backup_task(
                config.paths.database_path,
                config.paths.log_directory,
                max_backups=3,
            )
            if rollback_result.get("status") == "SUCCESS":
                logger.info(
                    f"Pre-run manifest backup created: {rollback_result['backup_path']} "
                    f"({rollback_result['backup_size_bytes']} bytes)"
                )
            else:
                logger.warning(
                    f"Pre-run manifest backup skipped: {rollback_result.get('reason', 'unknown')}"
                )
        except Exception as e:
            logger.warning(f"Pre-run manifest backup failed (non-critical): {e}")

        # GAP #3: Check if backup hasn't run for configured number of days
        try:
            no_run_alert = check_backup_not_run_alert_task(
                config.paths.log_directory,
                config.alerts.backup_not_run_warning_days,
            )
            if no_run_alert.get("status") == "ALERT":
                logger.warning(f"BACKUP NOT RUN ALERT: {no_run_alert['message']}")
                # Send email notification if configured
                if config.notifications.send_on_failure:
                    try:
                        from prefect.context import get_run_context
                        ctx = get_run_context()
                        flow_run_id = str(ctx.flow_run.id) if ctx and ctx.flow_run else "unknown"
                        _send_failure_email(
                            config_path,
                            flow_run_id,
                            f"Backup not run alert: {no_run_alert['message']}",
                        )
                    except Exception as email_err:
                        logger.warning(f"Failed to send no-run alert email: {email_err}")
        except Exception as e:
            logger.warning(f"No-run alert check failed (non-critical): {e}")

        # BUG FIX #5: Pre-backup manifest backup — protects against corruption during this run
        try:
            db = ManifestDB(config.paths.database_path)
            try:
                db.maintenance(max_size_mb=500)
            finally:
                db.close()
            logger.info("Manifest DB maintenance completed before backup")
        except Exception as e:
            logger.warning(f"Pre-backup manifest maintenance failed (non-critical): {e}")

        # Task 1c: Create VSS snapshot if enabled
        if config.vss.enabled:
            vss_result = create_vss_snapshot_task(
                config.vss.drive_letter,
                config.vss.fallback_on_failure,
            )
            vss_device_path = vss_result.get("device_path")
            vss_enabled = vss_result.get("vss_enabled", False)
            if vss_enabled:
                config = config.model_copy(
                    update={
                        "paths": config.paths.model_copy(
                            update={"source_drive": vss_result["source_path"]}
                        )
                    }
                )
                logger.info(f"Using VSS shadow copy as source: {vss_result['source_path']}")
            else:
                logger.info("Using direct source drive (VSS not used)")

        # Task 2: Pre-flight checks
        preflight_result = preflight_task(config.model_dump())
        config_dict = preflight_result["config"]

        # Rebuild config from preflight output
        from models.config_model import AppConfig
        config = AppConfig(**config_dict)

        # BUG FIX #1: Re-apply VSS source path after preflight rebuilds config
        if vss_enabled and vss_device_path:
            config = config.model_copy(
                update={
                    "paths": config.paths.model_copy(
                        update={"source_drive": vss_device_path}
                    )
                }
            )

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

            threshold = config.alerts.no_changes_warning_days
            if threshold > 0:
                from datetime import datetime, timezone, timedelta
                cutoff = datetime.now(timezone.utc) - timedelta(days=threshold)
                cutoff_iso = cutoff.isoformat()

                db = ManifestDB(config.paths.database_path)
                try:
                    all_entries = db.get_all_entries()
                    recent_backup = any(
                        (e.last_backed_up_lan or "") > cutoff_iso or
                        (e.last_backed_up_cloud or "") > cutoff_iso
                        for e in all_entries.values()
                    )
                    if not recent_backup and all_entries:
                        logger.warning(
                            f"No file changes detected in {threshold}+ days. "
                            f"Scanner may be misconfigured or source drive unchanged. "
                            f"Total files in manifest: {len(all_entries)}"
                        )
                finally:
                    db.close()

            # BUG FIX #3: Collect metrics even on "no change" runs
            try:
                duration = time.time() - start_time
                from prefect.context import get_run_context
                ctx = get_run_context()
                flow_run_id = str(ctx.flow_run.id) if ctx and ctx.flow_run else "unknown"

                collect_metrics_task(
                    log_directory=config.paths.log_directory,
                    flow_run_id=flow_run_id,
                    overall_status="COMPLETE",
                    lan_status="LAN_SKIPPED",
                    cloud_status="CLOUD_SKIPPED",
                    scan_new=0,
                    scan_modified=0,
                    scan_deleted=0,
                    scan_unchanged=scan_result.unchanged_count,
                    lan_files_copied=0,
                    lan_bytes_copied=0,
                    lan_files_failed=0,
                    cloud_mismatches=0,
                    cloud_missing=0,
                    duration_seconds=round(duration, 1),
                    total_source_bytes=scan_result.total_source_bytes,
                    total_file_count=scan_result.total_file_count,
                    lan_destination=config.paths.lan_destination,
                )
            except Exception as e:
                logger.warning(f"Metrics collection failed (non-critical): {e}")

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

        # BUG FIX #5: Backup manifest.db to both LAN and cloud
        try:
            backup_manifest_db_task(
                config.paths.database_path,
                config.paths.lan_destination,
                config.cloud_backup.enabled,
                gcs_key_path,
                config.cloud_backup.bucket,
                config.cloud_backup.remote_path,
                config.cloud_backup.gcs_location,
            )
        except Exception as e:
            logger.warning(f"manifest.db backup failed (non-critical): {e}")

        # Verify cloud integrity after successful cloud backup
        cloud_mismatches = 0
        cloud_missing = 0
        if cloud_status in ("CLOUD_COMPLETE", "CLOUD_PARTIAL"):
            try:
                verify_result = verify_cloud_integrity_task(config, gcs_key_path)
                cloud_mismatches = verify_result.get("mismatches", 0)
                cloud_missing = verify_result.get("missing", 0)
                if verify_result.get("status") == "MISMATCH":
                    logger.warning(
                        f"Cloud integrity check found mismatches: "
                        f"{cloud_mismatches} mismatches, "
                        f"{cloud_missing} missing"
                    )
                else:
                    logger.info(f"Cloud integrity check passed: {verify_result.get('matches', 0)} files verified")
            except Exception as e:
                logger.warning(f"Cloud integrity verification failed (non-critical): {e}")

        # Sync log files to cloud for disaster recovery
        try:
            backup_logs_cloud_task(
                config.paths.log_directory,
                gcs_key_path,
                config.cloud_backup.enabled,
                config.cloud_backup.bucket,
                config.cloud_backup.remote_path,
                config.cloud_backup.gcs_location,
            )
        except Exception as e:
            logger.warning(f"Log backup to cloud failed (non-critical): {e}")

        # Collect metrics for trend analysis
        try:
            duration = time.time() - start_time
            from prefect.context import get_run_context
            ctx = get_run_context()
            flow_run_id = str(ctx.flow_run.id) if ctx and ctx.flow_run else "unknown"

            collect_metrics_task(
                log_directory=config.paths.log_directory,
                flow_run_id=flow_run_id,
                overall_status=overall,
                lan_status=lan_status,
                cloud_status=cloud_status,
                scan_new=len(scan_result.new_files),
                scan_modified=len(scan_result.modified_files),
                scan_deleted=len(scan_result.deleted_files),
                scan_unchanged=scan_result.unchanged_count,
                lan_files_copied=lan_result.get("files_copied", 0),
                lan_bytes_copied=lan_result.get("bytes_copied", 0),
                lan_files_failed=lan_result.get("files_failed", 0),
                cloud_mismatches=cloud_mismatches,
                cloud_missing=cloud_missing,
                duration_seconds=round(duration, 1),
                total_source_bytes=scan_result.total_source_bytes,
                total_file_count=scan_result.total_file_count,
                lan_destination=config.paths.lan_destination,
                lan_checksum_verified=lan_result.get("lan_checksum", {}).get("verified", 0),
                lan_checksum_mismatches=lan_result.get("lan_checksum", {}).get("mismatches", 0),
            )
        except Exception as e:
            logger.warning(f"Metrics collection failed (non-critical): {e}")

        # SQLite maintenance: VACUUM, WAL checkpoint, size monitoring
        try:
            maintain_manifest_db_task(config.paths.database_path, max_size_mb=500)
        except Exception as e:
            logger.warning(f"Manifest DB maintenance failed (non-critical): {e}")

        # Check LAN destination free space and warn if approaching capacity
        try:
            import shutil
            lan_free = shutil.disk_usage(config.paths.lan_destination).free
            lan_free_gb = lan_free / (1024 ** 3)
            threshold_gb = config.alerts.lan_free_space_warning_gb
            if lan_free_gb < threshold_gb:
                logger.warning(
                    f"LAN destination low on space: {lan_free_gb:.1f} GB free "
                    f"(threshold: {threshold_gb} GB)"
                )
        except Exception as e:
            logger.debug(f"Could not check LAN disk space: {e}")

        # Check backup duration and warn if unusually slow
        duration_minutes = duration / 60
        duration_threshold = config.alerts.backup_duration_warning_minutes
        if duration_minutes > duration_threshold:
            logger.warning(
                f"Backup run took {duration_minutes:.0f} minutes "
                f"(threshold: {duration_threshold} minutes) — "
                f"check network speed and source drive health"
            )

        # Yearly archive: move previous FY data from active to archive prefix
        if config.cloud_archive.enabled and config.cloud_backup.enabled:
            try:
                from datetime import datetime, timezone
                today = datetime.now(timezone.utc)
                today_md = today.strftime("%m-%d")
                trigger_md = config.cloud_archive.trigger_date

                if today_md >= trigger_md:
                    logger.info(
                        f"Archive trigger date reached ({today_md} >= {trigger_md}) — "
                        f"checking if archive is needed for {today.year}"
                    )
                    archive_result = yearly_archive_task(
                        bucket=config.cloud_backup.bucket,
                        gcs_key_path=gcs_key_path,
                        active_path=config.cloud_archive.active_path,
                        archive_path=config.cloud_archive.archive_path,
                        log_directory=config.paths.log_directory,
                    )
                    if archive_result.get("status") == "SUCCESS":
                        logger.info(
                            f"Yearly archive completed: "
                            f"{archive_result['source']} → {archive_result['destination']}"
                        )
                    elif archive_result.get("status") == "SKIPPED":
                        logger.info(f"Yearly archive skipped: {archive_result.get('reason')}")
                    else:
                        logger.warning(
                            f"Yearly archive failed: {archive_result.get('status')} — "
                            f"{archive_result.get('error', 'unknown')}"
                        )
                else:
                    days_until = (
                        datetime(today.year, int(trigger_md[:2]), int(trigger_md[3:])) - today
                    ).days
                    logger.info(
                        f"Archive not yet due: {days_until} days until trigger date ({trigger_md})"
                    )
            except Exception as e:
                logger.warning(f"Yearly archive check failed (non-critical): {e}")

        # Test restore: verify random files from LAN and GCS
        if config.test_restore.enabled:
            try:
                run_counter = _get_and_increment_run_counter(config.paths.log_directory)
                if run_counter % config.test_restore.run_every_n_backups == 0:
                    logger.info(
                        f"Running test restore verification "
                        f"(every {config.test_restore.run_every_n_backups} runs, "
                        f"sample count: {config.test_restore.sample_count})"
                    )
                    test_restore_task(
                        database_path=config.paths.database_path,
                        source_drive=config.paths.source_drive,
                        lan_destination=config.paths.lan_destination,
                        cloud_enabled=config.cloud_backup.enabled,
                        gcs_key_path=gcs_key_path,
                        cloud_bucket=config.cloud_backup.bucket,
                        cloud_remote_path=config.cloud_backup.remote_path,
                        gcs_location=config.cloud_backup.gcs_location,
                        sample_count=config.test_restore.sample_count,
                    )
                else:
                    logger.info(
                        f"Test restore skipped (run #{run_counter}, "
                        f"next run in {config.test_restore.run_every_n_backups - (run_counter % config.test_restore.run_every_n_backups)} backups)"
                    )
            except Exception as e:
                logger.warning(f"Test restore verification failed (non-critical): {e}")

        # Generate weekly/monthly reports on scheduled days
        try:
            from datetime import datetime, timezone
            today = datetime.now(timezone.utc)
            today_name = today.strftime("%A").lower()

            if config.notifications.weekly_summary_enabled and today_name == config.notifications.weekly_summary_day.lower():
                logger.info(f"Generating weekly backup report ({today_name})")
                smtp_config = {
                    "smtp_host": config.notifications.smtp_host,
                    "smtp_port": config.notifications.smtp_port,
                    "smtp_username": config.notifications.smtp_username,
                    "smtp_password_credential": config.notifications.smtp_password_credential,
                    "sender": config.notifications.sender,
                    "recipients": config.notifications.recipients,
                }
                generate_report_task(
                    log_directory=config.paths.log_directory,
                    report_type="weekly",
                    smtp_config=smtp_config,
                )

            if today.day == 1:
                logger.info("Generating monthly backup report (1st of month)")
                smtp_config = {
                    "smtp_host": config.notifications.smtp_host,
                    "smtp_port": config.notifications.smtp_port,
                    "smtp_username": config.notifications.smtp_username,
                    "smtp_password_credential": config.notifications.smtp_password_credential,
                    "sender": config.notifications.sender,
                    "recipients": config.notifications.recipients,
                }
                generate_report_task(
                    log_directory=config.paths.log_directory,
                    report_type="monthly",
                    smtp_config=smtp_config,
                )
        except Exception as e:
            logger.warning(f"Report generation failed (non-critical): {e}")

        # Backup config.yaml to LAN and cloud destinations
        try:
            from tasks.config_backup_task import backup_config_task
            backup_config_task(
                config_path=config_path,
                lan_destination=config.paths.lan_destination,
                cloud_enabled=config.cloud_backup.enabled,
                gcs_key_path=gcs_key_path,
                cloud_bucket=config.cloud_backup.bucket,
                cloud_remote_path=config.cloud_backup.remote_path,
                gcs_location=config.cloud_backup.gcs_location,
            )
        except Exception as e:
            logger.warning(f"Config backup failed (non-critical): {e}")

        return overall

    finally:
        # BUG FIX #2 & #3: Always clean up VSS snapshot, even on failure or retry
        if vss_device_path:
            try:
                delete_vss_snapshot_task(vss_device_path)
                logger.info("VSS shadow copy deleted")
            except Exception as e:
                logger.warning(f"VSS cleanup failed: {e}")


if __name__ == "__main__":
    import sys
    if "--deploy" in sys.argv:
        nightly_backup.deploy(
            name="nightly-backup-production",
            work_pool_name="default",
            cron="0 23 * * *",
            parameters={"config_path": "config.yaml"},
            tags=["production", "backup", "aam-associates"],
            description="Nightly backup of D:\\ drive to LAN and GCS",
        )
    else:
        nightly_backup()
