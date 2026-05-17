# External Integrations

**Analysis Date:** 2026-05-18

## APIs & External Services

**Google Cloud Storage (GCS):**
- Purpose: Cloud backup destination — true mirror of D:\ via rclone sync
- Region: asia-south1 (Mumbai) — data residency in India
- Bucket: configured in `config.yaml` under `cloud_backup.bucket`
- Remote path: `D_Drive_Backup/` — root folder inside bucket
- Auth: GCS service account JSON key file
- Key location: `C:\BackupAgent\gcs_service_account.json`
- Credential store: Windows Credential Manager (`BackupAgent` / `BackupAgent_GCS`)
- Versioning: GCS native object versioning — 1 older version retained, 90-day lifecycle
- SDK/Client: rclone CLI binary (no Python SDK)
- Bandwidth limit: `10M` default (configurable via `cloud_backup.bandwidth_limit`)

**Prefect Server (self-hosted):**
- Purpose: Workflow orchestration — scheduling, state management, run history, task logs
- URL: `http://127.0.0.1:4200/api` (local), `http://192.168.10.5:4200` (LAN)
- Database: SQLite at `C:\BackupAgent\prefect.db`
- Auth: None (LAN-only access)
- Email automation: Prefect UI → Blocks → Email Server Credentials → Automations
- API used by: `ui/server.py` (queries flow run state, triggers manual runs)

## Data Storage

**Databases:**
- **FileManifest DB** (`manifest.db`)
  - Engine: SQLite with WAL mode
  - Location: `C:\BackupAgent\manifest.db`
  - Client: SQLAlchemy 2.x with `aiosqlite`
  - Table: `file_manifest` — tracks per-file backup state (relative_path, checksum, last_seen_at, etc.)
  - Indexes: `idx_manifest_relative_path`, `idx_manifest_last_seen`
  - Thread safety: `threading.Lock` on all writes, WAL mode for concurrent reads
  - WAL mode set on every connection via SQLAlchemy event listener

- **Prefect State DB** (`prefect.db`)
  - Engine: SQLite with aiosqlite
  - Location: `C:\BackupAgent\prefect.db`
  - Managed by: Prefect server (not our code)
  - Stores: flow run state, task logs, schedules, deployment config

**File Storage:**
- LAN: SMB share `\\192.168.10.10\hp srv manual backup$` — hidden share, mirror via Robocopy `/MIR`
- Cloud: GCS bucket — mirror via rclone sync
- Temp files: `C:\BackupAgent\rclone_temp\` — temp rclone config and filter files (deleted in finally blocks)

**Caching:**
- None — change detection uses SQLite manifest, not cache

## Authentication & Identity

**Auth Provider:**
- Windows Credential Manager (via `keyring` library)
  - Service: `BackupAgent`
  - Name: `BackupAgent_GCS`
  - Value: Full path to GCS service account JSON key file
  - Lookup: `keyring.get_password("BackupAgent", "BackupAgent_GCS")`

**Service Account:**
- PrefectWorker runs as least-privilege domain service account (provided during deployment)
- Required permissions: D:\ read, LAN share read/write, C:\BackupAgent\ access, Credential Manager access
- PrefectServer and BackupUI run as LocalSystem

## Monitoring & Observability

**Error Tracking:**
- None external — all logging is local

**Logs:**
- **Loguru** — two-sink setup (`core/logging_setup.py`):
  - File sink: `C:\BackupAgent\logs\backup_YYYY-MM-DD.log`, DEBUG+, daily rotation, 30-day retention, .gz compression, UTF-8, thread-safe (enqueue=True)
  - Stderr sink: WARNING+ (captured by NSSM into `service_stderr.log`)
- **Robocopy log**: `C:\BackupAgent\logs\robocopy_YYYY-MM-DD.log` (via `/UNILOG+`)
- **Rclone log**: JSON structured log via `--use-json-log --log-level INFO`
- **Prefect logs**: Loguru sink forwarded to Prefect task logger inside each task
- **Service logs**: NSSM stdout/stderr rotation daily

**Prefect UI:**
- Built-in dashboard at `http://192.168.10.5:4200`
- Shows: flow run history, task logs, schedules, deployment state

