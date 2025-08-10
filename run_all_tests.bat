@echo off
REM GopiAI Comprehensive Test Runner - Windows Batch Script
REM Single entry point for all test types with enhanced features

echo.
echo ================================================================================
echo GopiAI Comprehensive Test Runner
echo Single Entry Point for All Test Types
echo Features: Parallel Execution ^| Prioritization ^| Auto-Retry ^| Smart Reporting
echo ================================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not available in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

REM Check if test infrastructure exists
if not exist "test_infrastructure\master_test_runner.py" (
    echo ERROR: Test infrastructure not found
    echo Please ensure test_infrastructure directory exists
    pause
    exit /b 1
)

REM Run the Python test runner with all arguments passed through
python run_all_tests.py %*

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

REM Show completion message based on exit code
echo.
if %EXIT_CODE%==0 (
    echo ================================================================================
    echo SUCCESS: All tests completed successfully!
    echo ================================================================================
) else if %EXIT_CODE%==1 (
    echo ================================================================================
    echo WARNING: Some tests failed - check logs for details
    echo ================================================================================
) else if %EXIT_CODE%==130 (
    echo ================================================================================
    echo INFO: Test execution was interrupted by user
    echo ================================================================================
) else (
    echo ================================================================================
    echo ERROR: Test execution failed with code %EXIT_CODE%
    echo ================================================================================
)

REM Pause if running interactively (not from command line with arguments)
if "%~1"=="" (
    echo.
    echo Press any key to continue...
    pause >nul
)

exit /b %EXIT_CODE%