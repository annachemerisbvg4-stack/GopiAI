@echo off
ECHO Запуск GopiAI UI...
SET PYTHONPATH=%PYTHONPATH%;C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI
call C:\Users\crazy\GOPI_AI_MODULES\gopiai_env\Scripts\activate.bat
python C:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI\gopiai\ui\main.py
PAUSE
