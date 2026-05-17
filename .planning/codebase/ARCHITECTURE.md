<!-- refreshed: 2026-05-18 -->
# Architecture

**Analysis Date:** 2026-05-18

## System Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AAMBDC001 (192.168.10.5) — Windows Server 2016            │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        Prefect 3.x Self-Hosted                        │  │
│  │                                                                       │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────────┐  │  │
│  │  │  PrefectServer   │  │  PrefectWorker   │  │    BackupUI         │  │  │
│  │  │  (Windows Svc)   │  │  (Windows Svc)   │  │  (Windows Svc)      │  │  │
│  │  │  Port 4200       │  │  backup-pool     │  │  Port 8080          │  │  │
│  │  │  prefect.db      │  │  polls server    │  │  FastAPI + Alpine   │  │  │
│  │  └────────┬─────────┘  └────────┬─────────┘  └─────────┬───────────┘  │  │
│  │           │                     │                       │              │  │
│  │           │                     ▼                       │              │  │
│  │           │           ┌──────────────────┐              │              │  │
│  │           │           │  nightly-backup  │              │              │  │
│  │           │           │  flow (flow.py)  │              │              │  │
│  │           │           │  ThreadPool(2)   │              │              │  │
│  │           │           └────────┬─────────┘              │              │  │
│  │           │                    │                        │              │  │
│  │           │      ┌─────────────┼─────────────┐          │              │  │
│  │           │      ▼             ▼             ▼          │              │  │
│  │           │  load_config   scan_task    lan_backup_task │              │  │
│  │           │  (sequential)  (sequential)  (concurrent)   │              │  │
│  │           │                                │            │              │  │
│  │           │                     cloud_backup_task       │              │  │
│  │           │                     (concurrent)            │              │  │
│  │           └────────────────────┼────────────────────────┘              │  │
│  └────────────────────────────────┼───────────────────────────────────────┘  │
│                                    │                                         │
│  ┌─────────────────────────────────┼──────────────────────────────────────┐  │
│  │                    Application Layer (C:\BackupAgent\)                  │  │
│  │                                 │                                       │  │
│  │  ┌──────────────┐  ┌────────────┼───────────┐  ┌────────────────────┐  │  │
│  │  │  core/       │  │  tasks/    │           │  │  models/           │  │  │
│  │  │  config_loader│  │  config_  │           │  │  config_model      │  │  │
│  │  │  manifest_db  │  │  scan_    │           │  │  manifest_model    │  │  │
│  │  │  scanner      │  │  lan_     │           │  │  scan_result       │  │  │
│  │  │  wol          │  │  cloud_   │           │  └────────────────────┘  │  │
│  │  │  robocopy     │  └─────────────────────────┘                        │  │
│  │  │  rclone       │                                                     │  │
│  │  │  logging_setup│  ┌──────────────────────────────────────────────┐   │  │
│  │  └──────────────┘  │  config.yaml  ←  Re-read every flow run       │   │  │
│  │                    │  manifest.db  ←  FileManifest (SQLite WAL)     │   │  │
│  │                    └──────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└────────────┬───────────────────────────────────────────────┬────────────────┘
             │                                               │
             ▼                                               ▼
┌────────────────────────┐                  ┌────────────────────────────────┐
│  LAN Backup Server     │                  │  Google Cloud Storage          │
│  192.168.10.10         │                  │  asia-south1 (Mumbai)          │
│  \\192.168.10.10\      │                  │  Bucket: [config]              │
│  hp srv manual backup$ │                  │  /D_Drive_Backup/              │
│  Robocopy /MIR         │                  │  rclone sync                   │
│  True mirror           │                  │  True mirror                   │
│  No versioning         │                  │  1 older version / 90 days     │
└────────────────────────┘                  └────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| PrefectServer | Stores flow run state, schedules, task logs; serves Prefect UI | NSSM Windows Service |
| PrefectWorker | Polls server for scheduled runs; executes backup flow | NSSM Windows Service |
| BackupUI | Serves HTML status page on LAN; queries Prefect API | `ui/server.py` |
| Flow Orchestrator | Coordinates 4 tasks, evaluates overall status | `flow.py` |
| Config Loader | Reads config.yaml, validates via Pydantic, retrieves credentials | `core/config_loader.py` |
| Scanner | Walks D:\, applies exclusions, classifies files, computes checksums | `core/scanner.py` |
| ManifestDB | SQLite operations with threading.Lock, WAL mode on every connection | `core/manifest_db.py` |
| WoL Module | Ping check, magic packet, stability wait | `core/wol.py` |
| Robocopy Wrapper | Subprocess execution, exit code classification, manifest update | `core/robocopy.py` |
| Rclone Wrapper | Temp config/filter creation, subprocess execution, retry logic | `core/rclone.py` |
| Logging Setup | Loguru two-sink configuration (file + stderr) | `core/logging_setup.py` |

## Pattern Overview

**Overall:** Single-machine Prefect-orchestrated backup system with concurrent dual-destination mirror

