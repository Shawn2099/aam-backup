# BACKUP AUTOMATION SYSTEM — Agent Context

## What This Is

Automated daily backup of a Windows Server 2016 D:\ drive (~370GB, 200K+ files) to two destinations simultaneously:
- **LAN** (192.168.10.10) via Robocopy `/MIR` — true mirror
- **GCS** (asia-south1) via Rclone `sync` — true mirror

Both destinations mirror source exactly. Deletions propagate. GCS retains 1 older version for 90 days. LAN has no versioning.

## Critical Rules (Never Violate)

1. **No hardcoded values** — everything from `config.yaml` or Windows Credential Manager
2. **No `shell=True`** — subprocess calls use argument lists only
3. **`pathlib.Path` throughout** — never `os.path`
4. **ManifestDB `threading.Lock`** — all writes acquire lock, no exceptions
5. **Temp files in `finally` blocks** — always cleaned up
6. **Config re-read every flow run** — not cached between runs
7. **UTC ISO8601 timestamps** in SQLite

## Architecture Facts (Not Obvious from Filenames)

- **Prefect 3.x self-hosted** is the orchestrator — our code is a set of Prefect tasks in a flow
- **Single shared `ManifestDB` instance** passed to all tasks — threading.Lock must be shared across threads
- **LAN + cloud run concurrently** via `ThreadPoolTaskRunner(max_workers=2)`
- **SQLite WAL mode** set on every connection (not just creation) via SQLAlchemy event listener
- **xxHash64** for checksums (not SHA256) — speed for 200K+ files
- **Deleted files removed from manifest** — mirror tools handle deletion, manifest reflects reality
- **`checksum="pending"`** for new files until first backup confirmation

## Permanently Out of Scope

Soft delete, custom versioning, anomaly detection, canary files, integrity verification, automatic server shutdown, SMART monitoring, restore interface, PyInstaller packaging.

## Development Phases

| Phase | Items | Status |
|-------|-------|--------|
| 1 — Foundation | Scaffolding, models, logging | ✅ Done |
| 2 — Core | Config loader, ManifestDB, scanner, WoL, Robocopy wrapper, Rclone wrapper | ✅ Done |
| 3 — Orchestration | Prefect tasks, flow definition, email automation | ✅ Done |
| 4 — UI | FastAPI status page (Alpine.js + Tailwind) | ✅ Done |
| 5 — Scripts | setup_credentials, validate_config, seed_cloud, test_connections, deploy scripts | ✅ Done |
| 6 — Tests | Unit + integration tests (115 tests, incremental) | ✅ Done |
| 7 — Pre-Flight | Disk space, GCS quota, connectivity checks | ✅ Done |

## P0 Fixes (Completed)

| # | Fix | File | Status |
|---|-----|------|--------|
| 1 | Manifest drift — parse Robocopy per-file failures | `core/robocopy.py` | ✅ Done |
| 2 | `file_size` column overflow (Integer → BigInteger) | `models/manifest_model.py` | ✅ Done |
| 3 | Email notifications wired into `on_failure` hook | `flow.py` | ✅ Done |
| 4 | Rclone exit code 5 → CLOUD_PARTIAL (allow Prefect retries) | `core/rclone.py` | ✅ Done |
| 5 | Robocopy `/XJ` flag — exclude junction points | `core/robocopy.py` | ✅ Done |
| 6 | Full test suite verification (115 passing) | `tests/` | ✅ Done |

## Production Readiness Gaps (Pre-Deployment)

| # | Gap | Priority | Status |
|---|-----|----------|--------|
| 1 | manifest.db backup after each successful run | Critical | ✅ Done — `tasks/manifest_backup_task.py` + integrated in flow |
| 2 | Post-backup integrity verification (`rclone check`) | Critical | ✅ Done — `run_rclone_check()` + `tasks/verification_task.py` |
| 3 | Batch manifest lookups in scanner (200K+ files) | Critical | ✅ Done — `get_all_entries()` bulk load + in-memory dict |
| 4 | `deploy/setup_email_notifications.py` → real Prefect automations | Critical | ✅ Done — creates EmailServerCredentials block + automations |
| 5 | `install_services.bat` / `uninstall_services.bat` for deployment | Critical | ✅ Done — created in `deploy/` |
| 6 | VSS for locked Tally/Winman files (if apps run overnight) | Important | ✅ Done — `core/vss.py` + `tasks/vss_task.py`, fallback to direct if fails |
| 7 | Alerting on extended "no changes" periods | Important | ✅ Done — `alerts.no_changes_warning_days` config + flow check |
| 8 | `.env.example` for deployment documentation | Nice-to-have | ✅ Done |
| 9 | UI `/health` endpoint for Servy monitoring | Nice-to-have | ✅ Done |
| 10 | Backup metrics collection (duration, throughput trends) | Nice-to-have | ✅ Done — `tasks/metrics_task.py`, JSONL per run |
| 11 | Config versioning / backup | Nice-to-have | ✅ Done — `tasks/config_version_task.py`, keeps last 30 |
| 12 | Graceful shutdown handling | Nice-to-have | Skipped — Prefect handles cleanup on normal cancellation |
| 13 | Log files included in cloud backup | Nice-to-have | ✅ Done — `tasks/log_backup_task.py`, syncs to `_logs/` prefix |

## Key File Boundaries

```
core/        — Business logic (config_loader, manifest_db, scanner, wol, robocopy, rclone, logging_setup)
models/      — Pydantic config models, SQLAlchemy manifest model, ScanResult/FileInfo dataclasses
tasks/       — Prefect task wrappers (config_task, scan_task, lan_task, cloud_task)
ui/          — FastAPI server + templates/status.html
scripts/     — Deployment & setup scripts (standalone, not part of flow)
deploy/      — Servy service install/uninstall, Prefect deployment creation
tests/       — Pytest suite
flow.py      — Prefect flow definition (entry point for worker)
```

## Important Context

- **Target: Windows Server 2016** — all paths use Windows format, binaries are `.exe`
- **Dev on Linux** — use `pathlib.Path` for cross-platform compatibility
- **Service account provided during deployment** — use `[SERVICE_ACCOUNT]` placeholder in scripts, not domain admin
- **Robocopy exit codes are bitmasks** — evaluate with bitwise AND, never direct comparison
- **Rclone uses `sync`** — destination matches source exactly, deletions propagate
- **Prefect 3.x API** differs from 2.x — work pools, `task.submit()`, `ThreadPoolTaskRunner`

## Detailed Specs

- **`plan.md`** — Complete technical specification (every flag, exit code, algorithm, config field, DB column)
- **`DECISIONS.md`** — Audit trail of all decisions made during planning

Read `plan.md` for implementation details. This file is for quick orientation and preventing common mistakes.
