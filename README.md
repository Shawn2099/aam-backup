# AAM Backup Automation System

Automated daily backup of a Windows Server 2016 D:\ drive (~370GB, 200K+ files) to two destinations simultaneously:

- **LAN** (192.168.10.10) via Robocopy `/MIR` — true mirror
- **GCS** (asia-south1) via Rclone `sync` — true mirror

Both destinations mirror source exactly. Deletions propagate. GCS retains 1 older version for 90 days. LAN has no versioning.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  D:\ Drive  │────▶│  Prefect     │────▶│  LAN Share  │
│  (Source)   │     │  Flow        │     │  (Robocopy) │
└─────────────┘     │  (Orchestrator)│     └─────────────┘
                    │              │
                    │              │     ┌─────────────┐
                    │              │────▶│  GCS Bucket │
                    │              │     │  (Rclone)   │
                    └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Status UI  │
                    │  FastAPI    │
                    └─────────────┘
```

## Features

- **Prefect 3.x orchestration** — Flow with concurrent LAN + cloud tasks, exponential backoff retries, timeouts, failure hooks
- **SQLite manifest database** — Thread-safe, WAL mode, tracks file checksums (xxHash64), backup status
- **Wake-on-LAN** — Automatic server wake before backup
- **Comprehensive pre-flight checks** — 20+ checks across 8 categories (system, storage, network, credentials, services, cloud, config, database)
- **VSS shadow copies** — Volume Shadow Copy support for locked Tally/Winman files
- **Post-backup integrity** — `rclone check` verification after cloud backup
- **Status UI** — FastAPI + Alpine.js + Tailwind, last run status, manual trigger button, `/health` endpoint
- **Deployment scripts** — Config validation, credential setup, GCS seeding, NSSM Windows service
- **Metrics collection** — JSONL per-run metrics for trend analysis
- **Config versioning** — Automatic backup of config.yaml before each run
- **Log backup** — Syncs log files to cloud for disaster recovery
- **Alerting** — Email on failure, weekly summary, no-changes warning

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Validate configuration
uv run scripts/validate_config.py validate

# 3. Start Prefect server
prefect server start

# 4. Create work pool and start worker
prefect work-pool create --type process default
PREFECT_API_URL=http://127.0.0.1:4200/api prefect worker start --pool default

# 5. Deploy the flow
uv run deploy/create_deployment.py create

# 6. Start status UI
uv run uvicorn ui.server:app --host 0.0.0.0 --port 8080
```

## Project Structure

```
core/        — Business logic (config, manifest, scanner, WoL, robocopy, rclone, preflight)
models/      — Pydantic config models, SQLAlchemy manifest model, ScanResult dataclass
tasks/       — Prefect task wrappers (config, scan, lan, cloud, preflight)
ui/          — FastAPI server + status page template
scripts/     — CLI tools (validate, credentials, connections, seed)
deploy/      — Deployment scripts (create deployment, NSSM install/uninstall)
tests/       — Pytest suite (161 tests)
flow.py      — Prefect flow definition (entry point)
config.yaml  — Configuration template
```

## Testing

```bash
uv run pytest tests/ -v
```

## Requirements

- Python 3.12+
- Windows Server 2016 (production) / Linux (development)
- Robocopy (Windows built-in)
- Rclone
- NSSM (Windows service wrapper)
- Prefect 3.x (self-hosted)

### Optional Dependencies

- `psutil` — Memory checks in pre-flight (install: `uv add psutil`)
- `ntplib` — Time sync verification (install: `uv add ntplib`)

For enhanced pre-flight checks:
```bash
uv sync --extra preflight
```

## Deployment Checklist

1. [ ] Fill in `config.yaml` (IPs, MAC address, GCS bucket, SMTP settings)
2. [ ] Store GCS service account key in Windows Credential Manager
3. [ ] Store SMTP password in Windows Credential Manager
4. [ ] Install Rclone and add to PATH
5. [ ] Run `uv sync --extra preflight`
6. [ ] Run `uv run scripts/validate_config.py validate`
7. [ ] Run `uv run scripts/test_connections.py test`
8. [ ] Run `uv run scripts/setup_credentials.py setup`
9. [ ] Run `uv run deploy/create_deployment.py create`
10. [ ] Run `deploy/install_services.bat` (as Administrator)
11. [ ] Verify status UI at `http://<server>:8080`
