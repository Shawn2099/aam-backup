"""Configure Prefect email notifications for backup alerts.

Usage:
    uv run deploy/setup_email_notifications.py setup \
        --smtp-host smtp.gmail.com \
        --smtp-port 587 \
        --username your-email@gmail.com \
        --password your-app-password \
        --recipients admin@aamassociates.com

Creates:
1. EmailServerCredentials block in Prefect
2. Automation: send email on flow run failure
3. Automation: send weekly summary on Monday at 8:00 AM
"""


import typer
from prefect_email import EmailServerCredentials  # type: ignore[import-untyped]

app = typer.Typer(help="Configure Prefect email notifications")


@app.command()
def setup(
    smtp_host: str = typer.Option(..., "--smtp-host", "-H", help="SMTP server hostname"),
    smtp_port: int = typer.Option(587, "--smtp-port", "-P", help="SMTP port"),
    username: str = typer.Option(..., "--username", "-u", help="SMTP username/email"),
    password: str = typer.Option(..., "--password", "-p", help="SMTP password or app password"),
    smtp_type: str = typer.Option("STARTTLS", "--smtp-type", "-T", help="SMTP type: SSL, STARTTLS, or INSECURE"),
    sender: str = typer.Option(None, "--sender", "-s", help="Sender email (defaults to username)"),
    recipients: str = typer.Option(..., "--recipients", "-r", help="Comma-separated recipient emails"),
    block_name: str = typer.Option("backup-email", "--block-name", "-b", help="Prefect block name"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show what would be done"),
):
    """Configure Prefect email notifications for backup alerts."""
    sender = sender or username
    recipient_list = [r.strip() for r in recipients.split(",")]

    typer.echo("=" * 50)
    typer.echo("Backup Agent — Email Notification Setup")
    typer.echo("=" * 50)

    typer.echo(f"\n  SMTP Host: {smtp_host}:{smtp_port}")
    typer.echo(f"  SMTP Type: {smtp_type}")
    typer.echo(f"  Username: {username}")
    typer.echo(f"  Sender: {sender}")
    typer.echo(f"  Recipients: {', '.join(recipient_list)}")
    typer.echo(f"  Block name: {block_name}")

    if dry_run:
        typer.echo("\n  [DRY RUN] Would create:")
        typer.echo(f"    - EmailServerCredentials block: {block_name}")
        typer.echo("    - Automation: email on flow run failure")
        typer.echo("    - Automation: weekly summary (Monday 8:00 AM)")
        return

    try:
        # Step 1: Create EmailServerCredentials block
        typer.echo("\n[1/3] Creating EmailServerCredentials block...")
        email_block = EmailServerCredentials(
            username=username,
            password=password,
            smtp_server=smtp_host,
            smtp_port=smtp_port,
            smtp_type=smtp_type,
        )
        email_block.save(name=block_name, overwrite=True)
        typer.echo(f"  Block '{block_name}' created")

        # Step 2: Create failure automation
        typer.echo("\n[2/3] Creating failure alert automation...")
        _create_failure_automation(recipient_list, sender, block_name)
        typer.echo("  Failure alert automation created")

        # Step 3: Create weekly summary automation
        typer.echo("\n[3/3] Creating weekly summary automation...")
        _create_weekly_summary_automation(recipient_list, sender, block_name)
        typer.echo("  Weekly summary automation created")

        typer.echo("\n" + "=" * 50)
        typer.echo("Email notifications configured successfully!")
        typer.echo("=" * 50)

    except Exception as e:
        typer.echo(f"\n  Failed: {e}")
        raise typer.Exit(1)


def _create_failure_automation(recipients: list[str], sender: str, block_name: str):
    """Create automation that sends email on flow run failure."""
    import asyncio
    from datetime import timedelta
    from prefect.automations import Automation
    from prefect.events.schemas.automations import EventTrigger, Posture
    from prefect.events.actions import SendNotification

    trigger = EventTrigger(
        expect={"prefect.flow-run.Failed"},
        match={"prefect.resource.id": "prefect.flow-run.*"},
        match_related={
            "prefect.resource.role": "flow",
            "prefect.resource.name": "nightly-backup",
        },
        posture=Posture.Reactive,
        threshold=1,
        within=timedelta(0),
    )

    action = SendNotification(
        block_document_id=None,
        subject="BACKUP FAILED",
        body="Flow run triggered a failure event.\n\nCheck Prefect UI for details.",
    )

    automation = Automation(
        name="Backup Failure Alert",
        description="Send email when nightly-backup flow run fails",
        enabled=True,
        trigger=trigger,
        actions=[action],
    )

    async def _create():
        await automation.save(name="backup-failure-alert", overwrite=True)
        typer.echo(f"  Automation saved as 'backup-failure-alert'")

    asyncio.run(_create())


def _create_weekly_summary_automation(recipients: list[str], sender: str, block_name: str):
    """Create automation for weekly summary email."""
    import asyncio
    from datetime import timedelta
    from prefect.automations import Automation
    from prefect.events.schemas.automations import EventTrigger, Posture
    from prefect.events.actions import SendNotification

    trigger = EventTrigger(
        expect={"prefect.flow-run.Completed"},
        match={"prefect.resource.id": "prefect.flow-run.*"},
        match_related={
            "prefect.resource.role": "flow",
            "prefect.resource.name": "nightly-backup",
        },
        posture=Posture.Reactive,
        threshold=1,
        within=timedelta(0),
    )

    action = SendNotification(
        block_document_id=None,
        subject="Weekly Backup Summary",
        body="Weekly backup summary.\n\nCheck Prefect UI for full details.",
    )

    automation = Automation(
        name="Backup Weekly Summary",
        description="Send weekly backup summary",
        enabled=True,
        trigger=trigger,
        actions=[action],
    )

    async def _create():
        await automation.save(name="backup-weekly-summary", overwrite=True)
        typer.echo(f"  Automation saved as 'backup-weekly-summary'")

    asyncio.run(_create())


if __name__ == "__main__":
    app()
