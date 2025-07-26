import sys
import os
sys.path.append('.')

print("=== ПРОСТОЙ ТЕСТ КОМПОНЕНТОВ ===")

# Тест 1: ResponseFormatter
print("\n1. Тестируем ResponseFormatter...")
try:
    from tools.gopiai_integration.response_formatter import ResponseFormatter
    formatter = ResponseFormatter()
    
    test_data = {
        "response": "Привет! ```json {'tool': 'terminal'} ``` Команда выполнена!",
        "analysis": {"executed_commands": 1}
    }
    
    result = formatter.format_for_chat(test_data)
    print(f"✅ ResponseFormatter работает")
    print(f"Исходно: {len(test_data['response'])} символов")
    print(f"Очищено: {len(result['user_content'])} символов")
    
except Exception as e:
    print(f"❌ ResponseFormatter: {e}")

# Тест 2: HTMLSanitizer
print("\n2. Тестируем HTMLSanitizer...")
try:
    from tools.gopiai_integration.html_sanitizer import HTMLSanitizer
    sanitizer = HTMLSanitizer()
    
    test_html = "<p>Текст с <strong>тегами</strong> и <script>alert('test')</script></p>"
    clean = sanitizer.sanitize_for_file_export(test_html)
    
    print(f"✅ HTMLSanitizer работает")
    print(f"Исходно: {test_html}")
    print(f"Очищено: {clean}")
    
except Exception as e:
    print(f"❌ HTMLSanitizer: {e}")

# Тест 3: SmartDelegator
print("\n3. Тестируем SmartDelegator...")
try:
    from tools.gopiai_integration.smart_delegator import SmartDelegator
    delegator = SmartDelegator()
    
    has_formatter = hasattr(delegator, 'response_formatter') and delegator.response_formatter
    has_executor = hasattr(delegator, 'command_executor') and delegator.command_executor
    
    print(f"✅ SmartDelegator создан")
    print(f"ResponseFormatter: {'✅' if has_formatter else '❌'}")
    print(f"CommandExecutor: {'✅' if has_executor else '❌'}")
    
except Exception as e:
    print(f"❌ SmartDelegator: {e}")

print("\n=== ТЕСТ ЗАВЕРШЕН ===")
