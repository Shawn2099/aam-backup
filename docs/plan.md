Locked. All decisions final. Writing now.

---

# BACKUP AUTOMATION SYSTEM
## Phase 1 — Complete Scope & Technical Specification
### For AI-Assisted Development — Maximum Clarity Document
#### Version 3.0 — Final

---

# SECTION 1 — DOCUMENT PURPOSE AND RULES

## 1.1 Who This Document Is For

This document is written for an AI development tool (Claude, ChatGPT, or equivalent) or a human developer building Phase 1 of the Backup Automation System. Every decision is made. Every ambiguity is resolved. Every integration point is specified. Every provision for Phase 2 is explicitly marked.

Any developer reading this must be able to build Phase 1 completely without asking a single clarifying question.

## 1.2 How To Read This Document

Statements marked **[PHASE 1]** are in scope and must be built now.

Statements marked **[PHASE 2 ONLY]** mean: do not build, do not stub, do not reference in Phase 1 code at all.

Statements marked **[PHASE 2 PROVISION]** mean: create the stub, hook, placeholder, or database field now so a future enhancement can plug in without touching Phase 1 code. Do not implement the feature itself.

Statements marked **[PHASE 2 ONLY]** mean: do not build, do not stub, do not reference in Phase 1 code at all.

## 1.3 Absolute Rules For Implementation

No hardcoded values anywhere in the codebase. Every value comes from config.yaml or Windows Credential Manager.

No shell=True in any subprocess call. Ever. All subprocess calls use argument lists.

All file paths use pathlib.Path throughout. Never os.path string concatenation.

All database writes acquire the ManifestDB internal lock. No exceptions.

All temporary files are deleted in finally blocks. No exceptions.

Config is re-read at the start of every Prefect flow run. Not cached between runs.

Timestamps stored in SQLite are always UTC ISO8601. Displayed in logs as local time.

---

# SECTION 2 — WHAT PHASE 1 IS

## 2.1 The Single Sentence Definition

Phase 1 automates what the client currently does manually: copy changed files from the live server to the backup server and to cloud storage, every night, reliably, with basic visibility into what happened.

## 2.2 Phase 1 Delivers Exactly These Things

**[PHASE 1]** Automated daily incremental mirror copy of D:\ on AAMBDC001 to LAN backup server via Robocopy /MIR — true mirror, deletions propagate.

**[PHASE 1]** Automated daily incremental mirror copy of D:\ on AAMBDC001 to Google Cloud Storage via Rclone sync — true mirror, deletions propagate.

**[PHASE 1]** Both destinations run simultaneously and independently every night at 23:00 local server time.

**[PHASE 1]** Wake-on-LAN to power on backup server if offline. No automatic shutdown (DNS risk).

**[PHASE 1]** Change Detection Engine tracking which files changed since last backup via SQLite manifest.

**[PHASE 1]** Prefect 3.x self-hosted as workflow orchestrator — scheduling, state management, run history, task logs, retry logic.

**[PHASE 1]** Prefect email automation for failure alerts — zero custom notification code.

**[PHASE 1]** One FastAPI HTML status page accessible on LAN — last run result, next run time, manual trigger button.

**[PHASE 1]** Loguru rotating daily log files.

**[PHASE 1]** Windows Service deployment via NSSM for both Prefect server and Prefect worker.

**[PHASE 1]** Deployment and connection test scripts.

## 2.3 Phase 1 Explicitly Does Not Deliver

**[PHASE 2 ONLY]** Full notification system — daily run email, weekly summary via smtplib.

**[PHASE 2 ONLY]** Full UI dashboard — backup history table, restore interface, log viewer, audit report.

**[PHASE 2 ONLY]** Automatic backup server shutdown.

**[PHASE 2 ONLY]** SMART disk health monitoring.

**[PHASE 2 ONLY]** Restore interface.

**[PHASE 2 ONLY]** PyInstaller packaging — decided after Phase 1 is working.

**Note:** Soft delete, custom file versioning, anomaly detection, and integrity verification are permanently out of scope. Both LAN and cloud destinations are true mirrors of the source. Cloud provider native versioning (GCS object versioning with 1 older version retained for 90 days) and lifecycle retention rules provide protection against accidental deletion or corruption. No custom versioning or soft-delete logic is built.

---

# SECTION 3 — ENVIRONMENT

## 3.1 Live Server — Source and Agent Host

```
Hostname:         AAMBDC001
IP Address:       192.168.10.5
OS:               Windows Server 2016 Datacenter
Domain Role:      Primary Domain Controller for caaam.com
File Server Role: Yes — primary data store
RAM:              128GB
CPU:              Intel Xeon E5 series
NIC:              TeamNIC — NIC teaming enabled, ~2Gbps combined
Source Drive:     D:\ — approximately 370GB, 40,000+ folders, estimated 200,000+ files
Python:           3.11+ installed during deployment
Rclone:           Installed at C:\BackupAgent\rclone.exe during deployment
NSSM:             Installed during deployment
Prefect Server:   Self-hosted, running on this machine as Windows Service
Prefect DB:       SQLite at C:\BackupAgent\prefect.db
Prefect UI:       http://localhost:4200 and http://192.168.10.5:4200
```

## 3.2 Backup Server — LAN Destination

```
IP Address:       192.168.10.10
Domain Role:      Also serves as Domain DNS server for caaam.com
Share Path:       \\192.168.10.10\hp srv manual backup$
Share Type:       Hidden SMB share ($ suffix)
Power:            Manually managed by staff — powered on before backup, off after
WoL MAC:          [Set in config.yaml during deployment — obtained via getmac /v]
Critical Note:    This server is the DNS server for caaam.com
                  Automatic shutdown after backup would break domain DNS
                  Therefore automatic shutdown is NOT implemented in Phase 1
                  Staff manually power off after backup completes
Authentication:   Domain admin account running the Windows Service
                  has implicit access to SMB share — no separate auth needed
```

## 3.3 Cloud Destination — Google Cloud Storage

```
Provider:         Google Cloud Storage
Region:           asia-south1 (Mumbai) — data residency in India
Bucket:           [Created during deployment — name set in config.yaml]
Auth Method:      GCS service account JSON key file
Key Location:     C:\BackupAgent\gcs_service_account.json
                  ACL: readable only by service account
Credential Store: Path to key file stored in Windows Credential Manager
                  Service: BackupAgent
                  Name: BackupAgent_GCS
                  Value: C:\BackupAgent\gcs_service_account.json
Bucket Settings:  Object versioning enabled (provider-side, set during deployment)
                  Retains 1 older version per object
                  Lifecycle rule: delete older versions after 90 days
                  Uniform bucket-level access enabled
                  Public access blocked
                  Result: Latest data always present. Previous version retained for 90 days as safety net.
Remote Path:      D_Drive_Backup (root folder inside bucket)
                  All backed-up files sit under this path
                  Mirrors D:\ structure exactly
```

## 3.4 Network

```
LAN:              192.168.10.x subnet
                  Both servers on same subnet — WoL broadcasts work
Switch:           [Model confirmed during deployment — WoL broadcast support required]
Internet:         100Mbps, 95-99% uptime
SMTP Outbound:    Port 587 — tested and confirmed open
DNS:              192.168.10.10 (backup server) — internal
                  8.8.4.4 — external fallback
```

---

# SECTION 4 — WHAT GETS BACKED UP

## 4.1 Source

The entire D:\ drive on AAMBDC001 is the backup source. Everything under D:\ is backed up unless explicitly excluded.

This is a change from the original AAM-only design. The client wants the whole drive backed up.

## 4.2 Default Exclusion List

These are the defaults pending client confirmation from the questionnaire. The exclusion list is entirely config-driven. Adding or removing an exclusion requires only a config.yaml change and service restart.

**Excluded folders — these entire folder trees are skipped:**

```
D:\WINMAN\Winman's mir bkup       — Winman internal backup copies (redundant)
D:\WINMAN\winmanbackup             — Winman internal backup copies (redundant)
D:\WINMAN\winman_backup            — Winman internal backup copies (redundant)
D:\WINMAN\winman__backup           — Winman internal backup copies (redundant)
D:\Winman's mir bkup               — Winman internal backup copies (redundant)
D:\winman_backup                   — Winman internal backup copies (redundant)
D:\Common Folder                   — Software installers, no data value
D:\DELL SRV F                      — Single shortcut file, no value
D:\Software_IT                     — 35GB software installers, no data value
D:\BackupAgent                     — Our own agent directory, never back up
```

**Excluded file extensions — these file types are skipped everywhere:**

```
.lnk    — Windows shortcuts
.tmp    — Temporary files
.temp   — Temporary files
```

**Excluded filename patterns — these patterns are skipped everywhere:**

```
~$*         — Office temporary lock files
desktop.ini — Windows folder metadata
Thumbs.db   — Windows thumbnail cache
```

## 4.3 What Is Included — Explicitly Confirmed

```
D:\AAM WORKS          — Primary client work files — INCLUDED
D:\AAM Office         — Firm internal documents — INCLUDED
D:\ALSHABGROUPDATA    — Group client data — INCLUDED
D:\TallyPrime         — Tally accounting software and live data — INCLUDED
D:\WINMAN             — Winman active data (not its internal backups) — INCLUDED
D:\RAASTALLY          — Tally related files — INCLUDED
```

## 4.4 Tally and Winman File Handling

TallyPrime and Winman write live database files during business hours. Backup runs at 23:00 when office is closed. Risk of locked files is low but not zero.

Robocopy /Z flag (restartable mode) and /R /W retry flags handle locked files gracefully — retries the file, logs it as skipped if still locked, continues job. Since both destinations are true mirrors, skipped locked files remain unchanged on the backup — they will be retried on the next nightly run. This is acceptable.

