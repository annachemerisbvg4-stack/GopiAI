@echo off
REM Скрипт для отключения векторизации GopiAI (ускоряет запуск)
echo 🚫 Отключаем векторизацию для быстрого запуска...

REM Устанавливаем переменную среды для отключения embeddings
set GOPI_DISABLE_EMBEDDINGS=true

REM Запускаем GopiAI-UI
echo 🚀 Запускаем GopiAI без векторизации...
cd GopiAI-UI
python -m gopiai.ui

pause
