# AAM Backup System — Engineering Status Report

> **Date:** 2026-05-18
> **Project:** Automated Daily Backup of Windows Server 2016 D:\ Drive
> **Scope:** ~370GB, 200K+ files → LAN (Robocopy /MIR) + GCS (Rclone sync)
> **Orchestrator:** Prefect 3.x self-hosted

---

## 1. PROJECT OVERVIEW

**Goal:** Automated nightly backup of Windows Server 2016 D:\ drive to two destinations simultaneously:
- **LAN** (192.168.10.10) via Robocopy `/MIR` — true mirror, deletions propagate
- **GCS** (asia-south1) via Rclone `sync` — true mirror, GCS retains 1 older version for 90 days

**Status:** All 7 development phases complete. Code is production-ready pending deployment.

---

## 2. WHAT'S BUILT — COMPLETE FEATURE INVENTORY

### Phase 1 — Foundation

| Component | File | Status |
|-----------|------|--------|
| Project scaffolding | `pyproject.toml`, `.gitignore`, `.env.example` | Done |
| Pydantic config models (13 sub-models) | `models/config_model.py` | Done |
| SQLAlchemy manifest model | `models/manifest_model.py` | Done |
| ScanResult / FileInfo dataclasses | `models/scan_result.py` | Done |
| Loguru rotating log setup | `core/logging_setup.py` | Done |

**Details — Config Models (13 sub-models):**
- `FirmConfig` — firm name
- `PathsConfig` — source drive, LAN destination, log dir, database path, rclone temp dir
- `ScheduleConfig` — enabled, daily_time (HH:MM)
- `BackupScopeConfig` — exclude_folders, exclude_extensions, exclude_patterns
- `LanBackupConfig` — enabled, retry_count, retry_wait_seconds, subprocess_timeout_seconds
- `WolConfig` — enabled, mac_address, server_ip, wake/ping/stability timeouts
- `VssConfig` — enabled, drive_letter, fallback_on_failure
- `CloudBackupConfig` — enabled, provider, bucket, remote_path, bandwidth_limit, chunk_size, retry_count, subprocess_timeout_seconds
- `CloudCredentialsConfig` — credential_name
- `UIConfig` — enabled, host, port, prefect_api_url
- `NotificationsConfig` — SMTP settings, recipients, weekly summary
- `AlertsConfig` — no_changes_warning_days, lan_free_space_warning_gb, backup_duration_warning_minutes
- `TestRestoreConfig` — enabled, sample_count, run_every_n_backups

**Details — Manifest Model:**
- Table: `file_manifest`
- Columns: file_id (Text PK), relative_path (Text unique), file_size (BigInteger), last_modified_timestamp (REAL), checksum (Text), last_seen_at (Text), last_backed_up_lan/cloud (Text nullable), backed_up_to_lan/cloud (Integer default 0)
- Indexes: idx_manifest_relative_path, idx_manifest_last_seen
- Engine: SQLite with WAL mode, foreign_keys=ON, synchronous=NORMAL, cache_size=10000

### Phase 2 — Core Business Logic

| Component | File | Status |
|-----------|------|--------|
| YAML config loader + Pydantic validation | `core/config_loader.py` | Done |
| GCS key path from Windows Credential Manager | `core/config_loader.py:get_gcs_key_path()` | Done |
| ManifestDB (thread-safe SQLite, WAL mode, schema versioning) | `core/manifest_db.py` | Done |
| Change detection scanner (bulk manifest load, os.walk pruning) | `core/scanner.py` | Done |
| xxHash64 checksums (8MB chunked reads) | `core/scanner.py:compute_checksum()` | Done |
| Wake-on-LAN (ping -> WoL magic packet -> poll -> stability buffer) | `core/wol.py` | Done |
| Robocopy /MIR wrapper (bitmask exit codes, per-file failure parsing) | `core/robocopy.py` | Done |
| Rclone sync wrapper (temp config/filter, Windows ACL, finally cleanup) | `core/rclone.py` | Done |
| VSS shadow copy (PowerShell Get-CimInstance, context manager, fallback) | `core/vss.py` | Done |
| Pre-flight checks (20+ checks across 9 categories) | `core/preflight.py` | Done |
| Post-backup verification (LAN checksum, cloud size, dry-run previews) | `core/verify.py` | Done |

