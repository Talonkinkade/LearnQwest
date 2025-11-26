@echo off
REM ADA Background Service Launcher
REM Starts ADA service in foreground for testing

echo.
echo ========================================
echo   ADA Background Service
echo   Never Do Manual Work Again
echo ========================================
echo.
echo Starting ADA service...
echo Press Ctrl+C to stop
echo.

python ada_service.py

pause
