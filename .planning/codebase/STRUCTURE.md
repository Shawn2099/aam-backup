# Codebase Structure

**Analysis Date:** 2026-05-18

## Directory Layout

```
AAM_BACKUP_V2/
├── config.yaml              # Single config file — all settings, re-read every flow run
├── flow.py                  # Prefect flow definition — entry point for worker execution
├── pyproject.toml           # Project metadata, Ruff/mypy/pytest configuration
├── requirements.txt         # Runtime Python dependencies (to be created)
├── requirements-dev.txt     # Development and testing dependencies (to be created)
├── .python-version          # Python version pin (3.12)
├── .env.example             # Documents Prefect env vars (not for secrets)
├── README.md                # Deployment instructions
├── AGENTS.md                # Agent context file
├── DECISIONS.md             # Decision log
├── plan.md                  # Complete technical specification
├── manifest.db              # FileManifest SQLite — created on first run
├── prefect.db               # Prefect state SQLite — created by Prefect server
│
├── core/                    # Business logic modules
│   ├── __init__.py
│   ├── config_loader.py     # load_config(), ConfigurationError
│   ├── manifest_db.py       # ManifestDB class, threading.Lock, WAL mode
│   ├── scanner.py           # scan_drive(), compute_checksum(), exclusion functions
│   ├── wol.py               # ensure_server_online(), ping_host(), WolError, WolTimeout
│   ├── robocopy.py          # run_robocopy(), _classify_exit_code(), RobocopyResult
│   ├── rclone.py            # run_rclone(), _write_temp_config(), _write_filter_file(), RcloneResult
│   └── logging_setup.py     # configure_logging() — Loguru two-sink setup
│
├── models/                  # Data structures and validation
│   ├── __init__.py
│   ├── config_model.py      # AppConfig, FirmConfig, PathsConfig, LanBackupConfig, etc.
│   ├── manifest_model.py    # FileManifest — SQLAlchemy declarative model
│   └── scan_result.py       # FileInfo, ScanResult — dataclasses
│
├── tasks/                   # Prefect task wrappers
│   ├── __init__.py
│   ├── config_task.py       # load_config_task() — calls core.config_loader
│   ├── scan_task.py         # scan_task(config, db) — calls core.scanner
│   ├── lan_task.py          # lan_backup_task(config, scan_result, db) — calls core.wol + core.robocopy
│   └── cloud_task.py        # cloud_backup_task(config, gcs_key_path, scan_result, db) — calls core.rclone
│
├── ui/                      # FastAPI status page
│   ├── __init__.py
│   ├── server.py            # FastAPI app — GET /, POST /trigger
│   └── templates/
│       └── status.html      # Single HTML — Alpine.js + Tailwind CSS
│
├── scripts/                 # Deployment & setup scripts (standalone, not part of flow)
│   ├── setup_credentials.py # Store GCS key path in Credential Manager
│   ├── validate_config.py   # Validate config.yaml before starting services
│   ├── seed_cloud.py        # One-time initial full upload of D:\ to GCS
│   └── test_connections.py  # Test all connections before go-live
│
├── deploy/                  # Service installation & Prefect deployment
│   ├── install_services.bat # NSSM commands for PrefectServer, PrefectWorker, BackupUI
│   ├── uninstall_services.bat # Remove all three Windows Services
│   └── create_deployment.py # Register nightly-backup as Prefect deployment
│
├── tests/                   # Pytest test suite
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures: temp config, temp database, mock scan results
│   ├── test_config_loader.py
│   ├── test_scanner.py
│   ├── test_robocopy_wrapper.py
│   ├── test_rclone_wrapper.py
│   ├── test_wol.py
│   └── test_manifest_db.py
│
├── logs/                    # Loguru rotating daily logs
├── rclone_temp/             # Temp rclone configs (deleted after each run)
└── rclone.exe               # Rclone binary — copied here during deployment
```

## Directory Purposes

**core/:**
- Purpose: All business logic — the engine of the backup system
- Contains: Config loading, manifest database, file scanning, WoL, Robocopy wrapper, Rclone wrapper, logging setup
- Key files: `core/manifest_db.py` (thread-safe SQLite), `core/scanner.py` (change detection), `core/robocopy.py` (LAN backup), `core/rclone.py` (cloud backup)

**models/:**
- Purpose: Data structures — Pydantic config models, SQLAlchemy ORM, dataclasses
- Contains: AppConfig (validated config), FileManifest (DB model), ScanResult/FileInfo (scan output)
- Key files: `models/config_model.py` (all config sub-models with validators), `models/manifest_model.py` (SQLAlchemy table definition)

**tasks/:**
- Purpose: Prefect task wrappers — thin layer between Prefect and core logic
- Contains: Four tasks — config, scan, lan_backup, cloud_backup
- Key files: `tasks/lan_task.py` (WoL + Robocopy), `tasks/cloud_task.py` (Rclone with retry)

**ui/:**
- Purpose: Status page served on LAN — read-only view of backup state
- Contains: FastAPI server, single HTML template
- Key files: `ui/server.py` (queries Prefect API), `ui/templates/status.html` (Alpine.js + Tailwind)

