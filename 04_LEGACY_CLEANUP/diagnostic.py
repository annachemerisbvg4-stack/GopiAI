
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
    
    print("\n📦 Module imports:")
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
    
    print("\n📄 File existence:")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
    
    # 4. Проверка переменных окружения
    print("\n🌍 Environment variables:")
    env_vars = ['PYTHONPATH', 'QT_LOGGING_RULES', 'PATH']
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"  {var}: {value}")
    
    # 5. Проверка QtWebEngine
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        print("\n🌐 QtWebEngine: ✅ Available")
    except ImportError as e:
        print(f"\n🌐 QtWebEngine: ❌ {e}")
    
    # 6. Проверка WebChannel
    try:
        from PySide6.QtWebChannel import QWebChannel
        print("🌉 WebChannel: ✅ Available")
    except ImportError as e:
        print(f"🌉 WebChannel: ❌ {e}")

if __name__ == "__main__":
    diagnose_gopiai()
