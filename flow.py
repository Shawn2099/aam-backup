"""Prefect flow: nightly backup orchestration."""

import logging
import shutil
import time
from datetime import datetime, timezone

from prefect import flow
from prefect.context import get_run_context
from prefect.logging import get_run_logger

from core.config_loader import load_config
from core.logging_setup import configure_logging
from core.manifest_db import ManifestDB
from core.verify import compare_dry_run_deletions
from tasks.anomaly_task import anomaly_detection_task
from tasks.archive_task import yearly_archive_task
from tasks.cloud_task import cloud_backup_task
from tasks.config_backup_task import backup_config_task
from tasks.config_task import load_config_task
from tasks.config_version_task import version_config_task
from tasks.lan_task import lan_backup_task
from tasks.lan_integrity_task import lan_integrity_task
from tasks.log_backup_task import backup_logs_cloud_task
from tasks.maintenance_task import maintain_manifest_db_task
from tasks.manifest_backup_task import backup_manifest_db_task
from tasks.manifest_rollback_task import pre_run_manifest_backup_task
from tasks.metrics_task import collect_metrics_task
from tasks.no_run_alert_task import check_backup_not_run_alert_task
from tasks.preflight_task import preflight_task
from tasks.report_task import generate_report_task
from tasks.reconciliation_task import reconciliation_task
from tasks.restore_verify_task import restore_verify_task
from tasks.scan_task import scan_task
from tasks.shutdown_server_task import shutdown_server_task
from tasks.stale_backup_task import check_stale_backup_task
from tasks.verification_task import verify_cloud_integrity_task
from tasks.vss_task import create_vss_snapshot_task, delete_vss_snapshot_task


_hook_logger = logging.getLogger(__name__)


def _get_flow_run_id() -> str:
    """Get current flow run ID from Prefect context, or 'unknown' if unavailable."""
    ctx = get_run_context()
    return str(ctx.flow_run.id) if ctx and getattr(ctx, "flow_run", None) else "unknown"  # type: ignore[union-attr]


def _send_email_notification(
    config_path: str,
    flow_run_id: str,
    subject_suffix: str,
    is_failure: bool,
    custom_message: str = "",
) -> None:
    """Send email notification using unified send_email with Prefect block fallback."""
    from core.email_utils import send_email

    try:
        config = load_config(config_path)
        notif = config.notifications

        if not notif.smtp_host or not notif.sender or not notif.recipients:
            return

        status_label = "Failed" if is_failure else "Complete"
        color = "red" if is_failure else "green"
        firm_name = config.firm.name
        subject = f"Backup {status_label} — {subject_suffix}"

        if is_failure:
            source_free_gb = 0
            try:
                source_free_gb = round(shutil.disk_usage(config.paths.source_drive).free / (1024 ** 3), 1)
            except Exception:
                pass

            source_threshold = config.alerts.source_free_space_warning_gb
            low_space_note = ""
            if source_free_gb < source_threshold:
                low_space_note = (
                    f"\n⚠ Source drive low on space: {source_free_gb} GB free "
                    f"(threshold: {source_threshold} GB)"
                )

            body_text = (
                f"Backup Failure Notification\n"
                f"{'=' * 40}\n\n"
                f"Firm: {firm_name}\n"
                f"Flow Run ID: {flow_run_id}\n"
                f"Error: {custom_message}\n"
                f"Source drive free: {source_free_gb} GB{low_space_note}\n\n"
                f"Check Prefect UI for full details.\n"
            )
            body_html = f"""
            <html><body>
            <h2 style="color: {color};">Backup Failure Notification</h2>
            <table>
                <tr><td><strong>Firm:</strong></td><td>{firm_name}</td></tr>
                <tr><td><strong>Flow Run ID:</strong></td><td>{flow_run_id}</td></tr>
                <tr><td><strong>Error:</strong></td><td><code>{custom_message}</code></td></tr>
                <tr><td><strong>Source drive free:</strong></td><td>{source_free_gb} GB</td></tr>
                {f'<tr><td><strong>⚠ Low space:</strong></td><td style="color: red;">{source_free_gb} GB free (threshold: {source_threshold} GB)</td></tr>' if source_free_gb < source_threshold else ''}
            </table>
            <p>Check Prefect UI for full details.</p>
            </body></html>
            """
        else:
            body_text = (
                f"Backup Success Notification\n"
                f"{'=' * 40}\n\n"
                f"Firm: {firm_name}\n"
                f"Flow Run ID: {flow_run_id}\n\n"
                f"{custom_message}\n"
            )
            status_html = custom_message.replace("\n", "<br>")
            body_html = f"""
            <html><body>
            <h2 style="color: {color};">Backup Success Notification</h2>
            <table>
                <tr><td><strong>Firm:</strong></td><td>{firm_name}</td></tr>
                <tr><td><strong>Flow Run ID:</strong></td><td>{flow_run_id}</td></tr>
            </table>
            <pre style="font-family: monospace; margin-top: 1em;">{status_html}</pre>
            </body></html>
            """

        send_email(
            smtp_host=notif.smtp_host,
            smtp_port=notif.smtp_port,
            smtp_username=notif.smtp_username,
            smtp_type=notif.smtp_type,
            smtp_password_credential=notif.smtp_password_credential,
            sender=notif.sender,
            recipients=notif.recipients,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
        )

    except Exception as e:
        _hook_logger.error(f"Failed to send email notification: {e}")


