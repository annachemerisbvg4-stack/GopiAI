@echo off
REM GopiAI Test Reporting System
REM Generates comprehensive test reports and analysis

echo.
echo ========================================
echo   GopiAI Test Reporting System
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Create reports directory if it doesn't exist
if not exist "test_reports" mkdir test_reports

echo [1/5] Generating Coverage Report...
python -m test_infrastructure.coverage_reporter
if errorlevel 1 (
    echo WARNING: Coverage report generation failed
) else (
    echo ✅ Coverage report generated
)

echo.
echo [2/5] Analyzing Test Failures...
python -m test_infrastructure.failure_analyzer
if errorlevel 1 (
    echo WARNING: Failure analysis failed
) else (
    echo ✅ Failure analysis completed
)

echo.
echo [3/5] Tracking Quality Metrics...
python -m test_infrastructure.quality_tracker
if errorlevel 1 (
    echo WARNING: Quality tracking failed
) else (
    echo ✅ Quality metrics tracked
)

echo.
echo [4/5] Generating Dashboard...
python -c "from test_infrastructure.testing_dashboard import TestingDashboard; TestingDashboard().generate_dashboard()"
if errorlevel 1 (
    echo WARNING: Dashboard generation failed
) else (
    echo ✅ Dashboard generated
)

echo.
echo [5/5] Creating Master Report...
python -m test_infrastructure.master_reporter --no-tests
if errorlevel 1 (
    echo ERROR: Master report generation failed
    pause
    exit /b 1
) else (
    echo ✅ Master report created
)

echo.
echo ========================================
echo   Report Generation Complete!
echo ========================================
echo.
echo 📊 Reports available in: test_reports/
echo 📋 Executive summary: test_reports/executive_summary_latest.md
echo 🌐 Dashboard: test_reports/dashboard/index.html
echo.

REM Ask if user wants to open dashboard
set /p open_dashboard="Open dashboard in browser? (y/n): "
if /i "%open_dashboard%"=="y" (
    echo Opening dashboard...
    python -c "from test_infrastructure.testing_dashboard import TestingDashboard; TestingDashboard().serve_dashboard()"
)

pause