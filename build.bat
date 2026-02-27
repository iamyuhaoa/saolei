@echo off
REM Build script for Windows - create MinesweeperAI.exe

echo ========================================
echo MinesweeperAI - Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building EXE with PyInstaller...
pyinstaller build.spec
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Output: dist\MinesweeperAI.exe
echo.
echo To run:
echo   1. Open Minesweeper
echo   2. Double-click dist\MinesweeperAI.exe
echo.

pause
