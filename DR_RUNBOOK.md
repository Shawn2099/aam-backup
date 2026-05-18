# DISASTER RECOVERY RUNBOOK

## RTO / RPO Targets

| Metric | Target | Notes |
|--------|--------|-------|
| RPO (Recovery Point Objective) | 24 hours | Daily backup at 23:00 |
| RTO (Recovery Time Objective) | 8-12 hours | Depends on data volume and network speed |

## Backup Destinations

| Destination | Type | Access Method | Retention |
|-------------|------|---------------|-----------|
| LAN (`\\192.168.10.10\hp srv manual backup$`) | True mirror (`robocopy /MIR`) | Direct file access | Exact copy of source |
| GCS (`asia-south1`) | True mirror (`rclone sync`) | `rclone copy gcs_backup:bucket/path D:\restore` | Current + 1 older version (90-day retention) |

## Scenario 1: Single File Restore

### From LAN (fastest)
```
1. Open File Explorer
2. Navigate to \\192.168.10.10\hp srv manual backup$
3. Browse to the file path (mirrors D:\ exactly)
4. Copy the file back to D:\
```

### From GCS (if LAN unavailable)
```powershell
# Restore a single file
rclone copy gcs_backup:<bucket>/D_Drive_Backup/path/to/file.txt D:\restore\

# Restore a folder
rclone copy gcs_backup:<bucket>/D_Drive_Backup/path/to/folder D:\restore\folder
```

### Using the Restore CLI
```powershell
# List recent backups
python scripts/restore.py list --source lan

# Restore a specific file
python scripts/restore.py restore --source lan --path "WINMAN\data.mdb" --destination D:\restore\

# Verify file integrity
python scripts/restore.py verify --source gcs --path "WINMAN\data.mdb"
```

## Scenario 2: Full Server Recovery

### Prerequisites
- Replacement Windows Server 2016 (or newer) installed
- Same drive letter (D:\) available
- Network connectivity to `192.168.10.10`
- GCS service account key file available
- Rclone installed and configured
- Robocopy available (built into Windows Server)

### Step-by-Step

#### Phase 1: Restore from LAN (preferred — faster)

```powershell
# 1. Verify LAN connectivity
ping 192.168.10.10

# 2. Verify backup destination is accessible
dir "\\192.168.10.10\hp srv manual backup$"

# 3. Full restore with Robocopy (preserves permissions, timestamps)
robocopy "\\192.168.10.10\hp srv manual backup$" "D:\" /MIR /Z /R:3 /W:10 /NP /BYTES /TEE /LOG:C:\restore.log

# 4. Review restore log for errors
type C:\restore.log | findstr /C:"ERROR" /C:"FAILED"

# 5. Verify critical applications
#    - Tally: Open and verify company data
#    - Winman: Verify database connectivity
```

#### Phase 2: Restore from GCS (if LAN unavailable)

```powershell
# 1. Verify GCS access
rclone ls gcs_backup:<bucket>/D_Drive_Backup/ --config C:\BackupAgent\rclone.conf

# 2. Full restore (may take 8-12 hours for ~370GB)
rclone copy gcs_backup:<bucket>/D_Drive_Backup "D:\" ^
  --config C:\BackupAgent\rclone.conf ^
  --transfers 8 ^
  --checkers 16 ^
  --retries 3 ^
  --log-file C:\gcs_restore.log

# 3. Monitor progress (in another terminal)
rclone size gcs_backup:<bucket>/D_Drive_Backup/ --config C:\BackupAgent\rclone.conf

# 4. Verify integrity after restore
rclone check "D:\" gcs_backup:<bucket>/D_Drive_Backup/ ^
  --config C:\BackupAgent\rclone.conf ^
  --one-way ^
  --log-file C:\gcs_verify.log
```

#### Phase 3: Post-Restore Verification

```powershell
# 1. Check file counts match
# Source (before failure): check manifest.db or Prefect UI logs
# Restored: count files on D:\
(Get-ChildItem -Path "D:\" -Recurse -File).Count

# 2. Verify critical folders exist
Test-Path "D:\WINMAN"
Test-Path "D:\Tally"
Test-Path "D:\Common Folder"

# 3. Restore BackupAgent configuration
# Copy config.yaml, manifest.db, and rclone.conf from backup
# Or re-run deploy/setup scripts

# 4. Re-register services
# Re-run deploy/install_services.bat

# 5. Verify Prefect worker is running
prefect worker list

# 6. Trigger a test backup to verify everything works
prefect deployment run nightly-backup-production
```

## Scenario 3: manifest.db Corruption

```powershell
# 1. Stop the Prefect worker
net stop PrefectWorker

# 2. Restore manifest.db from LAN backup
copy "\\192.168.10.10\hp srv manual backup$\manifest.db" "C:\BackupAgent\manifest.db"

# 3. If LAN backup is stale, restore from GCS
rclone copyto gcs_backup:<bucket>/D_Drive_Backup/manifest.db "C:\BackupAgent\manifest.db" ^
  --config C:\BackupAgent\rclone.conf

# 4. Restart the worker
net start PrefectWorker

# 5. Next backup run will reconcile any differences via scanner
```

## Scenario 4: Ransomware / Malware Recovery

```powershell
# 1. ISOLATE the server from network immediately
#    - Disconnect network cable or disable adapter
#    - Do NOT shut down (preserves evidence)

# 2. Assess damage
#    - Identify which files are encrypted
#    - Check if backup destinations are affected
#    - LAN: dir \\192.168.10.10\hp srv manual backup$ /s
#    - GCS: rclone ls gcs_backup:<bucket>/D_Drive_Backup/

# 3. If backups are clean, proceed with full restore (Scenario 2)

# 4. If LAN backup is also affected, use GCS versioning:
#    # List available versions
#    rclone lsd gcs_backup:<bucket>/D_Drive_Backup/ --config C:\BackupAgent\rclone.conf

#    # Restore from older version
#    rclone copy gcs_backup:<bucket>/D_Drive_Backup/ "D:\" ^
#      --config C:\BackupAgent\rclone.conf ^
#      --max-age 90d

# 5. After restore:
#    - Run full antivirus scan
#    - Change all service account passwords
#    - Rotate GCS service account keys
#    - Review Windows Event Logs for intrusion indicators
```

## Contact & Escalation

| Role | Contact | When to Escalate |
|------|---------|-----------------|
| IT Admin | [Internal contact] | Any backup failure |
| Network Admin | [Internal contact] | LAN connectivity issues |
| Cloud Admin | [Internal contact] | GCS access issues |

## Prefect UI

- URL: `http://<server>:4200`
- Status page: `http://<server>:8080`
- Check flow runs for last successful backup timestamp

## Key Files Location

| File | Path | Purpose |
|------|------|---------|
| config.yaml | `C:\BackupAgent\config.yaml` | All backup configuration |
| manifest.db | `C:\BackupAgent\manifest.db` | File tracking database |
| Logs | `C:\BackupAgent\logs\` | Daily backup logs |
| Metrics | `C:\BackupAgent\logs\backup_metrics.jsonl` | Run metrics for trends |
| Rclone config | `C:\BackupAgent\rclone.conf` | GCS credentials (auto-generated) |