VSS shadow copy for locked file guarantee is not implemented. If the client confirms that Tally and Winman do NOT close at end of day, VSS must be added immediately. Default assumption is they close at end of day.

## 4.5 Cloud Structure

Cloud bucket mirrors D:\ exactly under the remote_path prefix.

```
GCS Bucket: [bucket-name]
  └── D_Drive_Backup/
        └── AAM WORKS/
              └── [mirrors D:\AAM WORKS\ exactly]
        └── AAM Office/
        └── ALSHABGROUPDATA/
        └── TallyPrime/
        └── WINMAN/
        └── RAASTALLY/
```

This structure is human-browsable in the GCS console. A non-technical person can log into GCS and find a specific file by navigating folders exactly as they would on Windows Explorer.

---

# SECTION 5 — SYSTEM ARCHITECTURE

## 5.1 Architecture Pattern

Single-machine deployment. All components run on AAMBDC001. No external servers except GCS.

Prefect 3.x self-hosted is the orchestration backbone. Our code is a set of Prefect tasks wrapped in a Prefect flow. Prefect handles everything else — scheduling, state, retry, logging, UI.

Our custom code is responsible only for business logic — change detection, Robocopy subprocess, Rclone subprocess, WoL, manifest database, status UI, config loading.

## 5.2 Component Map

```
AAMBDC001 (192.168.10.5)
│
├── [WINDOWS SERVICE] PrefectServer
│     Binary:      C:\Python311\Scripts\prefect.exe
│     Args:        server start --host 0.0.0.0 --port 4200
│     Database:    C:\BackupAgent\prefect.db (SQLite)
│     UI:          http://0.0.0.0:4200
│     Env:         PREFECT_API_DATABASE_CONNECTION_URL=
│                  sqlite+aiosqlite:///C:/BackupAgent/prefect.db
│     Purpose:     Stores flow run state, schedules, task logs
│                  Serves Prefect UI
│
├── [WINDOWS SERVICE] PrefectWorker
│     Binary:      C:\Python311\Scripts\prefect.exe
│     Args:        worker start --pool backup-pool --type process
│     Account:     [Service account provided during deployment]
│     Env:         PREFECT_API_URL=http://127.0.0.1:4200/api
│     Purpose:     Polls Prefect server for scheduled runs
│                  Executes backup flow when triggered
│
├── [WINDOWS SERVICE] BackupUI
│     Binary:      C:\Python311\python.exe
│     Args:        C:\BackupAgent\ui\server.py
│     Port:        8080
│     Purpose:     Serves simple HTML status page to LAN
│
├── [PREFECT FLOW] nightly-backup
│     File:        C:\BackupAgent\flow.py
│     Schedule:    Cron 0 23 * * * Asia/Kolkata
│     Work Pool:   backup-pool
│     Runner:      ThreadPoolTaskRunner(max_workers=2)
│     Tasks:
│       1. load_config_task
│       2. scan_task
│       3. lan_backup_task (concurrent)
│       4. cloud_backup_task (concurrent)
│
├── [OUR CODE] C:\BackupAgent\
│     flow.py              — Prefect flow definition
│     tasks\               — Four Prefect task modules
│     core\                — Business logic modules
│     models\              — Pydantic and SQLAlchemy models
│     ui\                  — FastAPI status page
│     scripts\             — Deployment and setup scripts
│     tests\               — Pytest test suite
│     config.yaml          — Single config file
│     manifest.db          — FileManifest SQLite database
│     prefect.db           — Prefect state database
│     logs\                — Loguru rotating daily logs
│     rclone_temp\         — Temp rclone configs (deleted after each run)
│     rclone.exe           — Rclone binary
│
├── [DATA] D:\             — Source — everything backed up per exclusion list
│
└── [DATA] C:\BackupAgent\ — Agent files — excluded from backup
```

## 5.3 Data Flow — One Complete Backup Run

```
23:00:00  Prefect scheduler triggers nightly-backup flow
          Prefect creates flow run record in prefect.db
          PrefectWorker picks up run from backup-pool

23:00:01  Task 1: load_config_task
          Reads C:\BackupAgent\config.yaml via pydantic-settings
          Validates every field via Pydantic validators
          Retrieves GCS key path from Windows Credential Manager via keyring
          Returns (AppConfig, gcs_key_path) to flow
          If config invalid: flow fails immediately, Prefect marks FAILED
          Prefect email automation sends failure alert

23:00:05  Task 2: scan_task
          Opens ManifestDB connection to C:\BackupAgent\manifest.db
          Walks D:\ using os.walk(topdown=True)
          Prunes excluded folders IN PLACE from dirnames before descent
          For each file: reads size and mtime via os.stat
          Compares against FileManifest entry by relative_path (indexed)
          Computes xxHash64 checksum ONLY when size or mtime differs
          Produces ScanResult: new_files, modified_files, deleted_files lists
          Updates last_seen_at for unchanged files
          Inserts pending manifest entries for new files
          Returns ScanResult to flow

23:10:00  Flow evaluates: has_changes?
          If no changes: flow completes immediately — COMPLETE
          If changes: submits Task 3 and Task 4 simultaneously

23:10:01  Task 3: lan_backup_task          Task 4: cloud_backup_task
          [CONCURRENT — both start now]    [CONCURRENT — both start now]

          Checks if backup server online    Writes temp rclone.conf
          via ping                          Applies Windows ACL to temp file
          If offline: sends WoL packet      Writes temp filter file
          Polls until online (5 min max)    Constructs rclone sync command
          Waits 30s stability buffer        Executes rclone subprocess
          Constructs Robocopy command       Parses exit codes
          Executes Robocopy subprocess      Retries on exit code 5
          Parses exit codes via bitmask     Updates manifest for cloud
          Updates manifest for LAN          Deletes temp files in finally
          Returns LAN result dict           Returns cloud result dict

          [Both tasks complete — flow collects results]

23:52:00  Flow computes overall status
          Both complete:     COMPLETE
          One failed:        PARTIAL_FAILURE
          Both failed:       FAILED
          Writes summary to Loguru log
          If FAILED: raises exception
          Prefect marks flow run as Completed or Failed
          If Failed: Prefect email automation fires failure alert

          [Flow run visible in Prefect UI with full task logs]
          [Status page at http://192.168.10.5:8080 updates on next refresh]
```

## 5.4 Concurrency Model

LAN backup and cloud backup run concurrently via Prefect's ThreadPoolTaskRunner with max_workers=2.

Both tasks are submitted using task.submit() which returns futures. The flow calls future.result() on both to wait for completion. Both futures must complete before the flow determines overall status.

Thread safety is handled by ManifestDB's internal threading.Lock on all write operations. Reads do not need the lock — SQLite WAL mode allows concurrent reads.

The Prefect flow itself (the orchestrator thread) never touches SQLite directly. Only the task threads do, via ManifestDB methods.

---

# SECTION 6 — PROJECT FILE STRUCTURE

Every file. Every directory. Every purpose. No ambiguity.