**Key Characteristics:**
- Prefect 3.x self-hosted as the orchestration backbone — all scheduling, state, retry, logging handled by Prefect
- Custom code is only business logic — change detection, subprocess wrappers, manifest DB, status UI
- LAN and cloud backup run concurrently via `ThreadPoolTaskRunner(max_workers=2)`
- Change detection via SQLite manifest with xxHash64 checksums — only changed files trigger backup
- Config re-read every flow run — never cached between runs
- All values from config.yaml or Windows Credential Manager — no hardcoded values
- `pathlib.Path` throughout — cross-platform compatible despite Windows target

## Layers

**Orchestration Layer:**
- Purpose: Schedule, execute, and monitor backup workflow
- Location: `flow.py`, `tasks/`
- Contains: Prefect flow definition, four task wrappers
- Depends on: Prefect 3.x, core modules, models
- Used by: PrefectWorker (Windows Service)

**Core Business Logic Layer:**
- Purpose: Change detection, file scanning, backup execution, WoL, logging
- Location: `core/`
- Contains: config_loader, manifest_db, scanner, wol, robocopy, rclone, logging_setup
- Depends on: models, external binaries (robocopy, rclone), libraries (xxhash, keyring, wakeonlan)
- Used by: tasks layer

**Models Layer:**
- Purpose: Data structures and validation
- Location: `models/`
- Contains: Pydantic config models, SQLAlchemy manifest model, dataclasses (FileInfo, ScanResult)
- Depends on: pydantic, sqlalchemy
- Used by: core and tasks layers

**UI Layer:**
- Purpose: Serve status page on LAN
- Location: `ui/`
- Contains: FastAPI server, HTML template
- Depends on: FastAPI, uvicorn, httpx (for Prefect API calls), Alpine.js, Tailwind CSS
- Used by: LAN users via browser

**Scripts Layer:**
- Purpose: Deployment, setup, testing, one-time operations
- Location: `scripts/`
- Contains: setup_credentials, validate_config, seed_cloud, test_connections
- Depends on: core modules, keyring, typer
- Used by: administrator during deployment

**Deployment Layer:**
- Purpose: Windows Service installation, Prefect deployment creation
- Location: `deploy/`
- Contains: install_services.bat, uninstall_services.bat, create_deployment.py
- Depends on: NSSM, Prefect CLI
- Used by: administrator during deployment

## Data Flow

### Primary Request Path (Nightly Backup)

1. **Prefect scheduler triggers** at 23:00 IST — `flow.py`
2. **load_config_task** — reads `config.yaml`, validates via Pydantic, retrieves GCS key from Credential Manager
3. **scan_task** — opens ManifestDB, walks D:\ with os.walk(topdown=True), prunes exclusions, classifies files (new/modified/deleted/unchanged), computes xxHash64 only for changed files
4. **Flow evaluates has_changes?** — if no changes, flow completes immediately
5. **lan_backup_task + cloud_backup_task submitted concurrently** via `task.submit()` — `flow.py`
6. **lan_backup_task** — WoL ping check → send magic packet if offline → stability wait → Robocopy `/MIR` subprocess → parse exit code bitmask → update manifest via `db.batch_mark_lan_backed_up()`
7. **cloud_backup_task** — write temp rclone.conf with ACL → write temp filter file → rclone sync subprocess → parse exit code → retry on code 5 with backoff → update manifest via `db.batch_mark_cloud_backed_up()` → delete temp files in finally
8. **Flow collects results** — both futures complete → compute overall status (COMPLETE/PARTIAL_FAILURE/FAILED)
9. **If FAILED** — raise exception → Prefect marks flow run as Failed → Prefect email automation fires failure alert

### WoL Flow (LAN Backup Pre-Check)

1. **Ping check** — `ping -n 3 -w 1000 [ip]` via subprocess (`core/wol.py`)
2. **If online** — skip WoL, proceed to Robocopy
3. **If offline** — send WoL magic packet via `wakeonlan.send_magic_packet()`
4. **Poll loop** — ping every 15s for up to 300s
5. **On response** — stability wait 30s → return True
6. **On timeout** — raise WolTimeout → task returns LAN_FAILED

### Change Detection Algorithm

1. **os.walk(topdown=True)** on source drive
2. **Prune dirnames in place** — `dirnames[:] = [d for d in dirnames if not is_excluded_folder(...)]`
3. **For each file**: extension check → pattern check → os.stat → relative_path computation → manifest lookup
4. **Classification**: not in manifest → NEW; size+mtime match → UNCHANGED; size or mtime differs → compute xxHash64 → checksum match → METADATA CHANGE; checksum differs → MODIFIED
5. **After walk**: deleted_files = manifest_paths - current_paths → remove from manifest

**State Management:**
- FileManifest SQLite database tracks per-file backup state
- `checksum="pending"` for new files until first backup confirmation
- `threading.Lock` on all ManifestDB writes, WAL mode for concurrent reads
- Prefect handles flow run state — separate from manifest.db

## Key Abstractions

**ScanResult:**
- Purpose: Output of scan_drive() — contains new_files, modified_files, deleted_files lists
- Examples: `models/scan_result.py`
- Pattern: Python dataclass with typed fields

