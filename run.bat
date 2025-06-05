@echo off
echo Starting GopiAI Application...
echo ===============================

REM Переходим в папку UI где находится main.py
cd /d "%~dp0UI"

REM Проверяем существование main.py
if not exist "main.py" (
    echo ERROR: main.py not found in UI folder!
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