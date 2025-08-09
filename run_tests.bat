@echo off
REM GopiAI Test Runner Batch Script
REM Provides easy access to the comprehensive testing system

setlocal enabledelayedexpansion

echo.
echo ========================================
echo GopiAI Comprehensive Testing System
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not available in PATH
    echo Please ensure Python is installed and added to PATH
    pause
    exit /b 1
)

REM Check if run_tests.py exists
if not exist "run_tests.py" (
    echo ERROR: run_tests.py not found
    echo Please ensure you are running this from the GopiAI root directory
    pause
    exit /b 1
)

REM Parse command line arguments
set "ARGS="
set "SHOW_HELP=0"

:parse_args
if "%~1"=="" goto :run_tests
if "%~1"=="--help" set "SHOW_HELP=1"
if "%~1"=="-h" set "SHOW_HELP=1"
if "%~1"=="help" set "SHOW_HELP=1"
if "%~1"=="?" set "SHOW_HELP=1"

set "ARGS=%ARGS% %~1"
shift
goto :parse_args

:run_tests
if "%SHOW_HELP%"=="1" (
    echo Usage: run_tests.bat [options]
    echo.
    echo Test Categories:
    echo   --all              Run all tests
    echo   --unit             Run unit tests only
    echo   --integration      Run integration tests only
    echo   --ui               Run UI tests only
    echo   --e2e              Run end-to-end tests only
    echo   --performance      Run performance tests only
    echo   --security         Run security tests only
    echo.
    echo Environment Options:
    echo   --env crewai_env   Run tests in CrewAI environment
    echo   --env gopiai_env   Run tests in GopiAI environment
    echo   --env txtai_env    Run tests in txtai environment
    echo.
    echo Module Options:
    echo   --module GopiAI-Core     Run tests for GopiAI-Core
    echo   --module GopiAI-UI       Run tests for GopiAI-UI
    echo   --module GopiAI-CrewAI   Run tests for GopiAI-CrewAI
    echo   --module GopiAI-Assets   Run tests for GopiAI-Assets
    echo.
    echo Execution Options:
    echo   --parallel         Run tests in parallel
    echo   --no-reports       Skip report generation
    echo   --timeout N        Set timeout in seconds
    echo.
    echo Discovery Options:
    echo   --discover-problems    Run problem discovery only
    echo   --discover-tests       Run test discovery only
    echo.
    echo Output Options:
    echo   --verbose, -v      Verbose output
    echo   --quiet, -q        Quiet output
    echo.
    echo Examples:
    echo   run_tests.bat --all
    echo   run_tests.bat --unit --parallel
    echo   run_tests.bat --integration --env crewai_env
    echo   run_tests.bat --discover-problems
    echo.
    pause
    exit /b 0
)

REM If no arguments provided, show interactive menu
if "%ARGS%"==" " (
    echo No arguments provided. Choose an option:
    echo.
    echo 1. Run all tests
    echo 2. Run unit tests only
    echo 3. Run integration tests only
    echo 4. Run UI tests only
    echo 5. Run problem discovery
    echo 6. Run test discovery
    echo 7. Show help
    echo 8. Exit
    echo.
    set /p "choice=Enter your choice (1-8): "
    
    if "!choice!"=="1" set "ARGS= --all"
    if "!choice!"=="2" set "ARGS= --unit"
    if "!choice!"=="3" set "ARGS= --integration"
    if "!choice!"=="4" set "ARGS= --ui"
    if "!choice!"=="5" set "ARGS= --discover-problems"
    if "!choice!"=="6" set "ARGS= --discover-tests"
    if "!choice!"=="7" set "ARGS= --help"
    if "!choice!"=="8" exit /b 0
    
    if "!ARGS!"==" " (
        echo Invalid choice. Exiting.
        pause
        exit /b 1
    )
)

echo Running: python run_tests.py%ARGS%
echo.

REM Execute the test runner
python run_tests.py%ARGS%
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if %EXIT_CODE% equ 0 (
    echo ✓ Test execution completed successfully
) else (
    echo ✗ Test execution failed with exit code %EXIT_CODE%
)

echo.
echo Press any key to exit...
pause >nul

exit /b %EXIT_CODE%