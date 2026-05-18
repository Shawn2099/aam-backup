@echo off
REM ═══════════════════════════════════════════════════
REM Install Windows Services for Backup Automation
REM ═══════════════════════════════════════════════════
REM This script installs three Windows services via NSSM:
REM   1. PrefectServer — Prefect workflow server
REM   2. PrefectWorker — Prefect worker (executes backup flows)
REM   3. BackupUI — FastAPI status page
REM
REM Usage: Run as Administrator
REM   install_services.bat [--service-account DOMAIN\user] [--password password]
REM ═══════════════════════════════════════════════════

setlocal enabledelayedexpansion

REM --- Parse arguments ---
set SERVICE_ACCOUNT=LocalSystem
set SERVICE_PASSWORD=

:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--service-account" (
    set SERVICE_ACCOUNT=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--password" (
    set SERVICE_PASSWORD=%~2
    shift
    shift
    goto parse_args
)
shift
goto parse_args
:args_done

REM --- Configuration ---
set BACKUP_DIR=C:\BackupAgent
set PYTHON_DIR=C:\Python312
set PYTHON_EXE=%PYTHON_DIR%\python.exe
set PIP_EXE=%PYTHON_DIR%\Scripts\pip.exe
set PREFECT_EXE=%PYTHON_DIR%\Scripts\prefect.exe
set UV_EXE=%PYTHON_DIR%\Scripts\uv.exe
set NSSM_EXE=nssm
set LOG_DIR=%BACKUP_DIR%\logs
set PREFECT_API_URL=http://127.0.0.1:4200/api
set PREFECT_DB_URL=sqlite+aiosqlite:///%BACKUP_DIR%/prefect.db

REM --- Verify prerequisites ---
echo ================================================
echo Backup Agent — Install Windows Services
echo ================================================
echo.

echo [1/6] Checking prerequisites...

where %NSSM_EXE% >nul 2>&1
if errorlevel 1 (
    echo ERROR: NSSM not found in PATH.
    echo Download from https://nssm.cc/download and add to PATH.
    pause
    exit /b 1
)

if not exist "%PYTHON_EXE%" (
    echo ERROR: Python not found at %PYTHON_EXE%
    echo Install Python 3.11+ for all users.
    pause
    exit /b 1
)

if not exist "%PREFECT_EXE%" (
    echo ERROR: Prefect not found at %PREFECT_EXE%
    echo Run: pip install prefect
    pause
    exit /b 1
)

if not exist "%BACKUP_DIR%\flow.py" (
    echo ERROR: Backup agent files not found at %BACKUP_DIR%
    echo Extract project files to %BACKUP_DIR% first.
    pause
    exit /b 1
)

echo Prerequisites OK
echo.

REM --- Create directories ---
echo [2/6] Creating directories...
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%BACKUP_DIR%\rclone_temp" mkdir "%BACKUP_DIR%\rclone_temp"
echo Directories created
echo.

REM --- Install PrefectServer ---
echo [3/6] Installing PrefectServer...
%NSSM_EXE% install PrefectServer "%PREFECT_EXE%" server start --host 0.0.0.0 --port 4200
%NSSM_EXE% set PrefectServer AppDirectory "%BACKUP_DIR%"
%NSSM_EXE% set PrefectServer AppEnvironmentExtra PREFECT_API_DATABASE_CONNECTION_URL=%PREFECT_DB_URL%
%NSSM_EXE% set PrefectServer Stdout "%LOG_DIR%\prefect_server_stdout.log"
%NSSM_EXE% set PrefectServer Stderr "%LOG_DIR%\prefect_server_stderr.log"
%NSSM_EXE% set PrefectServer Start SERVICE_AUTO_START
%NSSM_EXE% set PrefectServer AppRestartDelay 10000
%NSSM_EXE% set PrefectServer AppExit Default Restart
echo PrefectServer installed
echo.

REM --- Install PrefectWorker ---
echo [4/6] Installing PrefectWorker...
if /i "%SERVICE_ACCOUNT%"=="LocalSystem" (
    %NSSM_EXE% install PrefectWorker "%PREFECT_EXE%" worker start --pool default --type process
) else (
    %NSSM_EXE% install PrefectWorker "%PREFECT_EXE%" worker start --pool default --type process
    if defined SERVICE_PASSWORD (
        %NSSM_EXE% set PrefectWorker ObjectName "%SERVICE_ACCOUNT%" "%SERVICE_PASSWORD%"
    ) else (
        echo WARNING: No password provided for service account.
        echo You will be prompted to set it manually.
        %NSSM_EXE% edit PrefectWorker
    )
)
%NSSM_EXE% set PrefectWorker AppDirectory "%BACKUP_DIR%"
%NSSM_EXE% set PrefectWorker AppEnvironmentExtra PREFECT_API_URL=%PREFECT_API_URL%
%NSSM_EXE% set PrefectWorker Stdout "%LOG_DIR%\prefect_worker_stdout.log"
%NSSM_EXE% set PrefectWorker Stderr "%LOG_DIR%\prefect_worker_stderr.log"
%NSSM_EXE% set PrefectWorker Start SERVICE_AUTO_START
%NSSM_EXE% set PrefectWorker AppRestartDelay 30000
%NSSM_EXE% set PrefectWorker AppExit Default Restart
echo PrefectWorker installed
echo.

REM --- Install BackupUI ---
echo [5/6] Installing BackupUI...
%NSSM_EXE% install BackupUI "%PYTHON_EXE%" -m uvicorn ui.server:app --host 0.0.0.0 --port 8080
%NSSM_EXE% set BackupUI AppDirectory "%BACKUP_DIR%"
%NSSM_EXE% set BackupUI AppEnvironmentExtra PREFECT_API_URL=%PREFECT_API_URL%
%NSSM_EXE% set BackupUI Stdout "%LOG_DIR%\ui_stdout.log"
%NSSM_EXE% set BackupUI Stderr "%LOG_DIR%\ui_stderr.log"
%NSSM_EXE% set BackupUI Start SERVICE_AUTO_START
%NSSM_EXE% set BackupUI AppRestartDelay 10000
%NSSM_EXE% set BackupUI AppExit Default Restart
echo BackupUI installed
echo.

REM --- Start services ---
echo [6/7] Starting services...
net start PrefectServer
timeout /t 5 /nobreak >nul
net start PrefectWorker
timeout /t 3 /nobreak >nul
net start BackupUI
echo.

REM --- Create work pool ---
echo [7/7] Creating Prefect work pool...
timeout /t 3 /nobreak >nul
"%PREFECT_EXE%" work-pool create default --type process 2>nul
if errorlevel 1 (
    echo Work pool may already exist or server not ready yet.
    echo Run manually: prefect work-pool create default --type process
) else (
    echo Work pool 'default' created
)
echo.

echo ================================================
echo All services installed and started
echo ================================================
echo.
echo Services:
echo   PrefectServer  — http://localhost:4200
echo   PrefectWorker  — executes backup flows
echo   BackupUI       — http://localhost:8080
echo.
echo Next steps:
echo   1. Create deployment: uv run deploy/create_deployment.py create
echo   2. Configure email notifications in Prefect UI
echo   3. Verify status UI at http://localhost:8080
echo.
pause
