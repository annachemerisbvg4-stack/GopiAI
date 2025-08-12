#!/usr/bin/env python3
"""
🔧 Скрипт для исправления проблем с CrewAI сервером
Автоматически устанавливает недостающие зависимости и проверяет работоспособность
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            return True
        else:
            print(f"❌ {description} - ошибка:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} - исключение: {e}")
        return False

def check_import(module_name, description):
    """Проверяет возможность импорта модуля"""
    try:
        __import__(module_name)
        print(f"✅ {description} - доступен")
        return True
    except ImportError as e:
        print(f"❌ {description} - недоступен: {e}")
        return False

def main():
    print("🚀 Исправление проблем с CrewAI сервером")
    print("=" * 50)
    
    # Переходим в правильную директорию
    crewai_dir = Path(__file__).parent / "GopiAI-CrewAI"
    if crewai_dir.exists():
        os.chdir(crewai_dir)
        print(f"📁 Рабочая директория: {crewai_dir}")
    else:
        print("❌ Директория GopiAI-CrewAI не найдена")
        return False
    
    # 1. Проверяем основные зависимости
    print("\n1️⃣ Проверка основных зависимостей:")
    dependencies = [
        ("flask", "Flask"),
        ("crewai", "CrewAI"),
        ("pydantic", "Pydantic"),
        ("requests", "Requests")
    ]
    
    missing_deps = []
    for module, name in dependencies:
        if not check_import(module, name):
            missing_deps.append(module)
    
    # 2. Устанавливаем недостающие зависимости
    if missing_deps:
        print(f"\n2️⃣ Установка недостающих зависимостей: {', '.join(missing_deps)}")
        for dep in missing_deps:
            if not run_command(f"pip install {dep}", f"Установка {dep}"):
                print(f"⚠️ Не удалось установить {dep}")
    else:
        print("\n2️⃣ Все основные зависимости установлены")
    
    # 3. Проверяем импорт ключевых модулей
    print("\n3️⃣ Проверка ключевых модулей GopiAI:")
    key_modules = [
        ("tools.gopiai_integration.filesystem_tools", "FileSystem Tools"),
        ("tools.gopiai_integration.crewai_tools_integrator", "CrewAI Tools Integrator"),
        ("rag_system", "RAG System"),
        ("llm_rotation_config", "LLM Rotation Config")
    ]
    
    for module, name in key_modules:
        check_import(module, name)
    
    # 4. Проверяем специфический импорт, который вызывал ошибку
    print("\n4️⃣ Проверка проблемного импорта:")
    try:
        from tools.gopiai_integration.crewai_tools_integrator import get_crewai_tools_integrator
        integrator = get_crewai_tools_integrator()
        print("✅ get_crewai_tools_integrator - успешно импортирован и создан")
        print(f"   Найдено инструментов: {len(integrator.available_tools)}")
    except Exception as e:
        print(f"❌ get_crewai_tools_integrator - ошибка: {e}")
    
    # 5. Тестовый запуск сервера (проверка синтаксиса)
    print("\n5️⃣ Проверка синтаксиса сервера:")
    if run_command("python -m py_compile crewai_api_server.py", "Компиляция сервера"):
        print("✅ Синтаксис сервера корректен")
    
    # 6. Проверяем конфигурационные файлы
    print("\n6️⃣ Проверка конфигурационных файлов:")
    config_files = [
        "requirements.txt",
        "tools/model_configurations.json",
        "memory/chats.json"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ {config_file} - найден")
        else:
            print(f"⚠️ {config_file} - не найден")
    
    print("\n" + "=" * 50)
    print("🎯 РЕКОМЕНДАЦИИ:")
    print("1. Если сервер не запускается, выполните:")
    print("   pip install -r requirements.txt")
    print("2. Для запуска сервера используйте:")
    print("   python crewai_api_server.py")
    print("3. Сервер должен быть доступен на http://localhost:5051")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Скрипт прерван пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()