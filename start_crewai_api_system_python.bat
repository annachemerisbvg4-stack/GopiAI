@echo off
echo Запуск CrewAI API сервера с системным Python...
echo Текущая директория: %CD%

REM Переходим в домашний каталог пользователя
cd %USERPROFILE%
echo Переход в домашний каталог: %CD%

REM Запускаем Python-скрипт для запуска CrewAI API сервера
python "%USERPROFILE%\run_crewai_api_home.py"

pause