def _send_failure_email(config_path: str, flow_run_id: str, error_message: str) -> None:
    """Send failure notification email."""
    _send_email_notification(
        config_path=config_path,
        flow_run_id=flow_run_id,
        subject_suffix=error_message[:50] if error_message else "Unknown",
        is_failure=True,
        custom_message=error_message,
    )


def _send_success_email(config_path: str, flow_run_id: str, status: str,
                        duration: float, run_summary: dict | None = None) -> None:
    """Send success notification email with enriched run summary."""
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    duration_str = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"

    if run_summary:
        custom_message = _format_run_summary_text(status, duration_str, run_summary)
    else:
        custom_message = f"{status} — Duration: {duration_str}"

    _send_email_notification(
        config_path=config_path,
        flow_run_id=flow_run_id,
        subject_suffix=status,
        is_failure=False,
        custom_message=custom_message,
    )


def _on_backup_failure(flow_obj, flow_run, state):
    """Hook called when the backup flow fails."""
    _hook_logger.critical(
        f"Backup flow FAILED: {state.message or 'No details available'}. "
        f"Run ID: {flow_run.id}. "
        f"Check Prefect UI for details."
    )

    # Send email notification (best-effort)
    config_path = flow_run.parameters.get("config_path", "config.yaml")
    _send_failure_email(config_path, str(flow_run.id), state.message or "Unknown error")


def _on_backup_completion(flow_obj, flow_run, state):
    """Hook called when the backup flow completes successfully."""
    _hook_logger.info(f"Backup flow completed successfully. Run ID: {flow_run.id}")

    config_path = flow_run.parameters.get("config_path", "config.yaml")

    try:
        config = load_config(config_path)
    except Exception as e:
        _hook_logger.error(f"Failed to load config for completion hook: {e}")
        return

    if config.notifications.send_on_every_run:
        try:
            duration = flow_run.total_run_time or 0
            run_summary = _read_run_summary(config.paths.log_directory)
            _send_success_email(
                config_path,
                str(flow_run.id),
                _build_completion_subject(run_summary),
                duration,
                run_summary,
            )
        except Exception as e:
            _hook_logger.error(f"Failed to send success email: {e}")


