@echo off
REM ═══════════════════════════════════════════════════
REM Install Windows Services for Backup Automation
REM ═══════════════════════════════════════════════════
REM This script installs three Windows services via Servy:
REM   1. PrefectServer — Prefect workflow server
REM   2. PrefectWorker — Prefect worker (executes backup flows)
REM   3. BackupUI — FastAPI status page
REM
REM Usage: Run as Administrator
REM   install_services.bat [--service-account DOMAIN\user] [--password password]
REM
REM Prerequisites:
REM   - Servy installed (https://github.com/aliostad/Servy)
REM   - Python 3.12+ installed for all users
REM   - Project files extracted to C:\BackupAgent
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
set PREFECT_EXE=%PYTHON_DIR%\Scripts\prefect.exe
set SERVY_EXE=servy
set LOG_DIR=%BACKUP_DIR%\logs
set PREFECT_API_URL=http://127.0.0.1:4200/api
set PREFECT_DB_URL=sqlite+aiosqlite:///%BACKUP_DIR%/prefect.db
set HEALTH_CHECK_URL=http://127.0.0.1:8080/health

REM --- Verify prerequisites ---
echo ================================================
echo Backup Agent — Install Windows Services (Servy)
echo ================================================
echo.

echo [1/6] Checking prerequisites...

where %SERVY_EXE% >nul 2>&1
if errorlevel 1 (
    echo ERROR: Servy not found in PATH.
    echo Download from https://github.com/aliostad/Servy/releases
    echo Add servy.exe to PATH or place in system directory.
    pause
    exit /b 1
)

if not exist "%PYTHON_EXE%" (
    echo ERROR: Python not found at %PYTHON_EXE%
    echo Install Python 3.12+ for all users.
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
%SERVY_EXE% create PrefectServer ^
    --command "%PREFECT_EXE%" ^
    --args "server start --host 0.0.0.0 --port 4200" ^
    --working-directory "%BACKUP_DIR%" ^
    --log-file "%LOG_DIR%\prefect_server.log" ^
    --log-rotate ^
    --log-max-size-mb 50 ^
    --log-max-files 5 ^
    --restart-on-failure ^
    --restart-delay-seconds 10 ^
    --start-mode automatic
echo PrefectServer installed
echo.

REM --- Install PrefectWorker ---
echo [4/6] Installing PrefectWorker...
%SERVY_EXE% create PrefectWorker ^
    --command "%PREFECT_EXE%" ^
    --args "worker start --pool default --type process" ^
    --working-directory "%BACKUP_DIR%" ^
    --log-file "%LOG_DIR%\prefect_worker.log" ^
    --log-rotate ^
    --log-max-size-mb 50 ^
    --log-max-files 5 ^
    --restart-on-failure ^
    --restart-delay-seconds 30 ^
    --start-mode automatic ^
    --dependency PrefectServer ^
    --env PREFECT_API_URL=%PREFECT_API_URL%
echo PrefectWorker installed
echo.

REM --- Install BackupUI ---
echo [5/6] Installing BackupUI...
%SERVY_EXE% create BackupUI ^
    --command "%PYTHON_EXE%" ^
    --args "-m uvicorn ui.server:app --host 0.0.0.0 --port 8080" ^
    --working-directory "%BACKUP_DIR%" ^
    --log-file "%LOG_DIR%\backup_ui.log" ^
    --log-rotate ^
    --log-max-size-mb 20 ^
    --log-max-files 3 ^
    --restart-on-failure ^
    --restart-delay-seconds 10 ^
    --start-mode automatic ^
    --health-check-url %HEALTH_CHECK_URL% ^
    --health-check-interval-seconds 30 ^
    --health-check-timeout-seconds 5 ^
    --health-check-unhealthy-threshold 3 ^
    --env PREFECT_API_URL=%PREFECT_API_URL%
echo BackupUI installed
echo.

REM --- Start services ---
echo [6/7] Starting services...
%SERVY_EXE% start PrefectServer
timeout /t 5 /nobreak >nul
%SERVY_EXE% start PrefectWorker
timeout /t 3 /nobreak >nul
%SERVY_EXE% start BackupUI
echo.

REM --- Create work pool ---
echo [7/7] Creating Prefect work pool...
timeout /t 3 /nobreak >nul
"%PREFECT_EXE%" workpool create default --type process 2>nul
if errorlevel 1 (
    echo Work pool may already exist or server not ready yet.
    echo Run manually: prefect workpool create default --type process
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
echo Service Management:
echo   servy status              — view all services
echo   servy stop ^<name^>         — stop a service
echo   servy restart ^<name^>      — restart a service
echo   servy logs ^<name^>         — view service logs
echo.
echo Next steps:
echo   1. Create deployment: uv run deploy/create_deployment.py create
echo   2. Configure email notifications in Prefect UI
echo   3. Verify status UI at http://localhost:8080
echo.
pause
