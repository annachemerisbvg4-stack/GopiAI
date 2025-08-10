@echo off
REM Batch script for managing known issues in GopiAI test suite
REM This script provides easy access to the known issues management system

setlocal enabledelayedexpansion

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not available in PATH
    echo Please install Python or add it to your PATH
    exit /b 1
)

REM Check if we have arguments
if "%1"=="" (
    echo 🔧 GopiAI Known Issues Manager
    echo.
    echo Usage: manage_known_issues.bat ^<command^> [arguments]
    echo.
    echo Commands:
    echo   add       Add a new known issue
    echo   update    Update issue status
    echo   list      List issues
    echo   check     Check resolution progress
    echo   report    Generate comprehensive report
    echo   help      Show detailed help
    echo.
    echo Examples:
    echo   manage_known_issues.bat add ISSUE-001 "API timeout" "Description" "test_api_*"
    echo   manage_known_issues.bat update ISSUE-001 resolved
    echo   manage_known_issues.bat report
    echo.
    exit /b 0
)

REM Execute the Python script with all arguments
python manage_known_issues.py %*

REM Check if the command was successful
if errorlevel 1 (
    echo.
    echo ❌ Command failed. Run 'manage_known_issues.bat help' for usage information.
    exit /b 1
)

echo.
echo ✅ Command completed successfully.