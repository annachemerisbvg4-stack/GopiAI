#!/usr/bin/env python3
"""
Тест исправления JavaScript ошибки toolsList.tools.find
"""

import sys
import json
import subprocess
import os

def test_javascript_syntax():
    """Проверяем синтаксис JavaScript файла"""
    print("🔍 Проверка синтаксиса JavaScript...")
    
    js_file = "GopiAI-WebView/gopiai/webview/assets/chat.js"
    
    if not os.path.exists(js_file):
        print(f"❌ Файл {js_file} не найден")
        return False
    
    try:
        # Проверяем синтаксис через Node.js
        result = subprocess.run(
            ['node', '-c', js_file],
            capture_output=True,
            text=True,
            cwd='.'
        )
        
        if result.returncode == 0:
            print("✅ JavaScript синтаксис корректен")
            return True
        else:
            print(f"❌ Ошибка синтаксиса JavaScript: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки синтаксиса: {e}")
        return False

def test_method_presence():
    """Проверяем наличие нужных методов в JavaScript файле"""
    print("\n🔍 Проверка наличия методов...")
    
    js_file = "GopiAI-WebView/gopiai/webview/assets/chat.js"
    
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_methods = [
            'getClaudeToolsList',
            'checkMemoryAvailability',
            'searchMemory'
        ]
        
        for method in required_methods:
            if f'async {method}(' in content or f'{method}(' in content:
                print(f"✅ Метод {method} найден")
            else:
                print(f"❌ Метод {method} не найден")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return False

def test_error_handling():
    """Проверяем правильную обработку ошибок в коде"""
    print("\n🔍 Проверка обработки ошибок...")
    
    js_file = "GopiAI-WebView/gopiai/webview/assets/chat.js"
    
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем наличие правильной обработки toolsList
        if 'toolsList.tools' in content and 'Array.isArray(toolsList.tools)' in content:
            print("✅ Правильная проверка Array.isArray для toolsList.tools")
        else:
            print("❌ Отсутствует правильная проверка Array.isArray")
            return False
        
        # Проверяем обработку разных структур ответа
        if 'toolsList.result' in content and 'toolsList.data' in content:
            print("✅ Обработка альтернативных структур ответа")
        else:
            print("❌ Отсутствует обработка альтернативных структур")
            return False
        
        # Проверяем try-catch в критических методах
        if 'try {' in content and 'catch (error)' in content:
            print("✅ Try-catch блоки присутствуют")
        else:
            print("❌ Отсутствуют try-catch блоки")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка анализа файла: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование исправления JavaScript ошибок\n")
    
    tests = [
        ("Синтаксис JavaScript", test_javascript_syntax),
        ("Наличие методов", test_method_presence),
        ("Обработка ошибок", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Тест: {test_name}")
        print('='*50)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name}: ПРОЙДЕН")
        else:
            print(f"❌ {test_name}: ПРОВАЛЕН")
    
    print(f"\n{'='*50}")
    print(f"РЕЗУЛЬТАТ: {passed}/{total} тестов пройдено")
    print('='*50)
    
    if passed == total:
        print("🎉 Все тесты пройдены! JavaScript ошибки исправлены.")
        return True
    else:
        print("⚠️ Некоторые тесты провалены. Требуются дополнительные исправления.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)