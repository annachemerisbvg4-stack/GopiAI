@echo off
chcp 65001 > nul

echo ======================================================
echo    Тестирование интеграции CrewAI с чатом
echo ======================================================
echo.

:: Проверяем наличие окружения
if not exist crewai_env (
    echo [ОШИБКА] Окружение CrewAI не найдено!
    echo Сначала запустите run_crewai_api_server.bat для создания окружения.
    pause
    exit /b 1
)

:: Активируем окружение CrewAI
echo [1/2] Активация окружения CrewAI...
call crewai_env\Scripts\activate.bat

:: Проверяем, что окружение активировано
if errorlevel 1 (
    echo [ОШИБКА] Не удалось активировать окружение CrewAI!
    pause
    exit /b 1
)

:: Запускаем тестирование
echo [2/2] Запуск тестирования интеграции...
echo.

python test_chat_integration.py

:: В случае ошибки
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось выполнить тестирование!
    echo Проверьте, запущен ли API сервер (run_crewai_api_server.bat).
    pause
)

pause