@echo off
echo Installing missing dependencies for GopiAI-CrewAI...
echo.

REM Активируем окружение CrewAI если оно существует
set "CREWAI_VENV=C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\crewai_env"
if exist "%CREWAI_VENV%\Scripts\activate.bat" (
    echo Activating CrewAI environment...
    call "%CREWAI_VENV%\Scripts\activate.bat"
) else (
    echo Using global Python environment...
)

echo.
echo Installing txtai with FAISS support...
pip install "txtai[faiss]>=8.2.0"

echo.
echo Installing CrewAI and related packages...
pip install crewai crewai-tools

echo.
echo Installing MCP dependencies...
pip install mcp

echo.
echo Upgrading existing packages...
pip install --upgrade -r requirements.txt

echo.
echo ✅ Dependencies installation completed!
pause