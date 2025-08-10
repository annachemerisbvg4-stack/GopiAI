@echo off
REM Automated Test Runner Batch Script for Windows CI/CD
REM Supports different environments and test types

setlocal enabledelayedexpansion

REM Default values
set ENVIRONMENT=development
set TEST_TYPES=
set CONFIG_FILE=
set OUTPUT_DIR=
set VERBOSE=false

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :run_tests
if "%~1"=="--environment" (
    set ENVIRONMENT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-e" (
    set ENVIRONMENT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--test-types" (
    set TEST_TYPES=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-t" (
    set TEST_TYPES=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--config" (
    set CONFIG_FILE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-c" (
    set CONFIG_FILE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--output" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-o" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--verbose" (
    set VERBOSE=true
    shift
    goto :parse_args
)
if "%~1"=="--help" (
    goto :show_help
)
shift
goto :parse_args

:run_tests
echo ========================================
echo GopiAI Automated Test Runner
echo ========================================
echo Environment: %ENVIRONMENT%
echo Test Types: %TEST_TYPES%
echo Timestamp: %date% %time%
echo ========================================

REM Create necessary directories
if not exist "ci_cd\logs" mkdir "ci_cd\logs"
if not exist "ci_cd\reports" mkdir "ci_cd\reports"
if not exist "ci_cd\artifacts" mkdir "ci_cd\artifacts"

REM Set log file
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set LOG_FILE=ci_cd\logs\automated_tests_%TIMESTAMP%.log

echo Starting automated test execution... | tee %LOG_FILE%

REM Check Python availability
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not available in PATH | tee -a %LOG_FILE%
    exit /b 1
)

REM Build command
set PYTHON_CMD=python ci_cd\automated_test_runner.py --environment %ENVIRONMENT%

if not "%TEST_TYPES%"=="" (
    set PYTHON_CMD=%PYTHON_CMD% --test-types %TEST_TYPES%
)

if not "%CONFIG_FILE%"=="" (
    set PYTHON_CMD=%PYTHON_CMD% --config "%CONFIG_FILE%"
)

if not "%OUTPUT_DIR%"=="" (
    set PYTHON_CMD=%PYTHON_CMD% --output "%OUTPUT_DIR%"
)

REM Execute tests
echo Executing: %PYTHON_CMD% | tee -a %LOG_FILE%
echo. | tee -a %LOG_FILE%

if "%VERBOSE%"=="true" (
    %PYTHON_CMD% 2>&1 | tee -a %LOG_FILE%
) else (
    %PYTHON_CMD% >> %LOG_FILE% 2>&1
)

set EXIT_CODE=%errorlevel%

REM Show results
echo. | tee -a %LOG_FILE%
echo ======================================== | tee -a %LOG_FILE%
echo Test execution completed with exit code: %EXIT_CODE% | tee -a %LOG_FILE%
echo Log file: %LOG_FILE% | tee -a %LOG_FILE%

REM Show last execution result if available
if exist "ci_cd\last_execution_result.json" (
    echo. | tee -a %LOG_FILE%
    echo Last execution summary: | tee -a %LOG_FILE%
    type "ci_cd\last_execution_result.json" | tee -a %LOG_FILE%
)

echo ======================================== | tee -a %LOG_FILE%

REM Archive artifacts if tests passed
if %EXIT_CODE%==0 (
    call :archive_artifacts
)

exit /b %EXIT_CODE%

:archive_artifacts
echo Archiving test artifacts...
set ARCHIVE_DIR=ci_cd\artifacts\%TIMESTAMP%
if not exist "%ARCHIVE_DIR%" mkdir "%ARCHIVE_DIR%"

REM Copy reports
if exist "ci_cd\reports" (
    xcopy "ci_cd\reports\*" "%ARCHIVE_DIR%\reports\" /E /I /Q >nul 2>&1
)

REM Copy logs
copy "%LOG_FILE%" "%ARCHIVE_DIR%\" >nul 2>&1

REM Copy coverage files
if exist ".coverage" copy ".coverage" "%ARCHIVE_DIR%\" >nul 2>&1

echo Artifacts archived to: %ARCHIVE_DIR%
goto :eof

:show_help
echo GopiAI Automated Test Runner
echo.
echo Usage: run_automated_tests.bat [OPTIONS]
echo.
echo Options:
echo   --environment, -e    Target environment (development, staging, production)
echo   --test-types, -t     Test types to run (unit, integration, ui, e2e, performance, security)
echo   --config, -c         Configuration file path
echo   --output, -o         Output directory for reports
echo   --verbose            Show verbose output
echo   --help               Show this help message
echo.
echo Examples:
echo   run_automated_tests.bat --environment staging --test-types "unit integration"
echo   run_automated_tests.bat -e production -t "unit integration ui e2e"
echo   run_automated_tests.bat --config ci_cd\config\production.json --verbose
echo.
exit /b 0

endlocal