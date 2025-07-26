@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════
echo     🔍 GopiAI Project Analyzer - Быстрый режим
echo ═══════════════════════════════════════════════════════
echo.

REM Получаем путь к директории, где находится этот скрипт
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Проверяем, что project_cleanup_cli.py существует в родительской директории скрипта
if not exist "%SCRIPT_DIR%\..\..\project_cleanup_cli.py" (
    echo ❌ Ошибка: Не найден файл project_cleanup_cli.py в родительской директории
    echo.
    pause
    exit /b 1
)

REM Активируем окружение Python, если оно доступно
if exist "%SCRIPT_DIR%\..\gopiai_env\Scripts\activate.bat" (
    echo 🔄 Активация окружения gopiai_env...
    call "%SCRIPT_DIR%\..\gopiai_env\Scripts\activate.bat"
) else (
    echo ℹ️ Окружение gopiai_env не найдено, используем системный Python
)

echo.
echo 🔍 Запуск БЫСТРОГО анализа проекта GopiAI...
echo.

REM Запускаем скрипт анализа из правильной директории
pushd "%SCRIPT_DIR%\..\.."
python analyze_project.py
popd

REM Проверяем результат выполнения
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Анализ успешно завершен!
) else (
    echo.
    echo ❌ Анализ завершился с ошибкой (код %ERRORLEVEL%)
)

echo.
echo Нажмите любую клавишу для выхода...
pause > nul
