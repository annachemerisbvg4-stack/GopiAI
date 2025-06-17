#!/usr/bin/env python3
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