**Details — ManifestDB:**
- Thread-safe: all writes acquire `threading.Lock`
- WAL mode enforced on every connection via SQLAlchemy event listener
- Schema versioning with migration support (current SCHEMA_VERSION=1)
- Key methods: `upsert_entry()`, `batch_mark_lan_backed_up()`, `batch_mark_cloud_backed_up()`, `delete_entry()`, `get_all_entries()` (bulk load for 200K+ files), `get_all_paths()`, `get_entry()`, `update_last_seen()`
- Maintenance: `VACUUM`, `PRAGMA wal_checkpoint(TRUNCATE)`, size monitoring

**Details — Scanner Algorithm:**
1. Bulk load all manifest entries into memory dict (avoids 200K+ individual queries)
2. `os.walk(topdown=True)` for in-place directory pruning
3. Per-file: extension check -> pattern check (fnmatch) -> `os.stat()` -> in-memory dict lookup
4. Classification: NEW (not in manifest), UNCHANGED (size+mtime match within 1.0s tolerance), MODIFIED (checksum differs), METADATA CHANGE (checksum matches but size/mtime changed)
5. After walk: detect deleted files (manifest paths minus current paths), remove from manifest
6. Handles VSS device paths (`\\?\GLOBALROOT\...`) by computing relative paths manually

**Details — Robocopy Wrapper:**
- Command: `robocopy source dest /MIR /Z /XJ /FFT /R:3 /W:10 /NP /BYTES /TEE` + exclusions
- Exit code bitmask: bit 4 (16) = FAIL, bit 3 (8) = PARTIAL, bits 0-2 (<=7) = COMPLETE
- Parses output via regex for files_copied, bytes_copied, files_failed
- Parses failed files from `ERROR` lines for selective manifest marking
- Computes checksums for new files after successful backup
- No `shell=True`, uses subprocess argument lists

**Details — Rclone Wrapper:**
- Exit codes: 0=COMPLETE, 1/3/5/7=FAILED, 2/4/6/8=PARTIAL (code 5 allows Prefect retries)
- Creates temp `rclone.conf` with GCS service account, `bucket_policy_only=true`, `location=asia-south1`
- Creates temp filter file converting Windows paths to rclone syntax (`- folder/**`, `- *.ext`, `- pattern`)
- Temp files cleaned up in `finally` blocks
- Windows ACL restriction via `icacls /inheritance:r`
- Also provides `run_rclone_check()` for post-backup integrity verification

**Details — Pre-Flight Checks (20+ checks, 9 categories):**
- System: memory, time sync (NTP)
- Storage: source drive, LAN destination, temp directory, disk space
- Network: DNS resolution, port connectivity, ping
- Credentials: Windows Credential Manager, SMTP config
- Services: VSS service, Prefect API health
- Cloud: GCS key file validation, bucket connectivity (read+write verified), versioning status, rclone version
- Configuration: placeholder/empty value checks, exclude folder existence
- Database: manifest DB schema, log directory writability
- Dry Run: `robocopy /L` preview, `rclone --dry-run` preview
- Binaries: robocopy, rclone, python version
- Severity levels: PASS, WARN, FAIL, SKIP
- `PreflightReport`: `all_passed`, `has_warnings`, `summary()`, `to_dict()`

**Details — VSS Support:**
- Creates shadow copy via PowerShell `Get-CimInstance Win32_ShadowCopy`
- Deletes via `vssadmin Delete Shadow /ID={guid} /Quiet`
- Context manager: create -> yield path -> delete (always in finally)
- Fallback mode: if VSS fails and `fallback_on_failure=True`, yields original drive path

