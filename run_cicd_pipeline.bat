@echo off
REM Complete CI/CD Pipeline Runner for GopiAI
REM Provides easy access to the full CI/CD system

setlocal enabledelayedexpansion

REM Default values
set ENVIRONMENT=development
set VERSION=
set COMMIT_HASH=
set TEST_TYPES=
set FORCE_DEPLOY=false
set DRY_RUN=false

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :check_version
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
if "%~1"=="--version" (
    set VERSION=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-v" (
    set VERSION=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--commit-hash" (
    set COMMIT_HASH=%~2
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
if "%~1"=="--force-deploy" (
    set FORCE_DEPLOY=true
    shift
    goto :parse_args
)
if "%~1"=="--dry-run" (
    set DRY_RUN=true
    shift
    goto :parse_args
)
if "%~1"=="--help" (
    goto :show_help
)
shift
goto :parse_args

:check_version
if "%VERSION%"=="" (
    echo Error: Version is required
    echo Use --version or -v to specify version
    echo.
    goto :show_help
)

:run_pipeline
echo ========================================
echo GopiAI CI/CD Pipeline
echo ========================================
echo Environment: %ENVIRONMENT%
echo Version: %VERSION%
if not "%COMMIT_HASH%"=="" echo Commit Hash: %COMMIT_HASH%
if not "%TEST_TYPES%"=="" echo Test Types: %TEST_TYPES%
echo Force Deploy: %FORCE_DEPLOY%
echo Dry Run: %DRY_RUN%
echo Timestamp: %date% %time%
echo ========================================

REM Check Python availability
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not available in PATH
    exit /b 1
)

REM Build command
set PYTHON_CMD=python ci_cd\ci_cd_integration.py --environment %ENVIRONMENT% --version %VERSION%

if not "%COMMIT_HASH%"=="" (
    set PYTHON_CMD=%PYTHON_CMD% --commit-hash %COMMIT_HASH%
)

if not "%TEST_TYPES%"=="" (
    set PYTHON_CMD=%PYTHON_CMD% --test-types %TEST_TYPES%
)

if "%FORCE_DEPLOY%"=="true" (
    set PYTHON_CMD=%PYTHON_CMD% --force-deploy
)

if "%DRY_RUN%"=="true" (
    set PYTHON_CMD=%PYTHON_CMD% --dry-run
)

REM Execute pipeline
echo Executing: %PYTHON_CMD%
echo.

%PYTHON_CMD%

set EXIT_CODE=%errorlevel%

echo.
echo ========================================
echo Pipeline completed with exit code: %EXIT_CODE%
echo ========================================

REM Show results if available
if exist "ci_cd\pipeline_results\%ENVIRONMENT%_latest.json" (
    echo.
    echo Latest pipeline result:
    type "ci_cd\pipeline_results\%ENVIRONMENT%_latest.json"
)

exit /b %EXIT_CODE%

:show_help
echo GopiAI CI/CD Pipeline Runner
echo.
echo Usage: run_cicd_pipeline.bat [OPTIONS]
echo.
echo Required Options:
echo   --version, -v        Version to deploy (required)
echo.
echo Optional Options:
echo   --environment, -e    Target environment (development, staging, production)
echo                        Default: development
echo   --commit-hash        Git commit hash
echo   --test-types, -t     Test types to run (space-separated)
echo                        Options: unit integration ui e2e performance security
echo   --force-deploy       Force deployment even if auto-deploy is disabled
echo   --dry-run            Show what would be done without executing
echo   --help               Show this help message
echo.
echo Examples:
echo   run_cicd_pipeline.bat --version v1.2.3
echo   run_cicd_pipeline.bat --version v1.2.3 --environment staging
echo   run_cicd_pipeline.bat --version v1.2.3 --environment production --force-deploy
echo   run_cicd_pipeline.bat --version v1.2.3 --test-types "unit integration ui"
echo   run_cicd_pipeline.bat --version v1.2.3 --commit-hash abc123def --dry-run
echo.
exit /b 0

endlocal