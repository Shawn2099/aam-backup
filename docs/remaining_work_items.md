# Remaining Work Items — Post-Hardening

## Completed
- Flow hardening pass (12 fixes: hooks, orchestration, deduplication)
- Notification enrichment (4 existing channels enriched)
- Code deduplication (rclone config, flow_run_id, get_task_logger)
- Config model validation hardening (13 new validators, cross-field checks)
- Scripts & deployment tooling audit (12 fixes across 9 files)
- Report email consolidation (raw smtplib → `core/email_utils.send_email()`)
- UI audit + hardening (exception handlers, rate limiting, SQLite WAL, config caching)
- Error recovery (scanner single-transaction sync, mark-backed-up only after verification)
- Monitoring blind spots (retry count, manifest DB size in metrics)
- 254 tests passing

---

## Remaining

### 1. Testing Gaps

Current state: 254 tests. Most are unit tests with mocking. Not covered:

- **Missing config.yaml** — testable on Linux
- **Manifest.db WAL corruption** — needs Windows + SQLite corruption tooling
- **Manifest.db busy/timeout** — needs Windows file locking behavior
- **End-to-end integration** — needs actual Robocopy/Rclone binaries on Windows
- **Rclone exit codes in production** — needs `rclone` binary

### 2. UI HTTPS — "Not Secure" Warning

Two viable internal-network solutions:

- **Option A (domain-joined)**: Active Directory Certificate Services — already trusted by all domain machines, zero browser warnings, zero cost.
- **Option B (standalone)**: mkcert — generates locally-trusted certs. Install CA on the server + copy to client machines that access the UI.

Add SSL support to uvicorn startup (`--ssl-keyfile` / `--ssl-certfile`) and write a setup script for certificate generation.

### Execution Order

1. Testing gaps — write the testable ones on Linux first (missing config, E2E smoke)
2. UI HTTPS — certificate setup, per-firm decision
