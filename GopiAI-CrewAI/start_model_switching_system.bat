@echo off
REM Скрипт запуска системы переключения провайдеров LLM для Windows
REM Запуск REST API сервера и подготовка к работе UI

echo 🌟 Система переключения провайдеров LLM для GopiAI
echo ====================================================

REM Проверяем наличие Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден. Установите Python 3.8 или выше.
    pause
    exit /b 1
)

REM Переходим в директорию скрипта
cd /d "%~dp0"

REM Создаем директорию для состояния если её нет
if not exist "%USERPROFILE%\.gopiai" (
    mkdir "%USERPROFILE%\.gopiai"
    echo 📁 Создана директория состояния: %USERPROFILE%\.gopiai
)

REM Запускаем тесты
echo 🧪 Запуск проверки системы...
python run_all_tests.py
if %errorlevel% neq 0 (
    echo ❌ Система не прошла проверку. Запуск отменен.
    pause
    exit /b 1
)

echo.
echo 🚀 Запуск REST API сервера...
echo ====================================

REM Запускаем сервер в новом окне
start "GopiAI REST API Server" /D "%CD%" python crewai_api_server.py

echo ✅ REST API сервер запущен (порт 5051)
echo.
echo 🎨 Система готова к работе!
echo    - REST API сервер: http://localhost:5051
echo    - Для запуска UI используйте соответствующий скрипт
echo    - Для остановки сервера закройте окно сервера
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
