@echo off
REM Password Manager GUI Launcher for Windows

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if pm CLI is available
pm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pm CLI is not found in PATH
    echo Please build the CLI first: cargo build --release
    echo Then add it to PATH or run from the project directory
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "%SCRIPT_DIR%venv" (
    echo Installing Python dependencies...
    python -m venv "%SCRIPT_DIR%venv"
    call "%SCRIPT_DIR%venv\Scripts\activate.bat"
    pip install -r "%SCRIPT_DIR%requirements.txt"
) else (
    call "%SCRIPT_DIR%venv\Scripts\activate.bat"
)

REM Run the GUI
python "%SCRIPT_DIR%gui_new\password_manager.py"
