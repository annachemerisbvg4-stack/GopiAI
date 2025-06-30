@echo off
echo ===================================================================
echo RAG and CrewAI Integration Testing
echo ===================================================================
echo.
echo This script provides options for testing RAG and CrewAI integration.
echo Make sure you have the required services running before testing.
echo.
echo Test Matrix:
echo ^| RAG ^| CrewAI ^| Expected ^|
echo ^| --- ^| ---    ^| ---      ^|
echo ^| off ^| on     ^| Fast response (≤15 s), no freeze ^|
echo ^| on  ^| on     ^| Response with RAG context, no freeze ^|
echo ^| off ^| off    ^| Graceful fallback, UI warns, no freeze ^|
echo.

:MENU
echo ===================================================================
echo TEST OPTIONS
echo ===================================================================
echo 1. Run Manual Test Script (Interactive)
echo 2. Run Automated Test Matrix
echo 3. Check Service Status Only
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto MANUAL_TEST
if "%choice%"=="2" goto AUTO_TEST
if "%choice%"=="3" goto CHECK_STATUS
if "%choice%"=="4" goto EXIT
echo Invalid choice. Please try again.
goto MENU

:MANUAL_TEST
echo.
echo Starting Manual Test Script...
echo This will open an interactive menu for testing different configurations.
echo.
python manual_rag_crewai_test.py
pause
goto MENU

:AUTO_TEST
echo.
echo Starting Automated Test Matrix...
echo This will automatically test all configurations (requires service management).
echo.
python test_rag_crewai_matrix.py
pause
goto MENU

:CHECK_STATUS
echo.
echo Checking Service Status...
echo.
python -c "
import requests
try:
    response = requests.get('http://127.0.0.1:5050/api/health', timeout=3)
    print('CrewAI (port 5050): Running' if response.status_code == 200 else 'CrewAI (port 5050): Not responding')
except:
    print('CrewAI (port 5050): Not running')

try:
    response = requests.get('http://127.0.0.1:5051/api/health', timeout=3)
    print('RAG (port 5051): Running' if response.status_code == 200 else 'RAG (port 5051): Not responding')
except:
    print('RAG (port 5051): Not running')
"
echo.
pause
goto MENU

:EXIT
echo.
echo Exiting test script.
echo Thank you for using the RAG and CrewAI test suite!
exit /b 0