```
C:\BackupAgent\
│
├── config.yaml
│     Single config file. All settings. Re-read every flow run.
│     Never modified by the software.
│
├── flow.py
│     Prefect flow definition.
│     Imports and calls the four task modules.
│     Entry point for Prefect worker execution.
│
├── tasks\
│   ├── __init__.py
│   ├── config_task.py
│   │     Prefect task: load_config_task()
│   │     Calls core.config_loader.load_config()
│   │     Returns (AppConfig, gcs_key_path)
│   │
│   ├── scan_task.py
│   │     Prefect task: scan_task(config, db)
│   │     Calls core.scanner.scan_drive()
│   │     Returns ScanResult
│   │
│   ├── lan_task.py
│   │     Prefect task: lan_backup_task(config, scan_result, db)
│   │     Calls core.wol.ensure_server_online()
│   │     Calls core.robocopy.run_robocopy()
│   │     Updates manifest via db.batch_mark_lan_backed_up()
│   │     Returns result dict
│   │
│   └── cloud_task.py
│         Prefect task: cloud_backup_task(config, gcs_key_path, scan_result, db)
│         Calls core.rclone.run_rclone()
│         Updates manifest via db.batch_mark_cloud_backed_up()
│         Returns result dict
│
├── core\
│   ├── __init__.py
│   ├── config_loader.py
│   │     load_config() — reads yaml, validates, retrieves credentials
│   │     ConfigurationError — custom exception
│   │
│   ├── manifest_db.py
│   │     ManifestDB class — all SQLite operations
│   │     Internal threading.Lock for write safety
│   │     WAL mode enforced on every connection
│   │
│   ├── scanner.py
│   │     scan_drive(config, db) — full D:\ walk with exclusions
│   │     compute_checksum(path) — xxHash64
│   │     is_excluded_folder(), is_excluded_extension(), is_excluded_pattern()
│   │
│   ├── wol.py
│   │     ensure_server_online(config) — ping check then WoL if needed
│   │     ping_host(ip) — single ICMP ping via subprocess
│   │     WolError, WolTimeout — custom exceptions
│   │
│   ├── robocopy.py
│   │     run_robocopy(config) — subprocess wrapper
│   │     _classify_exit_code(code) — bitmask evaluation
│   │     _parse_robocopy_output(output) — extract files/bytes counts
│   │     RobocopyResult dataclass
│   │
│   ├── rclone.py
│   │     run_rclone(config, gcs_key_path) — subprocess wrapper
│   │     _write_temp_config() — secure temp file with ACL
│   │     _write_filter_file() — exclusion rules for rclone
│   │     _classify_exit_code(code) — exit code to status mapping
│   │     RcloneResult dataclass
│   │
│   └── logging_setup.py
│         configure_logging(log_dir) — Loguru two-sink setup
│         File sink: rotating daily, 30-day retention, UTF-8
│         Stderr sink: WARNING and above
│
├── models\
│   ├── __init__.py
│   ├── config_model.py
│   │     AppConfig — top-level pydantic-settings BaseSettings
│   │     FirmConfig, PathsConfig, ScheduleConfig, BackupScopeConfig
│   │     LanBackupConfig, WolConfig, CloudBackupConfig
│   │     CloudCredentialsConfig, UIConfig
│   │     All validators defined on each sub-model
│   │
│   ├── manifest_model.py
│   │     FileManifest — SQLAlchemy declarative model
│   │     All columns defined with types and constraints
│   │     All indexes defined in __table_args__
│   │
│   └── scan_result.py
│         FileInfo dataclass — one file found during scan
│         ScanResult dataclass — output of scan_drive()
│
├── ui\
│   ├── __init__.py
│   ├── server.py
│   │     FastAPI app — single route GET /
│   │     Reads last flow run state from Prefect API
│   │     Reads next scheduled run from Prefect API
│   │     Serves rendered HTML status page
│   │     POST /trigger — calls Prefect API to create flow run
│   │     Runs on port 8080 via uvicorn
│   │
│   └── templates\
│         status.html
│           Single HTML file — Alpine.js for interactivity
│           Tailwind CSS via CDN
│           Three sections: last run status, next run countdown, trigger button
│           Auto-refreshes every 60 seconds
│
├── scripts\
│   ├── setup_credentials.py
│   │     Interactive script to store GCS key path in Credential Manager
│   │     Run once during deployment as service account
│   │
│   ├── validate_config.py
│   │     Loads config and prints validation result
│   │     Run before starting services to confirm config is correct
│   │
│   ├── seed_cloud.py
│   │     One-time initial upload of full D:\ to GCS
│   │     Resumable — can be interrupted and restarted
│   │     Rate limited — does not saturate internet connection
│   │     Run before first nightly backup to establish baseline
│   │     Separate from nightly flow — standalone script
│   │
│   ├── test_connections.py
│   │     Tests all connections before go-live
│   │     Tests: config valid, D:\ accessible, LAN share accessible,
│   │            GCS bucket accessible, Prefect server responding,
│   │            backup server pingable
│   │     All tests must pass before services start
│   │
├── deploy\
│   ├── install_services.bat
│   │     NSSM commands to install PrefectServer, PrefectWorker, BackupUI
│   │     Sets all service parameters, accounts, recovery actions
│   │
│   ├── uninstall_services.bat
│   │     Stops and removes all three Windows Services
│   │
│   └── create_deployment.py
│         Registers nightly-backup flow as Prefect deployment
│         Sets cron schedule 0 23 * * * Asia/Kolkata
│         Sets work pool backup-pool
│         Run once after Prefect server is started
│
├── tests\
│   ├── __init__.py
│   ├── conftest.py
│   │     Shared fixtures: temp config, temp database, mock scan results
│   │
│   ├── test_config_loader.py
│   │     Valid config loads correctly
│   │     Missing required field raises ConfigurationError with field name
│   │     Invalid MAC address format raises ConfigurationError
│   │     Invalid bucket name raises ConfigurationError
│   │     Missing GCS credential raises ConfigurationError
│   │
│   ├── test_scanner.py
│   │     New file correctly classified as new
│   │     Modified file (size change) correctly classified as modified
│   │     Modified file (mtime change, same content) NOT classified as modified
│   │     Deleted file correctly identified
│   │     Excluded folder not walked
│   │     Excluded extension not included
│   │     Excluded pattern not included
│   │     Unreadable file added to cannot_read list
│   │     Empty directory handled without error
│   │
│   ├── test_robocopy_wrapper.py
│   │     Exit code 0 → LAN_COMPLETE
│   │     Exit code 1 → LAN_COMPLETE
│   │     Exit code 7 → LAN_COMPLETE
│   │     Exit code 8 → LAN_PARTIAL
│   │     Exit code 16 → LAN_FAILED
│   │     Timeout raises handled → LAN_FAILED
│   │     FileNotFoundError handled → LAN_FAILED
│   │
│   ├── test_rclone_wrapper.py
│   │     Exit code 0 → CLOUD_COMPLETE
│   │     Exit code 5 → retried up to retry_count times
│   │     Exit code 7 → CLOUD_FAILED
│   │     Temp config created and deleted in finally
│   │     Temp filter file created and deleted in finally
│   │     Temp config deleted even when rclone raises exception
│   │
│   ├── test_wol.py
│   │     Online server: ping succeeds, WoL packet NOT sent
│   │     Offline server: ping fails, WoL packet sent, polling starts
│   │     Timeout: WolTimeout raised after wake_timeout_seconds
│   │
│   └── test_manifest_db.py
│         WAL mode active after initialisation
│         Upsert creates new entry for unknown path
│         Upsert updates existing entry for known path
│         batch_mark_lan_backed_up updates correct rows
│         get_all_paths returns complete set
│         Thread safety: concurrent writes do not corrupt data
│
├── rclone.exe                  Rclone binary — copied here during deployment
├── requirements.txt            Runtime Python dependencies
├── requirements-dev.txt        Development and testing dependencies
├── pyproject.toml              Ruff, mypy, pytest configuration
├── .env.example                Example environment variable file
│                               Documents PREFECT_API_URL and other env vars
├── manifest.db                 FileManifest SQLite — created on first run
├── prefect.db                  Prefect state SQLite — created by Prefect server
└── README.md                   Deployment instructions — step by step
```

---

# SECTION 7 — CONFIGURATION SCHEMA

## 7.1 Complete config.yaml

Every key. Type. Required or optional. Default value. Validation rule. What happens if invalid.

