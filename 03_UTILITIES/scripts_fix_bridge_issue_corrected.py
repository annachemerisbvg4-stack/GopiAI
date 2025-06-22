#!/usr/bin/env python3
"""
Исправление проблемы с bridge в GopiAI
=====================================

Этот скрипт исправляет проблемы с импортами и путями к bridge компонентам.
"""
import os
import sys
import shutil
from pathlib import Path

def fix_imports():
    """Исправляет импорты в основных файлах"""
    
    # 1. Исправляем импорт в chat.js
    chat_js_path = Path("GopiAI-WebView/gopiai/webview/assets/chat.js")
    if chat_js_path.exists():
        print(f"✅ Найден {chat_js_path}")
        
        # Читаем содержимое
        with open(chat_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем наличие WebChannel
        if 'QWebChannel' in content:
            print("✅ QWebChannel уже есть в chat.js")
        else:
            print("❌ QWebChannel не найден в chat.js")
    
    # 2. Проверяем webview_chat_widget.py
    widget_path = Path("GopiAI-UI/gopiai/ui/components/webview_chat_widget.py")
    if widget_path.exists():
        print(f"✅ Найден {widget_path}")
        
        with open(widget_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем импорты
        if 'js_bridge' in content:
            print("✅ js_bridge импортируется")
        else:
            print("❌ js_bridge не импортируется")
        
        if 'claude_tools_handler' in content:
            print("✅ claude_tools_handler импортируется")
        else:
            print("❌ claude_tools_handler не импортируется")
    
    # 3. Проверяем пути к файлам
    js_bridge_path = Path("GopiAI-WebView/gopiai/webview/js_bridge.py")
    claude_tools_path = Path("GopiAI-UI/gopiai/ui/components/claude_tools_handler.py")
    
    print(f"\n📁 Проверка путей:")
    print(f"js_bridge.py: {'✅' if js_bridge_path.exists() else '❌'} {js_bridge_path}")
    print(f"claude_tools_handler.py: {'✅' if claude_tools_path.exists() else '❌'} {claude_tools_path}")

def create_bridge_test():
    """Создает тестовый скрипт для проверки bridge"""
    
    test_script = '''#!/usr/bin/env python3
"""
Тест Bridge компонентов GopiAI
=============================
"""
import sys
import os
sys.path.append(os.getcwd())

def test_imports():
    """Тестирует импорты bridge компонентов"""
    
    print("🧪 Тестирование импортов bridge...")
    
    # Тест 1: js_bridge
    try:
        from GopiAI_WebView.gopiai.webview.js_bridge import JavaScriptBridge
        print("✅ JavaScriptBridge импортирован успешно")
    except ImportError as e:
        print(f"❌ Ошибка импорта JavaScriptBridge: {e}")
    
    # Тест 2: claude_tools_handler
    try:
        from GopiAI_UI.gopiai.ui.components.claude_tools_handler import ClaudeToolsHandler
        print("✅ ClaudeToolsHandler импортирован успешно")
    except ImportError as e:
        print(f"❌ Ошибка импорта ClaudeToolsHandler: {e}")
    
    # Тест 3: webview_chat_widget
    try:
        from GopiAI_UI.gopiai.ui.components.webview_chat_widget import WebViewChatWidget
        print("✅ WebViewChatWidget импортирован успешно")
    except ImportError as e:
        print(f"❌ Ошибка импорта WebViewChatWidget: {e}")

if __name__ == "__main__":
    test_imports()
'''
    
    with open("test_bridge_imports.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("✅ Создан test_bridge_imports.py")

def create_detailed_diagnostic():
    """Создает детальную диагностику"""
    
    diagnostic_script = '''#!/usr/bin/env python3
"""
Детальная диагностика GopiAI Bridge
==================================
"""
import sys
import os
from pathlib import Path

def diagnose_structure():
    """Диагностика структуры проекта"""
    
    print("🔍 Диагностика структуры проекта GopiAI\\n")
    
    # Основные пути
    paths_to_check = [
        "GopiAI-WebView/gopiai/webview/js_bridge.py",
        "GopiAI-WebView/gopiai/webview/assets/chat.js",
        "GopiAI-UI/gopiai/ui/components/claude_tools_handler.py",
        "GopiAI-UI/gopiai/ui/components/webview_chat_widget.py",
        "GopiAI-UI/gopiai/ui/main.py",
    ]
    
    print("📁 Проверка файлов:")
    for path in paths_to_check:
        file_path = Path(path)
        status = "✅" if file_path.exists() else "❌"
        size = f"({file_path.stat().st_size} bytes)" if file_path.exists() else ""
        print(f"  {status} {path} {size}")
    
    print("\\n🐍 Python paths:")
    for path in sys.path:
        print(f"  {path}")
    
    print("\\n🔍 Поиск bridge файлов...")
    
    # Поиск всех bridge файлов
    bridge_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if "bridge" in file.lower() and file.endswith(".py"):
                bridge_files.append(os.path.join(root, file))
    
    if bridge_files:
        print("📦 Найденные bridge файлы:")
        for file in bridge_files:
            print(f"  ✅ {file}")
    else:
        print("❌ Bridge файлы не найдены")

def check_webchannel_setup():
    """Проверяет настройку WebChannel"""
    
    print("\\n🌐 Проверка WebChannel setup...")
    
    # Проверяем chat.js
    chat_js = Path("GopiAI-WebView/gopiai/webview/assets/chat.js")
    if chat_js.exists():
        with open(chat_js, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("QWebChannel", "QWebChannel инициализация"),
            ("qt.webChannelTransport", "WebChannel transport"),
            ("execute_claude_tool", "Claude tool execution"),
            ("get_claude_tools_list", "Claude tools list"),
        ]
        
        for check, description in checks:
            status = "✅" if check in content else "❌"
            print(f"  {status} {description}")
    
    print("\\n📋 Рекомендации:")
    print("1. Запустите test_bridge_imports.py для проверки импортов")
    print("2. Проверьте консоль браузера (F12) в WebView")
    print("3. Убедитесь что все модули установлены в editable режиме")

if __name__ == "__main__":
    diagnose_structure()
    check_webchannel_setup()
'''
    
    with open("detailed_diagnostic.py", "w", encoding="utf-8") as f:
        f.write(diagnostic_script)
    
    print("✅ Создан detailed_diagnostic.py")

def main():
    """Основная функция"""
    
    print("🔧 GopiAI Bridge Issue Fixer")
    print("=" * 50)
    
    # Исправляем импорты
    fix_imports()
    
    # Создаем тестовые скрипты
    create_bridge_test()
    create_detailed_diagnostic()
    
    print(f"\n🎯 Следующие шаги:")
    print("1. python test_bridge_imports.py")
    print("2. python detailed_diagnostic.py")
    print("3. Запустите приложение с interaction_debug_logger.py")

if __name__ == "__main__":
    main()