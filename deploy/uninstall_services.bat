@echo off
REM ═══════════════════════════════════════════════════
REM Uninstall Windows Services for Backup Automation
REM ═══════════════════════════════════════════════════
REM This script stops and removes three Windows services:
REM   1. PrefectServer
REM   2. PrefectWorker
REM   3. BackupUI
REM
REM Usage: Run as Administrator
REM   uninstall_services.bat [--keep-data]
REM
REM By default, this script does NOT delete:
REM   - config.yaml
REM   - manifest.db
REM   - prefect.db
REM   - log files
REM   - rclone.exe
REM   - GCS service account key
REM
REM Use --keep-data to explicitly preserve all data files.
REM ═══════════════════════════════════════════════════

setlocal enabledelayedexpansion

set KEEP_DATA=0

:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="--keep-data" (
    set KEEP_DATA=1
    shift
    goto parse_args
)
shift
goto parse_args
:args_done

set SERVY_EXE=servy

echo ================================================
echo Backup Agent — Uninstall Windows Services (Servy)
echo ================================================
echo.

REM --- Verify Servy ---
where %SERVY_EXE% >nul 2>&1
if errorlevel 1 (
    echo ERROR: Servy not found in PATH.
    echo Cannot uninstall services without Servy.
    echo Download from https://github.com/aliostad/Servy/releases
    pause
    exit /b 1
)

echo [1/4] Stopping services...

%SERVY_EXE% stop BackupUI >nul 2>&1
if errorlevel 1 (
    echo   BackupUI was not running
) else (
    echo   BackupUI stopped
)

%SERVY_EXE% stop PrefectWorker >nul 2>&1
if errorlevel 1 (
    echo   PrefectWorker was not running
) else (
    echo   PrefectWorker stopped
)

%SERVY_EXE% stop PrefectServer >nul 2>&1
if errorlevel 1 (
    echo   PrefectServer was not running
) else (
    echo   PrefectServer stopped
)

echo.
echo [2/4] Removing services...

%SERVY_EXE% delete PrefectServer >nul 2>&1
if errorlevel 1 (
    echo   PrefectServer not found
) else (
    echo   PrefectServer removed
)

%SERVY_EXE% delete PrefectWorker >nul 2>&1
if errorlevel 1 (
    echo   PrefectWorker not found
) else (
    echo   PrefectWorker removed
)

%SERVY_EXE% delete BackupUI >nul 2>&1
if errorlevel 1 (
    echo   BackupUI not found
) else (
    echo   BackupUI removed
)

echo.
echo [3/4] Services removed
echo.

echo [4/4] Data preservation
echo.
echo The following files were NOT deleted:
echo   - C:\BackupAgent\config.yaml
echo   - C:\BackupAgent\manifest.db
echo   - C:\BackupAgent\prefect.db
echo   - C:\BackupAgent\logs\*
echo   - C:\BackupAgent\rclone.exe
echo   - C:\BackupAgent\gcs_service_account.json
echo.

if %KEEP_DATA%==0 (
    echo To remove all data files, run:
    echo   rmdir /s /q C:\BackupAgent
    echo.
)

echo ================================================
echo Uninstall complete
echo ================================================
pause
