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
- **Pre-flight checks** — Disk space, connectivity, binary availability before backup starts
- **Status UI** — FastAPI + Alpine.js + Tailwind, last run status, manual trigger button
- **Deployment scripts** — Config validation, credential setup, GCS seeding, NSSM Windows service

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
tests/       — Pytest suite (115 tests)
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