**scripts/:**
- Purpose: Standalone scripts for deployment and one-time operations — NOT part of the backup flow
- Contains: Credential setup, config validation, cloud seeding, connection testing
- Key files: `scripts/seed_cloud.py` (initial full upload), `scripts/test_connections.py` (pre-flight checks)

**deploy/:**
- Purpose: Windows Service installation and Prefect deployment registration
- Contains: Batch files for NSSM, Python script for Prefect deployment
- Key files: `deploy/install_services.bat` (three services), `deploy/create_deployment.py` (cron schedule)

**tests/:**
- Purpose: Pytest test suite — unit tests for core modules
- Contains: conftest.py with shared fixtures, test files for each core module
- Key files: `tests/test_manifest_db.py` (thread safety tests), `tests/test_scanner.py` (exclusion logic tests)

**logs/:**
- Purpose: Loguru rotating daily log files
- Contains: `backup_YYYY-MM-DD.log`, `robocopy_YYYY-MM-DD.log`, service stdout/stderr logs
- Note: Created on first run, not committed to git

## Key File Locations

**Entry Points:**
- `flow.py`: Prefect flow definition — executed by PrefectWorker
- `ui/server.py`: FastAPI status UI — executed by NSSM as BackupUI service
- `deploy/install_services.bat`: Windows Service installation — run once during deployment
- `deploy/create_deployment.py`: Prefect deployment creation — run once after Prefect server starts

**Configuration:**
- `config.yaml`: Single config file — all settings, never modified by software
- `pyproject.toml`: Project metadata, tool configuration
- `.python-version`: Python version pin (3.12)

**Core Logic:**
- `core/scanner.py`: Change detection engine — the heart of the system
- `core/manifest_db.py`: Thread-safe SQLite with WAL mode
- `core/robocopy.py`: LAN backup via Robocopy `/MIR`
- `core/rclone.py`: Cloud backup via rclone sync

**Testing:**
- `tests/conftest.py`: Shared fixtures
- `tests/test_manifest_db.py`: Thread safety and WAL mode tests
- `tests/test_scanner.py`: Exclusion and classification tests

## Naming Conventions

**Files:**
- Python modules: snake_case (`config_loader.py`, `manifest_db.py`)
- Test files: `test_<module>.py` (`test_config_loader.py`)
- Batch files: snake_case with `.bat` extension (`install_services.bat`)
- Config: `config.yaml`
- Templates: snake_case with `.html` extension (`status.html`)

**Functions:**
- Public functions: snake_case (`load_config()`, `scan_drive()`, `run_robocopy()`)
- Private functions: leading underscore (`_classify_exit_code()`, `_write_temp_config()`)
- Prefect tasks: snake_case with `_task` suffix (`load_config_task()`, `scan_task()`)

**Classes:**
- Pydantic models: PascalCase (`AppConfig`, `FirmConfig`, `PathsConfig`)
- SQLAlchemy models: PascalCase (`FileManifest`)
- Dataclasses: PascalCase (`FileInfo`, `ScanResult`, `RobocopyResult`, `RcloneResult`)
- Exceptions: PascalCase with `Error` or `Timeout` suffix (`ConfigurationError`, `WolError`, `WolTimeout`)

**Directories:**
- All lowercase, singular (`core/`, `models/`, `tasks/`, `ui/`, `scripts/`, `deploy/`, `tests/`)

## Where to Add New Code

**New Core Module:**
- Implementation: `core/<module_name>.py`
- Tests: `tests/test_<module_name>.py`
- Import from tasks via: `from core.<module_name> import <function>`

**New Prefect Task:**
- Implementation: `tasks/<task_name>.py`
- Import in `flow.py` and call with `task.submit()` or directly

**New Model:**
- Pydantic config model: `models/config_model.py` (add sub-model, update AppConfig)
- SQLAlchemy model: `models/manifest_model.py` (add new table)
- Dataclass: `models/scan_result.py` or new file in `models/`

**New Script:**
- Implementation: `scripts/<script_name>.py`
- Use typer for CLI interface

**New UI Route:**
- Implementation: `ui/server.py` (add route)
- Template: `ui/templates/<page>.html`

**New Test:**
- Implementation: `tests/test_<module>.py`
- Fixtures: `tests/conftest.py`

**New Deployment Script:**
- Implementation: `deploy/<script_name>.py` or `deploy/<script_name>.bat`

## Special Directories

**logs/:**
- Purpose: Loguru rotating daily log files
- Generated: Yes — created on first run
- Committed: No — excluded from backup, not in git

**rclone_temp/:**
- Purpose: Temporary rclone config and filter files
- Generated: Yes — created at task start, deleted in finally blocks
- Committed: No — excluded from backup

**tests/:**
- Purpose: Pytest test suite
- Generated: No — written by developers
- Committed: Yes

**deploy/:**
- Purpose: Windows Service installation and Prefect deployment
- Generated: No — written by developers
- Committed: Yes

---

*Structure analysis: 2026-05-18*
