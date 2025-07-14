@echo off
echo Завершение процессов на порту 5052...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5051 ^| findstr LISTENING') do (
    echo Завершение процесса с PID %%a
    taskkill /F /PID %%a
)
echo Проверка завершения...
netstat -ano | findstr :5052 | findstr LISTENING
if %ERRORLEVEL% EQU 0 (
    echo ВНИМАНИЕ: Не все процессы завершены!
) else (
    echo Все процессы успешно завершены.
)
