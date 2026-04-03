@echo off
echo ========================================
echo   Exercise Posture Analysis System
echo ========================================
echo.
echo  1. Run Desktop App (OpenCV window)
echo  2. Run Web App  (open browser)
echo  3. Train ML Models
echo  4. Collect Training Data
echo  5. Run Tests
echo  6. Verify Installation
echo.
set /p choice="Enter choice (1-6): "

set "BASE=%~dp0"
set "PY=%BASE%venv\Scripts\python.exe"

:: Fallback to system python if venv not found
if not exist "%PY%" (
    echo WARNING: venv not found, using system Python...
    set "PY=python"
)

if "%choice%"=="1" (
    echo Starting desktop app...
    "%PY%" "%BASE%main_app.py"
)
if "%choice%"=="2" (
    echo Starting web app at http://localhost:5000
    start http://localhost:5000
    "%PY%" "%BASE%web_app.py"
)
if "%choice%"=="3" (
    echo Starting model trainer...
    "%PY%" "%BASE%train_model.py"
)
if "%choice%"=="4" (
    echo Starting data collector...
    "%PY%" "%BASE%data_collector.py"
)
if "%choice%"=="5" (
    echo Running tests...
    "%PY%" "%BASE%test_system.py"
)
if "%choice%"=="6" (
    echo Verifying installation...
    "%PY%" "%BASE%verify_setup.py"
)

pause