def _read_run_summary(log_directory: str) -> dict | None:
    """Read the run summary JSON if it exists."""
    import json
    from pathlib import Path
    summary_path = Path(log_directory) / "run_summary.json"
    if not summary_path.exists():
        return None
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _build_completion_subject(run_summary: dict | None) -> str:
    """Build an enriched subject line for the completion email."""
    if not run_summary:
        return "COMPLETE"

    scan = run_summary.get("scan", {})
    changed = scan.get("new", 0) + scan.get("modified", 0) + scan.get("deleted", 0)

    flags = []
    anomalies = run_summary.get("anomalies", {})
    if anomalies.get("has_anomalies"):
        flags.append("\u26a0")
    recon = run_summary.get("reconciliation", {})
    if recon.get("drift_found"):
        if recon.get("auto_corrected"):
            flags.append("drift-fixed")
        else:
            flags.append("\u26a0drift")
    lint_audit = run_summary.get("lan_integrity_audit", {})
    if lint_audit.get("status") == "MISMATCH_DETECTED":
        flags.append("\u26a0integrity")

    flag_str = " " + " ".join(flags) if flags else ""
    return f"COMPLETE — {changed} changed{flag_str}"


def _format_run_summary_text(status: str, duration_str: str, run_summary: dict) -> str:
    """Format run summary as a plain-text message body."""
    lines = [f"{status} — Duration: {duration_str}", ""]

    scan = run_summary.get("scan", {})
    lines.append(f"Files: {scan.get('new', 0)} new, "
                 f"{scan.get('modified', 0)} modified, "
                 f"{scan.get('deleted', 0)} deleted "
                 f"(of {scan.get('total_source_files', 0):,} total)")
    lines.append("")

    lan = run_summary.get("lan", {})
    if lan.get("status") != "LAN_SKIPPED":
        checksum_info = ""
        if lan.get("checksum_mismatches", 0) > 0:
            checksum_info = f" ({lan['checksum_verified']} verified, "
            checksum_info += f"{lan['checksum_mismatches']} checksum mismatches)"
        lines.append(f"LAN: {lan.get('status')} — "
                     f"{lan.get('files_copied', 0):,} files copied"
                     f"{checksum_info}")
    else:
        lines.append("LAN: skipped")

    cloud = run_summary.get("cloud", {})
    if cloud.get("status") != "CLOUD_SKIPPED":
        integrity_info = ""
        if cloud.get("integrity_mismatches", 0) > 0:
            integrity_info = f" ({cloud['integrity_mismatches']} integrity mismatches)"
        lines.append(f"Cloud: {cloud.get('status')}"
                     f"{integrity_info}")
    else:
        lines.append("Cloud: skipped")
    lines.append("")

    recon = run_summary.get("reconciliation", {})
    if recon.get("drift_found"):
        lines.append("Reconciliation: DRIFT DETECTED")
        if recon.get("auto_corrected"):
            lines.append("  Auto-corrected by re-sync.")
        else:
            lines.append(f"  LAN: {recon.get('lan_drift')}")
            lines.append(f"  Cloud: {recon.get('cloud_drift')}")
            lines.append("  Manual investigation recommended.")

    anomalies = run_summary.get("anomalies", {})
    if anomalies.get("has_anomalies"):
        lines.append("Anomalies detected:")
        for spike in anomalies.get("spikes", []):
            lines.append(f"  SPIKE: {spike}")
        for silence in anomalies.get("silence", []):
            lines.append(f"  SILENCE: {silence}")

    lint_audit = run_summary.get("lan_integrity_audit", {})
    if lint_audit.get("status") == "MISMATCH_DETECTED":
        lines.append("")
        lines.append(
            f"LAN Integrity Audit: {lint_audit.get('mismatches', 0)} mismatches, "
            f"{lint_audit.get('missing', 0)} missing "
            f"(of {lint_audit.get('verified', 0) + lint_audit.get('mismatches', 0) + lint_audit.get('missing', 0)} sampled)"
        )

    restore = run_summary.get("test_restore", {})
    if restore.get("status") == "OK":
        lines.append("")
        lines.append(f"Test Restore: LAN {restore.get('lan_ok', 0)} OK / "
                     f"Cloud {restore.get('cloud_ok', 0)} OK")

    return "\n".join(lines)


