@echo off
REM ADA Service Installation Script
REM Installs required packages and sets up service

echo.
echo ========================================
echo   ADA Service Installation
echo   Never Do Manual Work Again
echo ========================================
echo.

echo [1/3] Installing required packages...
python -m pip install pystray pillow pywin32 --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Package installation failed
    pause
    exit /b 1
)
echo [OK] Packages installed

echo.
echo [2/3] Creating directories...
if not exist "commands" mkdir commands
if not exist "commands\results" mkdir "commands\results"
if not exist "dropzones\inbox" mkdir "dropzones\inbox"
if not exist "dropzones\processing" mkdir "dropzones\processing"
if not exist "dropzones\completed" mkdir "dropzones\completed"
if not exist "dropzones\failed" mkdir "dropzones\failed"
echo [OK] Directories created

echo.
echo [3/3] Testing service...
python ada_service.py --help >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Service test had issues, but continuing...
) else (
    echo [OK] Service ready
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To start ADA service:
echo   1. Run: start_ada_service.bat
echo   2. Run: start_ada_tray.bat
echo.
echo Or add to Windows startup:
echo   - Copy start_ada_tray.bat to:
echo   - shell:startup folder
echo.
pause
