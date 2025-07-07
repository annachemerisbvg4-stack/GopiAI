@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════
echo     🚀 GOPI_AI Auto Development Launcher
echo ═══════════════════════════════════════════════════════
echo.

REM Настройка путей к виртуальным окружениям
set "CREWAI_VENV=C:\Users\crazy\GOPI_AI_MODULES\rag_memory_env"
set "UI_VENV=C:\Users\crazy\GOPI_AI_MODULES\rag_memory_env"

REM Проверяем окружения
echo 🔍 Checking virtual environments...
if exist "%CREWAI_VENV%\Scripts\activate.bat" (
    echo ✅ CrewAI environment found: %CREWAI_VENV%
) else (
    echo ⚠️  CrewAI environment not found at %CREWAI_VENV%
    echo    Using global Python for CrewAI
)

if exist "%UI_VENV%\Scripts\activate.bat" (
    echo ✅ UI environment found: %UI_VENV%
) else (
    echo ⚠️  UI environment not found at %UI_VENV%
    echo    Using rag_memory_env for UI
    set "UI_VENV=%CREWAI_VENV%"
)

echo.
echo 🚀 Starting development sequence...
echo.

REM Шаг 1: Запускаем CrewAI API Server
echo 1️⃣  Launching CrewAI API Server...
if exist "%CREWAI_VENV%\Scripts\activate.bat" (
    start "🤖 CrewAI API Server" cmd /k "title 🤖 CrewAI API Server && color 0A && cd /d C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI && echo. && echo ═══════════════════════════════════════ && echo    🤖 CrewAI API Server Environment && echo ═══════════════════════════════════════ && echo. && echo 🔄 Activating CrewAI environment... && call %CREWAI_VENV%\Scripts\activate.bat && echo ✅ Environment activated && echo 📂 Directory: GopiAI-CrewAI && echo 🐍 Environment: %CREWAI_VENV% && echo. && echo 🚀 Starting CrewAI API Server... && python crewai_api_server.py"
) else (
    start "🤖 CrewAI API Server" cmd /k "title 🤖 CrewAI API Server && color 0A && cd /d C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI && echo. && echo ═══════════════════════════════════════ && echo    🤖 CrewAI API Server Environment && echo ═══════════════════════════════════════ && echo. && echo ⚠️  Using global Python environment && echo 📂 Directory: GopiAI-CrewAI && echo. && echo 🚀 Starting CrewAI API Server... && python crewai_api_server.py"
)

echo ⏳ Waiting for CrewAI server to start (10 seconds)...
echo    🔄 Server initialization in progress...

REM Ждем 10 секунд для запуска CrewAI сервера
timeout /t 10 >nul

echo.
echo 2️⃣  Launching GopiAI-UI...

REM Шаг 2: Запускаем GopiAI-UI
if exist "%UI_VENV%\Scripts\activate.bat" (
    start "🖥️ GopiAI-UI" cmd /k "title 🖥️ GopiAI-UI Application && color 0E && cd /d C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI && echo. && echo ═══════════════════════════════════════ && echo    🖥️ GopiAI-UI Application && echo ═══════════════════════════════════════ && echo. && echo 🔄 Activating UI environment... && call %UI_VENV%\Scripts\activate.bat && echo ✅ Environment activated && echo 📂 Directory: GopiAI-UI && echo 🐍 Environment: %UI_VENV% && echo. && echo 🚀 Starting GopiAI-UI Application... && python gopiai\ui\main.py"
) else (
    start "🖥️ GopiAI-UI" cmd /k "title 🖥️ GopiAI-UI Application && color 0E && cd /d C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI && echo. && echo ═══════════════════════════════════════ && echo    🖥️ GopiAI-UI Application && echo ═══════════════════════════════════════ && echo. && echo ⚠️  Using global Python environment && echo 📂 Directory: GopiAI-UI && echo. && echo 🚀 Starting GopiAI-UI Application... && python gopiai\ui\main.py"
)

echo.
echo ✅ Both applications launched successfully!
echo.
echo 📋 What's Running:
echo    🤖 CrewAI API Server: crewai_api_server.py (Green Terminal)
echo    🖥️ GopiAI-UI App: gopiai\ui\main.py (Yellow Terminal)
echo.
echo 🔧 Control Commands:
echo    • Use Ctrl+C in any terminal to stop that service
echo    • Close terminal windows to stop applications
echo    • Restart either service independently as needed
echo.
echo 🎯 Development environment is ready, Анютка! 😊
echo    Both services should be running in their respective environments.
echo.
pause