**FileInfo:**
- Purpose: Represents one file found during scan — relative_path, size, mtime, checksum
- Examples: `models/scan_result.py`
- Pattern: Python dataclass

**AppConfig:**
- Purpose: Top-level validated configuration from config.yaml
- Examples: `models/config_model.py`
- Pattern: Pydantic BaseSettings with nested sub-models (FirmConfig, PathsConfig, LanBackupConfig, etc.)

**FileManifest:**
- Purpose: SQLAlchemy declarative model for file_manifest table
- Examples: `models/manifest_model.py`
- Pattern: SQLAlchemy ORM with indexes defined in `__table_args__`

**RobocopyResult / RcloneResult:**
- Purpose: Dataclass capturing subprocess execution outcome
- Examples: `core/robocopy.py`, `core/rclone.py`
- Pattern: Dataclass with status, exit_code, files_copied, bytes_copied, duration fields

## Entry Points

**Prefect Flow:**
- Location: `flow.py`
- Triggers: Cron schedule (23:00 IST), manual trigger from UI or CLI
- Responsibilities: Orchestrate 4 tasks, evaluate overall status

**FastAPI Status UI:**
- Location: `ui/server.py`
- Triggers: HTTP requests on port 8080
- Responsibilities: Serve status.html, query Prefect API for run state, handle POST /trigger

**Deployment Scripts:**
- Location: `deploy/install_services.bat`, `deploy/create_deployment.py`
- Triggers: Administrator execution during deployment
- Responsibilities: Install Windows Services, register Prefect deployment

## Architectural Constraints

- **Threading:** Single-machine, Prefect ThreadPoolTaskRunner(max_workers=2) for concurrent LAN+cloud tasks; ManifestDB uses threading.Lock for write safety
- **Global state:** No module-level singletons — single shared ManifestDB instance passed to all tasks via function arguments
- **Circular imports:** Not yet present (greenfield); layer dependency order: models → core → tasks → flow.py
- **No hardcoded values:** Every value from config.yaml or Windows Credential Manager
- **No shell=True:** All subprocess calls use argument lists only
- **pathlib.Path throughout:** Never os.path string concatenation
- **Config re-read every flow run:** Not cached between runs
- **UTC ISO8601 timestamps in SQLite:** Displayed as local time in logs

## Anti-Patterns

### Treating Robocopy Exit Code as Direct Value

**What happens:** Robocopy exit codes are bitmasks — bits are independent flags
**Why it's wrong:** Direct comparison (e.g., `exit_code == 1`) misses composite codes (e.g., 3 = files copied + extra files exist)
**Do this instead:** Use bitwise AND — `if exit_code & 16: LAN_FAILED; elif exit_code & 8: LAN_PARTIAL; elif exit_code <= 7: LAN_COMPLETE` (`core/robocopy.py`)

### Computing Checksums for New Files During Scan

**What happens:** New files would be read twice — once for checksum during scan, once by Robocopy/Rclone during backup
**Why it's wrong:** Doubles unnecessary disk I/O on a server with 200K+ files
**Do this instead:** Set `checksum="pending"` for new files, compute after backup confirmation (`core/scanner.py`, `core/robocopy.py`)

### Caching Config Between Flow Runs

**What happens:** Config loaded once at startup and reused
**Why it's wrong:** Config changes (exclusion list, schedule, credentials) would not take effect
**Do this instead:** Re-read config.yaml at the start of every flow run via `load_config_task` (`tasks/config_task.py`)

### Assigning New List to dirnames in os.walk

**What happens:** `dirnames = [d for d in dirnames if ...]` creates a new list
**Why it's wrong:** os.walk's descent is not affected — excluded folders are still walked
**Do this instead:** In-place modification — `dirnames[:] = [d for d in dirnames if ...]` (`core/scanner.py`)

## Error Handling

**Strategy:** Fail-fast with Prefect state management — invalid config fails flow immediately, backup failures marked at task level, overall status computed from both destinations

**Patterns:**
- Custom exceptions: `ConfigurationError`, `WolError`, `WolTimeout`, `DatabaseError` — defined in respective modules
- Config validation: Pydantic validators on every field — flow fails immediately if invalid
- Subprocess errors: Caught, logged, returned as status dict (LAN_FAILED/CLOUD_FAILED) — flow continues with other destination
- Temp file cleanup: Always in `finally` blocks — temp rclone config and filter files deleted even on exception
- WAL mode failure: Hard failure — if WAL mode cannot be set, raise DatabaseError immediately, log CRITICAL

## Cross-Cutting Concerns

**Logging:** Loguru with two sinks — rotating daily file (DEBUG+, 30-day retention, .gz compression) and stderr (WARNING+); inside Prefect tasks, Loguru also forwards to Prefect task logger
**Validation:** Pydantic validators on all config fields — path existence, UNC pattern, MAC format, bucket naming, range checks
**Authentication:** Windows Credential Manager via keyring for GCS key path; service account for PrefectWorker; no auth on status UI (LAN-only)

---

*Architecture analysis: 2026-05-18*