def _write_run_summary(
    log_directory: str,
    overall: str,
    flow_run_id: str,
    duration_seconds: float,
    scan_result,
    lan_result: dict,
    cloud_result: dict,
    cloud_mismatches: int,
    cloud_missing: int,
    recon_result: dict | None,
    anomaly_result: dict | None,
    lint_audit_result: dict,
    restore_result: dict,
    lan_checksum: dict,
) -> None:
    """Write a JSON run summary for enriched email and reporting."""
    import json
    from pathlib import Path

    summary_path = Path(log_directory) / "run_summary.json"
    summary = {
        "flow_run_id": flow_run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall,
        "duration_seconds": duration_seconds,
        "scan": {
            "new": len(scan_result.new_files),
            "modified": len(scan_result.modified_files),
            "deleted": len(scan_result.deleted_files),
            "unchanged": scan_result.unchanged_count,
            "total_source_files": scan_result.total_file_count,
            "total_source_bytes": scan_result.total_source_bytes,
        },
        "lan": {
            "status": lan_result.get("status", "LAN_SKIPPED"),
            "files_copied": lan_result.get("files_copied", 0),
            "bytes_copied": lan_result.get("bytes_copied", 0),
            "files_failed": lan_result.get("files_failed", 0),
            "checksum_verified": lan_checksum.get("verified", 0),
            "checksum_mismatches": lan_checksum.get("mismatches", 0),
        },
        "cloud": {
            "status": cloud_result.get("status", "CLOUD_SKIPPED"),
            "integrity_mismatches": cloud_mismatches,
            "integrity_missing": cloud_missing,
        },
        "reconciliation": {
            "status": recon_result.get("status", "SKIPPED") if recon_result else "N/A",
            "drift_found": recon_result.get("drift_found", False) if recon_result else False,
            "auto_corrected": recon_result.get("auto_correct", False) if recon_result else False,
            "lan_drift": recon_result.get("lan", {}).get("drift_summary", "") if recon_result else "",
            "cloud_drift": recon_result.get("cloud", {}).get("drift_summary", "") if recon_result else "",
        },
        "anomalies": {
            "has_anomalies": anomaly_result.get("has_anomalies", False) if anomaly_result else False,
            "spikes": anomaly_result.get("spike_details", []) if anomaly_result else [],
            "silence": anomaly_result.get("silence_details", []) if anomaly_result else [],
        },
        "lan_integrity_audit": {
            "status": lint_audit_result.get("status", "SKIPPED"),
            "verified": lint_audit_result.get("verified", 0),
            "mismatches": lint_audit_result.get("mismatches", 0),
            "missing": lint_audit_result.get("missing", 0),
        },
        "test_restore": {
            "status": restore_result.get("status", "SKIPPED"),
            "lan_ok": restore_result.get("lan", {}).get("ok", 0),
            "lan_failed": restore_result.get("lan", {}).get("failed", 0),
            "cloud_ok": restore_result.get("cloud", {}).get("ok", 0),
            "cloud_failed": restore_result.get("cloud", {}).get("failed", 0),
        },
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


def _run_anomaly_check(config, config_path: str, flow_run_id: str) -> dict | None:
    """Run anomaly detection and send failure email if anomalies found."""
    try:
        result = anomaly_detection_task(config.paths.log_directory, config)
    except Exception as e:
        logger = get_run_logger()
        logger.warning(f"Anomaly detection failed (non-critical): {e}")
        return None

    if result.get("has_anomalies") and config.notifications.send_on_failure:
        try:
            spike_details = "; ".join(result.get("spike_details", []))
            silence_details = "; ".join(result.get("silence_details", []))
            anomaly_msg = " ".join(filter(None, [spike_details, silence_details]))
            if anomaly_msg:
                _send_failure_email(config_path, flow_run_id, f"Anomaly detected: {anomaly_msg}")
        except Exception as e:
            logger = get_run_logger()
            logger.warning(f"Failed to send anomaly alert email: {e}")

    return result


@flow(
    name="nightly-backup",
    flow_run_name="backup-{config_path}-{date:%Y%m%d-%H%M%S}",
    log_prints=True,
    version="1.3.0",
    timeout_seconds=28800,  # 8 hours max
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

    try:
        # Track VSS state for cleanup (must survive exceptions)
        vss_enabled = False
        vss_device_path = None

        # Initialize conditional results (set in try blocks later)
        recon_result = None
        anomaly_result = None

        # Task 1: Load configuration
        config, gcs_key_path = load_config_task(config_path)

        # Configure logging now that we know the correct directory
        configure_logging(config.paths.log_directory)

        # Validate at least one backup destination is enabled
        dest_issues = config.validate_backup_destinations()
        for issue in dest_issues:
            logger.critical(issue)
        if dest_issues:
            raise RuntimeError("No backup destinations enabled. Check config.yaml.")

        # Log backup destination status
        dest = config.backup_destinations
        lan_status_str = "ENABLED" if dest["lan"]["enabled"] else "DISABLED"
        cloud_status_str = "ENABLED" if dest["cloud"]["enabled"] else "DISABLED"
        logger.info(f"Backup destinations — LAN: {lan_status_str}, Cloud: {cloud_status_str}")

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
                        flow_run_id = _get_flow_run_id()
                        _send_failure_email(
                            config_path,
                            flow_run_id,
                            f"Backup not run alert: {no_run_alert['message']}",
                        )
                    except Exception as email_err:
                        logger.warning(f"Failed to send no-run alert email: {email_err}")
        except Exception as e:
            logger.warning(f"No-run alert check failed (non-critical): {e}")

        # Pre-backup manifest maintenance — protects against corruption during this run
        try:
            maintain_manifest_db_task(config.paths.database_path, max_size_mb=500)
            logger.info("Manifest DB pre-backup maintenance completed")
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

        # Task 2: Pre-flight checks (includes dry run validation — D-006)
        preflight_result = preflight_task(config.model_dump())

        # D-006: Check dry run results to decide which modules to run
        lan_dry_run_failed = False
        cloud_dry_run_failed = False

        preflight_report = preflight_result.get("report", {})
        preflight_checks = preflight_report.get("checks", [])

        if preflight_checks:
            for check in preflight_checks:
                if check.get("category") == "Dry Run":
                    if check.get("name") == "LAN Preview" and check.get("severity") == "FAIL":
                        lan_dry_run_failed = True
                        logger.error(
                            f"LAN dry run failed: {check.get('message')} — "
                            f"skipping LAN backup task"
                        )
                    if check.get("name") == "Cloud Preview" and check.get("severity") == "FAIL":
                        cloud_dry_run_failed = True
                        logger.error(
                            f"Cloud dry run failed: {check.get('message')} — "
                            f"skipping cloud backup task"
                        )

        # If both dry runs failed, fail the flow early
        if lan_dry_run_failed and cloud_dry_run_failed:
            raise RuntimeError(
                "Both LAN and Cloud dry runs failed — "
                "real backup would also fail. Check destination accessibility and credentials."
            )

        # D-006: Compare deletion counts between dry runs and scanner
        if preflight_checks:
            lan_deletions = 0
            cloud_deletions = 0
            for check in preflight_checks:
                if check.get("category") == "Dry Run":
                    if check.get("name") == "LAN Preview":
                        # Parse deletions from message: "X files would change: Y new, Z modified, W deleted"
                        msg = check.get("message", "")
                        if "deleted" in msg:
                            try:
                                lan_deletions = int(msg.split("deleted")[0].split()[-1])
                            except (ValueError, IndexError):
                                pass
                    if check.get("name") == "Cloud Preview":
                        msg = check.get("message", "")
                        if "deletes" in msg:
                            try:
                                cloud_deletions = int(msg.split("deletes")[0].split()[-1])
                            except (ValueError, IndexError):
                                pass

            # We'll compare after scan completes (need scanner deleted count)
            # Store for later comparison
            _dry_run_deletions = {"lan": lan_deletions, "cloud": cloud_deletions}

        # Task 3: Scan drive
        scan_result = scan_task(config, config.paths.database_path)

        logger.info(
            f"Scan complete: {len(scan_result.new_files)} new, "
            f"{len(scan_result.modified_files)} modified, "
            f"{len(scan_result.deleted_files)} deleted, "
            f"{scan_result.unchanged_count} unchanged"
        )

        # D-006: Compare deletion counts (dry run vs scanner)
        try:
            comparison = compare_dry_run_deletions(
                {"deleted": _dry_run_deletions.get("lan", 0)},
                {"deletes": _dry_run_deletions.get("cloud", 0)},
                len(scan_result.deleted_files),
            )
            if comparison["mismatch"]:
                logger.error(
                    f"Deletion count mismatch (delta {comparison['max_delta_pct']}%): "
                    f"{comparison['details']} — "
                    f"This suggests exclusion config drift between tools. "
                    f"Aborting to prevent potential data loss."
                )
                raise RuntimeError(
                    f"Deletion count mismatch: {comparison['details']}"
                )
            else:
                logger.debug(f"Deletion counts aligned: {comparison['details']}")
        except RuntimeError:
            raise
        except Exception as e:
            logger.warning(f"Deletion comparison failed (non-critical): {e}")

        if not scan_result.has_changes:
            logger.info("No changes detected — backup complete")

            threshold = config.alerts.no_changes_warning_days
            if threshold > 0:
                try:
                    stale_result = check_stale_backup_task(
                        config.paths.database_path, threshold
                    )
                    if stale_result.get("status") == "WARNING":
                        logger.warning(
                            f"Stale backup: {stale_result.get('message')}"
                        )
                        if config.notifications.send_on_failure:
                            try:
                                flow_run_id = _get_flow_run_id()
                                _send_failure_email(
                                    config_path,
                                    flow_run_id,
                                    f"Stale backup warning: {stale_result['message']}",
                                )
                            except Exception as email_err:
                                logger.warning(f"Failed to send stale backup alert email: {email_err}")
                except Exception as e:
                    logger.warning(f"Stale backup check failed (non-critical): {e}")

            # Collect metrics even on "no change" runs
            try:
                duration = time.time() - start_time
                flow_run_id = _get_flow_run_id()

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
                    lan_retry_count=0,
                    manifest_db_size_mb=0.0,
                )
            except Exception as e:
                logger.warning(f"Metrics collection failed (non-critical): {e}")

            # Anomaly detection — check for suspicious scan patterns
            _run_anomaly_check(config, config_path, flow_run_id)

            return "COMPLETE"

        # Pre-backup check: LAN destination free space guard
        if config.lan_backup.enabled:
            try:
                lan_free = shutil.disk_usage(config.paths.lan_destination).free
                lan_free_gb = lan_free / (1024 ** 3)
                threshold_gb = config.alerts.lan_free_space_warning_gb
                if lan_free_gb < threshold_gb:
                    logger.warning(
                        f"LAN destination low on space BEFORE backup: "
                        f"{lan_free_gb:.1f} GB free (threshold: {threshold_gb} GB)"
                    )
                    if not config.cloud_backup.enabled:
                        raise RuntimeError(
                            f"LAN destination critically low on space "
                            f"({lan_free_gb:.1f} GB free, need {threshold_gb} GB) "
                            f"and cloud backup is disabled — aborting to prevent failures"
                        )
                else:
                    logger.info(
                        f"LAN destination has {lan_free_gb:.1f} GB free "
                        f"(threshold: {threshold_gb} GB) — proceeding with backup"
                    )
            except Exception as e:
                logger.debug(f"Could not check LAN disk space before backup: {e}")

        # Tasks 4 & 5: Sequential LAN then cloud backup (skip if dry run failed — D-006)
        # Sequential to avoid disk I/O contention on source drive and VSS shadow copy stress
        lan_result = {"status": "LAN_SKIPPED", "files_copied": 0, "bytes_copied": 0, "files_failed": 0}
        cloud_result = {"status": "CLOUD_SKIPPED"}

        if not lan_dry_run_failed:
            logger.info("Starting LAN backup...")
            lan_result = lan_backup_task(config, scan_result, config.paths.database_path)
        else:
            logger.warning("LAN backup skipped due to dry run failure")

        if not cloud_dry_run_failed:
            logger.info("Starting cloud backup...")
            cloud_result = cloud_backup_task(
                config, gcs_key_path, scan_result, config.paths.database_path
            )
        else:
            logger.warning("Cloud backup skipped due to dry run failure")

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
                config.manifest_backup.lan_path,
                config.manifest_backup.cloud_path,
                config.manifest_backup.retention_count,
            )
        except Exception as e:
            logger.warning(f"manifest.db backup failed (non-critical): {e}")

        # LAN integrity audit — periodic checksum verification of random samples
        # from the LAN mirror. Must run BEFORE reconciliation, which may auto-correct
        # LAN drift and overwrite evidence of bit-rot.
        lint_audit_result = {"status": "SKIPPED"}
        try:
            lint_audit_result = lan_integrity_task(config)
        except Exception as e:
            logger.warning(f"LAN integrity audit failed (non-critical): {e}")

        # D-003: Periodic destination reconciliation
        try:
            recon_result = reconciliation_task(
                config,
                config.paths.database_path,
                gcs_key_path,
            )
            if recon_result.get("status") != "SKIPPED":
                if recon_result.get("drift_found"):
                    logger.warning(
                        f"Reconciliation found drift: "
                        f"LAN={recon_result.get('lan', {}).get('drift_summary', 'none')}, "
                        f"Cloud={recon_result.get('cloud', {}).get('drift_summary', 'none')}"
                    )
                    if recon_result.get("auto_correct"):
                        logger.info("Auto-correction completed")
                else:
                    logger.info("Reconciliation: no drift detected")
        except Exception as e:
            logger.warning(f"Reconciliation task failed (non-critical): {e}")

        # Verify cloud integrity after successful cloud backup
        cloud_mismatches = 0
        cloud_missing = 0
        if cloud_status in ("CLOUD_COMPLETE", "CLOUD_PARTIAL"):
            try:
                verify_result = verify_cloud_integrity_task(
                    config,
                    gcs_key_path,
                    scan_result=scan_result,
                    database_path=config.paths.database_path,
                )
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

        # SQLite maintenance: VACUUM, WAL checkpoint, size monitoring (run before metrics to capture db size)
        manifest_db_size_mb = 0.0
        try:
            maint_result = maintain_manifest_db_task(config.paths.database_path, max_size_mb=500)
            manifest_db_size_mb = maint_result.get("size_mb", 0.0)
        except Exception as e:
            logger.warning(f"Manifest DB maintenance failed (non-critical): {e}")

        # Collect metrics for trend analysis
        try:
            duration = time.time() - start_time
            flow_run_id = _get_flow_run_id()

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
                lan_retry_count=lan_result.get("retry_count", 0),
                manifest_db_size_mb=manifest_db_size_mb,
            )
        except Exception as e:
            logger.warning(f"Metrics collection failed (non-critical): {e}")

        # Check backup duration and warn if unusually slow
        duration_minutes = duration / 60
        duration_threshold = config.alerts.backup_duration_warning_minutes
        if duration_minutes > duration_threshold:
            logger.warning(
                f"Backup run took {duration_minutes:.0f} minutes "
                f"(threshold: {duration_threshold} minutes) — "
                f"check network speed and source drive health"
            )

        # Anomaly detection — check for suspicious scan patterns (spikes, silence)
        _run_anomaly_check(config, config_path, flow_run_id)

        # Yearly archive: move previous FY data from active to archive prefix
        if config.cloud_archive.enabled and config.cloud_backup.enabled:
            try:
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
        restore_result = {"status": "SKIPPED", "lan": {"ok": 0, "failed": 0}, "cloud": {"ok": 0, "failed": 0}}
        if config.test_restore.enabled:
            try:
                db = ManifestDB(config.paths.database_path)
                run_counter = db.get_and_increment_run_counter()
                db.close()
                if run_counter % config.test_restore.run_every_n_backups == 0:
                    logger.info(
                        f"Running test restore verification "
                        f"(every {config.test_restore.run_every_n_backups} runs, "
                        f"sample count: {config.test_restore.sample_count})"
                    )
                    restore_result = restore_verify_task(
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
            today = datetime.now(timezone.utc)
            today_name = today.strftime("%A").lower()
            smtp_config = {
                "smtp_host": config.notifications.smtp_host,
                "smtp_port": config.notifications.smtp_port,
                "smtp_username": config.notifications.smtp_username,
                "smtp_type": config.notifications.smtp_type,
                "smtp_password_credential": config.notifications.smtp_password_credential,
                "sender": config.notifications.sender,
                "recipients": config.notifications.recipients,
            }

            if config.notifications.weekly_summary_enabled and today_name == config.notifications.weekly_summary_day.lower():
                logger.info(f"Generating weekly backup report ({today_name})")
                generate_report_task(
                    log_directory=config.paths.log_directory,
                    report_type="weekly",
                    smtp_config=smtp_config,
                )

            if today.day == 1:
                logger.info("Generating monthly backup report (1st of month)")
                generate_report_task(
                    log_directory=config.paths.log_directory,
                    report_type="monthly",
                    smtp_config=smtp_config,
                )
        except Exception as e:
            logger.warning(f"Report generation failed (non-critical): {e}")

        # Backup config.yaml to LAN and cloud destinations
        try:
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

        # Shutdown backup server after successful LAN backup (if enabled)
        try:
            shutdown_result = shutdown_server_task(config.model_dump())
            if shutdown_result.get("shutdown_initiated"):
                logger.info(
                    f"Backup server {shutdown_result.get('server_ip')} shutting down in 5 minutes"
                )
        except Exception as e:
            logger.warning(f"Server shutdown failed (non-critical): {e}")

        # Build run summary for enriched email notifications and reports
        try:
            _write_run_summary(
                log_directory=config.paths.log_directory,
                overall=overall,
                flow_run_id=flow_run_id,
                duration_seconds=round(duration, 1),
                scan_result=scan_result,
                lan_result=lan_result,
                cloud_result=cloud_result,
                cloud_mismatches=cloud_mismatches,
                cloud_missing=cloud_missing,
                recon_result=recon_result,
                anomaly_result=anomaly_result,
                lint_audit_result=lint_audit_result,
                restore_result=restore_result,
                lan_checksum=lan_result.get("lan_checksum", {}),
            )
        except Exception as e:
            logger.warning(f"Run summary write failed (non-critical): {e}")

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
    nightly_backup.serve(
        name="nightly-backup-production",
        cron="0 23 * * *",
        parameters={"config_path": "config.yaml"},
        tags=["production", "backup", "aam-associates"],
        description="Nightly backup of D:\\ drive to LAN and GCS",
    )
