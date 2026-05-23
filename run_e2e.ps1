$ErrorActionPreference = "Stop"

# Map network drive for SMB auth
net use \\10.10.186.231\lan_backup Qwerty123innovizt@ /user:Administrator /persistent:no

# Run E2E core test
C:\Users\Administrator\Desktop\aam-backup-main\venv\Scripts\python.exe C:\Users\Administrator\Desktop\aam-backup-main\e2e_core_runner.py C:\Users\Administrator\Desktop\aam-backup-main\config.yaml
$result = $LASTEXITCODE

net use \\10.10.186.231\lan_backup /delete /y 2>$null
exit $result
