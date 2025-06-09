@echo off

chcp 65001 >nul || exit /b
REM Скрипт автоматического бэкапа
set timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%

echo [%timestamp%] Создание автобэкапа...

REM Создаем папку для бэкапов если её нет
if not exist "backups" mkdir backups

REM Добавляем все изменения
git add -A

REM Делаем коммит с временной меткой
git commit -m "Auto-backup: %timestamp%"

echo [%timestamp%] Бэкап создан!
