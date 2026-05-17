# BACKUP AUTOMATION SYSTEM — ROADMAP

## Overview

| Metric | Value |
|--------|-------|
| Phases | 7 |
| Requirements | 15 |
| All v1 requirements covered | ✓ |

## Phase 1: Foundation

**Goal:** Project scaffolding, data models, and logging infrastructure

**Requirements:** CORE-01 (partial), CORE-02 (partial)

**Success Criteria:**
1. `pyproject.toml` configured with all dependencies
2. Directory structure created (core/, models/, tasks/, ui/, scripts/, deploy/, tests/)
3. Pydantic config models validate a sample config.yaml
4. SQLAlchemy FileManifest model creates SQLite table with WAL mode
5. Loguru configured with daily rotating file + stderr WARNING sink

**Deliverables:**
- `pyproject.toml` with runtime + dev dependencies
- `config.yaml` template with all fields documented
- `models/config_model.py` — AppConfig with all sub-models and validators
- `models/manifest_model.py` — FileManifest SQLAlchemy model with indexes
- `models/scan_result.py` — FileInfo and ScanResult dataclasses
- `core/logging_setup.py` — configure_logging() with two sinks
- `core/__init__.py`, `models/__init__.py`, `tasks/__init__.py`, `ui/__init__.py`, `tests/__init__.py`

## Phase 2: Core Business Logic

**Goal:** All standalone business logic modules — config loading, manifest DB, scanner, WoL, Robocopy, Rclone

**Requirements:** CORE-01, CORE-02, CORE-03, CORE-04, CORE-05, CORE-06

**Success Criteria:**
1. `load_config()` reads YAML, validates via Pydantic, retrieves GCS key from keyring
2. `ManifestDB` class supports all CRUD operations with threading.Lock on writes
3. `scan_drive()` walks D:\ with pruning, classifies files as new/modified/unchanged/deleted
4. `ensure_server_online()` pings, sends WoL if needed, polls with timeout
5. `run_robocopy()` executes /MIR command, classifies exit codes via bitmask
6. `run_rclone()` creates temp config+ACL+filter, executes sync, retries on code 5, cleans up in finally

**Deliverables:**
- `core/config_loader.py` — load_config(), ConfigurationError
- `core/manifest_db.py` — ManifestDB class with all methods
- `core/scanner.py` — scan_drive(), compute_checksum(), exclusion helpers
- `core/wol.py` — ensure_server_online(), ping_host(), WolError, WolTimeout
- `core/robocopy.py` — run_robocopy(), _classify_exit_code(), _parse_robocopy_output(), RobocopyResult
- `core/rclone.py` — run_rclone(), _write_temp_config(), _write_filter_file(), _classify_exit_code(), RcloneResult

## Phase 3: Orchestration

**Goal:** Prefect flow definition, task wrappers, and email automation

**Requirements:** ORCH-01, ORCH-02

**Success Criteria:**
1. Four Prefect tasks defined: load_config_task, scan_task, lan_backup_task, cloud_backup_task
2. Flow runs with ThreadPoolTaskRunner(max_workers=2), LAN+cloud concurrent
3. Flow computes overall status (COMPLETE/PARTIAL_FAILURE/FAILED)
4. Prefect email automation configured for failure alerts via UI Blocks + Automations
5. Manual flow trigger works from Prefect UI

**Deliverables:**
- `flow.py` — nightly-backup flow definition
- `tasks/config_task.py` — load_config_task()
- `tasks/scan_task.py` — scan_task(config, db)
- `tasks/lan_task.py` — lan_backup_task(config, scan_result, db)
- `tasks/cloud_task.py` — cloud_backup_task(config, gcs_key_path, scan_result, db)
- Prefect deployment created via `deploy/create_deployment.py`

## Phase 4: Status UI

**Goal:** FastAPI HTML status page accessible on LAN

**Requirements:** UI-01

**Success Criteria:**
1. `GET /` returns HTML page with last run status, next run countdown, trigger button
2. `POST /trigger` creates immediate flow run via Prefect API
3. Page auto-refreshes every 60 seconds via Alpine.js
4. UI accessible at http://0.0.0.0:8080 from any LAN machine
5. Button disabled when backup already in progress

**Deliverables:**
- `ui/server.py` — FastAPI app with GET / and POST /trigger
- `ui/templates/status.html` — Alpine.js + Tailwind CSS single-page UI

## Phase 5: Deployment Scripts

**Goal:** All scripts and batch files for production deployment

**Requirements:** DEPLOY-01, DEPLOY-02, DEPLOY-03

**Success Criteria:**
1. `setup_credentials.py` stores GCS key path in Windows Credential Manager
2. `validate_config.py` loads config and prints validation result
3. `seed_cloud.py` does one-time initial GCS upload (resumable, rate-limited, updates manifest)
4. `test_connections.py` tests all connections — all must pass before services start
5. `install_services.bat` installs PrefectServer, PrefectWorker, BackupUI via NSSM
6. `uninstall_services.bat` stops and removes all three services
7. `create_deployment.py` registers nightly-backup flow with cron schedule

**Deliverables:**
- `scripts/setup_credentials.py`
- `scripts/validate_config.py`
- `scripts/seed_cloud.py`
- `scripts/test_connections.py`
- `deploy/install_services.bat`
- `deploy/uninstall_services.bat`
- `deploy/create_deployment.py`

## Phase 6: Tests

**Goal:** Unit and integration test suite

**Requirements:** TEST-01, TEST-02

**Success Criteria:**
1. All unit tests pass: config loader, scanner, robocopy, rclone, wol, manifestdb
2. Integration tests pass: flow definition, UI endpoints
3. Test coverage reported via pytest-cov
4. Tests run on Linux (dev environment) with mocked Windows-specific calls

**Deliverables:**
- `tests/conftest.py` — shared fixtures
- `tests/test_config_loader.py`
- `tests/test_scanner.py`
- `tests/test_robocopy_wrapper.py`
- `tests/test_rclone_wrapper.py`
- `tests/test_wol.py`
- `tests/test_manifest_db.py`
- Integration tests for flow and UI

## Phase 7: Pre-Flight Checks

**Goal:** Safety checks before backup runs

**Requirements:** PREFLIGHT-01

**Success Criteria:**
1. Disk space check on LAN backup server (enough for full D:\ mirror)
2. GCS bucket quota and accessibility verified
3. Network connectivity to backup server and GCS confirmed
4. Service account credential validated
5. Source drive accessibility and read permissions checked
6. Prefect server health check passes
7. Pre-flight runs before scan_task, fails flow if any check fails

**Deliverables:**
- `core/preflight.py` — all pre-flight check functions
- Integration into `flow.py` before scan_task

---
*Last updated: 2026-05-18 after roadmap creation*
