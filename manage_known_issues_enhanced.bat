@echo off
REM Enhanced Known Issues Management System - Windows Batch Script
REM
REM This script provides easy access to the enhanced known issues management system
REM with automatic resolution detection, progress reporting, and monitoring capabilities.

setlocal enabledelayedexpansion

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not available or not in PATH
    echo Please install Python and ensure it's in your PATH
    exit /b 1
)

REM Set script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if enhanced script exists
if not exist "manage_known_issues_enhanced.py" (
    echo ❌ Enhanced management script not found
    echo Please ensure manage_known_issues_enhanced.py is in the current directory
    exit /b 1
)

REM If no arguments provided, show help
if "%1"=="" (
    echo.
    echo 🔧 GopiAI Enhanced Known Issues Management System
    echo ================================================
    echo.
    echo Quick Commands:
    echo   %~nx0 status           - Show current status
    echo   %~nx0 check            - Check for auto-resolutions
    echo   %~nx0 progress         - Generate progress report
    echo   %~nx0 monitor          - Start monitoring
    echo   %~nx0 dashboard        - Generate dashboard
    echo   %~nx0 help             - Show detailed help
    echo.
    echo For detailed usage: %~nx0 help
    echo.
    goto :eof
)

REM Handle quick commands
if "%1"=="status" (
    echo 📊 Checking Known Issues Status...
    python manage_known_issues_enhanced.py list
    echo.
    python manage_known_issues_enhanced.py progress --team-metrics
    goto :eof
)

if "%1"=="check" (
    echo 🤖 Checking for Automatic Resolutions...
    python manage_known_issues_enhanced.py auto-resolve --check
    goto :eof
)

if "%1"=="progress" (
    echo 📈 Generating Progress Report...
    python manage_known_issues_enhanced.py progress --report
    goto :eof
)

if "%1"=="monitor" (
    echo 🔄 Starting Issue Monitoring...
    echo Press Ctrl+C to stop monitoring
    python manage_known_issues_enhanced.py monitor --start
    goto :eof
)

if "%1"=="dashboard" (
    echo 🎨 Generating Dashboard...
    python manage_known_issues_enhanced.py dashboard --generate
    echo.
    echo 📁 Dashboard files created in test_infrastructure/known_issues/
    echo 💡 Open the HTML files in your browser to view the dashboard
    goto :eof
)

if "%1"=="help" (
    echo.
    echo 🔧 GopiAI Enhanced Known Issues Management System
    echo ================================================
    echo.
    echo QUICK COMMANDS:
    echo   %~nx0 status           - Show current issues status and team metrics
    echo   %~nx0 check            - Check for automatic resolutions
    echo   %~nx0 progress         - Generate comprehensive progress report
    echo   %~nx0 monitor          - Start continuous monitoring daemon
    echo   %~nx0 dashboard        - Generate HTML dashboard
    echo.
    echo BASIC ISSUE MANAGEMENT:
    echo   %~nx0 add ISSUE-001 "Title" "Description" "test_pattern"
    echo   %~nx0 update ISSUE-001 resolved --notes "Fixed the issue"
    echo   %~nx0 list [status]    - List all issues or filter by status
    echo.
    echo AUTOMATIC RESOLUTION:
    echo   %~nx0 auto-resolve --check                    - Check for resolutions now
    echo   %~nx0 auto-resolve --enable-monitoring        - Enable continuous monitoring
    echo   %~nx0 auto-resolve --config                   - Show configuration
    echo   %~nx0 auto-resolve --history ISSUE-001       - Show resolution history
    echo.
    echo PROGRESS REPORTING:
    echo   %~nx0 progress --report                       - Comprehensive progress report
    echo   %~nx0 progress --trends                       - Analyze progress trends
    echo   %~nx0 progress --milestones                   - Show progress milestones
    echo   %~nx0 progress --team-metrics                 - Show team performance
    echo   %~nx0 progress --issue ISSUE-001              - Progress for specific issue
    echo.
    echo MONITORING:
    echo   %~nx0 monitor --start                         - Start monitoring daemon
    echo   %~nx0 monitor --stop                          - Stop monitoring daemon
    echo   %~nx0 monitor --status                        - Show monitoring status
    echo   %~nx0 monitor --alerts                        - Show recent alerts
    echo.
    echo DASHBOARD:
    echo   %~nx0 dashboard --generate                    - Generate HTML dashboard
    echo   %~nx0 dashboard --export json                 - Export data to JSON
    echo.
    echo WORKFLOW INTEGRATION:
    echo   %~nx0 workflow --suggest                      - Suggest new issues from failures
    echo   %~nx0 workflow --auto-create                  - Auto-create suggested issues
    echo   %~nx0 workflow --update-markers               - Update pytest markers
    echo   %~nx0 workflow --ci-report                    - Generate CI/CD report
    echo.
    echo COMPREHENSIVE REPORTING:
    echo   %~nx0 report                                  - Generate comprehensive report
    echo   %~nx0 report --format json --output report.json
    echo   %~nx0 report --format html
    echo.
    echo EXAMPLES:
    echo   # Add a new critical issue
    echo   %~nx0 add ISSUE-001 "API timeout" "API calls timing out" "test_api_*" --priority critical
    echo.
    echo   # Check and auto-resolve issues
    echo   %~nx0 check
    echo.
    echo   # Generate full dashboard
    echo   %~nx0 dashboard
    echo.
    echo   # Start monitoring (runs continuously)
    echo   %~nx0 monitor
    echo.
    echo FILES AND DIRECTORIES:
    echo   • Database: test_infrastructure/known_issues/known_issues.db
    echo   • Reports: test_infrastructure/known_issues/
    echo   • Configuration: test_infrastructure/known_issues/*_config.json
    echo   • Pytest Markers: pytest_markers.py
    echo.
    goto :eof
)

REM For all other commands, pass through to the Python script
python manage_known_issues_enhanced.py %*

REM Check exit code and provide helpful message
if errorlevel 1 (
    echo.
    echo ❌ Command failed. Use '%~nx0 help' for usage information.
    exit /b 1
)

echo.
echo ✅ Command completed successfully.