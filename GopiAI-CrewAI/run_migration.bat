@echo off
REM Скрипт запуска руководства по миграции для Windows

echo 🌟 Руководство по миграции на улучшенную систему переключения провайдеров LLM
echo ==============================================================================

REM Проверяем наличие Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден. Установите Python 3.8 или выше.
    pause
    exit /b 1
)

REM Переходим в директорию скрипта
cd /d "%~dp0"

echo 🚀 Запуск руководства по миграции...
echo.

python migration_guide.py

echo.
echo Нажмите любую клавишу для выхода...
pause >nul
