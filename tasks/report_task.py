"""Prefect task: generate weekly and monthly backup reports."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from prefect import task
from prefect.logging import get_run_logger


@task(
    name="generate_backup_report",
    tags=["reporting"],
    retries=0,
    task_run_name="generate-backup-report",
)
def generate_report_task(
    log_directory: str,
    report_type: str = "weekly",
    smtp_config: dict = None,
) -> dict:
    """Generate weekly or monthly backup report from metrics JSONL.

    Reads metrics collected by collect_metrics_task and produces
    a summary report with success rate, throughput trends, and issues.

    Args:
        log_directory: Path to log directory containing metrics.jsonl.
        report_type: "weekly" or "monthly".
        smtp_config: Dict with SMTP settings for email delivery.

    Returns:
        Report dict with summary statistics.
    """
    logger = get_run_logger()

    metrics_file = Path(log_directory) / "backup_metrics.jsonl"
    if not metrics_file.exists():
        logger.warning(f"No metrics file found at {metrics_file}")
        return {"status": "SKIPPED", "reason": "no metrics data"}

    # Calculate date range
    now = datetime.now(timezone.utc)
    if report_type == "weekly":
        start = now - timedelta(days=7)
    else:
        start = now - timedelta(days=30)

    # Parse metrics
    runs = []
    with open(metrics_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                run_time = datetime.fromisoformat(entry.get("timestamp", ""))
                if run_time >= start:
                    runs.append(entry)
            except (json.JSONDecodeError, ValueError):
                continue

    if not runs:
        logger.info(f"No backup runs in the last {report_type} period")
        return {"status": "SKIPPED", "reason": f"no runs in {report_type} period"}

    # Calculate statistics
    total_runs = len(runs)
    successful = sum(1 for r in runs if r.get("overall_status") == "COMPLETE")
    partial = sum(1 for r in runs if r.get("overall_status") == "PARTIAL_FAILURE")
    failed = sum(1 for r in runs if r.get("overall_status") == "FAILED")

    success_rate = (successful / total_runs * 100) if total_runs > 0 else 0

    total_duration = sum(r.get("duration_seconds", 0) for r in runs)
    avg_duration = total_duration / total_runs if total_runs > 0 else 0

    total_new = sum(r.get("scan_new", 0) for r in runs)
    total_modified = sum(r.get("scan_modified", 0) for r in runs)
    total_deleted = sum(r.get("scan_deleted", 0) for r in runs)

    total_lan_files = sum(r.get("lan_files_copied", 0) for r in runs)
    total_lan_bytes = sum(r.get("lan_bytes_copied", 0) for r in runs)
    total_lan_failed = sum(r.get("lan_files_failed", 0) for r in runs)

    total_cloud_mismatches = sum(r.get("cloud_mismatches", 0) for r in runs)
    total_cloud_missing = sum(r.get("cloud_missing", 0) for r in runs)

    # Find issues
    failed_runs = [r for r in runs if r.get("overall_status") == "FAILED"]
    partial_runs = [r for r in runs if r.get("overall_status") == "PARTIAL_FAILURE"]

    report = {
        "report_type": report_type,
        "generated_at": now.isoformat(),
        "period_start": start.isoformat(),
        "period_end": now.isoformat(),
        "total_runs": total_runs,
        "successful": successful,
        "partial_failures": partial,
        "failures": failed,
        "success_rate": round(success_rate, 1),
        "avg_duration_seconds": round(avg_duration, 1),
        "total_new_files": total_new,
        "total_modified_files": total_modified,
        "total_deleted_files": total_deleted,
        "total_lan_files_copied": total_lan_files,
        "total_lan_bytes_copied": total_lan_bytes,
        "total_lan_files_failed": total_lan_failed,
        "total_cloud_mismatches": total_cloud_mismatches,
        "total_cloud_missing": total_cloud_missing,
        "failed_run_details": [
            {
                "flow_run_id": r.get("flow_run_id"),
                "timestamp": r.get("timestamp"),
                "lan_status": r.get("lan_status"),
                "cloud_status": r.get("cloud_status"),
            }
            for r in failed_runs
        ],
        "partial_run_details": [
            {
                "flow_run_id": r.get("flow_run_id"),
                "timestamp": r.get("timestamp"),
                "lan_status": r.get("lan_status"),
                "cloud_status": r.get("cloud_status"),
            }
            for r in partial_runs
        ],
    }

    # Write report to file
    report_file = Path(log_directory) / f"backup_report_{report_type}_{now.strftime('%Y%m%d')}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(
        f"{report_type.capitalize()} report generated: "
        f"{total_runs} runs, {success_rate:.1f}% success rate, "
        f"avg duration: {avg_duration:.0f}s"
    )

    # Send email if SMTP configured
    if smtp_config and smtp_config.get("smtp_host"):
        try:
            _send_report_email(smtp_config, report)
        except Exception as e:
            logger.warning(f"Failed to send report email: {e}")

    return report


def _send_report_email(smtp_config: dict, report: dict):
    """Send report via email."""
    import smtplib
    import keyring
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    smtp_host = smtp_config.get("smtp_host", "")
    smtp_port = smtp_config.get("smtp_port", 587)
    smtp_username = smtp_config.get("smtp_username", "")
    smtp_password_credential = smtp_config.get("smtp_password_credential", "BackupAgent_SMTP")
    sender = smtp_config.get("sender", "")
    recipients = smtp_config.get("recipients", [])

    if not smtp_host or not sender or not recipients:
        return

    smtp_password = keyring.get_password("BackupAgent", smtp_password_credential)
    if not smtp_password:
        return

    report_type = report["report_type"].capitalize()
    success_rate = report["success_rate"]
    total_runs = report["total_runs"]
    avg_duration = report["avg_duration_seconds"]

    hours = int(avg_duration // 3600)
    minutes = int((avg_duration % 3600) // 60)
    avg_duration_str = f"{hours}h {minutes}m" if hours else f"{minutes}m"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📊 {report_type} Backup Report — {success_rate:.0f}% success rate"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    body_text = (
        f"{report_type} Backup Report\n"
        f"{'=' * 40}\n\n"
        f"Period: {report['period_start'][:10]} to {report['period_end'][:10]}\n"
        f"Total Runs: {total_runs}\n"
        f"Successful: {report['successful']}\n"
        f"Partial Failures: {report['partial_failures']}\n"
        f"Failures: {report['failures']}\n"
        f"Success Rate: {success_rate:.1f}%\n"
        f"Avg Duration: {avg_duration_str}\n\n"
        f"Files Changed: {report['total_new_files']} new, {report['total_modified_files']} modified, {report['total_deleted_files']} deleted\n"
        f"LAN Files Copied: {report['total_lan_files_copied']:,}\n"
        f"Cloud Mismatches: {report['total_cloud_mismatches']}\n"
    )

    body_html = f"""
    <html><body>
    <h2>{report_type} Backup Report</h2>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr><td><strong>Period</strong></td><td>{report['period_start'][:10]} to {report['period_end'][:10]}</td></tr>
        <tr><td><strong>Total Runs</strong></td><td>{total_runs}</td></tr>
        <tr><td><strong>Successful</strong></td><td style="color: green;">{report['successful']}</td></tr>
        <tr><td><strong>Partial Failures</strong></td><td style="color: orange;">{report['partial_failures']}</td></tr>
        <tr><td><strong>Failures</strong></td><td style="color: red;">{report['failures']}</td></tr>
        <tr><td><strong>Success Rate</strong></td><td><strong>{success_rate:.1f}%</strong></td></tr>
        <tr><td><strong>Avg Duration</strong></td><td>{avg_duration_str}</td></tr>
        <tr><td><strong>New Files</strong></td><td>{report['total_new_files']}</td></tr>
        <tr><td><strong>Modified Files</strong></td><td>{report['total_modified_files']}</td></tr>
        <tr><td><strong>Deleted Files</strong></td><td>{report['total_deleted_files']}</td></tr>
        <tr><td><strong>LAN Files Copied</strong></td><td>{report['total_lan_files_copied']:,}</td></tr>
        <tr><td><strong>Cloud Mismatches</strong></td><td>{report['total_cloud_mismatches']}</td></tr>
    </table>
    </body></html>
    """

    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender, recipients, msg.as_string())
