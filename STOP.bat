@echo off
setlocal EnableDelayedExpansion
title PostureAI - Stopping...

for /f %%a in ('echo prompt $E^| cmd') do set "ESC=%%a"
set "CYAN=%ESC%[96m"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "RED=%ESC%[91m"
set "BOLD=%ESC%[1m"
set "RESET=%ESC%[0m"
set "DIM=%ESC%[2m"

cls
echo.
echo %CYAN%%BOLD%╔══════════════════════════════════════════════════════════════╗%RESET%
echo %CYAN%%BOLD%║           PostureAI - Stopping Services                     ║%RESET%
echo %CYAN%%BOLD%╚══════════════════════════════════════════════════════════════╝%RESET%
echo.

set "KILLED=0"

:: ─── Kill by port 5000 ───────────────────────────────────────────────────
echo   %CYAN%Looking for PostureAI server on port 5000...%RESET%

for /f "tokens=5" %%p in (
    'netstat -ano ^| findstr ":5000 " ^| findstr "LISTENING" 2^>nul'
) do (
    echo   %YELLOW%  Found process on port 5000  (PID %%p)%RESET%
    taskkill /PID %%p /F >nul 2>&1
    if not errorlevel 1 (
        echo   %GREEN%  ✔  PID %%p stopped.%RESET%
        set "KILLED=1"
    ) else (
        echo   %RED%  ✘  Could not stop PID %%p (may need admin rights)%RESET%
    )
)

:: ─── Fallback: kill web_app.py by name ───────────────────────────────────
echo.
echo   %CYAN%Checking for any web_app.py Python processes...%RESET%

for /f "tokens=2" %%p in (
    'tasklist /FI "IMAGENAME eq python.exe" /NH 2^>nul ^| findstr "python"'
) do (
    :: Check command line to confirm it's web_app.py
    for /f "tokens=*" %%c in (
        'wmic process where "ProcessId=%%p" get CommandLine /value 2^>nul ^| findstr "web_app"'
    ) do (
        echo   %YELLOW%  Found web_app.py  (PID %%p)  — stopping...%RESET%
        taskkill /PID %%p /F >nul 2>&1
        echo   %GREEN%  ✔  PID %%p stopped.%RESET%
        set "KILLED=1"
    )
)

:: ─── Result ──────────────────────────────────────────────────────────────
echo.
if "%KILLED%"=="1" (
    echo %GREEN%%BOLD%╔══════════════════════════════════════════════════════════════╗%RESET%
    echo %GREEN%%BOLD%║   ✔  PostureAI stopped successfully.                        ║%RESET%
    echo %GREEN%%BOLD%╚══════════════════════════════════════════════════════════════╝%RESET%
    echo.
    echo   %DIM%  Run START.bat to launch again.%RESET%
) else (
    echo %YELLOW%%BOLD%╔══════════════════════════════════════════════════════════════╗%RESET%
    echo %YELLOW%%BOLD%║   ⚠  No running PostureAI process was found.                ║%RESET%
    echo %YELLOW%%BOLD%╚══════════════════════════════════════════════════════════════╝%RESET%
    echo.
    echo   %DIM%  The app may already be stopped, or was started differently.%RESET%
)

echo.
timeout /t 3 /nobreak >nul
