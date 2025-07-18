@echo off
echo === Исправление проблемы с кратковременной памятью ИИ ===
echo.

REM Проверяем наличие Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python не найден! Пожалуйста, установите Python и добавьте его в PATH.
    goto :end
)

REM Запускаем скрипт исправления
python apply_memory_fix.py
if %ERRORLEVEL% NEQ 0 (
    echo Произошла ошибка при выполнении скрипта.
    goto :end
)

echo.
echo Для применения изменений перезапустите приложение.
echo.

:end
pause