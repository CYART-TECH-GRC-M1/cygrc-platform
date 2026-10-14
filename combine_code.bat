@echo off
setlocal

title CyGRC - Combine Codebase Files

echo ====================================================================
echo       CyGRC Platform - Export Codebase to Single File
echo ====================================================================
echo.

cd /d "%~dp0"

:: 1. Check if virtual environment python exists
if exist ".venv\Scripts\python.exe" (
    echo [INFO] Running using virtual environment Python: .venv
    ".venv\Scripts\python.exe" "scripts\combine_code.py"
    goto finished
)

:: 2. Check if global python exists
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Running using system Python
    python "scripts\combine_code.py"
    goto finished
)

:: 3. Check if py launcher exists
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Running using Python Launcher
    py "scripts\combine_code.py"
    goto finished
)

:: 4. Fallback to PowerShell if Python is not found
echo [WARN] Python not found. Falling back to PowerShell...
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\combine_code.ps1"

:finished
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================================================
    echo [SUCCESS] Codebase export complete!
    echo Output saved to: combined_codebase.txt
    echo ====================================================================
) else (
    echo.
    echo [ERROR] Export encountered an error. Check messages above.
)

echo.
pause
