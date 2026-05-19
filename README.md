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
- **Comprehensive pre-flight checks** — 20+ checks across 9 categories (system, storage, network, credentials, services, cloud, config, database, dry-run preview)
- **Dry-run preview** — `robocopy /L` and `rclone --dry-run` before each backup to preview changes
- **VSS shadow copies** — Volume Shadow Copy support for locked Tally/Winman files
- **Post-backup integrity** — `rclone check` verification after cloud backup, xxHash64 checksum verification on LAN
- **Automated test restore** — Periodic random file verification from both LAN and GCS
- **Status UI** — FastAPI + Alpine.js + Tailwind, last run status, manual trigger, `/health`, `/metrics` endpoints
- **Deployment scripts** — Config validation, credential setup, GCS seeding, Servy Windows service
- **Metrics collection** — JSONL per-run metrics for trend analysis (throughput, capacity, file counts)
- **Config versioning** — Automatic backup of config.yaml before each run + copy to LAN/GCS
- **Log backup** — Syncs log files to cloud for disaster recovery
- **Alerting** — Email on failure, weekly/monthly reports, no-changes warning, LAN space warning, duration warning
- **Capacity tracking** — LAN free space monitoring, total source size/file count per run
- **Restore CLI** — List, restore, and verify backups from LAN or GCS

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Validate configuration
uv run scripts/validate_config.py validate

# 3. Start Prefect server
prefect server start

# 4. Create work pool and start worker
prefect work-pool create default --type process
PREFECT_API_URL=http://127.0.0.1:4200/api prefect worker start --pool default

# 5. Deploy the flow
uv run deploy/create_deployment.py create

# 6. Start status UI
uv run uvicorn ui.server:app --host 0.0.0.0 --port 8080
```

## Project Structure

```
core/        — Business logic (config, manifest, scanner, WoL, robocopy, rclone, preflight, verify)
models/      — Pydantic config models, SQLAlchemy manifest model, ScanResult dataclass
tasks/       — Prefect task wrappers (config, scan, lan, cloud, preflight, report, metrics, test_restore)
ui/          — FastAPI server + status page template
scripts/     — CLI tools (validate, credentials, connections, seed, restore)
deploy/      — Deployment scripts (create deployment, Servy install/uninstall)
tests/       — Pytest suite (210 tests)
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
- Servy (Windows service wrapper)
- Prefect 3.x (self-hosted)

### Optional Dependencies

- `psutil` — Memory checks in pre-flight (install: `uv add psutil`)
- `ntplib` — Time sync verification (install: `uv add ntplib`)

For enhanced pre-flight checks:
```bash
uv sync --extra preflight
```

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete step-by-step deployment guide on Windows Server 2016.

### Quick Deploy Checklist

1. [ ] Install Python 3.12+, uv, rclone, Servy
2. [ ] Create GCS bucket + service account
3. [ ] Copy project files to `C:\BackupAgent\`
4. [ ] Fill in `config.yaml` (IPs, MAC, bucket, SMTP)
5. [ ] Store credentials in Windows Credential Manager
6. [ ] Run `uv sync --extra preflight`
7. [ ] Run `uv run scripts/validate_config.py validate`
8. [ ] Run `uv run scripts/test_connections.py test`
9. [ ] Run `deploy/install_services.bat` (as Administrator)
10. [ ] Run `uv run deploy/create_deployment.py create`
11. [ ] Verify status UI at `http://<server>:8080`
12. [ ] Run post-deployment verification (see docs/DEPLOYMENT.md)

## Disaster Recovery

See [docs/DR_RUNBOOK.md](docs/DR_RUNBOOK.md) for recovery procedures including:
- Single file restore (LAN, GCS, CLI)
- Full server recovery (RTO: 8-12 hours)
- manifest.db corruption recovery
- Ransomware recovery