**Status UI:**
- FastAPI + Alpine.js at `http://192.168.10.5:8080`
- Shows: last run status, next run countdown, manual trigger button
- Auto-refreshes every 60 seconds

## CI/CD & Deployment

**Hosting:**
- Single-machine deployment on AAMBDC001 (192.168.10.5)
- No external CI/CD — deployed via USB drive with offline wheels

**CI Pipeline:**
- None — manual deployment sequence (18 steps in plan.md Section 17)

**Deployment Tools:**
- NSSM — Windows Service manager
  - `deploy/install_services.bat` — installs PrefectServer, PrefectWorker, BackupUI
  - `deploy/uninstall_services.bat` — removes all three services
- `deploy/create_deployment.py` — registers nightly-backup flow as Prefect deployment
- `scripts/setup_credentials.py` — stores GCS key path in Credential Manager
- `scripts/validate_config.py` — validates config.yaml before starting services
- `scripts/test_connections.py` — tests all connections before go-live
- `scripts/seed_cloud.py` — one-time initial full upload of D:\ to GCS

## Environment Configuration

**Required env vars (set via NSSM):**
- `PREFECT_API_DATABASE_CONNECTION_URL=sqlite+aiosqlite:///C:/BackupAgent/prefect.db`
- `PREFECT_API_URL=http://127.0.0.1:4200/api`
- `PREFECT_SERVER_API_HOST=0.0.0.0`
- `PREFECT_SERVER_API_PORT=4200`

**Config file** (`config.yaml`):
- `firm.name` — firm identification
- `paths.source_drive` — D:\
- `paths.lan_destination` — UNC path to backup server
- `paths.log_directory` — log output directory
- `paths.database_path` — manifest.db location
- `schedule.daily_time` — "23:00"
- `backup_scope.exclude_folders/extensions/patterns` — exclusion lists
- `lan_backup.*` — Robocopy settings
- `wol.*` — WoL settings (mac_address, server_ip, timeouts)
- `cloud_backup.*` — Rclone settings (provider, bucket, bandwidth, chunk_size)
- `cloud_credentials.credential_name` — Credential Manager lookup name
- `ui.*` — FastAPI server settings (host, port, prefect_api_url)
- `notifications.*` — Phase 2 SMTP settings (not used in Phase 1)

**Secrets location:**
- GCS service account key: `C:\BackupAgent\gcs_service_account.json` (ACL restricted to service account)
- Key path stored in Windows Credential Manager (not in config.yaml)
- SMTP credentials (Phase 2): stored in Credential Manager as `BackupAgent_SMTP`

## Webhooks & Callbacks

**Incoming:**
- Prefect worker polls Prefect server for scheduled runs (no webhooks)
- Status UI: `POST /trigger` — manual backup trigger via Prefect API

**Outgoing:**
- Prefect email automation — sends failure alert when flow run state changes to Failed
  - Configured in Prefect UI → Automations
  - Trigger: Flow run Failed, filter: flow name = "nightly-backup"
  - SMTP: port 587, credentials from Prefect Email Server Credentials block

## Subprocess Integrations

**Robocopy** (`core/robocopy.py`):
- Binary: `robocopy.exe` (built into Windows Server 2016)
- Mode: `/MIR` (true mirror)
- Auth: Domain service account has implicit SMB share access
- Exit codes: bitmask evaluation (bit 0-4)
- Security: `shell=False`, argument lists only, path validation before command construction

**Rclone** (`core/rclone.py`):
- Binary: `C:\BackupAgent\rclone.exe`
- Mode: `sync` (true mirror)
- Auth: Service account JSON key via temp config with restricted ACL
- Exit codes: 0-8 mapped to status (0=COMPLETE, 5=RETRYABLE, 7=FAILED, etc.)
- Temp files: config and filter files created with ACL, deleted in finally blocks

**WoL** (`core/wol.py`):
- Library: `wakeonlan.send_magic_packet()`
- Ping: `ping.exe -n 3 -w 1000 [ip]` via subprocess
- MAC address format: `XX:XX:XX:XX:XX:XX` or `XX-XX-XX-XX-XX-XX`

---

*Integration audit: 2026-05-18*