```yaml
# ═══════════════════════════════════════════════════
# FIRM IDENTIFICATION
# Used in log headers and Phase 2 email subjects
# ═══════════════════════════════════════════════════
firm:
  name: "AAM Associates"
  # Type:       string
  # Required:   YES
  # Validation: non-empty after strip
  # Error:      "firm.name cannot be empty"

# ═══════════════════════════════════════════════════
# FILE SYSTEM PATHS
# All paths use Windows format — backslashes doubled in YAML
# ═══════════════════════════════════════════════════
paths:
  source_drive: "D:\\"
  # Type:       string — converted to pathlib.Path internally
  # Required:   YES
  # Validation: path must exist on disk at config load time
  # Error:      "paths.source_drive does not exist: [value]"

  lan_destination: "\\\\192.168.10.10\\hp srv manual backup$"
  # Type:       string — UNC path
  # Required:   YES
  # Validation: must start with \\\\ (four backslashes in Python, two in YAML)
  #             must match pattern ^\\\\.+\\.+$ after parsing
  # Error:      "paths.lan_destination must be a UNC path starting with \\\\"
  # Security:   validated against UNC pattern before any subprocess call
  # Note:       hidden share — $ suffix is valid and expected

  log_directory: "C:\\BackupAgent\\logs"
  # Type:       string — converted to pathlib.Path
  # Required:   YES
  # Validation: parent directory must exist or be creatable
  # Behaviour:  directory created on startup if it does not exist

  database_path: "C:\\BackupAgent\\manifest.db"
  # Type:       string — converted to pathlib.Path
  # Required:   YES
  # Validation: parent directory must exist or be creatable
  # Note:       this is the FileManifest database
  #             Prefect database is at C:\BackupAgent\prefect.db
  #             set via environment variable — not in config.yaml

  rclone_temp_directory: "C:\\BackupAgent\\rclone_temp"
  # Type:       string — converted to pathlib.Path
  # Required:   NO — default: C:\BackupAgent\rclone_temp
  # Validation: parent must be creatable
  # Behaviour:  directory created on startup if it does not exist
  # Security:   temp rclone configs written here with restricted ACL
  #             deleted in finally blocks after each run

# ═══════════════════════════════════════════════════
# SCHEDULE
# ═══════════════════════════════════════════════════
schedule:
  enabled: true
  # Type:       boolean
  # Required:   NO — default: true
  # Purpose:    set false during debugging to prevent automatic triggering
  #             flow still runs when triggered manually from UI or CLI

  daily_time: "23:00"
  # Type:       string HH:MM format 24-hour
  # Required:   NO — default: "23:00"
  # Validation: must match regex ^\d{2}:\d{2}$
  #             hour must be 00-23, minute must be 00-59
  # Timezone:   Asia/Kolkata (IST) — set in Prefect deployment cron
  # Note:       this value is used when creating the Prefect deployment
  #             changing it requires re-running create_deployment.py

# ═══════════════════════════════════════════════════
# BACKUP SCOPE — WHAT GETS BACKED UP
# Pending final confirmation from client questionnaire
# Defaults are safe and conservative
# ═══════════════════════════════════════════════════
backup_scope:
  exclude_folders:
  # Type:       list of strings — Windows absolute paths
  # Required:   NO — default: list below
  # Validation: each entry must be an absolute path starting with drive letter
  # Matching:   case-insensitive
  #             exact match OR any subfolder of excluded path is excluded
  # Effect:     excluded folders are pruned from os.walk before descent
  #             their contents are never scanned or backed up
    - "D:\\WINMAN\\Winman's mir bkup"
    - "D:\\WINMAN\\winmanbackup"
    - "D:\\WINMAN\\winman_backup"
    - "D:\\WINMAN\\winman__backup"
    - "D:\\Winman's mir bkup"
    - "D:\\winman_backup"
    - "D:\\Common Folder"
    - "D:\\DELL SRV F"
    - "D:\\Software_IT"
    - "D:\\BackupAgent"

  exclude_extensions:
  # Type:       list of strings — each must start with dot
  # Required:   NO — default: list below
  # Validation: each entry must start with "."
  #             stored and compared in lowercase
  # Effect:     any file with matching extension is skipped
    - ".lnk"
    - ".tmp"
    - ".temp"

  exclude_patterns:
  # Type:       list of strings — glob patterns matched against filename only
  # Required:   NO — default: list below
  # Matching:   fnmatch case-insensitive against filename (not full path)
  # Effect:     any file whose name matches any pattern is skipped
    - "~$*"
    - "desktop.ini"
    - "Thumbs.db"

# ═══════════════════════════════════════════════════
# LAN BACKUP — ROBOCOPY SETTINGS
# ═══════════════════════════════════════════════════
lan_backup:
  enabled: true
  # Type:       boolean
  # Required:   NO — default: true
  # Effect:     false disables entire LAN stack cleanly
  #             no WoL, no Robocopy, lan_status = LAN_SKIPPED in Prefect
  #             no errors, no alerts about LAN

  retry_count: 3
  # Type:       integer
  # Required:   NO — default: 3
  # Validation: 1 to 10
  # Effect:     passed to Robocopy as /R flag
  # Error:      "lan_backup.retry_count must be between 1 and 10"

  retry_wait_seconds: 10
  # Type:       integer
  # Required:   NO — default: 10
  # Validation: 1 to 300
  # Effect:     passed to Robocopy as /W flag
  # Error:      "lan_backup.retry_wait_seconds must be between 1 and 300"

  subprocess_timeout_seconds: 14400
  # Type:       integer — seconds
  # Required:   NO — default: 14400 (4 hours)
  # Validation: minimum 3600 (1 hour)
  # Effect:     if Robocopy subprocess runs longer than this it is killed
  #             job marked LAN_FAILED, critical log written
  # Error:      "lan_backup.subprocess_timeout_seconds minimum is 3600"

# ═══════════════════════════════════════════════════
# WAKE-ON-LAN
# ═══════════════════════════════════════════════════
wol:
  enabled: true
  # Type:       boolean
  # Required:   NO — default: true
  # Effect:     false means no WoL sent, no ping check
  #             assumes backup server is always online
  #             proceed directly to Robocopy

  mac_address: ""
  # Type:       string
  # Required:   YES when wol.enabled is true
  # Validation: must match XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX
  # How to get: run getmac /v on backup server during deployment
  # Error:      "wol.mac_address is required when wol.enabled is true"
  #             "wol.mac_address format must be XX:XX:XX:XX:XX:XX"

  server_ip: "192.168.10.10"
  # Type:       string — IPv4 address
  # Required:   YES when wol.enabled is true
  # Validation: must match IPv4 pattern \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}
  # Error:      "wol.server_ip must be a valid IPv4 address"

  wake_timeout_seconds: 300
  # Type:       integer — seconds
  # Required:   NO — default: 300 (5 minutes)
  # Validation: 60 to 600
  # Effect:     if server does not respond within this time
  #             WolTimeout is raised, LAN backup marked LAN_FAILED
  # Error:      "wol.wake_timeout_seconds must be between 60 and 600"

  ping_interval_seconds: 15
  # Type:       integer — seconds
  # Required:   NO — default: 15
  # Validation: 5 to 60
  # Effect:     how often to ping while waiting for server to wake

  stability_wait_seconds: 30
  # Type:       integer — seconds
  # Required:   NO — default: 30
  # Effect:     additional wait after server responds before starting Robocopy
  #             allows Windows SMB services to fully initialise after boot
  #             skipped if server was already online (no WoL needed)

# ═══════════════════════════════════════════════════
# CLOUD BACKUP — RCLONE SETTINGS
# ═══════════════════════════════════════════════════
cloud_backup:
  enabled: true
  # Type:       boolean
  # Required:   NO — default: true
  # Effect:     false disables entire cloud stack cleanly
  #             cloud_status = CLOUD_SKIPPED in Prefect

  provider: "gcs"
  # Type:       string
  # Required:   YES when cloud_backup.enabled is true
  # Validation: must be one of: gcs, b2, s3, gdrive
  # Default:    gcs (Google Cloud Storage)
  # Effect:     determines rclone backend type in temp config
  # Error:      "cloud_backup.provider must be one of: gcs, b2, s3, gdrive"

  bucket: ""
  # Type:       string
  # Required:   YES when cloud_backup.enabled is true
  # Validation: GCS naming rules — lowercase, letters, numbers, hyphens only
  #             pattern: ^[a-z0-9][a-z0-9\-]{1,61}[a-z0-9]$
  # Error:      "cloud_backup.bucket is required when cloud_backup.enabled is true"
  #             "cloud_backup.bucket must contain only lowercase letters, numbers, hyphens"

  remote_path: "D_Drive_Backup"
  # Type:       string
  # Required:   NO — default: D_Drive_Backup
  # Validation: alphanumeric, hyphens, underscores, forward slashes only
  #             pattern: ^[\w\-_/]+$
  # Effect:     root folder inside the bucket
  #             all backed-up files sit under bucket/remote_path/
  # Error:      "cloud_backup.remote_path contains invalid characters"

  bandwidth_limit: "10M"
  # Type:       string
  # Required:   NO — default: 10M (10 MB/s)
  # Validation: must match pattern \d+[kMG]
  # Effect:     passed to rclone as --bwlimit
  #             prevents cloud upload from saturating 100Mbps internet
  # Error:      "cloud_backup.bandwidth_limit must match format like 10M, 500k, 1G"

  chunk_size: "100M"
  # Type:       string
  # Required:   NO — default: 100M
  # Validation: must match pattern \d+[MG], minimum 5M
  # Effect:     passed to rclone as --gcs-chunk-size
  #             controls multipart upload chunk size for large files

  retry_count: 3
  # Type:       integer
  # Required:   NO — default: 3
  # Validation: 1 to 10
  # Effect:     orchestrator-level retries for rclone exit code 5
  #             separate from rclone's own internal --retries flag
  #             total retry attempts before marking CLOUD_FAILED

  subprocess_timeout_seconds: 21600
  # Type:       integer — seconds
  # Required:   NO — default: 21600 (6 hours)
  # Validation: minimum 3600

# ═══════════════════════════════════════════════════
# CLOUD CREDENTIALS
# Actual credentials stored in Windows Credential Manager
# Only the lookup name is stored in config.yaml
# ═══════════════════════════════════════════════════
cloud_credentials:
  credential_name: "BackupAgent_GCS"
  # Type:       string
  # Required:   YES when cloud_backup.enabled is true
  # Validation: non-empty string
  # Effect:     keyring.get_password("BackupAgent", credential_name)
  #             returns the full path to GCS service account JSON key file
  # Error:      "Credential '[name]' not found in Windows Credential Manager"

# ═══════════════════════════════════════════════════
# STATUS UI
# FastAPI serving single HTML page on LAN
# ═══════════════════════════════════════════════════
ui:
  enabled: true
  # Type:       boolean
  # Required:   NO — default: true
  # Effect:     false disables BackupUI Windows Service

  host: "0.0.0.0"
  # Type:       string — IP address or 0.0.0.0 for all interfaces
  # Required:   NO — default: 0.0.0.0
  # Effect:     uvicorn bind address
  # Note:       0.0.0.0 makes UI accessible from any LAN machine
  #             restrict to 127.0.0.1 for localhost only

  port: 8080
  # Type:       integer
  # Required:   NO — default: 8080
  # Validation: 1024 to 65535
  # Effect:     uvicorn port
  # Note:       Windows Firewall is disabled on this server
  #             no firewall rule needed

  prefect_api_url: "http://127.0.0.1:4200/api"
  # Type:       string — URL
  # Required:   NO — default: http://127.0.0.1:4200/api
  # Effect:     UI queries Prefect API at this URL for run state
  #             and to trigger manual flow runs

# ═══════════════════════════════════════════════════
# NOTIFICATIONS (for Phase 2 email automation)
# Prefect email automation handles failure alerts in Phase 1
# Full smtplib notification module implemented later
# ═══════════════════════════════════════════════════
notifications:
  smtp_host: ""
  smtp_port: 587
  smtp_username: ""
  smtp_password_credential: "BackupAgent_SMTP"
  sender: ""
  recipients: []
  send_on_every_run: true
  send_on_failure: true
  weekly_summary_enabled: true
  weekly_summary_day: "monday"
  weekly_summary_time: "08:00"
```

---

# SECTION 8 — DATABASE SCHEMA

## 8.1 FileManifest Database — manifest.db

This is our database. It is separate from Prefect's database.

Prefect stores flow run state, task logs, schedules, and deployment config in prefect.db.

We store file-level backup state in manifest.db. Prefect has no knowledge of individual files.

## 8.2 FileManifest Table — Complete Definition

