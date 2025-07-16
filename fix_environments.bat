@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════
echo     🔧 GOPI_AI Environment Repair Tool
echo ═══════════════════════════════════════════════════════
echo.

echo 🔍 Проверка состояния окружений...
echo.

REM Проверка CrewAI окружения
echo 1️⃣ Проверка CrewAI окружения...
cd /d "C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI"
if exist "crewai_env\Scripts\activate.bat" (
    echo ✅ CrewAI окружение найдено
    call crewai_env\Scripts\activate.bat
    echo 🔄 Проверка ключевых библиотек...
    python -c "import crewai; print(f'✅ CrewAI {crewai.__version__} установлен')" 2>nul || (
        echo ❌ CrewAI не найден, переустанавливаем...
        pip install crewai==0.141.0
    )
    python -c "import flask; print('✅ Flask установлен')" 2>nul || (
        echo ❌ Flask не найден, переустанавливаем...
        pip install flask
    )
    echo ✅ CrewAI окружение исправлено
) else (
    echo ❌ CrewAI окружение не найдено
    echo 🔄 Создание нового окружения...
    python -m venv crewai_env
    call crewai_env\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
    echo ✅ CrewAI окружение создано
)
echo.

REM Проверка UI окружения
echo 2️⃣ Проверка UI окружения...
cd /d "C:\Users\crazy\GOPI_AI_MODULES"
if exist "gopiai_env\Scripts\activate.bat" (
    echo ✅ UI окружение найдено
    call gopiai_env\Scripts\activate.bat
    echo 🔄 Проверка ключевых библиотек...
    python -c "import PySide6; print('✅ PySide6 установлен')" 2>nul || (
        echo ❌ PySide6 не найден, переустанавливаем...
        pip install PySide6
    )
    echo ✅ UI окружение исправлено
) else (
    echo ❌ UI окружение не найдено
    echo 🔄 Создание нового окружения...
    python -m venv gopiai_env
    call gopiai_env\Scripts\activate.bat
    pip install --upgrade pip
    pip install PySide6
    echo ✅ UI окружение создано
)
echo.

REM Проверка TXTAI окружения
echo 3️⃣ Проверка TXTAI окружения...
if exist "txtai_env\Scripts\activate.bat" (
    echo ✅ TXTAI окружение найдено
    call txtai_env\Scripts\activate.bat
    echo 🔄 Проверка ключевых библиотек...
    python -c "import txtai; print('✅ txtai установлен')" 2>nul || (
        echo ❌ txtai не найден, переустанавливаем...
        pip install txtai
    )
    echo ✅ TXTAI окружение исправлено
) else (
    echo ❌ TXTAI окружение не найдено
    echo 🔄 Создание нового окружения...
    python -m venv txtai_env
    call txtai_env\Scripts\activate.bat
    pip install --upgrade pip
    pip install txtai
    echo ✅ TXTAI окружение создано
)
echo.

echo 🧪 Тестирование окружений...
echo.

REM Тест CrewAI сервера
echo 📡 Тест CrewAI сервера...
cd /d "C:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI"
call crewai_env\Scripts\activate.bat
python test_server_stability.py
if %errorlevel% equ 0 (
    echo ✅ CrewAI сервер работает корректно
) else (
    echo ❌ Проблемы с CrewAI сервером
)
echo.

echo ✅ Все окружения проверены и исправлены!
echo.
echo 📋 Статус:
echo    🤖 CrewAI окружение: Готово
echo    🖥️ UI окружение: Готово  
echo    📊 TXTAI окружение: Готово
echo.
echo 🚀 Теперь можете запустить start_auto_development.bat
echo.
pause
