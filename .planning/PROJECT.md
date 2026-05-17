# BACKUP AUTOMATION SYSTEM

## What This Is

Automated daily backup of a Windows Server 2016 D:\ drive (~370GB, 200K+ files) to two destinations simultaneously:
- **LAN** (192.168.10.10) via Robocopy `/MIR` — true mirror
- **GCS** (asia-south1, Mumbai) via Rclone `sync` — true mirror

Both destinations mirror source exactly. Deletions propagate. GCS retains 1 older version for 90 days. LAN has no versioning.

## Core Value

Reliable, automated daily backup that runs without human intervention — replacing the current manual copy process. If nothing else works, the 23:00 backup must complete successfully.

## Context

- **Server:** AAMBDC001 (192.168.10.5), Windows Server 2016, Primary Domain Controller for caaam.com
- **Source:** D:\ drive — 370GB, 200K+ files, 40K+ folders
- **LAN destination:** \\192.168.10.10\hp srv manual backup$ (hidden SMB share)
- **Cloud destination:** GCS bucket in asia-south1 (Mumbai) — data residency in India
- **Backup server is also DNS server** — no automatic shutdown allowed
- **Network:** 192.168.10.x subnet, 100Mbps internet
- **Timezone:** Asia/Kolkata (IST)

## Constraints

- Windows Server 2016 target — all paths use Windows format
- Development on Linux — use pathlib.Path for cross-platform compatibility
- Service account provided during deployment (not domain admin)
- No hardcoded values — everything from config.yaml or Windows Credential Manager
- Prefect 3.x self-hosted as orchestrator
- SQLite WAL mode for manifest database
- Both destinations are true mirrors — deletions propagate immediately

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Both destinations are true mirrors | Client accepted — no soft delete needed | Robocopy /MIR, Rclone sync |
| GCS native versioning only | 1 older version, 90-day retention — no custom code | Provider-side protection |
| xxHash64 for checksums | Speed for 200K+ files | Not SHA256 |
| Prefect email automation | Zero custom notification code | Blocks + Automations |
| Service account at deployment | Least-privilege, not domain admin | Placeholder in scripts |
| Pre-flight checks after core | Build core first, safety checks later | Phase 7 |

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] **CORE-01:** Config loader reads YAML, validates with Pydantic, retrieves GCS key from Windows Credential Manager
- [ ] **CORE-02:** ManifestDB tracks per-file backup state in SQLite WAL with thread-safe writes
- [ ] **CORE-03:** Scanner walks D:\ with exclusion pruning, detects new/modified/deleted files via xxHash64
- [ ] **CORE-04:** WoL powers on backup server if offline, polls until ready with timeout
- [ ] **CORE-05:** Robocopy wrapper runs /MIR incremental backup, parses exit codes via bitmask
- [ ] **CORE-06:** Rclone wrapper runs sync to GCS, handles temp config/ACL/filter, retries on transient errors
- [ ] **ORCH-01:** Prefect flow orchestrates tasks with ThreadPoolTaskRunner(max_workers=2) for concurrent LAN+cloud
- [ ] **ORCH-02:** Prefect email automation sends failure alerts via Blocks + Automations
- [ ] **UI-01:** FastAPI status page shows last run status, next run countdown, manual trigger button
- [ ] **DEPLOY-01:** NSSM Windows Services for PrefectServer, PrefectWorker, BackupUI
- [ ] **DEPLOY-02:** Deployment scripts install services, create Prefect deployment, test connections
- [ ] **DEPLOY-03:** seed_cloud.py for one-time initial GCS upload (resumable, rate-limited)
- [ ] **TEST-01:** Unit tests for config, scanner, robocopy, rclone, wol, manifestdb
- [ ] **TEST-02:** Integration tests for flow definition and UI endpoints
- [ ] **PREFLIGHT-01:** Pre-flight checks for disk space, GCS quota, connectivity, service account validation

### Out of Scope

- Soft delete / 30-day retention — client accepted mirror behavior
- Custom file versioning — GCS native versioning sufficient
- Anomaly detection / ransomware detection / canary files — permanently out of scope
- Integrity verification / weekly re-hash — permanently out of scope
- Automatic backup server shutdown — DNS server role prevents this
- SMART disk health monitoring — permanently out of scope
- Restore interface — permanently out of scope
- PyInstaller packaging — decided after system is working

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-18 after initialization*
