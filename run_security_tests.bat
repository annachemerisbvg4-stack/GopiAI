@echo off
REM Security test runner for GopiAI comprehensive testing system
REM Requirements: 7.1, 7.2, 7.3, 7.4

echo.
echo ========================================
echo   GopiAI Security Test Runner
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if pytest is available
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo Error: pytest is not installed
    echo Please install pytest: pip install pytest
    pause
    exit /b 1
)

REM Parse command line arguments
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=all

echo Running security tests: %COMMAND%
echo.

REM Run security tests based on command
if "%COMMAND%"=="api" (
    echo Running API Security Tests ^(Requirement 7.1^)...
    python tests/security/test_runner_security.py api
) else if "%COMMAND%"=="secrets" (
    echo Running Secret Management Tests ^(Requirement 7.2^)...
    python tests/security/test_runner_security.py secrets
) else if "%COMMAND%"=="auth" (
    echo Running Authentication Security Tests ^(Requirement 7.3^)...
    python tests/security/test_runner_security.py auth
) else if "%COMMAND%"=="files" (
    echo Running File System Security Tests ^(Requirement 7.4^)...
    python tests/security/test_runner_security.py files
) else if "%COMMAND%"=="all" (
    echo Running All Security Tests...
    python tests/security/test_runner_security.py all
) else if "%COMMAND%"=="quick" (
    echo Running Quick Security Scan...
    python -m pytest tests/security/ -v -m security --tb=short
) else if "%COMMAND%"=="coverage" (
    echo Running Security Tests with Coverage...
    python -m pytest tests/security/ -v -m security --cov=gopiai --cov-report=html --cov-report=term
) else if "%COMMAND%"=="help" (
    goto :show_help
) else (
    echo Unknown command: %COMMAND%
    goto :show_help
)

echo.
echo Security tests completed.
echo Check security_report.json for detailed results.
echo.

if errorlevel 1 (
    echo.
    echo ⚠️  SECURITY ISSUES DETECTED!
    echo Please review and fix security vulnerabilities before deployment.
    echo.
) else (
    echo.
    echo ✅ All security tests passed!
    echo.
)

goto :end

:show_help
echo.
echo Usage: run_security_tests.bat [command]
echo.
echo Commands:
echo   api       - Run API security tests ^(Requirement 7.1^)
echo   secrets   - Run secret management tests ^(Requirement 7.2^)
echo   auth      - Run authentication security tests ^(Requirement 7.3^)
echo   files     - Run file system security tests ^(Requirement 7.4^)
echo   all       - Run all security tests ^(default^)
echo   quick     - Run quick security scan
echo   coverage  - Run tests with coverage report
echo   help      - Show this help message
echo.
echo Examples:
echo   run_security_tests.bat
echo   run_security_tests.bat api
echo   run_security_tests.bat all
echo   run_security_tests.bat coverage
echo.

:end
pause