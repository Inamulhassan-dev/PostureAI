@echo off
title PostureAI - Stopping...

echo =======================================================
echo   Stopping PostureAI Services...
echo =======================================================
echo.

:: 1. Stop anything listening on port 5000
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $conns = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue; if ($conns) { foreach ($c in $conns) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } } }" 

:: 2. Stop any remaining python processes running web_app.py
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { Get-WmiObject Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -match 'web_app' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue } }"

echo   [OK] PostureAI stopped successfully.
echo.
echo   Run START.bat to launch again.
echo.
timeout /t 3 /nobreak >nul
