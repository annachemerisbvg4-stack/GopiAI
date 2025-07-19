@echo off

REM Setting UTF-8 encoding
chcp 65001 >nul

echo.
echo ===============================================
echo     GOPI_AI System - Starting all components
echo ===============================================
echo.

REM Loading Smithery MCP environment variables
IF EXIST "%~dp0smithery_env.bat" (
    echo [INFO] Loading Smithery API settings...
    call "%~dp0smithery_env.bat"
) ELSE (
    echo [WARNING] Smithery API settings not found
    echo    Create smithery_env.bat with your API key to enable MCP tools
)

REM Setting paths to virtual environments
set "CREWAI_VENV=C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\crewai_env"
set "UI_VENV=C:\Users\crazy\GOPI_AI_MODULES\gopiai_env"
set "TXTAI_VENV=C:\Users\crazy\GOPI_AI_MODULES\txtai_env"

REM Checking environments
echo [INFO] Checking virtual environments...
if exist "%CREWAI_VENV%\Scripts\activate.bat" (
    echo [OK] CrewAI environment found: %CREWAI_VENV%
) else (
    echo [WARNING] CrewAI environment not found at %CREWAI_VENV%
    echo    Using global Python for CrewAI
)

if exist "%UI_VENV%\Scripts\activate.bat" (
    echo [OK] UI environment found: %UI_VENV%
) else (
    echo [WARNING] UI environment not found at %UI_VENV%
    echo    Using gopiai_env for UI
    set "UI_VENV=%gopiai_env%"
)

if exist "%TXTAI_VENV%\Scripts\activate.bat" (
    echo [OK] TXTAI environment found: %TXTAI_VENV%
) else (
    echo [WARNING] TXTAI environment not found at %TXTAI_VENV%
    echo    Using gopiai_env for TXTAI
    set "TXTAI_VENV=%gopiai_env%"
)

REM Creating necessary directories for memory if they don't exist
echo [INFO] Checking and creating memory directories...
if not exist "C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\memory" (
    echo [INFO] Creating memory directory...
    mkdir "C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\memory"
)

if not exist "C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\memory\vectors" (
    echo [INFO] Creating vector indices directory...
    mkdir "C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\memory\vectors"
)

if not exist "C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\memory\chats.json" (
    echo [INFO] Creating chats.json file...
    echo {} > "C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\memory\chats.json"
)

echo.
echo [INFO] Starting deployment sequence...
echo.

REM Step 1: Start CrewAI API Server with extended logging
echo [STEP 1] Starting CrewAI API Server...
if exist "%CREWAI_VENV%\Scripts\activate.bat" (
    start "CrewAI API Server" cmd /k "title CrewAI API Server && color 0A && cd /d C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI && echo. && echo ======================================== && echo    CrewAI API Server Environment && echo ======================================== && echo. && echo [INFO] Activating CrewAI environment... && call %CREWAI_VENV%\Scripts\activate.bat && echo [OK] Environment activated && echo [INFO] Directory: GopiAI-CrewAI && echo [INFO] Environment: %CREWAI_VENV% && echo. && echo [INFO] Starting CrewAI API Server on port 5051... && echo [DIAGNOSTIC] Starting server with extended logging... && set FLASK_DEBUG=1 && python crewai_api_server.py --port 5051 --debug > crewai_api_server_debug.log 2>&1"
) else (
    start "CrewAI API Server" cmd /k "title CrewAI API Server && color 0A && cd /d C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI && echo. && echo ======================================== && echo    CrewAI API Server Environment && echo ======================================== && echo. && echo [WARNING] Using global Python environment && echo [INFO] Directory: GopiAI-CrewAI && echo. && echo [INFO] Starting CrewAI API Server on port 5051... && echo [DIAGNOSTIC] Starting server with extended logging... && set FLASK_DEBUG=1 && python crewai_api_server.py --port 5051 --debug > crewai_api_server_debug.log 2>&1"
)

echo Waiting for CrewAI server to start (30 seconds)...
echo    Initializing server...

REM Step 2: Activate TXTAI environment for vector memory
timeout /t 210 >nul

REM Step 2: Activate TXTAI environment for vector memory
echo.
echo [STEP 2] Activating TXTAI environment for vector memory...
if exist "%TXTAI_VENV%\Scripts\activate.bat" (
    start "TXTAI API Server" cmd /k "title TXTAI API Server && color 09 && cd /d C:\Users\crazy\GOPI_AI_MODULES\txtai_env && echo. && echo ======================================== && echo    TXTAI API Server Environment && echo ======================================== && echo. && echo [INFO] Activating TXTAI environment... && call %TXTAI_VENV%\Scripts\activate.bat && echo [OK] Environment activated && echo [INFO] Directory: txtai_env && echo [INFO] Environment: %TXTAI_VENV% && echo. && echo [OK] TXTAI environment ready for vector memory"
) else (
    start "TXTAI API Server" cmd /k "title TXTAI API Server && color 09 && cd /d C:\Users\crazy\GOPI_AI_MODULES\txtai_env && echo. && echo ======================================== && echo    TXTAI API Server Environment && echo ======================================== && echo. && echo [WARNING] Using global Python environment && echo [INFO] Directory: txtai_env && echo. && echo [OK] TXTAI environment ready for vector memory"
)

echo [INFO] Waiting for TXTAI environment activation (5 seconds)...
timeout /t 5 >nul

REM Step 3: Start GopiAI-UI with correct memory settings
echo.
echo [STEP 3] Starting GopiAI-UI...
if exist "%UI_VENV%\Scripts\activate.bat" (
    start "GopiAI-UI" cmd /k "title GopiAI-UI Application && color 0E && cd /d C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI && echo. && echo ======================================== && echo    GopiAI-UI Application && echo ======================================== && echo. && echo [INFO] Activating UI environment... && call %UI_VENV%\Scripts\activate.bat && echo [OK] Environment activated && echo [INFO] Directory: GopiAI-UI && echo [INFO] Environment: %UI_VENV% && echo. && echo [INFO] Starting GopiAI-UI Application... && set MEMORY_ENABLED=1 && set CREWAI_API_URL=http://127.0.0.1:5051 && python gopiai\ui\main.py"
) else (
    start "GopiAI-UI" cmd /k "title GopiAI-UI Application && color 0E && cd /d C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI && echo. && echo ======================================== && echo    GopiAI-UI Application && echo ======================================== && echo. && echo [WARNING] Using global Python environment && echo [INFO] Directory: GopiAI-UI && echo. && echo [INFO] Starting GopiAI-UI Application... && set MEMORY_ENABLED=1 && set CREWAI_API_URL=http://127.0.0.1:5051 && python gopiai\ui\main.py"
)

echo.
echo [INFO] All applications started successfully!
echo.
echo [INFO] What's running:
echo    CrewAI API Server: crewai_api_server.py (Green terminal)
echo    TXTAI Environment: Activated txtai_env environment (Blue terminal)
echo    GopiAI-UI App: gopiai\ui\main.py (Yellow terminal)
echo.
echo [INFO] Control commands:
echo    * Use Ctrl+C in any terminal to stop the corresponding service
echo    * Close terminal windows to stop applications
echo    * Restart any service independently if needed
echo.
echo [INFO] Development environment ready!
echo    All services should be running in their respective environments.
echo.
pause
