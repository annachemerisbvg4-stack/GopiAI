@echo off
chcp 65001 > nul

python "%~dp0start_crewai_server.py"

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start CrewAI API server!
    echo Check the console for errors.
    pause
)