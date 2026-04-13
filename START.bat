@echo off
setlocal EnableDelayedExpansion
:: Ensure Windows system commands are available
set "PATH=%SystemRoot%\System32;%SystemRoot%\System32\wbem;%PATH%"

title PostureAI - Starting...

REM =========================================================================
:: ANSI colour helper (requires Windows 10 1903+)
REM =========================================================================
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
echo %CYAN%%BOLD%+==============================================================+%RESET%
echo %CYAN%%BOLD%^|     PostureAI - Exercise Posture Analysis                    ^|%RESET%
echo %CYAN%%BOLD%^|     Intelligent Computer Vision System  ^|  Launcher          ^|%RESET%
echo %CYAN%%BOLD%+==============================================================+%RESET%
echo.

REM =========================================================================
:: STEP 1 — Find project base directory
REM =========================================================================
set "BASE=%~dp0"
echo %DIM%  Project root : %BASE%%RESET%
echo.

REM =========================================================================
:: STEP 2 — Check that Python is installed
REM =========================================================================
echo %CYAN%%BOLD%  [1/5]  Checking Python installation...%RESET%
python --version >nul 2>&1
if errorlevel 1 (
    echo   %RED%[!!]  Python is not installed or not in PATH!%RESET%
    echo   %YELLOW%  ->  Download Python 3.10+ from https://python.org%RESET%
    echo   %YELLOW%  ->  Make sure to check "Add Python to PATH" during install%RESET%
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo   %GREEN%[OK]%RESET%  %%v detected
echo.

REM =========================================================================
:: STEP 3 — Check that venv exists, create if not
REM =========================================================================
echo %CYAN%%BOLD%  [2/5]  Setting up virtual environment...%RESET%
if not exist "%BASE%venv\Scripts\python.exe" (
    echo   %YELLOW%[??]  venv not found — creating now...%RESET%
    python -m venv "%BASE%venv"
    if errorlevel 1 (
        echo   %RED%[!!]  Could not create venv. Is Python installed correctly?%RESET%
        echo   %YELLOW%  ->  Download Python 3.10+ from https://python.org%RESET%
        pause
        exit /b 1
    )
    echo   %GREEN%[OK]%RESET%  Virtual environment created.
) else (
    echo   %GREEN%[OK]%RESET%  Virtual environment found.
)

:: Upgrade pip silently
"%BASE%venv\Scripts\python.exe" -m pip install --upgrade pip --quiet 2>nul
echo.

REM =========================================================================
:: STEP 4 — Install / verify packages
REM =========================================================================
echo %CYAN%%BOLD%  [3/5]  Verifying pip packages...%RESET%

"%BASE%venv\Scripts\python.exe" -c ^
  "import cv2,mediapipe,flask,sklearn,numpy,pandas,joblib,matplotlib,seaborn,PIL" ^
  2>nul
if errorlevel 1 (
    echo   %YELLOW%[??]  Some packages missing — installing from requirements.txt...%RESET%
    echo   %DIM%       (this may take a few minutes on first run)%RESET%
    "%BASE%venv\Scripts\pip.exe" install -r "%BASE%requirements.txt" --quiet
    if errorlevel 1 (
        echo   %RED%[!!]  pip install failed. Check your internet connection.%RESET%
        echo   %YELLOW%  ->  Try manually: venv\Scripts\pip install -r requirements.txt%RESET%
        pause
        exit /b 1
    )
    echo   %GREEN%[OK]%RESET%  All packages installed.
) else (
    echo   %GREEN%[OK]%RESET%  All core packages present.
)
echo.

REM =========================================================================
:: STEP 5 — Check ML models, auto-train if missing
REM =========================================================================
echo %CYAN%%BOLD%  [4/5]  Checking ML models...%RESET%

set "MODELS_OK=1"
for %%e in (squat pushup bicep_curl lunge shoulder_press) do (
    if not exist "%BASE%models\%%e_model.pkl" (
        set "MODELS_OK=0"
    )
)

if "!MODELS_OK!"=="0" (
    echo   %YELLOW%[??]  Some ML models missing — auto-training now...%RESET%
    echo   %DIM%       (this is a one-time process, takes ~30 seconds)%RESET%
    "%BASE%venv\Scripts\python.exe" -X utf8 -c "import sys,os; sys.path.insert(0,r'%BASE%'); os.chdir(r'%BASE%'); from train_model import PostureModelTrainer; t=PostureModelTrainer(); t.train_all_exercises()" 2>nul
    if errorlevel 1 (
        echo   %RED%[!!]  Model training failed.%RESET%
        echo   %YELLOW%  ->  Try manually: venv\Scripts\python train_model.py  (choose option 2)%RESET%
        pause
        exit /b 1
    )
    echo   %GREEN%[OK]%RESET%  All ML models trained successfully.
) else (
    echo   %GREEN%[OK]%RESET%  All 5 ML models present.
)
echo.

REM =========================================================================
:: STEP 6 — Run diagnostic (non-blocking for camera/port warnings)
REM =========================================================================
echo %CYAN%%BOLD%  [5/5]  Running system diagnostic...%RESET%
echo           %DIM%(checking files, modules, features, camera, routes)%RESET%
echo.

"%BASE%venv\Scripts\python.exe" -X utf8 "%BASE%check_system.py"
set DIAG_CODE=%ERRORLEVEL%

if %DIAG_CODE% NEQ 0 (
    echo.
    echo   %RED%%BOLD%  =================================================================%RESET%
    echo   %RED%%BOLD%  Diagnostic found issues. Fix them then re-run START.bat%RESET%
    echo   %RED%%BOLD%  =================================================================%RESET%
    echo.
    pause
    exit /b 1
)

REM:: ═══════════════════════════════════════════════════════════════════════════
:: STEP 7 — Kill any old instance on port 5000
:: ═══════════════════════════════════════════════════════════════════════════
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $conns = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue; if ($conns) { foreach ($c in $conns) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } } }" >nul 2>&1

REM =========================================================================
:: LAUNCH
REM =========================================================================
echo.
echo %GREEN%%BOLD%+==============================================================+%RESET%
echo %GREEN%%BOLD%^|  [OK]  All checks passed! Launching PostureAI...             ^|%RESET%
echo %GREEN%%BOLD%+==============================================================+%RESET%
echo.
echo   %CYAN%  Web App URL  :  http://localhost:5000%RESET%
echo   %DIM%  Press Ctrl+C to stop  ^|  Or run STOP.bat in another window%RESET%
echo.

:: Open browser after a short delay (3 seconds)
start "" /b cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

:: Start the Flask server (in this window so logs are visible)
title PostureAI - RUNNING on http://localhost:5000
"%BASE%venv\Scripts\python.exe" "%BASE%web_app.py"

:: If we get here, Flask exited
echo.
echo   %YELLOW%  PostureAI has stopped.%RESET%
pause
