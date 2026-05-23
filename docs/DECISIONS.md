# ARCHITECTURAL DECISIONS — Backup Automation System

## Decision Log

> Format: Decision ID | Topic | Status | Summary

---

### D-001: Deletion Handling
**Status:** CONFIRMED  
**Topic:** How manifest handles files deleted from source  
**Decision:** Current approach is correct — scanner deletes from manifest immediately when file gone from D:\. Robocopy/Rclone enforce source = destination. Manifest is a reporting layer for source state, not destination tracking.  
**Gap:** Need reporting/alerting when destinations diverge from source.

---

### D-002: Full Re-Scan Frequency
**Status:** IMPLEMENTED  
**Topic:** How often to checksum ALL files regardless of size+mtime  
**Decision:** Every 30 runs (monthly). xxHash64 on all 200K+ files. Catches content-change-with-same-size edge cases. Inherently cleans stale manifest entries via set difference.  
**Config:** `backup_scope.full_rescan_every_n_runs: 30`  
**Implementation:**  
- `ManifestDB.get_and_increment_run_counter()` — thread-safe persistent counter in SQLite  
- `scan_task()` checks run number % interval → passes `is_full_rescan` flag  
- `scan_drive()` with `is_full_rescan=True` computes checksums for ALL files (not just size/mtime changed)  
- Files with `PENDING_CHECKSUM` from first scan get their first real checksum during full rescan  
- Files with pending checksum that were actually modified (size/mtime differ) are correctly classified as modified  
**Files changed:** `core/scanner.py`, `core/manifest_db.py`, `tasks/scan_task.py`, `models/config_model.py`, `tests/test_scanner.py`

---

### D-003: Nth Run Destination Reconciliation
**Status:** IMPLEMENTED  
**Topic:** Periodic full audit of both destinations against source  
**Decision:** Every Nth run (default 7 = weekly), after normal backup completes, audit both destinations against source manifest. If ANY drift found, run full `robocopy /MIR` and `rclone sync` to auto-correct. Log drift % in run summary (visible on failure/review, not a separate user alert).  
**Implementation:**  
- `tasks/reconciliation_task.py` — orchestrates: walk LAN → compare manifest → `rclone check` GCS → auto-correct if drift  
- Reuses existing modules: `core/robocopy.run_robocopy`, `core/rclone.run_rclone`, `core/rclone.run_rclone_check`, `core/verify.verify_lan_checksums`  
- Configurable via `reconciliation.run_every_n_backups`, `reconciliation.enabled`, `reconciliation.auto_correct`  
- Integrated into `flow.py` after manifest backup, before cloud integrity check  
**Files changed:** `tasks/reconciliation_task.py` (new), `models/config_model.py` (ReconciliationConfig), `flow.py`, `config.yaml`

---

### D-009: Destination Independence
**Status:** CONFIRMED  
**Topic:** No files missed if one destination/tool is disabled  
**Decision:** Scanner is the single source of truth — classifies ALL files regardless of destination status. Each backup task checks its own `enabled` flag independently. If LAN disabled, Cloud still gets everything. If Cloud disabled, LAN still gets everything. Dry run comparison skips disabled destinations.  
**Rationale:** Latest data must always be preserved to at least one destination.

---

### D-004: GCS Quota Check
**Status:** SKIPPED  
**Topic:** Check GCS bucket space/quota in pre-flight  
**Decision:** Not needed. Only `rclone about` for accessibility confirmation. No space checks — GCS is effectively unlimited.

---

### D-005: Source Free Space Check
**Status:** IMPLEMENTED  
**Topic:** Keep 5GB source drive free space check as system health indicator  
**Decision:** 5GB threshold, configurable via `alerts.source_free_space_warning_gb` in `config.yaml`. Warning only — never blocks backup run. If D:\ is truly full, robocopy/rclone fail naturally and trigger failure notification.  
**Alerting:** Log warning + UI dashboard indicator + included in failure email if backup fails and low space was a contributing factor.  
**Implementation:** `core/preflight.py` uses `config.alerts.source_free_space_warning_gb` for `check_disk_space()`. Added to `AlertsConfig` model.  
**Files changed:** `models/config_model.py` (source_free_space_warning_gb field), `core/preflight.py` (configurable threshold)

