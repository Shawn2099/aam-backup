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
| 6 — Tests | Unit + integration tests (88 tests, incremental) | ✅ Done |
| 7 — Pre-Flight | Disk space, GCS quota, connectivity checks | Next |

## Key File Boundaries

```
core/        — Business logic (config_loader, manifest_db, scanner, wol, robocopy, rclone, logging_setup)
models/      — Pydantic config models, SQLAlchemy manifest model, ScanResult/FileInfo dataclasses
tasks/       — Prefect task wrappers (config_task, scan_task, lan_task, cloud_task)
ui/          — FastAPI server + templates/status.html
scripts/     — Deployment & setup scripts (standalone, not part of flow)
deploy/      — NSSM service install/uninstall, Prefect deployment creation
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