**Details — WoL:**
- Flow: ping -> if offline send WoL magic packet -> poll with ping until timeout -> stability buffer
- Uses `wakeonlan` library for magic packet
- Cross-platform ping command
- Exceptions: `WolError` (base), `WolTimeout` (server didn't respond)
- CLI via Typer: `ping` and `wol` commands

### Phase 3 — Orchestration

| Component | File | Status |
|-----------|------|--------|
| Prefect flow `nightly_backup()` (cron 23:00, 8h timeout, 1 retry) | `flow.py` | Done |
| ConcurrencyGuard (file-based PID lock) | `flow.py:ConcurrencyGuard` | Done |
| Failure email hook (smtplib + keyring) | `flow.py:_on_backup_failure` | Done |
| Success email hook (optional, on every run) | `flow.py:_on_backup_completion` | Done |
| 16 Prefect task wrappers | `tasks/` (16 files) | Done |
| Concurrent LAN+cloud via `ThreadPoolTaskRunner(max_workers=2)` | `flow.py` | Done |
| No-changes warning detection (configurable days threshold) | `flow.py` | Done |
| Overall status computation (COMPLETE / PARTIAL_FAILURE / FAILED) | `flow.py` | Done |

**Details — Flow Execution Order:**
1. Configure Loguru logging
2. Acquire ConcurrencyGuard (file-based PID lock)
3. Load configuration (`load_config_task`)
4. Version config before run (`version_config_task`, keeps last 30)
5. Pre-backup manifest maintenance
6. Create VSS snapshot if enabled (`create_vss_snapshot_task`)
7. Run pre-flight checks (`preflight_task`)
8. Scan source drive (`scan_task`)
9. If no changes: log warning if no changes for N days, collect metrics, return COMPLETE
10. If changes: submit LAN + cloud tasks concurrently
11. Compute overall status from LAN + cloud results
12. If FAILED: raise RuntimeError (triggers on_failure hook)
13. Backup manifest.db to LAN and cloud (`backup_manifest_db_task`)
14. Verify cloud integrity (`verify_cloud_integrity_task`)
15. Sync log files to cloud (`backup_logs_cloud_task`)
16. Collect metrics (`collect_metrics_task`)
17. SQLite maintenance (`maintain_manifest_db_task`)
18. Check LAN disk space, backup duration warnings
19. Test restore verification (every N runs, `test_restore_task`)
20. Generate weekly/monthly reports (`generate_report_task`)
21. Backup config.yaml to LAN and cloud (`backup_config_task`)
22. Finally: delete VSS snapshot, release ConcurrencyGuard

**Details — Flow Configuration:**
- `name="nightly-backup"`, `version="1.2.0"`
- `flow_run_name="backup-{config_path}-{date:%Y%m%d-%H%M%S}"`
- `task_runner=ThreadPoolTaskRunner(max_workers=2)`
- `timeout_seconds=28800` (8 hours)
- `retries=1`, `retry_delay_seconds=300` (5 minutes)
- `on_failure=[_on_backup_failure]`, `on_completion=[_on_backup_completion]`

**Details — Prefect Tasks (16 files):**

| Task | File | Retries | Timeout | Description |
|------|------|---------|---------|-------------|
| `load_config_task` | `tasks/config_task.py` | 0 | - | Loads config.yaml + retrieves GCS key path |
| `version_config_task` | `tasks/config_version_task.py` | 0 | - | Versions config.yaml (keeps last 30) |
| `scan_task` | `tasks/scan_task.py` | 1 | 1h | Scans source drive, returns ScanResult |
| `lan_backup_task` | `tasks/lan_task.py` | 3 (exponential backoff) | 4h | WoL -> Robocopy -> checksum verification |
| `cloud_backup_task` | `tasks/cloud_task.py` | 3 (exponential backoff) | 6h | Rclone sync -> manifest update |
| `preflight_task` | `tasks/preflight_task.py` | 0 | - | Runs all pre-flight checks |
| `verify_cloud_integrity_task` | `tasks/verification_task.py` | 0 | - | Runs `rclone check` for cloud integrity |
| `collect_metrics_task` | `tasks/metrics_task.py` | 0 | - | Collects per-run metrics to JSONL |
| `backup_manifest_db_task` | `tasks/manifest_backup_task.py` | 0 | - | Backs up manifest.db to LAN and cloud |
| `maintain_manifest_db_task` | `tasks/maintenance_task.py` | 0 | - | SQLite VACUUM + WAL checkpoint |
| `backup_logs_cloud_task` | `tasks/log_backup_task.py` | 0 | - | Syncs log files to cloud `_logs/` prefix |
| `test_restore_task` | `tasks/test_restore_task.py` | 0 | 1h | Periodic random file verification from LAN + GCS |
| `generate_report_task` | `tasks/report_task.py` | 0 | - | Generates weekly/monthly email reports |
| `create_vss_snapshot_task` | `tasks/vss_task.py` | 0 | - | Creates VSS shadow copy |
| `delete_vss_snapshot_task` | `tasks/vss_task.py` | 0 | - | Deletes VSS shadow copy |
| `backup_config_task` | `tasks/config_backup_task.py` | 0 | - | Backs up config.yaml to LAN and cloud |

### Phase 4 — Status UI

| Component | File | Status |
|-----------|------|--------|
| FastAPI server (4 endpoints) | `ui/server.py` | Done |
| Status page (Jinja2 + Alpine.js + Tailwind) | `ui/templates/status.html` | Done |
| Manual backup trigger via Prefect API | `ui/server.py:/trigger` | Done |
| Health check endpoint | `ui/server.py:/health` | Done |
| Metrics endpoint | `ui/server.py:/metrics` | Done |
| Graceful degradation when Prefect unavailable | `ui/server.py` | Done |

**Details — Endpoints:**
- `GET /` — Serves status.html showing last run status, next scheduled run, in-progress indicator
- `GET /health` — Checks Prefect API connectivity, returns `{"status": "healthy/degraded"}`
- `POST /trigger` — Creates flow run via Prefect API for manual backup
- `GET /metrics` — Reads latest from `backup_metrics.jsonl`, returns scan/lan/cloud/capacity data

### Phase 5 — Deployment Scripts

| Component | File | Status |
|-----------|------|--------|
| Config validation CLI | `scripts/validate_config.py` | Done |
| Credential Manager setup (interactive) | `scripts/setup_credentials.py` | Done |
| Connection test suite | `scripts/test_connections.py` | Done |
| GCS initial seed (resumable, rate-limited) | `scripts/seed_cloud.py` | Done |
| Restore CLI (list/restore/verify from LAN or GCS) | `scripts/restore.py` | Done |
| Prefect deployment creation | `deploy/create_deployment.py` | Done |
| NSSM service install | `deploy/install_services.bat` | Done |
| NSSM service uninstall | `deploy/uninstall_services.bat` | Done |
| Email notification automation setup | `deploy/setup_email_notifications.py` | Done |
| Prefect worker service install | `deploy/install_service.py` | Done |
| Prefect worker service uninstall | `deploy/uninstall_service.py` | Done |

### Phase 6 — Tests

| Metric | Value |
|--------|-------|
| Total tests collected | 211 |
| Passing | 210 |
| Error | 1 (fixture issue) |
| Test files | 19 |

**Test Files:**

| File | Tests | Coverage |
|------|-------|----------|
| `test_config_loader.py` | Multiple | Valid config, missing fields, invalid MAC, invalid bucket, missing credential |
| `test_scanner.py` | Multiple | New file, modified file (size), modified file (mtime same content), deleted file, excluded folder, excluded extension, excluded pattern, unreadable file, empty directory |
| `test_robocopy_wrapper.py` | Multiple | Exit codes 0/1/7 -> COMPLETE, 8 -> PARTIAL, 16 -> FAILED, timeout, FileNotFoundError |
| `test_rclone_wrapper.py` | Multiple | Exit code 0 -> COMPLETE, 5 -> retried, 7 -> FAILED, temp config created/deleted, temp filter created/deleted |
| `test_wol.py` | 6 | Online server (ping succeeds, no WoL), offline server (WoL sent, polling), timeout, WoL disabled |
| `test_manifest_db.py` | Multiple | WAL mode active, upsert new, upsert update, batch_mark, get_all_paths, thread safety |
| `test_preflight.py` | Multiple | All pre-flight check functions |
| `test_verify.py` | Multiple | LAN checksum, cloud checksum, dry-run LAN, dry-run cloud |
| `test_vss.py` | Multiple | VSS creation, deletion, context manager, fallback |
| `test_flow.py` | Multiple | Flow execution, concurrency guard, email hooks |
| `test_flow_fixes.py` | Multiple | P0 fix verifications |
| `test_ui.py` | Multiple | UI endpoints, health check, trigger, metrics |
| `test_logging_setup.py` | Multiple | Loguru configuration |
| `test_maintenance.py` | Multiple | Manifest DB maintenance |
| `test_restore_report.py` | Multiple | Restore and report tasks |
| `test_restore_verify.py` | 10 | LAN file verify, cloud file verify, restore task (1 fixture error) |
| `test_scripts.py` | Multiple | Deployment scripts |

### Phase 7 — Pre-Flight

| Component | Status |
|-----------|--------|
| Disk space checks (source, LAN, temp) | Done |
| GCS connectivity (read + write verified via test file upload/delete) | Done |
| Network connectivity (ping, DNS, port) | Done |
| Credential validation (Credential Manager, SMTP) | Done |
| Binary checks (robocopy, rclone, python version) | Done |
| Dry-run previews (robocopy /L, rclone --dry-run) | Done |
| VSS service check | Done |
| Prefect API health check | Done |
| Configuration completeness (placeholder detection) | Done |
| Database schema validation | Done |
| Log directory writability | Done |
| GCS versioning status check | Done |
| Rclone version check | Done |

---

## 3. BUG FIXES APPLIED (6 P0 Fixes)

| # | Fix | File | Impact |
|---|-----|------|--------|
| 1 | Manifest drift — parse Robocopy per-file failures | `core/robocopy.py` | Added `_parse_failed_files()` to extract failed file paths from Robocopy output. Manifest now only marks files that actually succeeded, not all changed files. Accurate manifest state on partial failures. |
| 2 | `file_size` column overflow | `models/manifest_model.py` | Changed `Integer` to `BigInteger`. Supports files >2GB (max ~9.2 quintillion bytes vs ~2.1 billion). |
| 3 | Email notifications in `on_failure` hook | `flow.py` | Added `_send_failure_email()` using `smtplib` + `keyring` for credential retrieval. Wired into `_on_backup_failure` hook. Sends HTML + plain text emails. Failure alerts sent immediately. |
| 4 | Rclone exit code 5 -> CLOUD_PARTIAL | `core/rclone.py` | Exit code 5 mapped to `CLOUD_PARTIAL` instead of `CLOUD_FAILED`. Prefect retries work correctly for transient network errors. |
| 5 | Robocopy `/XJ` flag | `core/robocopy.py` | Added `/XJ` to Robocopy command to exclude junction points. Prevents infinite loops from junction points. |
| 6 | Full test suite verification | `tests/` | 210/211 tests passing. All P0 fixes verified by tests. |

---

## 4. SECURITY PRACTICES ENFORCED

| Practice | Implementation |
|----------|---------------|
| No hardcoded values | Everything from `config.yaml` or Windows Credential Manager |
| No `shell=True` | All subprocess calls use argument lists |
| `pathlib.Path` throughout | No `os.path` string concatenation |
| ManifestDB `threading.Lock` | All write operations acquire lock, no exceptions |
| Temp files in `finally` blocks | Rclone config, filter files always cleaned up |
| Config re-read every flow run | Not cached between runs |
| UTC ISO8601 timestamps | All timestamps stored in SQLite as UTC |
| File-based concurrency guard | PID-based lock prevents simultaneous backup runs |
| VSS cleanup in `finally` | Always runs even on failure or retry |
| Windows ACL on temp config | `icacls /inheritance:r` restricts rclone config access |
| GCS key path in Credential Manager | Not stored in config.yaml, only credential lookup name |
| SMTP password in Credential Manager | Retrieved via `keyring.get_password()` at runtime |

---

## 5. ARCHITECTURE DECISIONS (Final — No Changes Planned)

| Decision | Rationale |
|----------|-----------|
| Both destinations are true mirrors (`/MIR` + `sync`) | Client accepted — simpler, no custom versioning logic needed |
| No soft delete / custom versioning / anomaly detection | Permanently out of scope — GCS native versioning provides 90-day safety net |
| xxHash64 (not SHA256 or MD5) | Speed for 200K+ files, collision risk negligible for change detection |
| Checksum deferred for new files | Computed after backup confirmation, avoids double disk I/O |
| Bulk manifest load (dict in memory) | Avoids 200K+ individual queries during scan — O(1) dict access |
| SQLite WAL mode on every connection | Prevents corruption from concurrent access, allows concurrent reads |
| Prefect 3.x self-hosted (not cloud) | Single-machine deployment, no external dependencies beyond GCS |
| Config re-read every run (not cached) | Allows config changes without service restart |
| 1.0 second mtime tolerance | Filesystem quirks can cause minor mtime drift |
| `os.walk(topdown=True)` | Mandatory for in-place `dirnames` pruning of excluded folders |
| `checksum="pending"` for new files | Marked as pending until first backup confirmation, then computed |
| Deleted files removed from manifest | Mirror tools handle deletion, manifest should reflect reality |
| ConcurrencyGuard via PID file | Prevents duplicate runs if cron triggers while previous run still active |
| LAN + cloud run concurrently | `ThreadPoolTaskRunner(max_workers=2)` — independent destinations |
| Single shared ManifestDB instance | Passed to all tasks, threading.Lock shared across threads |

---

## 6. KNOWN ISSUES / GAPS

### 6.1 Test Fixture Error (Minor)
- **File:** `tests/test_restore_verify.py` line 15
- **Issue:** `test_restore_task` is decorated with `@task()` in `tasks/test_restore_task.py`. When pytest imports it, the decorator causes pytest to look for a `database_path` fixture that doesn't exist in conftest.
- **Impact:** 1 test errors out of 211 (210 pass). Does not affect production code.
- **Fix needed:** Either remove `@task` decorator from the task definition in the test import path, or add a `database_path` fixture to `conftest.py`.

### 6.2 Loguru Rotation Issue on Linux (Dev-only)
- Loguru file rotation uses `user.loguru_crtime` extended attribute which doesn't exist on all Linux filesystems.
- Falls back to `st_mtime` but can cause `FileNotFoundError` if temp directories are cleaned between test runs.
- **Impact:** Cosmetic test noise only. Does not affect production (Windows Server 2016).

### 6.3 ROS pytest Plugin Conflict (Dev-only)
- System has ROS humble pytest plugins installed globally that conflict with project tests.
- **Workaround:** Run with `PYTHONPATH=""` to isolate venv from system Python path.
- **Impact:** CI/CD on Windows won't have this issue. Only affects this Linux dev machine.

### 6.4 Missing Production Items (Deployment-Time Only)

These are not code gaps — they are operational items to complete during deployment:

| Item | Priority | Status | Details |
|------|----------|--------|---------|
| GCS bucket creation | Critical | To be done | Create bucket, enable object versioning, set lifecycle rule (delete older versions after 90 days) |
| GCS service account | Critical | To be done | Create service account with Storage Object Admin role, download JSON key |
| Service account permissions | Critical | To be done | Read D:\, read/write LAN share, read/write C:\BackupAgent\, read GCS key, Credential Manager access |
| Python 3.12+ install | Critical | To be done | Install on Windows Server 2016 |
| uv install | Critical | To be done | Python package manager |
| rclone install | Critical | To be done | Copy rclone.exe to C:\BackupAgent\ |
| NSSM install | Critical | To be done | Windows service wrapper |
| `config.yaml` — bucket field | Critical | Empty (`""`) | Must be filled with real bucket name before first run |
| `config.yaml` — WoL MAC address | Important | Empty (`""`) | Must be filled if WoL enabled (get via `getmac /v` on backup server) |
| `config.yaml` — SMTP settings | Important | All empty | smtp_host, smtp_username, sender, recipients must be filled for email alerts |
| Windows Credential Manager — GCS | Critical | To be done | Store GCS key path: Service=`BackupAgent`, Name=`BackupAgent_GCS` |
| Windows Credential Manager — SMTP | Important | To be done | Store SMTP password: Service=`BackupAgent`, Name=`BackupAgent_SMTP` |
| `config.yaml` — exclude folders | Review | Set | 10 folders excluded — confirm with client before go-live |

---

## 7. PRODUCTION READINESS ASSESSMENT

### Code Readiness: READY

- All 7 phases implemented
- 210/211 tests passing (1 fixture issue, non-critical)
- All 6 P0 bug fixes applied and verified
- Security practices enforced throughout
- Comprehensive pre-flight checks (20+ checks)
- Post-backup integrity verification (LAN checksum + cloud rclone check)
- Failure email notifications wired into flow hooks
- Status UI with health check, manual trigger, metrics
- Deployment scripts complete (NSSM, Prefect deployment, credential setup)
- Config versioning (keeps last 30)
- Log backup to cloud for disaster recovery
- Test restore verification (periodic random file checks)
- Weekly/monthly report generation
- SQLite maintenance (VACUUM, WAL checkpoint)
- Capacity tracking (LAN free space, total source size)

### Deployment Readiness: PENDING OPERATIONAL SETUP

The code is ready. What's needed before go-live:

1. **Infrastructure setup** — GCS bucket + versioning + lifecycle, service account + permissions, Python 3.12+/uv/rclone/NSSM installed
2. **Configuration** — Fill `config.yaml` with real values (bucket name, WoL MAC, SMTP host/user/sender/recipients)
3. **Credentials** — Store GCS key path and SMTP password in Windows Credential Manager
4. **Initial seed** — Run `scripts/seed_cloud.py` for first full GCS upload (resumable, rate-limited)
5. **Service installation** — Run `deploy/install_services.bat` as Administrator (creates PrefectServer, PrefectWorker, BackupUI services)
6. **Deployment creation** — Run `deploy/create_deployment.py` (registers flow with cron schedule)
7. **First run verification** — Manual trigger via UI, verify LAN mirror, verify GCS mirror, verify emails, verify UI updates

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| First scan takes 20-40 min (cold manifest) | Certain | Low | Expected behavior, runs at 23:00 when office is closed |
| Locked Tally/Winman files | Low | Low | VSS support available with fallback to direct access; Robocopy /Z retries |
| LAN server offline at backup time | Medium | Low | WoL handles automatically — sends magic packet, polls until online, waits stability buffer |
| Network interruption during cloud upload | Medium | Low | Rclone retries (3x, 30s sleep between), Prefect task retries (3x exponential backoff, 60s factor) |
| manifest.db corruption | Low | Medium | Pre/post-backup manifest backup to LAN+GCS, WAL mode, threading.Lock on all writes |
| Config misconfiguration | Medium | High | Pre-flight checks catch most issues, `validate_config.py` script before service start |
| GCS bucket not writable | Low | Medium | Pre-flight check verifies read+write (uploads test file, then deletes) |
| Backup runs longer than 8 hours | Low | Medium | Flow timeout kills run, raises exception, sends failure email, next run proceeds normally |
| Both LAN and cloud fail | Low | High | Flow raises RuntimeError, Prefect marks FAILED, email alert sent, manual investigation needed |

---

## 8. PROJECT FILE STRUCTURE (As Built)

```
AAM_BACKUP_V2/
├── flow.py                          # Prefect flow definition (entry point)
├── config.yaml                      # Configuration file (all settings)
├── pyproject.toml                   # Project metadata, dependencies, pytest config
├── uv.lock                          # Locked dependencies
├── .env.example                     # Environment variable documentation
├── .gitignore                       # Git ignore rules
├── README.md                        # Project overview and quick start
├── DECISIONS.md                     # Decision log
├── DEPLOYMENT.md                    # Deployment guide
├── DR_RUNBOOK.md                    # Disaster recovery procedures
├── ENTERPRISE_COMPARISON.md         # Comparison with enterprise backup solutions
├── V2_VS_PRODUCTION_COMPARISON.md   # V2 vs production comparison
├── plan.md                          # Complete technical specification
├── AGENTS.md                        # Agent context file
│
├── core/                            # Business logic
│   ├── __init__.py
│   ├── config_loader.py             # YAML loader + Pydantic validation + Credential Manager
│   ├── logging_setup.py             # Loguru configuration (rotating daily files)
│   ├── manifest_db.py               # ManifestDB (thread-safe SQLite, WAL mode)
│   ├── preflight.py                 # 20+ pre-flight checks across 9 categories
│   ├── rclone.py                    # Rclone sync wrapper + rclone check
│   ├── robocopy.py                  # Robocopy /MIR wrapper + exit code parsing
│   ├── scanner.py                   # Change detection engine (os.walk, xxHash64)
│   ├── verify.py                    # Post-backup verification + dry-run previews
│   ├── vss.py                       # Volume Shadow Copy support
│   └── wol.py                       # Wake-on-LAN (ping + magic packet)
│
├── models/                          # Data models
│   ├── __init__.py
│   ├── config_model.py              # Pydantic config models (13 sub-models)
│   ├── manifest_model.py            # SQLAlchemy FileManifest model
│   └── scan_result.py               # ScanResult and FileInfo dataclasses
│
├── tasks/                           # Prefect task wrappers (16 files)
│   ├── __init__.py
│   ├── cloud_task.py                # Cloud backup (Rclone sync)
│   ├── config_backup_task.py        # Config.yaml backup to LAN + cloud
│   ├── config_task.py               # Config loading + GCS key retrieval
│   ├── config_version_task.py       # Config versioning (keeps last 30)
│   ├── lan_task.py                  # LAN backup (WoL + Robocopy + checksum)
│   ├── log_backup_task.py           # Log files sync to cloud
│   ├── maintenance_task.py          # SQLite maintenance (VACUUM, checkpoint)
│   ├── manifest_backup_task.py      # manifest.db backup to LAN + cloud
│   ├── metrics_task.py              # Per-run metrics collection (JSONL)
│   ├── preflight_task.py            # Pre-flight checks execution
│   ├── report_task.py               # Weekly/monthly report generation
│   ├── scan_task.py                 # Source drive scanning
│   ├── test_restore_task.py         # Periodic random file verification
│   ├── verification_task.py         # Cloud integrity verification (rclone check)
│   └── vss_task.py                  # VSS snapshot create/delete
│
├── ui/                              # Status UI
│   ├── __init__.py
│   ├── server.py                    # FastAPI server (/, /health, /trigger, /metrics)
│   └── templates/
│       └── status.html              # Status page (Alpine.js + Tailwind)
│
├── scripts/                         # CLI tools
│   ├── __init__.py
│   ├── restore.py                   # Restore CLI (list/restore/verify)
│   ├── seed_cloud.py                # Initial GCS seed (resumable)
│   ├── setup_credentials.py         # Credential Manager setup
│   ├── test_connections.py          # Connection test suite
│   └── validate_config.py           # Config validation CLI
│
├── deploy/                          # Deployment scripts
│   ├── __init__.py
│   ├── create_deployment.py         # Prefect deployment creation
│   ├── install_service.py           # NSSM service install
│   ├── install_services.bat         # Batch: install all services
│   ├── setup_email_notifications.py # Prefect email block + automations
│   ├── uninstall_service.py         # NSSM service uninstall
│   └── uninstall_services.bat       # Batch: uninstall all services
│
├── tests/                           # Pytest suite (19 files, 211 tests)
│   ├── __init__.py
│   ├── conftest.py                  # Shared fixtures
│   ├── test_config_loader.py
│   ├── test_flow.py
│   ├── test_flow_fixes.py
│   ├── test_logging_setup.py
│   ├── test_maintenance.py
│   ├── test_manifest_db.py
│   ├── test_preflight.py
│   ├── test_rclone_wrapper.py
│   ├── test_restore_report.py
│   ├── test_restore_verify.py
│   ├── test_robocopy_wrapper.py
│   ├── test_scanner.py
│   ├── test_scripts.py
│   ├── test_ui.py
│   ├── test_verify.py
│   ├── test_vss.py
│   └── test_wol.py
│
└── logs/                            # Loguru rotating daily logs (created at runtime)
```

---

## 9. DEPENDENCIES

### Runtime Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | >=0.136.1 | Status UI web framework |
| httpx | >=0.28.1 | Async HTTP client (UI -> Prefect API) |
| keyring | >=25.7.0 | Windows Credential Manager access |
| loguru | >=0.7.3 | Rotating daily log files |
| prefect | >=3.7.1 | Workflow orchestration |
| prefect-email | >=0.4.0 | Prefect email automation |
| pydantic | >=2.13.4 | Configuration validation |
| pyyaml | >=6.0.3 | YAML config parsing |
| sqlalchemy | >=2.0.49 | SQLite ORM |
| typer | >=0.25.1 | CLI framework |
| uvicorn | >=0.47.0 | ASGI server for FastAPI |
| wakeonlan | >=3.1.0 | WoL magic packet sending |
| xxhash | >=3.7.0 | Fast checksum computation |

### Optional Dependencies (preflight extra)
| Package | Version | Purpose |
|---------|---------|---------|
| psutil | >=6.0.0 | Memory checks in pre-flight |
| ntplib | >=0.4.0 | Time sync verification (NTP) |

### Development Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| freezegun | >=1.5.5 | Time mocking in tests |
| mypy | >=2.1.0 | Static type checking |
| pytest | >=9.0.3 | Test framework |
| pytest-asyncio | >=1.3.0 | Async test support |
| pytest-cov | >=7.1.0 | Coverage reporting |
| pytest-mock | >=3.15.1 | Mocking utilities |
| ruff | >=0.15.13 | Linting and formatting |

---

## 10. RECOMMENDED NEXT STEPS

1. **Fix the 1 test error** — `tests/test_restore_verify.py` fixture issue (5 min fix)
   - Add `database_path` fixture to `conftest.py` or adjust test import to avoid `@task` decorator side effects

2. **Deploy to staging/test server** — Validate end-to-end on a non-production Windows Server
   - Install Python 3.12+, uv, rclone, NSSM
   - Create test GCS bucket
   - Fill `config.yaml` with test values
   - Run full backup cycle

3. **Run first full backup** — Monitor timing, verify LAN mirror, verify GCS mirror
   - Expect 20-40 minutes for cold manifest (first scan)
   - Verify file counts match between source, LAN, and GCS
   - Verify manifest.db is populated correctly

4. **Configure email notifications** — Fill SMTP settings, verify failure/success emails
   - Set smtp_host, smtp_port, smtp_username, sender, recipients
   - Store SMTP password in Credential Manager
   - Trigger test failure to verify email delivery

5. **Schedule go-live** — After 2-3 successful test runs, switch production to automated schedule
   - Confirm with client that Tally/Winman close at end of day (or enable VSS)
   - Confirm exclusion list with client
   - Set cron schedule to 23:00 IST
   - Monitor first 7 production runs closely

---

## 11. QUICK REFERENCE — KEY COMMANDS

```bash
# Install dependencies
uv sync

# Install with preflight extras
uv sync --extra preflight

# Run tests
PYTHONPATH="" .venv/bin/python -m pytest tests/ -v --tb=short

# Run specific test file
PYTHONPATH="" .venv/bin/python -m pytest tests/test_scanner.py -v

# Validate configuration
uv run scripts/validate_config.py validate

# Test connections
uv run scripts/test_connections.py test

# Run linting
uv run ruff check .

# Run type checking
uv run mypy .

# Format code
uv run ruff check --fix .

# Start Prefect server
prefect server start

# Start Prefect worker
PREFECT_API_URL=http://127.0.0.1:4200/api prefect worker start --pool default

# Deploy flow
uv run deploy/create_deployment.py create

# Start status UI
uv run uvicorn ui.server:app --host 0.0.0.0 --port 8080

# Run flow manually
uv run python flow.py
```

---

*Report generated from live codebase analysis on 2026-05-18. All file contents, test results, and configurations verified against repository state.*
