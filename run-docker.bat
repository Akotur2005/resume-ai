@echo off
cd /d "%~dp0"
echo ========================================================
echo   Resume-AI Multi-Agent System - Docker Startup
echo ========================================================
echo.

docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Docker Desktop engine is not running yet.
    echo     Please open "Docker Desktop" from your Windows Start Menu,
    echo     wait 10 seconds for the engine to initialize, then run this file again!
    echo.
    pause
    exit /b 1
)

echo Starting PostgreSQL (pgvector), Flask Multi-Agent Backend, and React Frontend...
echo.
docker-compose up --build
pause
