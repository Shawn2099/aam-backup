"""Pydantic configuration models for the backup automation system."""

import re
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, field_validator, model_validator


class FirmConfig(BaseModel):
    name: str = Field(..., min_length=1)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("firm.name cannot be empty")
        return v.strip()


class PathsConfig(BaseModel):
    source_drive: str
    lan_destination: str
    log_directory: str
    database_path: str
    rclone_temp_directory: str = "C:\\BackupAgent\\rclone_temp"

    @field_validator("source_drive")
    @classmethod
    def source_drive_exists(cls, v: str) -> str:
        import platform
        if platform.system() != "Windows":
            return v
        if not Path(v).exists():
            raise ValueError(f"paths.source_drive does not exist: {v}")
        return v

    @field_validator("lan_destination")
    @classmethod
    def is_unc_path(cls, v: str) -> str:
        if not re.match(r"^\\\\.+\\.+$", v):
            raise ValueError("paths.lan_destination must be a UNC path starting with \\\\")
        return v

    @field_validator("log_directory")
    @classmethod
    def log_dir_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("paths.log_directory cannot be empty")
        return v.strip()

    @field_validator("database_path")
    @classmethod
    def db_path_format(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("paths.database_path cannot be empty")
        v = v.strip()
        if not v.endswith(".db"):
            raise ValueError("paths.database_path must end with .db")
        return v

    @field_validator("rclone_temp_directory")
    @classmethod
    def rclone_temp_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("paths.rclone_temp_directory cannot be empty")
        return v.strip()


class ScheduleConfig(BaseModel):
    enabled: bool = True
    daily_time: str = "23:00"

    @field_validator("daily_time")
    @classmethod
    def valid_time_format(cls, v: str) -> str:
        if not re.match(r"^\d{2}:\d{2}$", v):
            raise ValueError("schedule.daily_time must be HH:MM format")
        hour, minute = map(int, v.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("schedule.daily_time has invalid hour/minute")
        return v


class BackupScopeConfig(BaseModel):
    exclude_folders: List[str] = Field(default_factory=list)
    exclude_extensions: List[str] = Field(default_factory=lambda: [".lnk", ".tmp", ".temp"])
    exclude_patterns: List[str] = Field(default_factory=lambda: ["~$*", "desktop.ini", "Thumbs.db"])
    full_rescan_every_n_runs: int = Field(default=30, ge=1)
    """Perform a full re-scan (checksum ALL files, clean stale entries) every N runs."""

    @field_validator("exclude_extensions")
    @classmethod
    def extensions_start_with_dot(cls, v: List[str]) -> List[str]:
        for ext in v:
            if not ext.startswith("."):
                raise ValueError(f"exclude_extensions entry must start with '.': {ext}")
        return [e.lower() for e in v]

    @field_validator("exclude_folders")
    @classmethod
    def folders_not_empty(cls, v: List[str]) -> List[str]:
        result = []
        for folder in v:
            stripped = folder.strip()
            if not stripped:
                raise ValueError("exclude_folders entries cannot be empty or whitespace-only")
            result.append(stripped)
        return result


class LanBackupConfig(BaseModel):
    enabled: bool = True
    retry_count: int = Field(default=3, ge=1, le=10)
    retry_wait_seconds: int = Field(default=10, ge=1, le=300)
    subprocess_timeout_seconds: int = Field(default=14400, ge=3600)
    shutdown_after_backup: bool = False


class WolConfig(BaseModel):
    enabled: bool = True
    mac_address: str = ""
    server_ip: str = "192.168.10.10"
    wake_timeout_seconds: int = Field(default=300, ge=60, le=600)
    ping_interval_seconds: int = Field(default=15, ge=5, le=60)
    stability_wait_seconds: int = Field(default=30, ge=0)

    @field_validator("mac_address")
    @classmethod
    def valid_mac_when_enabled(cls, v: str, info) -> str:
        enabled = info.data.get("enabled", True)
        if enabled and not v.strip():
            raise ValueError("wol.mac_address is required when wol.enabled is true")
        if v and not re.match(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$", v):
            raise ValueError("wol.mac_address format must be XX:XX:XX:XX:XX:XX")
        return v

    @field_validator("server_ip")
    @classmethod
    def valid_ipv4(cls, v: str) -> str:
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", v):
            raise ValueError("wol.server_ip must be a valid IPv4 address")
        return v


class VssConfig(BaseModel):
    enabled: bool = False
    """Use Volume Shadow Copy to back up locked files (Tally/Winman)."""
    drive_letter: str = "D"
    fallback_on_failure: bool = True
    """If VSS creation fails, fall back to direct backup instead of failing."""

    @field_validator("drive_letter")
    @classmethod
    def valid_drive_letter(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z]$", v):
            raise ValueError("vss.drive_letter must be a single letter A-Z")
        return v.upper()


class CloudArchiveConfig(BaseModel):
    """Yearly archive configuration for moving old FY data from active to archive prefix."""
    enabled: bool = True
    """Enable yearly archive task."""
    trigger_date: str = "04-01"
    """Date to trigger archive (MM-DD format). Runs on first backup after this date each year."""
    active_path: str = "D_Drive_Backup/active/"
    """GCS prefix for active (current FY) data."""
    archive_path: str = "D_Drive_Backup/archive/"
    """GCS prefix for archived (previous FY) data."""
    storage_class: str = "ARCHIVE"
    """Storage class for archived data."""

    @field_validator("trigger_date")
    @classmethod
    def valid_trigger_date(cls, v: str) -> str:
        if not re.match(r"^\d{2}-\d{2}$", v):
            raise ValueError("cloud_archive.trigger_date must be MM-DD format (e.g., 04-15)")
        month, day = map(int, v.split("-"))
        if not (1 <= month <= 12 and 1 <= day <= 31):
            raise ValueError("cloud_archive.trigger_date has invalid month or day")
        return v

    @field_validator("active_path")
    @classmethod
    def active_path_ends_with_slash(cls, v: str) -> str:
        if not v.endswith("/"):
            return v + "/"
        return v

    @field_validator("archive_path")
    @classmethod
    def archive_path_ends_with_slash(cls, v: str) -> str:
        if not v.endswith("/"):
            return v + "/"
        return v

    @field_validator("storage_class")
    @classmethod
    def valid_storage_class(cls, v: str) -> str:
        valid = {"STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"}
        if v.upper() not in valid:
            raise ValueError(f"cloud_archive.storage_class must be one of: {', '.join(sorted(valid))}")
        return v.upper()


class CloudBackupConfig(BaseModel):
    enabled: bool = True
    provider: str = "gcs"
    bucket: str = ""
    remote_path: str = "D_Drive_Backup"
    gcs_location: str = "asia-south1"
    bandwidth_limit: str = "10M"
    chunk_size: str = "100M"
    retry_count: int = Field(default=3, ge=1, le=10)
    subprocess_timeout_seconds: int = Field(default=21600, ge=3600)
    storage_class: str = "COLDLINE"
    """Storage class for new uploads to GCS."""

    @field_validator("provider")
    @classmethod
    def valid_provider(cls, v: str) -> str:
        valid = {"gcs", "b2", "s3", "gdrive"}
        if v not in valid:
            raise ValueError(f"cloud_backup.provider must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("bucket")
    @classmethod
    def valid_bucket_when_enabled(cls, v: str, info) -> str:
        values = info.data
        if values.get("enabled", True) and not v:
            raise ValueError("cloud_backup.bucket is required when cloud_backup.enabled is true")
        if v and not re.match(r"^[a-z0-9][a-z0-9\-]{1,61}[a-z0-9]$", v):
            raise ValueError("cloud_backup.bucket must contain only lowercase letters, numbers, hyphens")
        return v

    @field_validator("remote_path")
    @classmethod
    def valid_remote_path(cls, v: str) -> str:
        if not re.match(r"^[\w\-_/]+$", v):
            raise ValueError("cloud_backup.remote_path contains invalid characters")
        return v

    @field_validator("bandwidth_limit")
    @classmethod
    def valid_bandwidth(cls, v: str) -> str:
        if not re.match(r"^\d+[kMG]$", v):
            raise ValueError("cloud_backup.bandwidth_limit must match format like 10M, 500k, 1G")
        return v

    @field_validator("chunk_size")
    @classmethod
    def valid_chunk_size(cls, v: str) -> str:
        if not re.match(r"^\d+[MG]$", v):
            raise ValueError("cloud_backup.chunk_size must match format like 100M, 5G")
        return v

    @field_validator("storage_class")
    @classmethod
    def valid_storage_class(cls, v: str) -> str:
        valid = {"STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"}
        if v.upper() not in valid:
            raise ValueError(f"cloud_backup.storage_class must be one of: {', '.join(sorted(valid))}")
        return v.upper()

    @field_validator("gcs_location")
    @classmethod
    def valid_gcs_region(cls, v: str) -> str:
        gcs_regions = {
            "asia-east1", "asia-east2", "asia-northeast1", "asia-northeast2",
            "asia-northeast3", "asia-south1", "asia-south2", "asia-southeast1",
            "asia-southeast2", "australia-southeast1", "australia-southeast2",
            "europe-central2", "europe-north1", "europe-southwest1",
            "europe-west1", "europe-west2", "europe-west3", "europe-west4",
            "europe-west6", "europe-west8", "europe-west9", "europe-west10",
            "europe-west12", "me-central1", "me-central2", "me-west1",
            "northamerica-northeast1", "northamerica-northeast2",
            "southamerica-east1", "southamerica-west1",
            "us-central1", "us-east1", "us-east4", "us-east5",
            "us-south1", "us-west1", "us-west2", "us-west3", "us-west4",
            # Dual-region
            "asia1", "eur4", "eur5", "nam4",
            # Multi-region
            "asia", "eu", "us",
        }
        if v not in gcs_regions:
            raise ValueError(f"cloud_backup.gcs_location '{v}' is not a valid GCS region")
        return v


class CloudCredentialsConfig(BaseModel):
    credential_name: str = "BackupAgent_GCS"

    @field_validator("credential_name")
    @classmethod
    def credential_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("cloud_credentials.credential_name cannot be empty")
        return v.strip()


class UIConfig(BaseModel):
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = Field(default=8080, ge=1024, le=65535)
    prefect_api_url: str = "http://127.0.0.1:4200/api"


class NotificationsConfig(BaseModel):
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password_credential: str = "BackupAgent_SMTP"
    smtp_type: str = "STARTTLS"  # SSL, STARTTLS, or INSECURE
    sender: str = ""
    recipients: List[str] = Field(default_factory=list)
    send_on_every_run: bool = True
    send_on_failure: bool = True
    weekly_summary_enabled: bool = True
    weekly_summary_day: str = "monday"
    weekly_summary_time: str = "08:00"

    @field_validator("smtp_type")
    @classmethod
    def valid_smtp_type(cls, v: str) -> str:
        valid = {"SSL", "STARTTLS", "INSECURE"}
        if v.upper() not in valid:
            raise ValueError(f"notifications.smtp_type must be one of: {', '.join(sorted(valid))}")
        return v.upper()

    @field_validator("sender")
    @classmethod
    def valid_sender_email(cls, v: str) -> str:
        if not v:
            return v
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("notifications.sender must be a valid email address")
        return v.strip()

    @field_validator("recipients")
    @classmethod
    def valid_recipients(cls, v: List[str]) -> List[str]:
        result = []
        for addr in v:
            stripped = addr.strip()
            if not stripped:
                raise ValueError("notifications.recipients entries cannot be empty")
            if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", stripped):
                raise ValueError(f"notifications.recipients contains invalid email: {stripped}")
            result.append(stripped)
        return result

    @field_validator("weekly_summary_day")
    @classmethod
    def valid_weekday(cls, v: str) -> str:
        valid = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
        if v.lower() not in valid:
            raise ValueError(f"notifications.weekly_summary_day must be a valid weekday (got: {v})")
        return v.lower()

    @field_validator("weekly_summary_time")
    @classmethod
    def valid_summary_time(cls, v: str) -> str:
        if not re.match(r"^\d{2}:\d{2}$", v):
            raise ValueError("notifications.weekly_summary_time must be HH:MM format")
        hour, minute = map(int, v.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("notifications.weekly_summary_time has invalid hour/minute")
        return v


class AlertsConfig(BaseModel):
    no_changes_warning_days: int = Field(default=7, ge=1, le=365)
    """If no file changes detected for this many days, log a warning."""
    lan_free_space_warning_gb: int = Field(default=50, ge=1)
    """Alert when LAN destination free space drops below this threshold (GB)."""
    backup_duration_warning_minutes: int = Field(default=180, ge=30)
    """Alert when backup run duration exceeds this threshold (minutes)."""
    backup_not_run_warning_days: int = Field(default=2, ge=1, le=30)
    """Alert when no backup run has been detected for this many days (GAP #3)."""
    source_free_space_warning_gb: int = Field(default=5, ge=1)
    """Alert when source drive free space drops below this threshold (GB)."""


class TestRestoreConfig(BaseModel):
    enabled: bool = True
    sample_count: int = Field(default=10, ge=1, le=100)
    """Number of random files to verify per run."""
    run_every_n_backups: int = Field(default=7, ge=1)
    """Run test restore verification every N backup runs."""


class LanIntegrityConfig(BaseModel):
    enabled: bool = True
    """Enable periodic full LAN integrity audit (random sample checksum verification)."""
    run_every_n_backups: int = Field(default=7, ge=1)
    """Run full LAN integrity audit every N backup runs (default 7 = weekly)."""
    sample_count: int = Field(default=500, ge=10, le=5000)
    """Number of random files to checksum-verify per audit."""
    checksum_concurrency: int = Field(default=4, ge=1, le=16)
    """Number of parallel checksum workers (uses ProcessPoolExecutor)."""


class ReconciliationConfig(BaseModel):
    enabled: bool = True
    """Enable periodic destination reconciliation."""
    run_every_n_backups: int = Field(default=7, ge=1)
    """Run reconciliation every N backup runs (default 7 = weekly)."""
    auto_correct: bool = True
    """Auto-correct drift by running full sync when drift is detected."""

    @field_validator("auto_correct")
    @classmethod
    def warn_auto_correct_when_disabled(cls, v: bool, info) -> bool:
        if v and not info.data.get("enabled", True):
            raise ValueError(
                "reconciliation.auto_correct cannot be true when reconciliation.enabled is false"
            )
        return v


class AnomalyDetectionConfig(BaseModel):
    enabled: bool = True
    """Enable anomaly detection to flag suspicious scan patterns."""
    max_file_count_spike_ratio: float = Field(default=5.0, ge=1.0, le=100.0)
    """Max ratio of changed files vs 7-day average before warning (default 5x)."""
    max_deletion_spike_ratio: float = Field(default=10.0, ge=1.0, le=1000.0)
    """Max ratio of deleted files vs 7-day average before warning (default 10x)."""
    silence_days_alert: int = Field(default=7, ge=1, le=365)
    """Alert when no file changes detected for this many consecutive days."""
    lookback_window_days: int = Field(default=14, ge=3, le=90)
    """Number of days of JSONL metrics to analyze for baseline."""


class ManifestBackupConfig(BaseModel):
    enabled: bool = True
    """Enable manifest.db backup after each successful run."""
    lan_path: str = "_manifest/"
    """Relative path on LAN destination for manifest backups."""
    cloud_path: str = "_manifest/"
    """Relative path on GCS for manifest backups (last-resort fallback)."""
    retention_count: int = Field(default=7, ge=1, le=30)
    """Number of historical manifest backups to retain."""


class AppConfig(BaseModel):
    """Top-level application configuration."""

    firm: FirmConfig
    paths: PathsConfig
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    backup_scope: BackupScopeConfig = Field(default_factory=BackupScopeConfig)
    lan_backup: LanBackupConfig = Field(default_factory=LanBackupConfig)
    wol: WolConfig = Field(default_factory=WolConfig)
    vss: VssConfig = Field(default_factory=VssConfig)
    cloud_backup: CloudBackupConfig = Field(default_factory=CloudBackupConfig)
    cloud_archive: CloudArchiveConfig = Field(default_factory=CloudArchiveConfig)
    cloud_credentials: CloudCredentialsConfig = Field(default_factory=CloudCredentialsConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    notifications: NotificationsConfig = Field(default_factory=NotificationsConfig)
    alerts: AlertsConfig = Field(default_factory=AlertsConfig)
    test_restore: TestRestoreConfig = Field(default_factory=TestRestoreConfig)
    reconciliation: ReconciliationConfig = Field(default_factory=ReconciliationConfig)
    manifest_backup: ManifestBackupConfig = Field(default_factory=ManifestBackupConfig)
    anomaly_detection: AnomalyDetectionConfig = Field(default_factory=AnomalyDetectionConfig)
    lan_integrity: LanIntegrityConfig = Field(default_factory=LanIntegrityConfig)

    @model_validator(mode="after")
    def cross_field_validation(self) -> "AppConfig":
        # C15: Cloud enabled requires non-empty credential name
        if self.cloud_backup.enabled and not self.cloud_credentials.credential_name.strip():
            raise ValueError(
                "cloud_credentials.credential_name is required when cloud_backup.enabled is true"
            )
        # C16: LAN enabled requires non-empty lan_destination
        if self.lan_backup.enabled and not self.paths.lan_destination.strip():
            raise ValueError(
                "paths.lan_destination is required when lan_backup.enabled is true"
            )
        return self

    @property
    def backup_destinations(self) -> dict:
        """Return status of each backup destination.

        Returns dict with keys: lan, cloud, any_enabled, all_disabled, warning.
        """
        lan = {
            "enabled": self.lan_backup.enabled,
            "label": "LAN Backup",
            "destination": self.paths.lan_destination,
        }
        cloud = {
            "enabled": self.cloud_backup.enabled,
            "label": "Cloud Backup",
            "provider": self.cloud_backup.provider,
            "bucket": self.cloud_backup.bucket,
        }
        any_enabled = lan["enabled"] or cloud["enabled"]
        all_disabled = not any_enabled

        warning = None
        if all_disabled:
            warning = "Both LAN and Cloud backup are disabled. No data will be backed up."

        return {
            "lan": lan,
            "cloud": cloud,
            "any_enabled": any_enabled,
            "all_disabled": all_disabled,
            "warning": warning,
        }

    def validate_backup_destinations(self) -> list[str]:
        """Validate that at least one backup destination is enabled.

        Returns list of warning/error messages. Empty list means OK.
        """
        issues = []
        if not self.lan_backup.enabled and not self.cloud_backup.enabled:
            issues.append(
                "CRITICAL: Both LAN and Cloud backup are disabled. "
                "No data will be backed up. Enable at least one destination in config.yaml."
            )
        return issues
