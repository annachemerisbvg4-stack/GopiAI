@echo off
echo ===============================================
echo    Очистка запущенных Python-серверов
echo ===============================================
echo.

echo 1. Поиск процессов Python, связанных с Flask-серверами...
wmic process where "commandline like '%%flask%%'" get processid,commandline
echo.

echo 2. Поиск процессов Python, связанных с CrewAI-серверами...
wmic process where "commandline like '%%crewai%%'" get processid,commandline
echo.

echo 3. Поиск всех процессов на порту 5051...
netstat -ano | findstr :5051
echo.

echo 4. Завершение процессов на порту 5051...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5051 ^| findstr LISTENING') do (
    echo Завершение процесса с PID: %%a
    taskkill /F /PID %%a
)
echo.

echo 5. Завершение тестовых Flask-серверов...
taskkill /F /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE like %%minimal_flask_server.py%%"
taskkill /F /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE like %%test_flask%%"
echo.

echo 6. Завершение тестовых CrewAI-серверов...
taskkill /F /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE like %%minimal_crewai_server.py%%"
echo.

echo 7. Проверка результатов (должно быть пусто)...
netstat -ano | findstr :5051
echo.

echo Очистка завершена! Теперь можно запускать основной сервер.
pause
