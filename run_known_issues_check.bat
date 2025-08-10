@echo off
REM Comprehensive known issues check for GopiAI test suite
REM This script runs the complete known issues management workflow

setlocal enabledelayedexpansion

echo 🔧 GopiAI Known Issues Check
echo ============================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not available in PATH
    echo Please install Python or add it to your PATH
    exit /b 1
)

REM Parse command line arguments
set AUTO_CREATE=
set UPDATE_MARKERS=
set FULL_REPORT=
set CHECK_PROGRESS=
set QUICK_MODE=

:parse_args
if "%1"=="" goto run_script
if "%1"=="--auto-create" set AUTO_CREATE=--auto-create
if "%1"=="--update-markers" set UPDATE_MARKERS=--update-markers
if "%1"=="--full-report" set FULL_REPORT=--full-report
if "%1"=="--check-progress" set CHECK_PROGRESS=--check-progress
if "%1"=="--quick" set QUICK_MODE=--quick
if "%1"=="--help" goto show_help
shift
goto parse_args

:run_script
REM Build command
set COMMAND=python run_known_issues_check.py %AUTO_CREATE% %UPDATE_MARKERS% %FULL_REPORT% %CHECK_PROGRESS% %QUICK_MODE%

REM Execute the command
echo Running: %COMMAND%
echo.
%COMMAND%

REM Check exit code
if errorlevel 1 (
    echo.
    echo ❌ Known issues check completed with warnings or errors
    echo Run with --help for usage information
    exit /b 1
) else (
    echo.
    echo ✅ Known issues check completed successfully
    exit /b 0
)

:show_help
echo.
echo GopiAI Known Issues Check
echo ========================
echo.
echo Usage: run_known_issues_check.bat [options]
echo.
echo Options:
echo   --auto-create      Automatically create known issues for recurring failures
echo   --update-markers   Update pytest markers and configuration
echo   --full-report      Generate full HTML and JSON reports
echo   --check-progress   Check resolution progress for all active issues
echo   --quick            Run quick check only
echo   --help             Show this help message
echo.
echo Examples:
echo   run_known_issues_check.bat
echo   run_known_issues_check.bat --auto-create --update-markers
echo   run_known_issues_check.bat --quick
echo   run_known_issues_check.bat --full-report --check-progress
echo.
echo Reports are saved to: test_infrastructure\known_issues\
echo.
exit /b 0