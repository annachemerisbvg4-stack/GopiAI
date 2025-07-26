#!/usr/bin/env python3
"""
Комплексный тест улучшений отображения чата
Проверяет ResponseFormatter, HTMLSanitizer и интеграцию с SmartDelegator
"""

import sys
import os
import logging

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_response_formatter():
    """Тестируем ResponseFormatter"""
    print("\n🔧 === ТЕСТ ResponseFormatter ===")
    
    try:
        from tools.gopiai_integration.response_formatter import ResponseFormatter
        
        formatter = ResponseFormatter()
        print("✅ ResponseFormatter создан успешно")
        
        # Тестовый ответ с JSON командами и HTML
        test_response = {
            "response": """Привет! Создаю папку для тебя.
            
```json
{'tool': 'terminal', 'params': {'command': 'mkdir C:\\\\Users\\\\crazy\\\\GOPI_AI_MODULES\\\\TEST_FORMATTER'}}
```

Папка создана! Вот результат с <strong>HTML тегами</strong> и <script>alert('test')</script>.

🔧 **Результаты выполнения команд:**
✅ `mkdir TEST_FORMATTER` - выполнено успешно""",
            "analysis": {
                "executed_commands": 1,
                "analysis_time": 2.5
            },
            "processed_with_crewai": False
        }
        
        # Тест форматирования для чата
        print("\n📱 Тестируем форматирование для чата...")
        chat_formatted = formatter.format_for_chat(test_response)
        
        print(f"Исходный ответ: {len(test_response['response'])} символов")
        print(f"Отформатированный: {len(chat_formatted['user_content'])} символов")
        print(f"Есть команды: {chat_formatted['has_commands']}")
        print(f"Первые 200 символов: {chat_formatted['user_content'][:200]}...")
        
        # Тест форматирования для файла
        print("\n📄 Тестируем форматирование для файла...")
        file_formatted = formatter.format_for_file_export(test_response)
        
        print(f"Для файла: {len(file_formatted)} символов")
        print(f"Первые 200 символов: {file_formatted[:200]}...")
        
        # Проверяем, что JSON блоки удалены
        if '```json' not in chat_formatted['user_content']:
            print("✅ JSON блоки успешно удалены из чата")
        else:
            print("❌ JSON блоки остались в чате")
            
        # Проверяем, что HTML теги удалены из файла
        if '<strong>' not in file_formatted and '<script>' not in file_formatted:
            print("✅ HTML теги успешно удалены из файла")
        else:
            print("❌ HTML теги остались в файле")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования ResponseFormatter: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_html_sanitizer():
    """Тестируем HTMLSanitizer"""
    print("\n🧹 === ТЕСТ HTMLSanitizer ===")
    
    try:
        from tools.gopiai_integration.html_sanitizer import HTMLSanitizer
        
        sanitizer = HTMLSanitizer()
        print("✅ HTMLSanitizer создан успешно")
        
        # Тестовый HTML контент
        test_html = """
        <html>
        <head><title>Test</title></head>
        <body>
            <p>Обычный текст с <strong>жирным</strong> и <em>курсивом</em>.</p>
            <script>alert('dangerous');</script>
            <div>Блок с <span style="color: red;">цветным текстом</span></div>
            <br>
            Текст с &lt;экранированными&gt; символами &amp; entities.
        </body>
        </html>
        """
        
        # Тест санитизации для файла
        print("\n📄 Тестируем санитизацию для файла...")
        file_clean = sanitizer.sanitize_for_file_export(test_html)
        
        print(f"Исходный HTML: {len(test_html)} символов")
        print(f"Очищенный текст: {len(file_clean)} символов")
        print(f"Результат: {file_clean}")
        
        # Проверяем удаление опасных тегов
        if '<script>' not in file_clean and '<html>' not in file_clean:
            print("✅ Опасные и структурные теги удалены")
        else:
            print("❌ Опасные теги остались")
            
        # Тест санитизации для UI
        print("\n🖥️ Тестируем санитизацию для UI...")
        ui_clean = sanitizer.sanitize_for_ui_display(test_html)
        
        print(f"Для UI: {len(ui_clean)} символов")
        print(f"Результат: {ui_clean[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования HTMLSanitizer: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_smart_delegator_integration():
    """Тестируем интеграцию с SmartDelegator"""
    print("\n🧠 === ТЕСТ SmartDelegator Integration ===")
    
    try:
        from tools.gopiai_integration.smart_delegator import SmartDelegator
        
        print("Создаем SmartDelegator...")
        delegator = SmartDelegator()
        
        # Проверяем, что все компоненты инициализированы
        checks = [
            ("CommandExecutor", hasattr(delegator, 'command_executor') and delegator.command_executor),
            ("ResponseFormatter", hasattr(delegator, 'response_formatter') and delegator.response_formatter)
        ]
        
        for component, status in checks:
            if status:
                print(f"✅ {component} интегрирован")
            else:
                print(f"❌ {component} НЕ интегрирован")
                
        # Проверяем методы форматировщика
        if delegator.response_formatter:
            print("🔧 Тестируем методы ResponseFormatter...")
            
            test_data = {
                "response": "Тест с ```json {'test': 'data'} ``` блоком",
                "analysis": {"executed_commands": 0}
            }
            
            formatted = delegator.response_formatter.format_for_chat(test_data)
            print(f"Форматирование работает: {len(formatted['user_content'])} символов")
            
        return all(status for _, status in checks)
        
    except Exception as e:
        print(f"❌ Ошибка тестирования SmartDelegator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_export():
    """Тестируем экспорт в файл с санитизацией"""
    print("\n💾 === ТЕСТ File Export ===")
    
    try:
        from tools.gopiai_integration.response_formatter import format_response_for_file
        
        # Тестовые данные с HTML и JSON
        test_data = {
            "response": """
            <h1>Заголовок</h1>
            <p>Текст с <strong>форматированием</strong></p>
            
            ```json
            {'tool': 'terminal', 'params': {'command': 'test'}}
            ```
            
            <script>alert('test');</script>
            Обычный текст в конце.
            """,
            "analysis": {"executed_commands": 1}
        }
        
        # Форматируем для файла
        clean_content = format_response_for_file(test_data)
        
        # Сохраняем в тестовый файл
        test_file = "test_export_clean.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(clean_content)
            
        print(f"✅ Файл сохранен: {test_file}")
        print(f"Размер: {len(clean_content)} символов")
        print(f"Содержимое: {clean_content[:200]}...")
        
        # Проверяем чистоту
        issues = []
        if '<' in clean_content and '>' in clean_content:
            issues.append("HTML теги")
        if '```json' in clean_content:
            issues.append("JSON блоки")
        if '<script>' in clean_content:
            issues.append("Опасные скрипты")
            
        if not issues:
            print("✅ Файл полностью очищен от артефактов")
        else:
            print(f"❌ Остались артефакты: {', '.join(issues)}")
            
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Ошибка тестирования экспорта: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Запуск всех тестов"""
    print("🚀 === КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ УЛУЧШЕНИЙ ЧАТА ===")
    print("=" * 60)
    
    tests = [
        ("ResponseFormatter", test_response_formatter),
        ("HTMLSanitizer", test_html_sanitizer),
        ("SmartDelegator Integration", test_smart_delegator_integration),
        ("File Export", test_file_export)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте {test_name}: {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ УСПЕХ" if result else "❌ ОШИБКА"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nПройдено тестов: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("Система улучшений чата готова к работе!")
    else:
        print(f"\n⚠️ ЕСТЬ ПРОБЛЕМЫ: {len(tests) - passed} тестов не прошли")
        print("Требуется дополнительная отладка")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
