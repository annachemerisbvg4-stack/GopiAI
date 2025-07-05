"""
Быстрый пример интеграции Smart Browser Agent в GopiAI-UI
Запустите этот файл для добавления умной навигации
"""

import sys
import os
from pathlib import Path

# Добавляем текущую директорию в PATH для импортов
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def integrate_smart_browser():
    """Интегрирует Smart Browser Agent в GopiAI-UI"""
    
    print("🚀 Интеграция Smart Browser Agent в GopiAI-UI")
    print("=" * 50)
    
    try:
        from SmartBrowserAgent import SmartBrowserAgent
        from browser_integration import enhance_browser_widget_with_smart_navigation, patch_enhanced_browser_widget
        
        # Ваш Brave API ключ
        BRAVE_API_KEY = "BSAEcqmI0ZUDsktUV1FKYYYq7HaQlnt"
        
        print("✅ Модули успешно импортированы")
        
        # Тестируем Smart Browser Agent
        print("\n🧪 Тестирование Smart Browser Agent...")
        agent = SmartBrowserAgent(BRAVE_API_KEY)
        
        test_command = "зайди на сайт leonardo ai"
        result = agent.process_command(test_command)
        
        if result['success']:
            print(f"✅ Тест пройден: {test_command} → {result['url']}")
        else:
            print(f"❌ Тест не пройден: {result['message']}")
        
        # Попытка интеграции с enhanced_browser_widget
        print("\n🔧 Попытка интеграции с enhanced_browser_widget...")
        integration_success = patch_enhanced_browser_widget()
        
        if integration_success:
            print("✅ Интеграция успешна!")
        else:
            print("⚠️ Автоматическая интеграция не удалась, но модули готовы к ручному использованию")
        
        print("\n📋 Инструкции по использованию:")
        print("1. Теперь ваши браузерные виджеты поддерживают умную навигацию")
        print("2. Используйте команды типа:")
        print("   - 'зайди на сайт leonardo ai'")
        print("   - 'открой github'")
        print("   - 'перейди на stackoverflow'")
        print("3. Для ручной интеграции используйте:")
        print("   enhance_browser_widget_with_smart_navigation(your_widget, api_key)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что все файлы находятся в одной директории:")
        print("- SmartBrowserAgent.py")
        print("- browser_integration.py")
        print("- Установлен модуль requests")
        return False
    
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False


def create_usage_example():
    """Создает пример использования для разработчиков"""
    
    usage_code = '''
# Пример использования Smart Browser Agent в вашем коде

from SmartBrowserAgent import SmartBrowserAgent
from browser_integration import enhance_browser_widget_with_smart_navigation

# 1. Инициализация агента
agent = SmartBrowserAgent("ваш_brave_api_ключ")

# 2. Обработка команд
result = agent.process_command("зайди на сайт leonardo ai")
if result['success']:
    print(f"URL найден: {result['url']}")

# 3. Интеграция с существующим браузерным виджетом
# enhance_browser_widget_with_smart_navigation(your_browser_widget, "ваш_brave_api_ключ")
# your_browser_widget.smart_navigate("открой github")

# 4. История команд
history = agent.get_session_history()
for entry in history:
    print(f"{entry['command']} → {entry['detected_url']}")
'''
    
    with open('usage_example.py', 'w', encoding='utf-8') as f:
        f.write(usage_code)
    
    print("📝 Создан файл usage_example.py с примерами использования")


def check_dependencies():
    """Проверяет зависимости"""
    
    print("🔍 Проверка зависимостей...")
    
    dependencies = {
        'requests': 'pip install requests',
        're': 'встроенный модуль',
        'typing': 'встроенный модуль (Python 3.5+)',
        'logging': 'встроенный модуль',
        'urllib.parse': 'встроенный модуль'
    }
    
    missing = []
    
    for dep, install_cmd in dependencies.items():
        try:
            __import__(dep)
            print(f"✅ {dep} - OK")
        except ImportError:
            print(f"❌ {dep} - НЕ НАЙДЕН ({install_cmd})")
            missing.append((dep, install_cmd))
    
    if missing:
        print("\n⚠️ Установите недостающие зависимости:")
        for dep, cmd in missing:
            if not cmd.startswith('встроенный'):
                print(f"  {cmd}")
        return False
    
    print("✅ Все зависимости установлены!")
    return True


if __name__ == "__main__":
    print("🎯 Quick Integration для Smart Browser Agent")
    print("=" * 60)
    
    # Проверяем зависимости
    if not check_dependencies():
        print("\n❌ Сначала установите недостающие зависимости")
        sys.exit(1)
    
    print()
    
    # Интегрируем Smart Browser Agent
    success = integrate_smart_browser()
    
    if success:
        print("\n🎉 Интеграция завершена успешно!")
        
        # Создаем примеры использования
        create_usage_example()
        
        print("\n📚 Дополнительная информация:")
        print("- Читайте SMART_BROWSER_README.md для подробной документации")
        print("- Смотрите usage_example.py для примеров кода")
        print("- Ваш Brave API ключ: BSAEcqmI0ZUDsktUV1FKYYYq7HaQlnt")
        
    else:
        print("\n💡 Не расстраивайтесь! Модули созданы и готовы к ручному использованию")
        print("Следуйте инструкциям в SMART_BROWSER_README.md")
    
    print("\n🎊 Готово! Теперь ваш браузер стал умнее! 🧠✨")
