@echo off
REM Generate comprehensive test documentation for GopiAI

echo Generating test documentation...
echo.

REM Generate main documentation
python test_infrastructure/test_documentation_generator.py --output 02_DOCUMENTATION/TEST_SUITE_DOCUMENTATION.md

REM Generate JSON report for programmatic access
python test_infrastructure/test_documentation_generator.py --json test_documentation_report.json

echo.
echo Documentation generation complete!
echo.
echo Generated files:
echo - 02_DOCUMENTATION/TEST_SUITE_DOCUMENTATION.md
echo - test_documentation_report.json
echo.
echo Additional guides available:
echo - 02_DOCUMENTATION/TESTING_SYSTEM_GUIDE.md
echo - 02_DOCUMENTATION/ADDING_NEW_TESTS_GUIDE.md  
echo - 02_DOCUMENTATION/TEST_TROUBLESHOOTING_GUIDE.md
echo.
pause