```
Table name:   file_manifest
Engine:       SQLite with WAL mode
Purpose:      Track per-file backup state across all backup runs

Columns:

file_id
  Type:         TEXT
  Constraint:   PRIMARY KEY
  Format:       UUID4 string e.g. "550e8400-e29b-41d4-a716-446655440000"
  Generation:   uuid.uuid4() when file first encountered
  Immutable:    never changes for the same relative_path

relative_path
  Type:         TEXT
  Constraint:   NOT NULL, UNIQUE
  Format:       Path relative to source_drive root
                No leading backslash
                Windows separators — backslash
  Example:      "AAM WORKS\ClientA\FY2425\Balance_Sheet.xlsx"
  Case:         Stored exactly as returned by os.walk — preserves original case
  Max length:   2048 characters (Windows MAX_PATH is 260 but can be extended)

file_size
  Type:         INTEGER
  Constraint:   NOT NULL
  Unit:         bytes
  Source:       os.stat().st_size

last_modified_timestamp
  Type:         REAL
  Constraint:   NOT NULL
  Format:       Unix timestamp float from os.stat().st_mtime
  Precision:    float — preserves sub-second precision
  Comparison:   1.0 second tolerance used when comparing
                (filesystem quirks can cause minor mtime drift)

checksum
  Type:         TEXT
  Constraint:   NOT NULL
  Format:       xxHash64 hex string — 16 hex characters
  Example:      "a1b2c3d4e5f67890"
  Special:      "pending" for new files before first backup confirmation
                Updated to real checksum after first successful backup

last_seen_at
  Type:         TEXT
  Constraint:   NOT NULL
  Format:       ISO8601 UTC timestamp "2025-03-28T23:05:00.000000+00:00"
  Updated:      every scan run — even for unchanged files
  Purpose:      detect files that have been deleted from source

last_backed_up_lan
  Type:         TEXT
  Constraint:   nullable
  Format:       ISO8601 UTC timestamp
  Value:        NULL if file has never been backed up to LAN
  Updated:      after Robocopy completes with LAN_COMPLETE or LAN_PARTIAL

last_backed_up_cloud
  Type:         TEXT
  Constraint:   nullable
  Format:       ISO8601 UTC timestamp
  Value:        NULL if file has never been backed up to cloud
  Updated:      after Rclone completes with CLOUD_COMPLETE or CLOUD_PARTIAL

backed_up_to_lan
  Type:         INTEGER
  Constraint:   NOT NULL, DEFAULT 0
  Values:       0 = never backed up to LAN
                1 = has been backed up to LAN at least once
  Note:         does not mean current version is backed up
                check last_backed_up_lan for recency

backed_up_to_cloud
  Type:         INTEGER
  Constraint:   NOT NULL, DEFAULT 0
  Values:       0 = never backed up to cloud
                1 = has been backed up to cloud at least once
```

## 8.3 Phase 2 Provisions in Schema

No additional columns or tables are planned. The current file_manifest schema is final. Both destinations are true mirrors with no custom versioning or soft delete logic. Cloud provider native versioning (GCS object versioning) and lifecycle retention rules handle protection against accidental deletion or corruption.

## 8.4 Required Indexes

```
idx_manifest_relative_path
  Table:    file_manifest
  Column:   relative_path
  Type:     B-tree (default)
  Purpose:  Primary lookup — get_entry(relative_path)
            Called for every file in every scan — must be O(log n)
            Without this: full table scan on 200,000 rows per file = catastrophic

idx_manifest_last_seen
  Table:    file_manifest
  Column:   last_seen_at
  Purpose:  Detect files not seen recently — identifies files deleted from source
```

## 8.5 WAL Mode — Mandatory Configuration

WAL mode must be set on every database connection. Not just on creation. Every connection.

This is done via SQLAlchemy connection event listener that fires on every new connection:

```
On every connection open:
  PRAGMA journal_mode=WAL
  Verify response is "wal" — if not, raise DatabaseError
  PRAGMA foreign_keys=ON
  PRAGMA synchronous=NORMAL
  PRAGMA cache_size=10000
```

If WAL mode cannot be set (another process has file open in incompatible mode), raise DatabaseError immediately. Do not continue. Log CRITICAL. This is a hard failure — not a warning.

---

# SECTION 9 — CHANGE DETECTION ENGINE

## 9.1 Algorithm — Complete Specification

The change detection engine is the core of the system. Every design decision here is deliberate and must be followed exactly.

**Walk strategy:**
os.walk with topdown=True. This is mandatory — topdown=True allows modifying dirnames in place to prune excluded directories before descent. Without topdown=True, pruning is not possible and excluded folders would be walked anyway.

**Excluded folder pruning:**
Inside the os.walk loop, before processing files, prune dirnames in place:
```
dirnames[:] = [d for d in dirnames if not is_excluded_folder(join(dirpath, d))]
```
The in-place modification ([:] =) is critical. A new list assignment would not affect os.walk's descent. In-place modification prevents os.walk from descending into excluded directories.

**File classification logic — in order of evaluation:**

Step 1 — Extension check: if file extension (lowercased) is in exclude_extensions list — skip. Do not stat. Do not hash. Do not query manifest.

Step 2 — Pattern check: if filename (lowercased) matches any pattern in exclude_patterns via fnmatch — skip.

Step 3 — stat: call os.stat(full_path). If OSError (permission denied, file disappeared, locked) — add to cannot_read list, log WARNING, continue to next file.

Step 4 — Compute relative_path: strip source_drive prefix from full_path, strip leading separator. Store exactly as-is from Windows — preserves original case.

Step 5 — Add to current_paths set.

Step 6 — Manifest lookup: db.get_entry(relative_path). Uses indexed query — O(log n).

Step 7a — Not in manifest: NEW FILE. Append FileInfo to new_files with empty checksum string. Insert preliminary manifest entry with checksum="pending". Checksum computed after backup confirmation.

Step 7b — In manifest, size AND mtime match (within 1.0 second tolerance): UNCHANGED. Call db.update_last_seen(relative_path). Increment unchanged_count. Do not hash. Do not add to any list. Continue.

Step 7c — In manifest, size OR mtime differs: compute xxHash64 checksum. If checksum matches manifest: METADATA CHANGE ONLY — update last_seen_at, update size and mtime in manifest, not a backup event. If checksum differs: MODIFIED FILE. Append FileInfo to modified_files with the new checksum.

**After walk completes — deleted file detection:**
Get all manifest paths via db.get_all_paths() (returns a set).
Compute deleted_files = all_manifest_paths minus current_paths.
For each deleted file: log at INFO level. Remove from manifest via db.delete_entry(relative_path). The file will be deleted from both backup destinations by the mirror tools (Robocopy /MIR and rclone sync) on the next run.

## 9.2 Checksum Strategy

Algorithm: xxHash64. Not MD5. Not SHA256. xxHash64 is significantly faster for large files and has sufficient collision resistance for change detection purposes.

Implementation: xxhash.xxh64() — Python xxhash library. Read file in 8MB chunks to avoid loading large files into memory. Return hexdigest() as 16-character hex string.

When computed: only when size or mtime differs from manifest. Never on unchanged files. Never during walk for new files (computed after backup confirmation).

Why not compute for new files during scan: a new file would be read twice — once for checksum during scan, once by Robocopy or Rclone during backup. On a server with disk I/O constraints this doubles unnecessary I/O. Compute once after backup is confirmed.

## 9.3 Performance Characteristics

For the AAM client environment specifically:
- 370GB, estimated 200,000 files, 40,000+ folders
- First scan (cold manifest): 20-40 minutes. All files are new. No checksums computed (new file checksum deferred). Pure os.walk and os.stat.
- Subsequent scans (warm manifest, 2-4GB changed daily): 5-15 minutes. Only changed files trigger checksum computation. The index on relative_path ensures O(log n) manifest lookup per file.
- The bottleneck is disk I/O for the stat calls on 200,000 files, not CPU.

---

# SECTION 10 — WOL MODULE

## 10.1 Complete Behaviour Specification

**Entry point:** ensure_server_online(config) called by lan_backup_task before Robocopy.

**If wol.enabled is false:** log INFO "WoL disabled — assuming backup server is online". Return True immediately. Proceed to Robocopy.

**If wol.enabled is true:**

Step 1 — Ping check:
Send 3 ICMP pings to wol.server_ip using Windows ping command.
Command: ping -n 3 -w 1000 [ip] (3 pings, 1000ms timeout each)
If any ping succeeds (returncode 0): server is online. Log INFO "Backup server already online — skipping WoL". Skip WoL packet. Skip stability wait. Return True.
If all pings fail: server is offline. Proceed to Step 2.

Step 2 — Send WoL magic packet:
wakeonlan.send_magic_packet(config.wol.mac_address)
Log INFO "WoL magic packet sent to [mac_address]"
If exception: raise WolError with message.

Step 3 — Poll for response:
Loop: while elapsed < wake_timeout_seconds
  Sleep ping_interval_seconds
  Send single ping to server_ip
  If ping succeeds: break loop
  Log DEBUG "Server not yet responding... [elapsed]s / [timeout]s"
If loop exits without success: raise WolTimeout with message including mac_address, server_ip, and timeout value.

Step 4 — Stability wait:
Sleep stability_wait_seconds (default 30)
Log INFO "Stability wait complete — SMB services should be ready"
Return True

**WolTimeout handling in lan_backup_task:**
Catch WolTimeout. Log error. Return {"status": "LAN_FAILED", ...}.
Prefect marks the task as failed. Flow continues with cloud backup.
Prefect failure automation fires if overall flow is FAILED.

---

# SECTION 11 — ROBOCOPY WRAPPER

## 11.1 Command Specification

The exact Robocopy command constructed and why each flag is chosen:

