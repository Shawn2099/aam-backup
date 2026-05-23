$ErrorActionPreference = "Stop"

# Map network drive
net use \\10.10.186.231\lan_backup Qwerty123innovizt@ /user:Administrator /persistent:no

# Run E2E
C:\BackupAgent\venv\Scripts\python.exe C:\BackupAgent\e2e_core_runner.py C:\BackupAgent\config.yaml
$result = $LASTEXITCODE

# Cleanup
net use \\10.10.186.231\lan_backup /delete /y 2>$null

exit $result
