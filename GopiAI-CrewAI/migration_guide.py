#!/usr/bin/env python3
"""
Руководство по миграции на улучшенную систему переключения провайдеров LLM.
"""
import os
import sys
from pathlib import Path

def print_migration_guide():
    """Вывод руководства по миграции."""
    print("🔄 Руководство по миграции на улучшенную систему переключения провайдеров LLM")
    print("=" * 80)
    print()
    
    print("🚀 НОВЫЕ ВОЗМОЖНОСТИ:")
    print("   ✅ Стабильная синхронизация состояния между UI и Backend")
    print("   ✅ Мягкий черный список для моделей с превышением лимитов")
    print("   ✅ Надежный цикл API ключей без дубликатов")
    print("   ✅ Автоматические тесты для предотвращения регрессий")
    print()
    
    print("📋 ШАГИ ДЛЯ МИГРАЦИИ:")
    print()
    print("1. ЗАМЕНА ИМПОРТОВ:")
    print("   Было:")
    print("   >>> from llm_rotation_config import ...")
    print()
    print("   Стало:")
    print("   >>> from llm_rotation_config_fixed import ...")
    print()
    
    print("2. НАСТРОЙКА API КЛЮЧЕЙ:")
    print("   Добавьте в ваш .env файл:")
    print("   >>> GEMINI_API_KEY=ваш_ключ_gemini")
    print("   >>> OPENROUTER_API_KEY=ваш_ключ_openrouter")
    print()
    
    print("3. ЗАПУСК СИСТЕМЫ:")
    print("   Windows:")
    print("   >>> start_model_switching_system.bat")
    print()
    print("   Linux/Mac:")
    print("   >>> python start_model_switching_system.py")
    print()
    
    print("4. ПРОВЕРКА РАБОТЫ:")
    print("   >>> python run_all_tests.py")
    print()
    
    print("📚 ДОКУМЕНТАЦИЯ:")
    print("   - MODEL_SWITCHING_README.md - подробное описание системы")
    print("   - MODEL_SWITCHING_FINAL_REPORT.md - финальный отчет")
    print()
    
    print("🔧 ТЕСТИРОВАНИЕ:")
    print("   Запустите тесты для проверки корректности миграции:")
    print("   >>> cd GopiAI-CrewAI")
    print("   >>> python test_model_switching.py")
    print("   >>> python test_api_endpoints.py")
    print()

def check_current_setup():
    """Проверка текущей конфигурации."""
    print("🔍 Проверка текущей конфигурации...")
    print()
    
    # Проверяем наличие необходимых файлов
    required_files = [
        "llm_rotation_config_fixed.py",
        "crewai_api_server.py", 
        "state_manager.py",
        "model_selector_widget.py"
    ]
    
    crewai_dir = Path(__file__).parent
    missing_files = []
    
    for file_name in required_files:
        file_path = crewai_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name} - найден")
        else:
            print(f"❌ {file_name} - НЕ НАЙДЕН")
            missing_files.append(file_name)
    
    print()
    if missing_files:
        print("❌ Обнаружены отсутствующие файлы. Установите полную версию системы.")
        return False
    else:
        print("✅ Все необходимые файлы найдены.")
        return True

def check_api_keys():
    """Проверка наличия API ключей."""
    print("🔑 Проверка API ключей...")
    print()
    
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        print("⚠️  Файл .env не найден. Создайте его в корневой директории проекта.")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        keys_found = []
        if "GEMINI_API_KEY" in content:
            keys_found.append("GEMINI_API_KEY")
        if "OPENROUTER_API_KEY" in content:
            keys_found.append("OPENROUTER_API_KEY")
        
        if keys_found:
            print(f"✅ Найдены API ключи: {', '.join(keys_found)}")
            return True
        else:
            print("⚠️  API ключи не найдены в .env файле.")
            print("   Добавьте строки:")
            print("   GEMINI_API_KEY=ваш_ключ_gemini")
            print("   OPENROUTER_API_KEY=ваш_ключ_openrouter")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка чтения .env файла: {e}")
        return False

def main():
    """Основная функция."""
    print("🌟 Миграция на улучшенную систему переключения провайдеров LLM")
    print("=" * 70)
    print()
    
    # Проверяем текущую конфигурацию
    if not check_current_setup():
        print("\n❌ Миграция не может быть выполнена из-за отсутствующих файлов.")
        return 1
    
    print()
    
    # Проверяем API ключи
    check_api_keys()
    
    print()
    print("-" * 70)
    
    # Выводим руководство по миграции
    print_migration_guide()
    
    print("🎉 Миграция завершена! Система готова к использованию.")
    print("   Для запуска используйте start_model_switching_system.bat (Windows)")
    print("   или start_model_switching_system.py (Linux/Mac)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
