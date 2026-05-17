# DECISION LOG — Backup Automation System

This file tracks every decision, change, and clarification made during planning and development. New sessions should read this to understand context.

## Decisions Made During Planning

### 2026-05-18 — Mirror Mode for Both Destinations
- **Decision:** Both LAN and cloud destinations are true mirrors of the source
- **Before:** LAN used Robocopy `/XO` (incremental, no deletion mirroring), cloud used `rclone sync` (mirror)
- **After:** LAN uses Robocopy `/MIR` (true mirror, deletions propagate), cloud uses `rclone sync` (true mirror, deletions propagate)
- **Reason:** Client accepted mirror behavior for both destinations
- **Impact:** Deleted files on source are deleted on both destinations immediately

### 2026-05-18 — No Custom Soft Delete or Versioning
- **Decision:** Removed soft delete, custom file versioning, anomaly detection, and integrity verification from scope permanently
- **Before:** These were planned as Phase 2 features with stubs/hooks in Phase 1
- **After:** Not built at all. No stubs, no hooks, no Phase 2 provisions for these features
- **Reason:** Client is comfortable with mirror behavior + cloud native versioning
- **Impact:** Simplified codebase, no Phase 2 migration scripts needed, schema is final

### 2026-05-18 — GCS Native Versioning Configuration
- **Decision:** GCS bucket configured with object versioning retaining 1 older version, lifecycle rule deletes older versions after 90 days
- **Details:** Set during deployment, not in code. Latest data always present on cloud. Previous version retained for 90 days as safety net against accidental deletion.
- **Impact:** Cloud has 90-day recovery window for accidental deletions. LAN has no versioning — deletions are immediate.

### 2026-05-18 — Deleted Files Removed from Manifest
- **Decision:** When files are deleted from source, they are removed from manifest.db (not just logged)
- **Before:** Deleted files were logged but kept in manifest
- **After:** `db.delete_entry(relative_path)` called for each deleted file during scan
- **Reason:** Mirror tools handle deletion, manifest should reflect reality
- **Impact:** Manifest accurately tracks only files that exist on source

### 2026-05-18 — Service Account for Deployment
- **Decision:** Service account provided during deployment (not domain admin)
- **Before:** PrefectWorker ran as `caaam\Administrator` (domain admin)
- **After:** PrefectWorker runs as least-privilege service account provided by client
- **Reason:** Security best practice
- **Impact:** Deployment scripts use `[SERVICE_ACCOUNT]` placeholder, ACL commands reference service account

### 2026-05-18 — Pre-Flight Checks Deferred
- **Decision:** Pre-flight checks (disk space, GCS quota, connectivity, etc.) added after core backup logic is complete
- **Reason:** Build core first, add safety checks later
- **Impact:** Core development can proceed without pre-flight module. Pre-flight checks will be added in Phase 7.

### 2026-05-18 — Removed Phase 2 Provision Stubs
- **Decision:** Removed all Phase 2 provision stubs from the codebase plan
- **Removed:**
  - `plant_canary_files.py` script
  - UI Phase 2 provision divs (`history-panel`, `restore-panel`, `logs-panel`)
  - Config sections: `soft_delete`, `lan_versioning`, `anomaly_detection`, `integrity_verification`
  - Database Phase 2 columns and tables
  - `ui.password_hash` config key
- **Reason:** No Phase 2 planned for these features
- **Impact:** Cleaner codebase, no dead code or unused stubs

## Pending Decisions (To Be Resolved During Deployment)

### GCS Bucket Lifecycle Configuration
- **Status:** Confirmed — 90-day retention for older versions
- **Action:** Set during deployment via GCS console or `gsutil`
- **Details:** Object versioning ON, retain 1 older version, lifecycle rule deletes older versions after 90 days

### Service Account Permissions
- **Status:** To be provided during deployment
- **Required permissions:**
  - Read access to D:\ (source drive)
  - Read/write access to `\\192.168.10.10\hp srv manual backup$` (LAN share)
  - Read/write access to `C:\BackupAgent\` (agent directory)
  - Read access to `C:\BackupAgent\gcs_service_account.json` (GCS key)
  - Access to Windows Credential Manager for `BackupAgent_GCS` credential

### Pre-Flight Check Thresholds
- **Status:** To be defined when implementing Phase 7
- **Planned checks:**
  - LAN backup server disk space (must have enough for full D:\ mirror ~370GB)
  - GCS bucket quota and accessibility
  - Network connectivity to backup server and GCS
  - Service account credential validation
  - Source drive accessibility and read permissions
  - Prefect server health check

## Architecture Decisions (From plan.md)

### Robocopy Flags
- `/MIR` — Mirror mode (copies new/changed, deletes from destination what's deleted from source)
- `/Z` — Restartable mode (handles network interruptions)
- `/R:[n]` — Retry count from config
- `/W:[n]` — Wait time between retries from config
- `/NP` — No progress percentage
- `/BYTES` — Show file sizes in bytes
- `/TEE` — Output to console and log file
- `/UNILOG+` — Append to Unicode log file
- `/XD` — Exclude directories
- `/XF` — Exclude files by pattern

### Rclone Flags
- `sync` — Makes destination match source
- `--config` — Temp config file with ACL
- `--filter-from` — Temp filter file
- `--bwlimit` — Bandwidth limit from config
- `--gcs-chunk-size` — Chunk size for multipart uploads
- `--transfers 4` — Parallel file transfers
- `--checkers 8` — Parallel file comparison threads
- `--retries` — Internal retries
- `--retries-sleep 30s` — Wait between retries
- `--stats 300s` — Transfer stats interval
- `--log-level INFO` — Verbosity
- `--use-json-log` — Structured JSON log output
- `--no-traverse` — Don't list remote before transfer

### Checksum Strategy
- Algorithm: xxHash64 (not MD5, not SHA256)
- Reason: Speed for 200K+ files, collision risk negligible for change detection
- Computed: Only when size or mtime differs from manifest
- New files: Checksum computed after backup confirmation (not during scan)
- Chunk size: 8MB reads to avoid loading large files into memory

### Concurrency Model
- `ThreadPoolTaskRunner(max_workers=2)` for concurrent LAN + cloud backup
- Both tasks submitted via `task.submit()`, flow waits via `future.result()`
- ManifestDB single shared instance passed to all tasks
- `threading.Lock` on all writes, SQLite WAL mode for concurrent reads

### Database WAL Mode
- Set on every connection (not just creation)
- PRAGMA journal_mode=WAL verified on every connection
- PRAGMA foreign_keys=ON
- PRAGMA synchronous=NORMAL
- PRAGMA cache_size=10000

## Notes for New Sessions

1. **Read `AGENTS.md` first** — it contains the full project context, architecture, config schema, database schema, and development plan.
2. **Read `plan.md` for detailed specifications** — it contains the complete technical specification with every flag, exit code, and algorithm defined.
3. **This file (`DECISIONS.md`)** tracks all changes and decisions made during planning. Use it to understand why certain decisions were made.
4. **The project is on Windows Server 2016** — all paths use Windows format, all binaries are Windows executables.
5. **Development is happening on Linux** — code is written for Windows but developed/tested on Linux. Use `pathlib.Path` for cross-platform compatibility.
6. **No hardcoded values** — this is the most important rule. Everything comes from config or Credential Manager.
7. **Service account is provided during deployment** — don't assume domain admin. Use placeholders in scripts.
