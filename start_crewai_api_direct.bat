@echo off
echo Starting CrewAI API server with system Python...
echo Current directory: %CD%

REM Change to CrewAI directory
cd GopiAI-CrewAI
echo Changed to directory: %CD%

REM Run CrewAI API server
python crewai_api_server.py

pause