---

### D-006: Dry Run Comparison
**Status:** IMPLEMENTED  
**Topic:** Compare robocopy /L vs rclone --dry-run deletion counts before actual backup  
**Decision:** Run every backup run. Dry run uses ALL the same flags/exclusions as the real run (`/XF`, `/XD`, `--exclude`, retries, timeouts, etc.).  
**Validation:**  
- Dry run exit code checked — failure means the real run would also fail (credential expiry, share inaccessible, permissions revoked)  
- If LAN dry run fails → skip LAN backup task (Cloud still runs)  
- If Cloud dry run fails → skip Cloud backup task (LAN still runs)  
- If both dry runs fail → fail entire flow immediately (triggers failure email, saves hours of wasted execution)  
**Deletion count comparison:** `compare_dry_run_deletions()` compares robocopy vs rclone vs scanner deletion counts. Threshold: 10% delta.  
- Delta ≤ 10% → silent audit log only  
- Delta > 10% → fail the flow early with clear error message  
**Implementation:**  
- `core/verify.py` — `run_dry_run_lan()` and `run_dry_run_cloud()` now accept exclusion params and use identical flags as real runs  
- `core/verify.py` — `compare_dry_run_deletions()` for deletion count comparison  
- `core/preflight.py` — `check_dry_run_lan()` and `check_dry_run_cloud()` now validate exit codes (FAIL on dry run failure)  
**Files changed:** `core/verify.py`, `core/preflight.py`, `config.yaml`

---

### D-007: Checksum Verification
**Status:** IMPLEMENTED  
**Topic:** Improve LAN verification beyond 5-file sample, GCS integrity  
**Decision:**  
- LAN: Verify ALL changed files (xxHash64 source vs LAN destination) after every robocopy run. Removed random sampling.  
- GCS: `rclone check` with `--differ`, `--missing-on-dst`, `--error` flags writing to temp files (one path per line). Zero stdout parsing. Reads server-side MD5 from GCS metadata — zero egress cost.  
- `_read_path_file()` helper reads rclone output files reliably.  
- Nth run reconciliation: Skip `rclone check --download` (unnecessary bandwidth cost). Server-side MD5 comparison is sufficient.  
**Files changed:** `core/verify.py`, `core/rclone.py`, `tasks/lan_task.py`, `tests/test_verify.py`  
**Facts confirmed:** Robocopy has NO hash verification. GCS stores MD5+CRC32C as object metadata retrievable via API without downloading. rclone `--differ`/`--missing-on-dst`/`--error` flags confirmed in rclone v1.74.1 docs.

---

### D-008: Manifest Backup Strategy
**Status:** IMPLEMENTED  
**Topic:** WAL checkpoint before copy, SHA256 hash for integrity, corruption recovery  
**Decision:**  
- **Where:** LAN destination preferred (`_manifest/` subfolder). GCS also synced but only as last-resort fallback (download costs).  
- **Retention:** Last 7 daily backups (1 week of history).  
- **Integrity:** SHA256 hash stored in separate `.sha256` file alongside each backup copy.  
- **When:** After each successful run — WAL checkpoint first, then copy.  
- **Recovery order:**  
  1. Try LAN `_manifest/` latest backup (verify SHA256)  
  2. If LAN unavailable, try GCS `_manifest/` latest backup (verify SHA256)  
  3. If both fail, rebuild manifest fresh via full scan — no failure, just a warning  
**Implementation:**  
- `tasks/manifest_backup_task.py` — enhanced with `_wal_checkpoint()`, `_compute_sha256()`, `_prune_old_backups()`, cloud pruning  
- Configurable via `manifest_backup.enabled`, `lan_path`, `cloud_path`, `retention_count`  
- `flow.py` passes new config params to `backup_manifest_db_task()`  
**Files changed:** `tasks/manifest_backup_task.py`, `models/config_model.py` (ManifestBackupConfig), `flow.py`, `config.yaml`

---

## Pending Discussions

| Topic | Key Question |
|-------|-------------|
| None | All decisions finalized. Ready for implementation phase. |
