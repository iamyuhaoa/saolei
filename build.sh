#!/bin/bash
# Build script for testing on Unix-like systems
# Note: This creates a test build only. For Windows EXE, run build.bat on Windows

echo "========================================"
echo "MinesweeperAI - Test Build Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "Installing dependencies..."
python3 -m pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "Running tests..."
python3 -m pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "WARNING: Some tests failed"
fi

echo ""
echo "========================================"
echo "Note: To create Windows EXE:"
echo "1. Copy project to Windows machine"
echo "2. Run build.bat"
echo "========================================"
