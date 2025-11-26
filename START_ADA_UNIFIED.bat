@echo off
REM ========================================
REM LearnQwest ADA - Unified Launcher
REM ========================================

echo.
echo ========================================
echo   LearnQwest ADA Unified Launcher
echo ========================================
echo.

REM Deactivate any existing venv first
call deactivate 2>nul

REM Activate the correct venv
call learnqwest_test_venv\Scripts\activate.bat

REM Verify Python and Ada
python -c "import sys; print('Using Python:', sys.executable)" 2>nul
python -c "from ada_orchestrator import ADAOrchestrator; print(' Ada Orchestrator loaded')" 2>nul

echo.
echo ========================================
echo   Choose Your Mode:
echo ========================================
echo   1. Start Ada API (REST API on port 5001)
echo   2. Start Aider (Code assistant)
echo   3. Test Ada Orchestrator
echo   4. Interactive Python (with Ada loaded)
echo   5. Open Command Center in Browser
echo   6. Open in VS Code
echo   7. Exit
echo ========================================
echo.

set /p choice="Enter choice (1-7): "

if "%choice%"=="1" goto start_api
if "%choice%"=="2" goto start_aider
if "%choice%"=="3" goto test_ada
if "%choice%"=="4" goto interactive
if "%choice%"=="5" goto open_command
if "%choice%"=="6" goto vscode
if "%choice%"=="7" goto end

:start_api
echo.
echo [API] Starting Ada API Server...
echo Server will be available at: http://localhost:5001
echo Command Center: http://localhost:5001/command
echo Dashboard: http://localhost:5001
echo.
python ada_api.py
goto end

:start_aider
echo.
echo [AIDER] Starting Aider with Ada files...
echo.
aider --model claude-3-5-sonnet-20241022 ada_orchestrator.py ada_api.py
goto end

:test_ada
echo.
echo [TEST] Testing Ada Orchestrator...
echo.
python -c "from ada_orchestrator import ADAOrchestrator; ada = ADAOrchestrator(); print(' Ada Orchestrator initialized successfully!'); import json; print(json.dumps(ada.get_system_status(), indent=2))"
echo.
pause
goto end

:interactive
echo.
echo [PYTHON] Starting Interactive Python...
echo Ada modules are pre-loaded!
echo.
python -i -c "from ada_orchestrator import ADAOrchestrator; ada = ADAOrchestrator(); print(' Ada loaded! Use: ada.get_system_status()')"
goto end

:open_command
echo.
echo [BROWSER] Opening Command Center...
start http://localhost:5001/command
echo.
echo Command Center opened in browser!
echo Make sure Ada API is running (Option 1)
echo.
pause
goto end

:vscode
echo.
echo [VS CODE] Opening LearnQwest in VS Code...
code C:\Users\talon\OneDrive\Projects\LearnQwest
goto end

:end
echo.
echo Goodbye! 
pause
