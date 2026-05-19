# DEPLOYMENT GUIDE — Windows Server 2016

Complete step-by-step guide for deploying the backup system on a fresh Windows Server 2016.

## Prerequisites

| Item | Version | Download |
|------|---------|----------|
| Python | 3.12+ | https://www.python.org/downloads/windows/ |
| Rclone | Latest | https://rclone.org/downloads/ |
| Servy | Latest | https://github.com/aliostad/Servy/releases |
| GCS Bucket | — | Create via Google Cloud Console |

## Phase 1: Install Prerequisites

### 1.1 Install Python 3.12+

1. Download Python 3.12+ installer from python.org
2. Run installer **as Administrator**
3. Select **"Install for all users"** (installs to `C:\Python312\`)
4. Check **"Add Python to PATH"**
5. Verify:
   ```cmd
   python --version
   pip --version
   ```

### 1.2 Install uv (dependency manager)

```cmd
pip install uv
uv --version
```

### 1.3 Install Rclone

1. Download Windows AMD64 ZIP from https://rclone.org/downloads/
2. Extract `rclone.exe` to `C:\Windows\System32\` (or any PATH directory)
3. Verify:
   ```cmd
   rclone version
   ```

### 1.4 Install Servy (Windows service wrapper)

1. Download latest release from https://github.com/aliostad/Servy/releases
2. Extract `servy.exe` to `C:\Windows\System32\` (or any PATH directory)
3. Verify:
   ```cmd
   servy --version
   ```

### 1.5 Create GCS Bucket

1. Go to Google Cloud Console → Cloud Storage → Create Bucket
2. Settings:
   - **Name**: Choose a unique name (lowercase letters, numbers, hyphens)
   - **Region**: `asia-south1` (Mumbai)
   - **Storage class**: Standard
   - **Access control**: Uniform
   - **Public access**: Prevent public access (checked)
3. Enable versioning:
   ```cmd
   gsutil versioning set on gs://YOUR_BUCKET_NAME
   ```
4. Set lifecycle rule (retain 1 older version for 90 days):
   ```cmd
   gsutil lifecycle set lifecycle.json gs://YOUR_BUCKET_NAME
   ```
   Where `lifecycle.json`:
   ```json
   {
     "rule": [
       {
         "action": {"type": "Delete"},
         "condition": {
           "isLive": false,
           "numNewerVersions": 1,
           "age": 90
         }
       }
     ]
   }
   ```

### 1.6 Create GCS Service Account

1. Go to IAM & Admin → Service Accounts → Create Service Account
2. Name: `backup-agent`
3. Grant role: **Storage Object Admin** (for the bucket)
4. Create and download JSON key file
5. Save to `C:\BackupAgent\gcs_service_account.json`

## Phase 2: Deploy Application Files

### 2.1 Create Directory Structure

```cmd
mkdir C:\BackupAgent
mkdir C:\BackupAgent\logs
mkdir C:\BackupAgent\rclone_temp
```

### 2.2 Copy Project Files

Copy all project files to `C:\BackupAgent\`:
```
C:\BackupAgent\
├── core\
├── models\
├── tasks\
├── ui\
├── scripts\
├── deploy\
├── tests\
├── flow.py
├── config.yaml
├── pyproject.toml
└── ...
```

### 2.3 Install Dependencies

```cmd
cd C:\BackupAgent
uv sync --extra preflight
```

This installs all dependencies including optional `psutil` and `ntplib` for enhanced pre-flight checks.

### 2.4 Configure config.yaml

Edit `C:\BackupAgent\config.yaml` and fill in:

```yaml
paths:
  source_drive: "D:\\"
  lan_destination: "\\\\192.168.10.10\\hp srv manual backup$"

wol:
  enabled: true
  mac_address: "XX:XX:XX:XX:XX:XX"    # LAN server MAC

cloud_backup:
  enabled: true
  bucket: "your-bucket-name"           # GCS bucket name

notifications:
  smtp_host: "smtp.gmail.com"          # Your SMTP server
  smtp_port: 587
  smtp_username: "alerts@yourdomain.com"
  sender: "backup-alerts@yourdomain.com"
  recipients: ["admin@yourdomain.com"]
  send_on_every_run: true
  weekly_summary_enabled: true
  weekly_summary_day: "monday"
  weekly_summary_time: "08:00"

alerts:
  no_changes_warning_days: 7
  lan_free_space_warning_gb: 50
  backup_duration_warning_minutes: 180

test_restore:
  enabled: true
  sample_count: 10
  run_every_n_backups: 7
```

### 2.5 Store Credentials in Windows Credential Manager

```cmd
# GCS service account key path
cmdkey /generic:BackupAgent /user:BackupAgent_GCS /pass:C:\BackupAgent\gcs_service_account.json

# SMTP password
cmdkey /generic:BackupAgent /user:BackupAgent_SMTP /pass:YOUR_SMTP_PASSWORD
```

Or use the setup script:
```cmd
uv run scripts/setup_credentials.py setup
```

### 2.6 Validate Configuration

```cmd
uv run scripts/validate_config.py validate
```

### 2.7 Test Connections

```cmd
uv run scripts/test_connections.py test
```

This tests:
- LAN server connectivity (ping)
- GCS bucket access (rclone ls)
- SMTP server connectivity

## Phase 3: Install Windows Services

### 3.1 Run Installation Script

Open **Command Prompt as Administrator**:

```cmd
cd C:\BackupAgent
deploy\install_services.bat
```

This installs three services:
- **PrefectServer** — Prefect API server (port 4200)
- **PrefectWorker** — Executes backup flows
- **BackupUI** — Status page (port 8080)

### 3.2 Create Prefect Deployment

```cmd
cd C:\BackupAgent
uv run deploy/create_deployment.py create
```

This creates a deployment named `nightly-backup-production` with the cron schedule from `config.yaml`.

### 3.3 Setup Email Notifications

```cmd
uv run deploy/setup_email_notifications.py
```

This creates the Prefect email notification block and automations for failure alerts.

## Phase 4: Post-Deployment Verification

### 4.1 Verify Services

```cmd
sc query PrefectServer
sc query PrefectWorker
sc query BackupUI
```

All should show `STATE: 4 RUNNING`.

### 4.2 Verify Prefect UI

Open browser: `http://localhost:4200`
- Should show Prefect UI
- Navigate to **Deployments** → `nightly-backup-production` should be listed

### 4.3 Verify Status UI

Open browser: `http://localhost:8080`
- Should show backup status page
- Click **"Trigger Backup"** to run a test backup

### 4.4 Verify Health Endpoint

```cmd
curl http://localhost:8080/health
```

Expected response:
```json
{"status": "healthy", "prefect_api": "connected", "service": "backup-ui"}
```

### 4.5 Verify Metrics Endpoint

```cmd
curl http://localhost:8080/metrics
```

Should return latest backup metrics including capacity info.

### 4.6 Run a Test Backup

From Prefect UI or:
```cmd
prefect deployment run nightly-backup-production
```

Monitor in Prefect UI: `http://localhost:4200`

### 4.7 Verify Backup Results

After the backup completes, check:

1. **LAN destination**: `\\192.168.10.10\hp srv manual backup$` — files should be present
2. **GCS bucket**: `gsutil ls gs://YOUR_BUCKET/D_Drive_Backup/` — files should be present
3. **manifest.db**: `C:\BackupAgent\manifest.db` — should exist and have entries
4. **Logs**: `C:\BackupAgent\logs\` — should contain log files and `backup_metrics.jsonl`
5. **Config backup**: Both LAN and GCS should have `config.yaml`

### 4.8 Verify Dry-Run Preview

Check the pre-flight logs for "Dry Run" section showing:
- LAN Preview: X files would change (new/modified/deleted)
- Cloud Preview: X files would change (transfers/deletes)

### 4.9 Verify Test Restore

After 7 successful backups (or set `run_every_n_backups: 1` for testing), check logs for:
```
Running test restore verification (every 7 runs, sample count: 10)
Test restore LAN: 10/10 OK (OK)
Test restore cloud: 10/10 OK (OK)
```

### 4.10 Verify Email Notifications

If SMTP is configured, you should receive:
- **Success email** after each backup (if `send_on_every_run: true`)
- **Failure email** if any backup fails
- **Weekly report** on configured day (default: Monday 08:00)

## Troubleshooting

### Service Won't Start

Check service logs:
```cmd
type C:\BackupAgent\logs\prefect_worker_stderr.log
type C:\BackupAgent\logs\prefect_server_stderr.log
type C:\BackupAgent\logs\ui_stderr.log
```

### Rclone Not Found

Ensure `rclone.exe` is in PATH:
```cmd
where rclone
```

### Python Version Mismatch

If services reference wrong Python path, edit with Servy:
```cmd
servy edit PrefectWorker
```
Update application path to correct Python location.

### GCS Access Denied

Verify service account has correct permissions:
```cmd
rclone ls gcs_backup:YOUR_BUCKET --config C:\BackupAgent\rclone.conf
```

### Backup Stuck in "Running"

Check Prefect UI for task logs. Common causes:
- LAN server offline (WoL not working)
- Network connectivity issues
- Insufficient disk space

## Uninstall

```cmd
deploy\uninstall_services.bat
```

This stops and removes all three Windows services.

## File Locations

| File | Path | Purpose |
|------|------|---------|
| config.yaml | `C:\BackupAgent\config.yaml` | All backup configuration |
| manifest.db | `C:\BackupAgent\manifest.db` | File tracking database |
| prefect.db | `C:\BackupAgent\prefect.db` | Prefect internal database |
| Logs | `C:\BackupAgent\logs\` | Daily backup logs |
| Metrics | `C:\BackupAgent\logs\backup_metrics.jsonl` | Run metrics |
| Config versions | `C:\BackupAgent\logs\config_versions\` | Timestamped config backups |
| Rclone temp | `C:\BackupAgent\rclone_temp\` | Temporary rclone configs |
| Service logs | `C:\BackupAgent\logs\*.log` | Servy service output (with rotation) |
