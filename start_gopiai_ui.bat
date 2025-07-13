@echo off
echo Запуск GopiAI UI...
echo Текущая директория: %CD%

REM Переходим в директорию UI
cd GopiAI-UI
echo Переход в директорию UI: %CD%

REM Запускаем UI
python -m gopiai.ui.main

pause
