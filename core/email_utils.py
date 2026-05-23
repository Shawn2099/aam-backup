"""Unified email sending with Prefect block primary + smtplib fallback.

send_email() is the single entry point for all email notifications in the system.
It tries Prefect's EmailServerCredentials block first (managed, cached, TLS-aware).
If the block is unavailable (server down, not configured), it falls back to direct
smtplib using credentials from Windows Credential Manager via keyring.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

_logger = logging.getLogger(__name__)


def send_email(
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_type: str,
    smtp_password_credential: str,
    sender: str,
    recipients: list[str],
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    block_name: str = "backup-email",
) -> bool:
    """Send an email via Prefect block (primary) or direct smtplib (fallback).

    Args:
        smtp_host: SMTP server hostname.
        smtp_port: SMTP port.
        smtp_username: SMTP username / email address.
        smtp_type: "SSL", "STARTTLS", or "INSECURE".
        smtp_password_credential: Credential name in Windows Credential Manager
            for the SMTP password. Also used by the Prefect block.
        sender: From email address.
        recipients: List of To email addresses.
        subject: Email subject line.
        body_text: Plain text email body.
        body_html: Optional HTML email body.
        block_name: Prefect block name for EmailServerCredentials (default: "backup-email").

    Returns:
        True if email was sent successfully, False otherwise.
    """
    if not smtp_host or not sender or not recipients:
        _logger.warning("send_email: missing required config (host/sender/recipients)")
        return False

    # --- Primary path: Prefect EmailServerCredentials block ---
    try:
        from prefect_email import EmailServerCredentials, email_send_message

        try:
            credentials = EmailServerCredentials.load(block_name)
        except Exception:
            _logger.debug(
                f"EmailServerCredentials block '{block_name}' not available, "
                "constructing from config"
            )
            # Get password from keyring for inline construction
            smtp_password = _get_smtp_password(smtp_password_credential)
            if not smtp_password:
                _logger.warning("SMTP password not found in Credential Manager")
                return False
            credentials = EmailServerCredentials(
                username=smtp_username,
                password=smtp_password,
                smtp_server=smtp_host,
                smtp_port=smtp_port,
                smtp_type=smtp_type,
            )

        email_send_message.fn(
            subject=subject,
            msg=body_html or body_text,
            msg_plain=body_text,
            email_server_credentials=credentials,
            email_from=sender,
            email_to=recipients,
        )
        _logger.debug(f"Email sent via Prefect block: {subject[:50]}")
        return True

    except Exception as e:
        _logger.warning(
            f"Prefect email block failed ({e}), falling back to direct smtplib"
        )

    # --- Fallback path: direct smtplib ---
    return _send_via_smtplib(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_username=smtp_username,
        smtp_type=smtp_type,
        smtp_password_credential=smtp_password_credential,
        sender=sender,
        recipients=recipients,
        subject=subject,
        body_text=body_text,
        body_html=body_html,
    )


def _send_via_smtplib(
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_type: str,
    smtp_password_credential: str,
    sender: str,
    recipients: list[str],
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
) -> bool:
    """Send email via direct smtplib connection (no Prefect dependency)."""
    smtp_password = _get_smtp_password(smtp_password_credential)
    if not smtp_password:
        _logger.warning("SMTP password not found in Credential Manager (smtplib fallback)")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(body_text, "plain"))
        if body_html:
            msg.attach(MIMEText(body_html, "html"))

        if smtp_type.upper() == "SSL":
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30) as server:
                server.login(smtp_username, smtp_password)
                server.sendmail(sender, recipients, msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
                if smtp_type.upper() != "INSECURE":
                    server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(sender, recipients, msg.as_string())

        _logger.debug(f"Email sent via smtplib fallback: {subject[:50]}")
        return True

    except Exception as e:
        _logger.error(f"smtplib fallback failed: {e}")
        return False


def _get_smtp_password(credential_name: str) -> Optional[str]:
    """Retrieve SMTP password from Windows Credential Manager."""
    try:
        import keyring
        return keyring.get_password("BackupAgent", credential_name)
    except Exception:
        return None
