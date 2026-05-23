# Flow Hardening Plan — Session 2026-05-22

## Full Flow Review — 12 Findings

### 🔴 Bugs / Robustness

| ID | Location | Finding | Severity |
|----|----------|---------|----------|
| **B1** | Line 225 | `_on_backup_completion`: `load_config()` outside try/except — crashes silently if config missing | Medium |
| **B2** | Lines 1077-1078 | `dir()` guards for `recon_result`/`anomaly_result` — fragile, should initialize to `None` at top | Medium |
| **B3** | Lines 915-927 | Duplicated anomaly detection block (×2) — maintenance risk | Medium |
| **B4** | Line 963 | Yearly archive date parsing `int(trigger_md[:2])` — no validation of `MM-DD` format | Low |

### 🟡 Code Quality

| ID | Location | Finding | Severity |
|----|----------|---------|----------|
| **Q1** | Line 67 | `import keyring` inline in `_send_email_notification` — should be at module level | Low |
| **Q2** | Line 86 | `import shutil` inline (duplicate of module-level `import shutil`) — dead import | Low |
| **Q3** | Line 624 | `from core.verify import compare_dry_run_deletions` inline in flow body — should be top-level | Low |
| **Q4** | Lines 1018-1025, 1035-1041 | Duplicated SMTP config dict construction for weekly/monthly reports | Low |
| **Q5** | Lines 562, 583 | `preflight_result.get("report")` called twice — redundant | Low |

### 🟢 Cosmetic / Hardening

| ID | Location | Finding | Severity |
|----|----------|---------|----------|
| **C1** | Line 202 | `_on_backup_failure`: `state.message` renders `"None"` in f-string when None | Cosmetic |
| **C2** | Lines 151-158 | `_send_email_notification`: fallback `EmailServerCredentials` hardcodes `"STARTTLS"` | Low |
| **C3** | Line 1006 | LAN integrity audit runs after reconciliation — should run before | Low |

---

## Detailed Fixes

### B1 — `_on_backup_completion`: load_config outside try/except
**Location:** line 225  
**Fix:** Wrap `load_config(config_path)` and the full email logic in a single try/except.

### B2 — Fragile `dir()` guards
**Location:** lines 1077–1078  
**Fix:** Add `recon_result = None` and `anomaly_result = None` at the top of `nightly_backup()` (near `vss_device_path` initialization). Then replace:
```python
recon_result=recon_result if "recon_result" in dir() else None,
anomaly_result=anomaly_result if "anomaly_result" in dir() else None,
```
with:
```python
recon_result=recon_result,
anomaly_result=anomaly_result,
```

### B3 — Duplicated anomaly detection
**Location:** lines 705–717 and 915–927  
**Fix:** Extract `_run_anomaly_check(config, config_path)` helper. Call from both branches.

### B4 — Yearly archive date parsing
**Location:** line 963  
**Fix:** Add a try/except around the date parse with a warning log on failure, preventing a crash from malformed `trigger_md`.

### Q1/Q2 — Inline imports
**Location:** lines 67, 86  
**Fix:** Remove `import keyring` and `import shutil` from inline — `keyring` is already attempted via try/except (stay inline?), `shutil` is a dead duplicate (already imported at module level on line 2).

### Q3 — Inline `compare_dry_run_deletions`
**Location:** line 624  
**Fix:** Move to module-level import.

### Q4 — Duplicated SMTP config dict
**Location:** lines 1018–1025 and 1035–1041  
**Fix:** Extract `_build_smtp_config(config)` helper.

### Q5 — Redundant `preflight_result.get("report")`
**Location:** lines 562, 583  
**Fix:** Store in a local variable after first call.

### C1 — `state.message` renders "None"
**Location:** line 202  
**Fix:** Use `state.message or "No details available"`.

### C2 — Hardcoded STARTTLS fallback
**Location:** lines 151–158  
**Fix:** Accept `smtp_type` from notification config if available, default to `"STARTTLS"`.

### C3 — LAN integrity audit ordering
**Location:** line 1006  
**Fix:** Move LAN integrity audit block to just before the reconciliation block (line 815). Audit captures bit-rot evidence before reconciliation may overwrite files.

---

## Execution Order

1. Q1/Q2: Fix inline imports at module level
2. Q3: Move `compare_dry_run_deletions` import to module level
3. B2: Initialize `recon_result`/`anomaly_result` to `None` at function top, remove `dir()` guards
4. B3: Extract `_run_anomaly_check()` helper, replace both call sites
5. C3: Move LAN integrity audit before reconciliation
6. B4: Add date parse validation in yearly archive block
7. Q4: Extract `_build_smtp_config()` helper
8. Q5: Store preflight report in local variable
9. B1, C1, C2: Hook-level fixes
10. Full test suite (254 tests)
