#!/bin/bash
# Password Manager GUI Launcher

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if pm CLI is available
if ! command -v pm &> /dev/null; then
    echo "Error: pm CLI is not found in PATH"
    echo "Please build the CLI first: cargo build --release"
    echo "Then add it to PATH or run from the project directory"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Installing Python dependencies..."
    python3 -m venv "$SCRIPT_DIR/venv"
    source "$SCRIPT_DIR/venv/bin/activate"
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Run the GUI
python3 "$SCRIPT_DIR/password_manager.py"
