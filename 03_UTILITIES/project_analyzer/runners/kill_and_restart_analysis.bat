@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════
echo     🛑 Остановка текущего анализа и перезапуск
echo ═══════════════════════════════════════════════════════
echo.

echo 🔍 Поиск запущенных процессов Python...
tasklist | findstr python >nul
if %ERRORLEVEL% EQU 0 (
    echo 🛑 Найдены запущенные Python процессы. Останавливаем...
    taskkill /f /im python.exe /t >nul 2>&1
    echo ✅ Процессы остановлены
) else (
    echo ℹ️  Запущенные Python процессы не найдены
)

timeout /t 3 /nobreak >nul

echo.
echo 🚀 Запуск быстрого анализа...
echo.
'c:/Users/crazy/GOPI_AI_MODULES/03_UTILITIES/project_analyzer/runners/analyze_gopi_project_quick.bat'

echo.
echo Нажмите любую клавишу для выхода...
pause > nul
