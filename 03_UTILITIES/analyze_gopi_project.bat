@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════
echo     🔍 GopiAI Project Analyzer
echo ═══════════════════════════════════════════════════════
echo.

REM Проверяем, что мы находимся в правильной директории
if not exist "project_cleanup_cli.py" (
    echo ❌ Ошибка: Запустите этот скрипт из директории 03_UTILITIES
    echo.
    pause
    exit /b 1
)

REM Активируем окружение Python, если оно доступно
if exist "..\gopiai_env\Scripts\activate.bat" (
    echo 🔄 Активация окружения gopiai_env...
    call ..\gopiai_env\Scripts\activate.bat
) else (
    echo ℹ️ Окружение gopiai_env не найдено, используем системный Python
)

echo.
echo 🔍 Запуск анализа проекта GopiAI...
echo.

REM Запускаем скрипт анализа
python analyze_project.py

REM Проверяем результат выполнения
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Анализ успешно завершен!
) else (
    echo.
    echo ❌ Анализ завершился с ошибкой (код %ERRORLEVEL%)
)

REM Деактивируем окружение, если оно было активировано
if exist "..\gopiai_env\Scripts\activate.bat" (
    call deactivate
)

echo.
echo Нажмите любую клавишу для выхода...
pause > nul