```
robocopy
  [source]              D:\
  [destination]         \\192.168.10.10\hp srv manual backup$
  /MIR                  Mirror mode — copies new/changed files, deletes from destination what's deleted from source
                        This makes the backup server an exact mirror of D:\
                        Equivalent to /E + /PURGE combined
  /Z                    Restartable mode — handles network interruptions
                        If connection drops mid-file, restarts from checkpoint
                        Critical for 370GB over LAN with potential NIC teaming issues
  /R:[n]                Retry count from config (default 3)
                        Number of retries on each failed file
  /W:[n]                Wait time between retries from config (default 10)
                        Seconds to wait between retries
  /NP                   No progress percentage in output
                        Reduces log verbosity significantly
  /BYTES                Show file sizes in bytes in summary
                        Needed for accurate bytes_copied parsing
  /TEE                  Output to both console and log file
  /UNILOG+:[path]       Append to Unicode log file
                        Path: C:\BackupAgent\logs\robocopy_YYYY-MM-DD.log
  /XD [folders]         Exclude directories — one /XD per excluded folder
  /XF [patterns]        Exclude files matching pattern — one /XF per pattern
                        Includes exclude_patterns and exclude_extensions
```

Note: /MIR makes the LAN backup a true mirror. Files deleted from D:\ are deleted from the backup server. This is intentional — both destinations mirror the current state of the source. GCS native object versioning (retaining 1 older version) provides a safety net against accidental deletions.

## 11.2 Exit Code Classification — Bitmask Rules

Robocopy exit codes are bitmasks. Each bit is independent. Evaluate with bitwise AND, never direct comparison.

```
Bit 0 (decimal 1):   Files were copied successfully
Bit 1 (decimal 2):   Extra files/directories exist in destination
Bit 2 (decimal 4):   Mismatched files detected
Bit 3 (decimal 8):   Some files could not be copied — COPY ERROR
Bit 4 (decimal 16):  Fatal error — Robocopy did not run properly

Classification logic:
  if exit_code & 16:       LAN_FAILED    — fatal, nothing copied
  elif exit_code & 8:      LAN_PARTIAL   — some files failed
  elif exit_code <= 7:     LAN_COMPLETE  — success (0 = already in sync)
  else:                    LAN_FAILED    — unknown code

Exit code 0 is SUCCESS. It means nothing needed to be copied — already in sync.
This is not an error. Do not treat 0 as "nothing happened".
```

## 11.3 Security Rules

All paths passed to Robocopy subprocess are validated before command construction:
- Source: must match [A-Z]:\\ exactly
- Destination: must match UNC pattern — validated at config load time
- Excluded folders: must be absolute paths starting with source drive letter

Arguments passed as list, never as string. shell=False always. No exceptions.

## 11.4 Manifest Update After LAN Backup

After Robocopy exits with LAN_COMPLETE or LAN_PARTIAL:

Get all relative paths from new_files + modified_files in ScanResult.
Call db.batch_mark_lan_backed_up(all_changed_paths) in a single transaction.
For new files with checksum="pending": compute xxHash64 for each file now. Update manifest entry with real checksum via db.upsert_entry().

Known limitation: on LAN_PARTIAL, we mark all files as backed up even though some may have failed. We cannot determine which specific files failed without parsing Robocopy's per-file log output.

---

# SECTION 12 — RCLONE WRAPPER

## 12.1 Command Specification

```
rclone sync
  [source]                    D:\
  [remote]:[bucket]/[path]    gcs_backup:[bucket]/D_Drive_Backup
  --config [temp_config]      Path to temporary rclone.conf
  --filter-from [filter_file] Path to temporary filter rules file
  --bwlimit [limit]           Bandwidth limit from config (default 10M)
  --gcs-chunk-size [size]     Chunk size for multipart uploads (default 100M)
  --transfers 4               4 parallel file transfers
  --checkers 8                8 parallel file comparison threads
  --retries [n]               Rclone internal retries (from config retry_count)
  --retries-sleep 30s         Wait between internal retries
  --stats 300s                Print transfer stats every 5 minutes
  --stats-log-level INFO      Include stats in log output
  --log-level INFO            Rclone log verbosity
  --use-json-log              Structured JSON log output for parsing
  --no-traverse               Do not list remote before transfer
                              More efficient for large initial runs
```

Note: rclone sync makes destination match source. Files deleted from source are deleted from destination. This is intentional — both LAN and cloud are true mirrors of the source. GCS native object versioning (configured during deployment, retaining 1 older version with lifecycle retention rules) provides protection against accidental deletion or corruption. No custom soft delete or versioning logic is built.

## 12.2 Temp Config Security

Location: C:\BackupAgent\rclone_temp\rclone_[job_id].conf where job_id is first 8 characters of a UUID4 generated at task start.

Content:
```ini
[gcs_backup]
type = google cloud storage
service_account_file = [path from credential manager]
bucket_policy_only = true
location = asia-south1
```

ACL applied immediately after file creation:
- Remove all inherited permissions (icacls /inheritance:r)
- Grant read access to service account only
- Remove access for Everyone and Users groups

Deletion: always in finally block. If deletion fails, log CRITICAL with exact file path and "Manual deletion required". Never silently leave temp files.

## 12.3 Filter File

Location: C:\BackupAgent\rclone_temp\rclone_filter_[job_id].txt

Format: rclone filter rules. Forward slashes required — rclone does not accept Windows backslashes in filter files.

Exclusions from config translated to rclone filter syntax:
- Excluded folders: "- FolderName/**"
- Excluded extensions: "- *.ext"
- Excluded patterns: "- pattern"

Deletion: same finally block as temp config.

## 12.4 Exit Code Classification

```
Code 0: CLOUD_COMPLETE   — success
Code 1: CLOUD_FAILED     — syntax error in command (our bug)
Code 2: CLOUD_PARTIAL    — non-categorised error
Code 3: CLOUD_FAILED     — source or destination not found
Code 4: CLOUD_PARTIAL    — specific file not found
Code 5: RETRYABLE        — temporary network error — retry with backoff
Code 6: CLOUD_PARTIAL    — less serious errors
Code 7: CLOUD_FAILED     — fatal error
Code 8: CLOUD_PARTIAL    — transfer limit exceeded
Other:  CLOUD_FAILED     — unknown exit code
```

## 12.5 Retry Logic

For RETRYABLE exit code (5):

```
Max retries:   cloud_backup.retry_count (default 3)
Backoff:       Attempt 1 failed → wait 60s
               Attempt 2 failed → wait 120s
               Attempt 3 failed → wait 240s
After max:     CLOUD_FAILED

Each retry:    Full rclone sync command re-invoked
               rclone sync is idempotent — retrying is always safe
               Same temp config and filter file reused (not recreated)
```

Separate from rclone's internal --retries flag which handles per-file retries within one rclone invocation. Orchestrator retry handles cases where rclone itself gives up.

## 12.6 Manifest Update After Cloud Backup

After Rclone exits with CLOUD_COMPLETE or CLOUD_PARTIAL:
Call db.batch_mark_cloud_backed_up(all_changed_paths) in single transaction.

Same limitation as LAN: on CLOUD_PARTIAL, all files marked as backed up. Per-file result parsing would be needed to identify specific failures.

---

# SECTION 13 — PREFECT INTEGRATION

## 13.1 Prefect Version and Installation

Version: Prefect 3.x — latest stable 3.x release at time of deployment.

Installation: pip install prefect==3.*

Prefect 3.x introduced significant changes from Prefect 2.x:
- Work pools replace work queues as primary execution mechanism
- Deployment API changed — use flow.deploy() or Deployment.build_from_flow()
- Task runner API changed — ThreadPoolTaskRunner replaces ConcurrentTaskRunner

## 13.2 Prefect Server Configuration

Prefect server runs self-hosted on AAMBDC001. All configuration via environment variables set in NSSM service configuration.

Required environment variable:
```
PREFECT_API_DATABASE_CONNECTION_URL=sqlite+aiosqlite:///C:/BackupAgent/prefect.db
```

Optional but recommended:
```
PREFECT_SERVER_API_HOST=0.0.0.0
PREFECT_SERVER_API_PORT=4200
PREFECT_LOGGING_LEVEL=WARNING
```

Prefect UI accessible at:
- http://localhost:4200 (on server)
- http://192.168.10.5:4200 (from any LAN machine)

## 13.3 Flow Definition Rules

The nightly-backup flow must be defined with these exact parameters:

```
@flow(
    name="nightly-backup",
    task_runner=ThreadPoolTaskRunner(max_workers=2),
    log_prints=True,
    version="1.0.0"
)
```

ThreadPoolTaskRunner with max_workers=2 enables concurrent task execution for LAN and cloud tasks. Each task submitted with task.submit() runs in a thread. flow.result() waits for completion.

## 13.4 Task Parameters

Each task defined with appropriate retry and tag configuration:

```
load_config_task:
  retries: 0
  tags: ["setup"]
  Reason: config errors are not retryable without investigation

scan_task:
  retries: 0
  tags: ["scan"]
  Reason: scan errors indicate data or permissions issue — not retryable

lan_backup_task:
  retries: 1
  retry_delay_seconds: 300
  tags: ["backup", "lan"]
  Reason: one retry after 5 minutes handles transient LAN issues

cloud_backup_task:
  retries: 2
  retry_delay_seconds: 120
  tags: ["backup", "cloud"]
  Reason: two retries for transient GCS API issues
  Note: separate from rclone internal retry — Prefect retry re-runs entire task
```

## 13.5 Prefect Deployment

Deployment created by running scripts/create_deployment.py after Prefect server starts.

```
Deployment name:  nightly-backup-production
Flow:             nightly-backup (from flow.py)
Schedule:         Cron "0 23 * * *" — 11PM daily
Timezone:         Asia/Kolkata — IST
Work pool:        backup-pool
Work pool type:   process
Tags:             ["production", "backup"]
```

## 13.6 Prefect Email Automation — Failure Alerts

Configured in Prefect UI after server starts. Zero custom code.

