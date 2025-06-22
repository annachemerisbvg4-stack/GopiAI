#!/usr/bin/env python3
"""
Детальная диагностика GopiAI Bridge
==================================
"""
import sys
import os
from pathlib import Path

def diagnose_structure():
    """Диагностика структуры проекта"""
    
    print("🔍 Диагностика структуры проекта GopiAI\n")
    
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
    
    print("\n🐍 Python paths:")
    for path in sys.path:
        print(f"  {path}")
    
    print("\n🔍 Поиск bridge файлов...")
    
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
    
    print("\n🌐 Проверка WebChannel setup...")
    
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
    
    print("\n📋 Рекомендации:")
    print("1. Запустите test_bridge_imports.py для проверки импортов")
    print("2. Проверьте консоль браузера (F12) в WebView")
    print("3. Убедитесь что все модули установлены в editable режиме")

if __name__ == "__main__":
    diagnose_structure()
    check_webchannel_setup()
