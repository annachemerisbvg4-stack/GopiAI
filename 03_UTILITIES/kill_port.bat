@echo off
echo 🔫 Port Killer - Очистка портов
echo ================================

set /p port="Введите номер порта для очистки (например 8080): "

echo Поиск процессов на порту %port%...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%port%"') do (
    echo Убиваем процесс с PID: %%a
    taskkill /F /PID %%a 2>nul
)

echo ✅ Порт %port% очищен!
pause