@echo off
echo Starting GopiAI Application...
echo ===============================

REM Переходим в папку с модульным UI
cd /d "%~dp0GopiAI-UI\gopiai\ui"

REM Проверяем существование main.py
if not exist "main.py" (
    echo ERROR: main.py not found in GopiAI-UI\gopiai\ui folder!
    pause
    exit /b 1
)

REM Запускаем приложение
echo Starting UI application...
python main.py

REM Если произошла ошибка
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Application failed to start!
    echo Error code: %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Application finished successfully.
pause