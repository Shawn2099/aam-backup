# Technology Stack

**Analysis Date:** 2026-05-18

## Languages

**Primary:**
- Python 3.12 — All application code (core logic, tasks, UI, scripts)
  - `.python-version` file pins to 3.12
  - `pyproject.toml` requires `>=3.12`
  - Production target: Python 3.11+ on Windows Server 2016

## Runtime

**Environment:**
- Windows Server 2016 Datacenter — production deployment target
- Linux — development environment

**Package Manager:**
- pip (via `.venv/` virtual environment present)
- Lockfile: not yet present (project is greenfield)

## Frameworks

**Core:**
- Prefect 3.x (`prefect==3.*`) — Workflow orchestration, scheduling, state management, retry logic, built-in UI
- Pydantic 2.x (`pydantic==2.*`) — Config validation via `pydantic-settings` BaseSettings models
- SQLAlchemy 2.x (`sqlalchemy==2.*`) — ORM for FileManifest SQLite database
- FastAPI (`fastapi==0.*`) — Status UI web server
- Uvicorn (`uvicorn==0.*`) — ASGI server for FastAPI

**Testing:**
- pytest 7.x (`pytest==7.*`) — Test runner
- pytest-mock 3.x (`pytest-mock==3.*`) — Mocking support
- pytest-cov 4.x (`pytest-cov==4.*`) — Coverage reporting
- pytest-asyncio 0.x (`pytest-asyncio==0.*`) — Async test support
- freezegun 1.x (`freezegun==1.*`) — Time freezing for tests

**Build/Dev:**
- ruff 0.x (`ruff==0.*`) — Linting
- mypy 1.x (`mypy==1.*`) — Type checking

## Key Dependencies

**Critical:**
- `pydantic-settings==2.*` — Config loading from `config.yaml` with validation
- `pyyaml==6.*` — YAML parsing for config file
- `aiosqlite==0.*` — Async SQLite driver for Prefect's database
- `xxhash==3.*` — xxHash64 checksums for change detection (8MB chunk reads)
- `tenacity==8.*` — Retry logic (rclone retry backoff)
- `wakeonlan==3.*` — WoL magic packet sending
- `keyring==24.*` — Windows Credential Manager integration for GCS key path
- `loguru==0.*` — Rotating daily log files with two-sink setup
- `httpx==0.*` — HTTP client for FastAPI UI to query Prefect API
- `typer==0.*` — CLI scripts (setup_credentials, validate_config, etc.)

**Infrastructure:**
- `robocopy.exe` — Built into Windows Server 2016, LAN mirror via `/MIR`
- `rclone.exe >= 1.60.0` — Cloud sync to GCS, deployed to `C:\BackupAgent\rclone.exe`
- `nssm.exe >= 2.24` — Windows Service manager for PrefectServer, PrefectWorker, BackupUI
- `ping.exe` — Built into Windows, WoL server reachability check
- `icacls.exe` — Built into Windows, temp file ACL management

## Configuration

**Environment:**
- `config.yaml` — Single config file, all settings, re-read every flow run
- Windows Credential Manager — GCS service account key path stored as `BackupAgent_GCS`
- `.env.example` — Documents Prefect env vars (not used for secrets)
- Environment variables set via NSSM service configuration:
  - `PREFECT_API_DATABASE_CONNECTION_URL` — SQLite path for Prefect state DB
  - `PREFECT_API_URL` — Local Prefect API endpoint
  - `PREFECT_SERVER_API_HOST` / `PREFECT_SERVER_API_PORT`

**Build:**
- `pyproject.toml` — Project metadata, Ruff/mypy/pytest config (not yet populated)
- `requirements.txt` — Runtime dependencies (not yet created)
- `requirements-dev.txt` — Dev dependencies (not yet created)

## Platform Requirements

**Development:**
- Python 3.12
- Virtual environment (`.venv/` already exists)
- Linux or macOS for development

**Production:**
- Windows Server 2016 Datacenter
- Python 3.11+ installed for all users
- NSSM installed at `C:\Windows\System32\nssm.exe`
- Rclone at `C:\BackupAgent\rclone.exe`
- Domain service account with LAN share access
- GCS service account JSON key at `C:\BackupAgent\gcs_service_account.json`
- Three Windows Services: PrefectServer (port 4200), PrefectWorker, BackupUI (port 8080)

## Frontend Stack (Status UI)

- Alpine.js — Client-side interactivity (auto-refresh, countdown, trigger button)
- Tailwind CSS via CDN — Styling
- Single HTML file: `ui/templates/status.html`
- No build step — served directly by FastAPI

---

*Stack analysis: 2026-05-18*
