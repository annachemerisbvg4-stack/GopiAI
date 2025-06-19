@echo off
REM Запуск минимальной версии приложения GopiAI из корня проекта
cd /d %~dp0..
set PYTHONPATH=.
python gopiai/main.py %*
REM Пример запуска с флагами:
REM python gopiai/main.py --debug --no-browser
