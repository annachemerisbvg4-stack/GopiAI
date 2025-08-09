@echo off
REM Performance Tests Runner for GopiAI
REM This script runs comprehensive performance tests for all system components

echo ========================================
echo GopiAI Performance Test Suite
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if pytest is available
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pytest is not installed
    echo Please install with: pip install pytest pytest-qt psutil
    pause
    exit /b 1
)

REM Set environment variables for performance testing
set PERF_MEMORY_THRESHOLD_MB=500
set PERF_CPU_THRESHOLD_PERCENT=80
set PERF_RESPONSE_TIME_THRESHOLD_MS=5000

echo Environment configured for performance testing
echo Memory threshold: %PERF_MEMORY_THRESHOLD_MB%MB
echo CPU threshold: %PERF_CPU_THRESHOLD_PERCENT%%%
echo Response time threshold: %PERF_RESPONSE_TIME_THRESHOLD_MS%ms
echo.

REM Parse command line arguments
set CATEGORIES=all
set SAVE_REPORT=true
set VERBOSE=false

if "%1"=="--help" goto :help
if "%1"=="-h" goto :help
if "%1"=="help" goto :help

if not "%1"=="" set CATEGORIES=%1
if "%2"=="--no-report" set SAVE_REPORT=false
if "%2"=="--verbose" set VERBOSE=true
if "%3"=="--verbose" set VERBOSE=true

echo Running performance tests for categories: %CATEGORIES%
echo.

REM Check if CrewAI server is running (for API tests)
if "%CATEGORIES%"=="all" (
    echo Checking if CrewAI server is running...
    curl -s http://localhost:5051/health >nul 2>&1
    if errorlevel 1 (
        echo WARNING: CrewAI server not running on port 5051
        echo API performance tests may fail
        echo Start the server with: start_crewai_server.bat
        echo.
    ) else (
        echo CrewAI server is running - API tests will be included
        echo.
    )
)

REM Run performance tests based on category
if "%CATEGORIES%"=="all" (
    echo Running complete performance test suite...
    python tests/performance/test_runner_performance.py
) else (
    echo Running performance tests for specific categories: %CATEGORIES%
    python tests/performance/test_runner_performance.py %CATEGORIES%
)

set TEST_EXIT_CODE=%errorlevel%

echo.
echo ========================================
echo Performance Test Execution Complete
echo ========================================

if %TEST_EXIT_CODE% equ 0 (
    echo Status: SUCCESS - All performance tests passed
    echo.
    echo Performance reports have been generated in the current directory
    echo Look for files matching: performance_report_*.json
) else (
    echo Status: FAILED - Some performance tests failed
    echo Exit code: %TEST_EXIT_CODE%
    echo.
    echo Check the output above for details on failed tests
    echo Review performance thresholds if tests are failing due to system limitations
)

echo.
echo Available performance test categories:
echo   api     - API endpoint benchmarks
echo   memory  - Memory system performance
echo   ui      - UI responsiveness tests
echo   system  - System resource monitoring
echo.
echo Usage examples:
echo   %0                    - Run all performance tests
echo   %0 api               - Run only API performance tests
echo   %0 api,memory        - Run API and memory tests
echo   %0 system --verbose  - Run system tests with verbose output
echo.

if "%VERBOSE%"=="true" (
    echo Detailed test results are available above
    echo Check performance_report_*.json for comprehensive metrics
)

pause
exit /b %TEST_EXIT_CODE%

:help
echo.
echo GopiAI Performance Test Suite
echo.
echo Usage: %0 [categories] [options]
echo.
echo Categories:
echo   all      - Run all performance test categories (default)
echo   api      - API endpoint benchmarks
echo   memory   - Memory system performance tests
echo   ui       - UI responsiveness tests
echo   system   - System resource monitoring tests
echo.
echo You can specify multiple categories separated by commas:
echo   %0 api,memory
echo.
echo Options:
echo   --no-report  - Don't save performance report to file
echo   --verbose    - Show detailed test output
echo   --help, -h   - Show this help message
echo.
echo Examples:
echo   %0                           - Run all tests
echo   %0 api                       - Run only API tests
echo   %0 memory,system --verbose   - Run memory and system tests with details
echo   %0 ui --no-report           - Run UI tests without saving report
echo.
echo Environment Variables:
echo   PERF_MEMORY_THRESHOLD_MB     - Memory usage threshold (default: 500)
echo   PERF_CPU_THRESHOLD_PERCENT   - CPU usage threshold (default: 80)
echo   PERF_RESPONSE_TIME_THRESHOLD_MS - Response time threshold (default: 5000)
echo.
pause
exit /b 0