Steps:
1. In Prefect UI → Blocks → Create Email Server Credentials block
2. Enter SMTP host, port, username, password from client's email settings
3. In Prefect UI → Automations → Create automation
4. Trigger: Flow run state changes to Failed
5. Filter: Flow name = "nightly-backup"
6. Action: Send notification via Email block
7. Recipients: as confirmed from client questionnaire
8. Subject: "BACKUP FAILED — AAM Associates — [date]"
9. Body: include flow run URL for direct link to Prefect UI logs

This covers the failure notification requirement entirely without writing any notification code. SMTP settings for future daily/weekly email reports are defined in the notifications section of config.yaml.

---

# SECTION 14 — STATUS UI

## 14.1 What The Status Page Shows

One HTML page. Three elements only.

**Element 1 — Last Run Status:**
Shows the most recent nightly-backup flow run result.
Green box: "Last backup completed successfully"
Red box: "Last backup FAILED — check Prefect UI for details"
Yellow box: "Last backup completed with partial failure"
Grey box: "No backup runs yet" (first time)
Includes: start time, end time, duration, files new, files modified (from flow run result).

**Element 2 — Next Run:**
"Next backup scheduled at 11:00 PM tonight" or "Next backup scheduled tomorrow at 11:00 PM"
Countdown: "in 3 hours 42 minutes"
Updates on page refresh.

**Element 3 — Manual Trigger:**
Button: "Run Backup Now"
Clicking shows confirmation dialog: "This will start a backup job immediately. Continue?"
Confirm → POST /trigger → Prefect API creates a flow run → button shows "Backup starting..."
Disable button if a run is already in progress.

## 14.2 How The UI Gets Data

The FastAPI server queries the Prefect API to get run state and schedule information.

It does not query manifest.db directly. All backup state comes from Prefect.

Two Prefect API calls on page load:
1. GET /api/flow-runs?flow_name=nightly-backup&limit=1&sort=START_TIME_DESC — get last run
2. GET /api/deployments?name=nightly-backup-production — get schedule info

These are REST calls to the local Prefect server at config.ui.prefect_api_url.

Manual trigger: POST /api/flow-runs with deployment_id to create an immediate flow run.

## 14.3 Auto-Refresh

Page auto-refreshes every 60 seconds via Alpine.js interval. This keeps status current without staff manually refreshing. Interval is configurable via a JavaScript constant at the top of the page.

## 14.4 No Authentication in Phase 1

The UI is accessible to anyone on the LAN without a password. This is acceptable because:
- The server is in the client's internal office network only
- Windows Firewall is disabled on this server anyway
- Staff cannot do anything harmful from the UI — only trigger a backup or view status

---

# SECTION 15 — LOGGING

## 15.1 Two Log Outputs

**Output 1 — Rotating daily file:**
Location: C:\BackupAgent\logs\backup_YYYY-MM-DD.log
Level: DEBUG and above — everything
Rotation: midnight daily — new file each day
Retention: 30 days — older files deleted automatically on rotation
Compression: .gz after rotation
Encoding: UTF-8 — handles Windows paths with special characters
Thread safe: Loguru enqueue=True — async thread-safe writing

**Output 2 — Stderr:**
Level: WARNING and above
Captured by NSSM into C:\BackupAgent\logs\service_stderr.log
Used for service-level error tracking

## 15.2 Log Format

```
2025-03-28 23:00:01 [INFO    ] [core.config_loader] Config loaded for firm: AAM Associates
2025-03-28 23:00:05 [INFO    ] [core.scanner      ] Starting scan of D:\
2025-03-28 23:05:23 [INFO    ] [core.scanner      ] Scan complete: 203,847 files, 142 new, 38 modified, 3 deleted in 318s
2025-03-28 23:05:23 [INFO    ] [core.wol          ] Backup server already online — skipping WoL
2025-03-28 23:05:23 [INFO    ] [core.robocopy     ] Starting Robocopy: D:\ → \\192.168.10.10\hp srv manual backup$
2025-03-28 23:05:23 [INFO    ] [core.rclone       ] Starting Rclone sync: D:\ → gcs_backup:bucket/D_Drive_Backup
2025-03-28 23:47:12 [INFO    ] [core.robocopy     ] Robocopy complete. Exit: 1. Status: LAN_COMPLETE. Files: 180. Duration: 2509s
2025-03-28 23:52:44 [INFO    ] [core.rclone       ] Rclone complete. Exit: 0. Status: CLOUD_COMPLETE. Duration: 2841s
2025-03-28 23:52:44 [INFO    ] [flow              ] BACKUP COMPLETE. Status: COMPLETE. LAN: LAN_COMPLETE. Cloud: CLOUD_COMPLETE
```

Timestamps in log files use local server time (IST). Timestamps in SQLite use UTC. Conversion at write time.

## 15.3 Prefect Log Integration

Inside each Prefect task, Loguru logs are also forwarded to Prefect's task logger so they appear in the Prefect UI. This is done by adding a Loguru sink inside each task function that forwards to get_run_logger(). The sink is added at task start and removed at task end.

---

# SECTION 16 — WINDOWS SERVICE DEPLOYMENT

## 16.1 Three Windows Services

Phase 1 installs three Windows Services via NSSM.

**Service 1: PrefectServer**
```
Name:        PrefectServer
DisplayName: AAM Prefect Workflow Server
Binary:      C:\Python311\Scripts\prefect.exe
Args:        server start --host 0.0.0.0 --port 4200
Account:     LocalSystem (Prefect server does not need domain access)
Startup:     Automatic
WorkDir:     C:\BackupAgent
Env:         PREFECT_API_DATABASE_CONNECTION_URL=
             sqlite+aiosqlite:///C:/BackupAgent/prefect.db
Recovery:    Restart after 10s (1st failure), 30s (2nd), 60s (subsequent)
Stdout log:  C:\BackupAgent\logs\prefect_server_stdout.log
Stderr log:  C:\BackupAgent\logs\prefect_server_stderr.log
Rotate:      Daily
```

**Service 2: PrefectWorker**
```
Name:        PrefectWorker
DisplayName: AAM Backup Worker
Binary:      C:\Python311\Scripts\prefect.exe
Args:        worker start --pool backup-pool --type process
Account:     [Service account provided during deployment — needs LAN share access]
Password:    [set during deployment]
Startup:     Automatic — but delayed 30s after PrefectServer starts
             Achieved via AppRestartDelay 30000 on first start
WorkDir:     C:\BackupAgent
Env:         PREFECT_API_URL=http://127.0.0.1:4200/api
Recovery:    Restart after 10s (1st failure), 30s (2nd), 60s (subsequent)
Stdout log:  C:\BackupAgent\logs\prefect_worker_stdout.log
Stderr log:  C:\BackupAgent\logs\prefect_worker_stderr.log
Rotate:      Daily
```

**Service 3: BackupUI**
```
Name:        BackupUI
DisplayName: AAM Backup Status UI
Binary:      C:\Python311\python.exe
Args:        -m uvicorn ui.server:app --host 0.0.0.0 --port 8080
Account:     LocalSystem (UI only reads from Prefect API — no domain access needed)
Startup:     Automatic
WorkDir:     C:\BackupAgent
Env:         PREFECT_API_URL=http://127.0.0.1:4200/api
Recovery:    Restart after 10s
Stdout log:  C:\BackupAgent\logs\ui_stdout.log
Stderr log:  C:\BackupAgent\logs\ui_stderr.log
```

## 16.2 Service Start Order

PrefectServer must start before PrefectWorker.
Both must be running before BackupUI (UI queries Prefect API).

NSSM does not have native service dependency support. Handle via:
PrefectWorker configured with 30-second restart delay — by the time it is ready, PrefectServer is running.
BackupUI configured with 60-second restart delay and graceful fallback — if Prefect API is not reachable, UI shows "Prefect server starting..." instead of error.

## 16.3 Service Account

PrefectWorker runs as the service account provided during deployment. This account:
- Has access to D:\ (source drive)
- Has access to \\192.168.10.10\hp srv manual backup$ (backup share)
- Has access to C:\BackupAgent\ (agent directory)
- Can write to C:\BackupAgent\logs\ (log directory)
- Can read C:\BackupAgent\gcs_service_account.json (GCS key)
- Can access Windows Credential Manager for BackupAgent_GCS credential

**Security note:** The service account must be a least-privilege account with only the permissions listed above.

---

# SECTION 17 — DEPLOYMENT SEQUENCE

Every step in exact order. No step skipped. Each has a verification check.

## 17.1 Pre-Deployment Preparation (Before Remote Session)

Prepare GCS:
- Create GCP project (or use existing)
- Create GCS bucket: region asia-south1, uniform bucket access, object versioning ON, lifecycle rule: delete older versions after 90 days
- Create GCS service account: Storage Object Admin role on bucket only
- Download JSON key file
- Copy key file to USB drive

Prepare installation files on USB:
- Python 3.11+ Windows installer (64-bit, all users)
- NSSM from nssm.cc
- rclone.exe Windows 64-bit from rclone.org (verify version >= 1.60.0)
- All Python packages as wheels for offline install
- BackupAgent project files (zip of C:\BackupAgent\ structure)

## 17.2 Deployment Steps (Remote Desktop or On-Site)

**Step 1 — Python**
Run Python installer. Install for all users. Add to PATH.
Verify: python --version returns 3.11+

**Step 2 — Python packages**
pip install prefect pydantic pydantic-settings pyyaml sqlalchemy aiosqlite xxhash tenacity wakeonlan keyring typer loguru httpx fastapi uvicorn
Verify: python -c "import prefect; print(prefect.__version__)" returns 3.x

**Step 3 — NSSM**
Copy nssm.exe to C:\Windows\System32\
Verify: nssm version returns version string

