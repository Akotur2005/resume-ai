@echo off
echo ==============================================
echo Installing pgvector for PostgreSQL 18...
echo ==============================================

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Administrator permissions required!
    echo Please right-click this file and select "Run as administrator".
    echo.
    pause
    exit /b 1
)

set "SRC_DIR=%~dp0pgvector_files"
set "PG_DIR=C:\Program Files\PostgreSQL\18"

echo Copying vector.dll to "%PG_DIR%\lib"...
copy /Y "%SRC_DIR%\lib\vector.dll" "%PG_DIR%\lib\"

echo Copying extension files to "%PG_DIR%\share\extension"...
copy /Y "%SRC_DIR%\share\extension\*.*" "%PG_DIR%\share\extension\"

if not exist "%PG_DIR%\include\server\extension\vector" (
    mkdir "%PG_DIR%\include\server\extension\vector"
)
echo Copying header files to "%PG_DIR%\include\server\extension\vector"...
copy /Y "%SRC_DIR%\include\server\extension\vector\*.*" "%PG_DIR%\include\server\extension\vector\"

echo.
echo ==============================================
echo [SUCCESS] pgvector installed successfully!
echo.
echo Now go back to pgAdmin and run:
echo    CREATE EXTENSION vector;
echo ==============================================
pause
