#!/usr/bin/env python3
"""
Анализатор проблем в chat.js и цепочке взаимодействий
"""

import os
import re
import json
from pathlib import Path

def analyze_chat_js_issues():
    """Анализ потенциальных проблем в chat.js"""
    
    print("🔍 Анализ проблем в chat.js")
    print("=" * 50)
    
    # Читаем chat.js
    chat_js_path = "GopiAI-WebView/gopiai/webview/assets/chat.js"
    
    if not os.path.exists(chat_js_path):
        print(f"❌ Файл {chat_js_path} не найден")
        return
    
    with open(chat_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 1. Проверяем инициализацию puter.js
    if 'waitForPuter()' in content:
        print("✅ Есть проверка загрузки puter.js")
    else:
        issues.append("❌ Отсутствует проверка загрузки puter.js")
    
    # 2. Проверяем обработку ошибок в sendMessage
    sendmessage_match = re.search(r'async sendMessage\(\)\s*{(.*?)}', content, re.DOTALL)
    if sendmessage_match:
        sendmessage_code = sendmessage_match.group(1)
        
        if 'try' in sendmessage_code and 'catch' in sendmessage_code:
            print("✅ Есть обработка ошибок в sendMessage")
        else:
            issues.append("❌ Отсутствует обработка ошибок в sendMessage")
        
        if 'puter.ai.chat' in sendmessage_code:
            print("✅ Используется puter.ai.chat")
        else:
            issues.append("❌ Не используется puter.ai.chat")
    else:
        issues.append("❌ Метод sendMessage не найден")
    
    # 3. Проверяем WebChannel инициализацию
    if 'QWebChannel' in content and 'qt.webChannelTransport' in content:
        print("✅ Есть инициализация WebChannel")
    else:
        issues.append("❌ Проблемы с инициализацией WebChannel")
    
    # 4. Проверяем bridge методы
    if 'execute_claude_tool' in content:
        print("✅ Есть вызовы execute_claude_tool")
    else:
        issues.append("⚠️ Отсутствуют вызовы execute_claude_tool")
    
    if 'get_claude_tools_list' in content:
        print("✅ Есть вызовы get_claude_tools_list")
    else:
        issues.append("⚠️ Отсутствуют вызовы get_claude_tools_list")
    
    # 5. Проверяем типичные проблемы
    if 'console.log' in content:
        print("✅ Есть отладочные логи")
    else:
        issues.append("⚠️ Мало отладочных логов")
    
    # Выводим найденные проблемы
    if issues:
        print("\n🚨 НАЙДЕННЫЕ ПРОБЛЕМЫ:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ Явных проблем в коде не найдено")
    
    return issues

def analyze_webview_bridge():
    """Анализ WebView bridge"""
    
    print("\n🔍 Анализ WebView Bridge")
    print("=" * 50)
    
    # Ищем webview_bridge.py
    possible_paths = [
        "GopiAI-WebView/gopiai/webview/webview_bridge.py",
        "GopiAI/GopiAI-WebView/gopiai/webview/webview_bridge.py"
    ]
    
    bridge_path = None
    for path in possible_paths:
        if os.path.exists(path):
            bridge_path = path
            break
    
    if not bridge_path:
        print("❌ WebView bridge не найден")
        return []
    
    print(f"✅ Найден WebView bridge: {bridge_path}")
    
    with open(bridge_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Проверяем ключевые методы
    if 'execute_claude_tool' in content:
        print("✅ Метод execute_claude_tool присутствует")
    else:
        issues.append("❌ Метод execute_claude_tool отсутствует")
    
    if 'get_claude_tools_list' in content:
        print("✅ Метод get_claude_tools_list присутствует")
    else:
        issues.append("❌ Метод get_claude_tools_list отсутствует")
    
    # Проверяем импорты
    if 'from GopiAI' in content or 'import GopiAI' in content:
        print("✅ Есть импорты GopiAI модулей")
    else:
        issues.append("⚠️ Возможны проблемы с импортами")
    
    return issues

def analyze_claude_tools():
    """Анализ Claude Tools Handler"""
    
    print("\n🔍 Анализ Claude Tools")
    print("=" * 50)
    
    # Ищем claude_tools_handler.py
    possible_paths = [
        "GopiAI-Extensions/claude_tools/claude_tools_handler.py",
        "GopiAI/GopiAI-Extensions/claude_tools/claude_tools_handler.py"
    ]
    
    tools_path = None
    for path in possible_paths:
        if os.path.exists(path):
            tools_path = path
            break
    
    if not tools_path:
        print("❌ Claude Tools Handler не найден")
        return []
    
    print(f"✅ Найден Claude Tools Handler: {tools_path}")
    
    with open(tools_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Проверяем основные методы
    if 'execute_tool' in content:
        print("✅ Метод execute_tool присутствует")
    else:
        issues.append("❌ Метод execute_tool отсутствует")
    
    if 'list_tools' in content:
        print("✅ Метод list_tools присутствует")
    else:
        issues.append("❌ Метод list_tools отсутствует")
    
    # Проверяем обработку ошибок
    if 'try:' in content and 'except' in content:
        print("✅ Есть обработка ошибок")
    else:
        issues.append("⚠️ Недостаточная обработка ошибок")
    
    return issues

def create_diagnostic_script():
    """Создание диагностического скрипта"""
    
    diagnostic_code = '''
import sys
import os
import json
import traceback
from pathlib import Path

def diagnose_gopiai():
    """Диагностика GopiAI системы"""
    
    print("🔍 GopiAI System Diagnostic")
    print("=" * 50)
    
    # 1. Проверка Python путей
    print("📂 Python paths:")
    for path in sys.path:
        print(f"  {path}")
    
    # 2. Проверка импортов
    modules_to_check = [
        'GopiAI.GopiAI-WebView.gopiai.webview.webview_bridge',
        'GopiAI.GopiAI-Extensions.claude_tools.claude_tools_handler',
        'PySide6.QtCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebChannel'
    ]
    
    print("\\n📦 Module imports:")
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
    
    # 3. Проверка файлов
    files_to_check = [
        'GopiAI-UI/gopiai/ui/main.py',
        'GopiAI-WebView/gopiai/webview/webview_bridge.py',
        'GopiAI-WebView/gopiai/webview/assets/chat.js',
        'GopiAI-Extensions/claude_tools/claude_tools_handler.py'
    ]
    
    print("\\n📄 File existence:")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
    
    # 4. Проверка переменных окружения
    print("\\n🌍 Environment variables:")
    env_vars = ['PYTHONPATH', 'QT_LOGGING_RULES', 'PATH']
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"  {var}: {value}")
    
    # 5. Проверка QtWebEngine
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        print("\\n🌐 QtWebEngine: ✅ Available")
    except ImportError as e:
        print(f"\\n🌐 QtWebEngine: ❌ {e}")
    
    # 6. Проверка WebChannel
    try:
        from PySide6.QtWebChannel import QWebChannel
        print("🌉 WebChannel: ✅ Available")
    except ImportError as e:
        print(f"🌉 WebChannel: ❌ {e}")

if __name__ == "__main__":
    diagnose_gopiai()
'''
    
    with open('diagnostic.py', 'w', encoding='utf-8') as f:
        f.write(diagnostic_code)
    
    print(f"\n📝 Создан диагностический скрипт: diagnostic.py")

def main():
    """Основная функция анализа"""
    
    print("🚀 GopiAI Problem Analyzer")
    print("=" * 60)
    
    # Анализируем компоненты
    chat_issues = analyze_chat_js_issues() or []
    bridge_issues = analyze_webview_bridge() or []
    tools_issues = analyze_claude_tools() or []
    
    # Создаем диагностический скрипт
    create_diagnostic_script()
    
    # Общий отчет
    total_issues = len(chat_issues) + len(bridge_issues) + len(tools_issues)
    
    print(f"\n📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    print(f"Всего найдено проблем: {total_issues}")
    
    if total_issues == 0:
        print("✅ Явных проблем не найдено.")
        print("🔍 Рекомендуется использовать interaction_debug_logger.py для детальной диагностики")
    else:
        print("🚨 Найдены потенциальные проблемы:")
        
        all_issues = chat_issues + bridge_issues + tools_issues
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
    
    print("\n📋 РЕКОМЕНДАЦИИ:")
    print("1. Запустите diagnostic.py для системной диагностики")
    print("2. Используйте interaction_debug_logger.py для детального логирования")
    print("3. Проверьте консоль браузера в WebView (F12)")
    print("4. Убедитесь что все зависимости установлены")

if __name__ == "__main__":
    main()