**Step 4 — Rclone**
Create C:\BackupAgent\rclone_temp\ directory
Copy rclone.exe to C:\BackupAgent\
Verify: C:\BackupAgent\rclone.exe --version returns version >= 1.60.0

**Step 5 — Project files**
Extract BackupAgent.zip to C:\BackupAgent\
Create directories: logs\, rclone_temp\
Verify: C:\BackupAgent\flow.py exists

**Step 6 — GCS key file**
Copy gcs_service_account.json from USB to C:\BackupAgent\
Set ACL: readable only by service account
icacls C:\BackupAgent\gcs_service_account.json /inheritance:r
icacls "C:\BackupAgent\gcs_service_account.json" /grant:r "[SERVICE_ACCOUNT]:(R)"
Verify: ACL shows only service account has access

**Step 7 — Store credentials**
Run as service account: python scripts\setup_credentials.py
Enter path: C:\BackupAgent\gcs_service_account.json
Enter name: BackupAgent_GCS
Verify: script prints "Credential stored successfully"

**Step 8 — Config file**
Edit C:\BackupAgent\config.yaml
Fill all required fields: firm.name, paths.lan_destination, cloud_backup.bucket
Set wol.mac_address (from getmac /v on backup server)
Set cloud_credentials.credential_name to BackupAgent_GCS
Run: python scripts\validate_config.py
Verify: prints "Config valid"

**Step 9 — Start Prefect server manually (test)**
Run: prefect server start --host 0.0.0.0 --port 4200
Open browser: http://localhost:4200
Verify: Prefect UI loads correctly
Stop: Ctrl+C

**Step 10 — Install Windows Services**
Run: deploy\install_services.bat
Verify: sc query PrefectServer shows RUNNING
Verify: sc query PrefectWorker shows RUNNING
Verify: sc query BackupUI shows RUNNING
Wait 60 seconds for all services to stabilise

**Step 11 — Create work pool and deployment**
Run: prefect work-pool create backup-pool --type process
Run: python deploy\create_deployment.py
Verify: Prefect UI shows deployment "nightly-backup-production" with schedule

**Step 12 — Configure failure email in Prefect UI**
Navigate to: http://localhost:4200 → Blocks → Add Email Server Credentials
Enter SMTP settings from client questionnaire answers
Navigate to: Automations → Create
Configure: trigger on nightly-backup flow run Failed, send email notification

**Step 13 — Connection tests**
Run: python scripts\test_connections.py
All tests must show ✓ before proceeding
Fix any ✗ items before going to Step 14

**Step 14 — Initial cloud seed**
If this is the first deployment — D:\ has never been uploaded to GCS:
Run: python scripts\seed_cloud.py
This uploads full D:\ to GCS at limited bandwidth (does not start nightly jobs)
Script is resumable — can be interrupted and restarted
Estimated time: 370GB at 10MB/s = ~10 hours — run overnight
Do not start nightly jobs until seed completes
After seed: run scripts\test_connections.py again to verify GCS bucket has files

**Step 15 — Manual flow run test**
Trigger manual run from Prefect UI: Deployments → nightly-backup-production → Run
Monitor flow run in Prefect UI — watch task logs
Verify: all four tasks complete, flow run shows Completed
Verify: files appear on backup server (check a few folders)
Verify: files appear in GCS bucket (check via GCS console)
Verify: log file written at C:\BackupAgent\logs\backup_[date].log

**Step 16 — First scheduled run**
Wait for 23:00
Monitor Prefect UI — flow run should appear automatically
Monitor log file: Get-Content C:\BackupAgent\logs\backup_[date].log -Wait
Verify: flow completes, status COMPLETE or PARTIAL_FAILURE

**Step 17 — Status UI verification**
Open browser: http://192.168.10.5:8080
Verify: last run status shows correctly
Verify: next run time shows correctly
Verify: manual trigger button works

**Step 18 — Two-week monitoring**
Check Prefect UI daily for first two weeks
Check log files every two days
Document any issues
Phase 1 is complete when 14 consecutive successful runs occur

---

# SECTION 18 — DESIGN DECISIONS AND FUTURE ENHANCEMENTS

Both destinations are true mirrors. No custom soft delete, versioning, anomaly detection, or integrity verification is built. Cloud provider native features (GCS object versioning with 1 older version retained, lifecycle retention rules) provide protection against accidental deletion or corruption.

## 18.1 Database

FileManifest table schema is final. No migration scripts needed.
Schema: relative_path (unique, indexed), file_size, last_modified_timestamp, checksum, last_seen_at, last_backed_up_lan, last_backed_up_cloud, backed_up_to_lan, backed_up_to_cloud.

## 18.2 Config

notifications section defined for future smtplib email automation (daily run reports, weekly summaries).
No soft_delete, lan_versioning, anomaly_detection, or integrity_verification sections — permanently out of scope.

## 18.3 Code Provisions

ScanResult.deleted_files is populated and used to remove deleted files from the manifest.
ManifestDB has separate LAN and cloud backed-up flags for tracking.
All excluded folder paths in config — used by both Robocopy and Rclone.

## 18.4 Pre-Flight Checks (Planned After Core)

After core backup logic is complete and tested, pre-flight checks will be added:
- LAN backup server disk space (must have enough for full D:\ mirror)
- GCS bucket quota and accessibility
- Network connectivity to backup server and GCS
- Service account credential validation
- Source drive accessibility and read permissions
- Prefect server health check

## 18.5 Authentication Provision

BackupUI Windows Service runs as LocalSystem.
Future authentication would add FastAPI session middleware, bcrypt password hashing, and login route.

## 18.6 Service Account

A dedicated least-privilege domain service account will be provided during deployment.
PrefectWorker will run under this least-privilege account.

---

# SECTION 19 — KNOWN LIMITATIONS

These are intentional design choices. They are not bugs. They are documented so the client understands the trade-offs.

**Both destinations are true mirrors:**
Files deleted from D:\ are deleted from both the backup server (by Robocopy /MIR) and GCS (by rclone sync). Deleted files are logged and removed from the manifest. GCS native object versioning (retaining 1 older version with lifecycle rules configured during deployment) provides a safety net for accidental deletions on the cloud side. The LAN side has no versioning — deletions are immediate.

**Partial success manifest ambiguity:**
On LAN_PARTIAL or CLOUD_PARTIAL, all changed files are marked as backed up in manifest even though some may have failed. We cannot determine which specific files failed without parsing Robocopy's per-file log output.

**No pre-flight checks:**
If backup server disk is full, GCS quota exceeded, or network is down, the job fails mid-run. Pre-flight checks (disk space, GCS quota, connectivity, service account validation) will be added after core backup logic is complete and tested.

**No automatic backup server shutdown:**
DNS server role prevents automatic shutdown. Staff manually power off after backup completes.

**No integrity verification:**
Silent disk corruption on backup server is not detected until a restore attempt. GCS checksums verify cloud integrity. LAN integrity relies on filesystem-level checks (chkdsk, SMART monitoring).

**No restore interface:**
Recovery requires manual Rclone commands or direct file copy from backup server.

**No authentication on UI:**
Status page accessible to all LAN users without password.

---

# SECTION 20 — DEPENDENCY LIST

## 20.1 Runtime (requirements.txt)

```
prefect==3.*
pydantic==2.*
pydantic-settings==2.*
pyyaml==6.*
sqlalchemy==2.*
aiosqlite==0.*
xxhash==3.*
tenacity==8.*
wakeonlan==3.*
keyring==24.*
typer==0.*
loguru==0.*
httpx==0.*
fastapi==0.*
uvicorn==0.*
```

## 20.2 Development (requirements-dev.txt)

```
pytest==7.*
pytest-mock==3.*
pytest-cov==4.*
freezegun==1.*
pytest-asyncio==0.*
ruff==0.*
mypy==1.*
```

## 20.3 External Binaries

```
rclone.exe    >= 1.60.0   — from rclone.org/downloads
nssm.exe      >= 2.24     — from nssm.cc
python.exe    >= 3.11     — from python.org
robocopy.exe  any         — built into Windows Server 2016
ping.exe      any         — built into Windows Server 2016
icacls.exe    any         — built into Windows Server 2016
```

---

# SECTION 21 — OPEN ITEMS PENDING CLIENT RESPONSE

These items are open because the client questionnaire has not come back yet. Phase 1 uses the defaults listed. When the questionnaire returns, update config.yaml accordingly — no code changes required.

**Exclusion list:** Default exclusions applied. Client may add or remove folders after reviewing the list. Change: edit backup_scope.exclude_folders in config.yaml, restart PrefectWorker service.

**VSS for Tally/Winman:** If Q8 answer is "they run overnight" — VSS must be added before go-live. VSS is a code change, not config. Flag this immediately when questionnaire returns.

**Cloud provider:** GCS default confirmed. If client changes mind: update cloud_backup.provider and cloud_credentials, re-run setup_credentials.py. No code changes.

**Backup schedule time:** 23:00 default. If Q9 answer suggests different time: update schedule.daily_time, re-run create_deployment.py to update Prefect schedule.

**Notification recipients:** Prefect email automation recipients set during deployment Step 12. Update in Prefect UI when questionnaire returns.

**Data residency:** GCS asia-south1 (Mumbai) set as default. Confirm with client before bucket creation. Cannot easily change after 370GB is uploaded.

---

*Backup Automation System — Phase 1 Complete Scope & Technical Specification*
*Version 3.0 — All Decisions Final — Maximum Technical Clarity*
*Any AI tool or developer reading this document has everything needed to build Phase 1*
*Phase 2 provisions are explicitly marked throughout — do not implement them in Phase 1*
