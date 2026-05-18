"""Pydantic configuration models for the backup automation system."""

import re
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, field_validator


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
        # Skip validation on non-Windows systems for testing
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

    @field_validator("exclude_extensions")
    @classmethod
    def extensions_start_with_dot(cls, v: List[str]) -> List[str]:
        for ext in v:
            if not ext.startswith("."):
                raise ValueError(f"exclude_extensions entry must start with '.': {ext}")
        return [e.lower() for e in v]


class LanBackupConfig(BaseModel):
    enabled: bool = True
    retry_count: int = Field(default=3, ge=1, le=10)
    retry_wait_seconds: int = Field(default=10, ge=1, le=300)
    subprocess_timeout_seconds: int = Field(default=14400, ge=3600)


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
        values = info.data
        if values.get("enabled", True) and not v:
            # Allow empty MAC during config reconstruction (preflight rebuild)
            # The actual flow validates this before WoL runs
            return v
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
    sender: str = ""
    recipients: List[str] = Field(default_factory=list)
    send_on_every_run: bool = True
    send_on_failure: bool = True
    weekly_summary_enabled: bool = True
    weekly_summary_day: str = "monday"
    weekly_summary_time: str = "08:00"


class AlertsConfig(BaseModel):
    no_changes_warning_days: int = Field(default=7, ge=1, le=365)
    """If no file changes detected for this many days, log a warning."""


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
    cloud_credentials: CloudCredentialsConfig = Field(default_factory=CloudCredentialsConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    notifications: NotificationsConfig = Field(default_factory=NotificationsConfig)
    alerts: AlertsConfig = Field(default_factory=AlertsConfig)
