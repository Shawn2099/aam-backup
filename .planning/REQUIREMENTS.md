# REQUIREMENTS

## v1 Requirements

### Core — Change Detection & Backup

- [ ] **CORE-01:** Config loader reads YAML, validates with Pydantic, retrieves GCS key from Windows Credential Manager
- [ ] **CORE-02:** ManifestDB tracks per-file backup state in SQLite WAL with thread-safe writes
- [ ] **CORE-03:** Scanner walks D:\ with exclusion pruning, detects new/modified/deleted files via xxHash64
- [ ] **CORE-04:** WoL powers on backup server if offline, polls until ready with timeout
- [ ] **CORE-05:** Robocopy wrapper runs /MIR incremental backup, parses exit codes via bitmask
- [ ] **CORE-06:** Rclone wrapper runs sync to GCS, handles temp config/ACL/filter, retries on transient errors

### Orchestration

- [ ] **ORCH-01:** Prefect flow orchestrates tasks with ThreadPoolTaskRunner(max_workers=2) for concurrent LAN+cloud
- [ ] **ORCH-02:** Prefect email automation sends failure alerts via Blocks + Automations

### UI

- [ ] **UI-01:** FastAPI status page shows last run status, next run countdown, manual trigger button

### Deployment

- [ ] **DEPLOY-01:** NSSM Windows Services for PrefectServer, PrefectWorker, BackupUI
- [ ] **DEPLOY-02:** Deployment scripts install services, create Prefect deployment, test connections
- [ ] **DEPLOY-03:** seed_cloud.py for one-time initial GCS upload (resumable, rate-limited)

### Testing

- [ ] **TEST-01:** Unit tests for config, scanner, robocopy, rclone, wol, manifestdb
- [ ] **TEST-02:** Integration tests for flow definition and UI endpoints

### Pre-Flight

- [ ] **PREFLIGHT-01:** Pre-flight checks for disk space, GCS quota, connectivity, service account validation

## v2 Requirements

(None — deferred)

## Out of Scope

- Soft delete / 30-day retention — client accepted mirror behavior
- Custom file versioning — GCS native versioning sufficient
- Anomaly detection / ransomware detection / canary files — permanently out of scope
- Integrity verification / weekly re-hash — permanently out of scope
- Automatic backup server shutdown — DNS server role prevents this
- SMART disk health monitoring — permanently out of scope
- Restore interface — permanently out of scope
- PyInstaller packaging — decided after system is working

## Traceability

| Requirement | Phase | Plan | Status |
|-------------|-------|------|--------|
| CORE-01 | Phase 1 + 2 | — | Not started |
| CORE-02 | Phase 1 + 2 | — | Not started |
| CORE-03 | Phase 2 | — | Not started |
| CORE-04 | Phase 2 | — | Not started |
| CORE-05 | Phase 2 | — | Not started |
| CORE-06 | Phase 2 | — | Not started |
| ORCH-01 | Phase 3 | — | Not started |
| ORCH-02 | Phase 3 | — | Not started |
| UI-01 | Phase 4 | — | Not started |
| DEPLOY-01 | Phase 5 | — | Not started |
| DEPLOY-02 | Phase 5 | — | Not started |
| DEPLOY-03 | Phase 5 | — | Not started |
| TEST-01 | Phase 6 | — | Not started |
| TEST-02 | Phase 6 | — | Not started |
| PREFLIGHT-01 | Phase 7 | — | Not started |
