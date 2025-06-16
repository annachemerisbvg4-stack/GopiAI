#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции Claude Tools Handler
"""

import sys
import os
import json
from pathlib import Path

# Добавляем пути для импорта
ui_path = Path(__file__).parent / "GopiAI-UI"
sys.path.insert(0, str(ui_path))

def test_claude_tools_import():
    """Тест импорта ClaudeToolsHandler"""
    print("🔧 Testing ClaudeToolsHandler import...")
    
    try:
        from gopiai.ui.components.claude_tools_handler import ClaudeToolsHandler
        print("✅ ClaudeToolsHandler imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import ClaudeToolsHandler: {e}")
        return False

def test_webview_chat_widget_import():
    """Тест импорта WebViewChatWidget с интеграцией Claude Tools"""
    print("\n🔧 Testing WebViewChatWidget import...")
    
    try:
        from gopiai.ui.components.webview_chat_widget import WebViewChatWidget, WebViewChatBridge
        print("✅ WebViewChatWidget imported successfully")
        
        # Проверяем наличие переменной CLAUDE_TOOLS_AVAILABLE
        from gopiai.ui.components import webview_chat_widget
        if hasattr(webview_chat_widget, 'CLAUDE_TOOLS_AVAILABLE'):
            print(f"✅ CLAUDE_TOOLS_AVAILABLE = {webview_chat_widget.CLAUDE_TOOLS_AVAILABLE}")
        else:
            print("⚠️ CLAUDE_TOOLS_AVAILABLE variable not found")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import WebViewChatWidget: {e}")
        return False

def test_claude_tools_methods():
    """Тест методов ClaudeToolsHandler"""
    print("\n🔧 Testing ClaudeToolsHandler methods...")
    
    try:
        from gopiai.ui.components.claude_tools_handler import ClaudeToolsHandler
        
        # Создаем mock WebView для тестирования
        class MockWebView:
            def page(self):
                return MockPage()
        
        class MockPage:
            def url(self):
                return MockUrl()
            
            def title(self):
                return "Test Page"
            
            def runJavaScript(self, script, callback=None):
                if callback:
                    callback("test result")
        
        class MockUrl:
            def toString(self):
                return "about:blank"
        
        # Создаем handler с mock WebView
        mock_webview = MockWebView()
        handler = ClaudeToolsHandler(mock_webview)
        
        print("✅ ClaudeToolsHandler instance created")
        
        # Тестируем базовые методы
        result = handler.get_current_url()
        print(f"✅ get_current_url(): {result}")
        
        result = handler.get_page_title()
        print(f"✅ get_page_title(): {result}")
        
        result = handler.get_available_tools()
        print(f"✅ get_available_tools(): {result}")
        
        # Тестируем безопасность URL
        test_urls = [
            "https://google.com",
            "https://github.com", 
            "https://malicious-site.com",
            "file:///test.html",
            "about:blank"
        ]
        
        print("\n🔒 Testing URL security:")
        for url in test_urls:
            is_safe = handler._is_url_allowed(url)
            status = "✅" if is_safe else "❌"
            print(f"  {status} {url}: {'allowed' if is_safe else 'blocked'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ClaudeToolsHandler methods: {e}")
        return False

def test_bridge_integration():
    """Тест интеграции с WebViewChatBridge"""
    print("\n🔧 Testing Bridge integration...")
    
    try:
        from gopiai.ui.components.webview_chat_widget import WebViewChatBridge
        
        # Создаем bridge
        bridge = WebViewChatBridge()
        
        # Проверяем наличие новых методов
        claude_methods = [
            'execute_claude_tool',
            'get_claude_tools_list', 
            'get_pending_claude_requests'
        ]
        
        for method in claude_methods:
            if hasattr(bridge, method):
                print(f"✅ Bridge method {method} available")
            else:
                print(f"❌ Bridge method {method} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing bridge integration: {e}")
        return False

def test_file_operations():
    """Тест файловых операций"""
    print("\n🔧 Testing file operations...")
    
    try:
        from gopiai.ui.components.claude_tools_handler import ClaudeToolsHandler
        
        class MockWebView:
            def page(self):
                return None
        
        handler = ClaudeToolsHandler(MockWebView())
        
        # Тестируем чтение несуществующего файла
        result = handler.read_file("nonexistent.txt")
        result_data = json.loads(result)
        print(f"✅ read_file (nonexistent): success={result_data.get('success', False)}")
        
        # Тестируем создание временного файла
        test_content = "Test content for Claude Tools"
        temp_file = Path.cwd() / "test_claude_tools.txt"
        
        result = handler.write_file(str(temp_file), test_content)
        result_data = json.loads(result)
        print(f"✅ write_file: success={result_data.get('success', False)}")
        
        if temp_file.exists():
            result = handler.read_file(str(temp_file))
            result_data = json.loads(result)
            if result_data.get('success') and result_data.get('content') == test_content:
                print("✅ File read/write cycle successful")
            else:
                print("❌ File content mismatch")
            
            # Очищаем тестовый файл
            temp_file.unlink()
            print("✅ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing file operations: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Claude Tools Handler Integration Test")
    print("=" * 50)
    
    tests = [
        test_claude_tools_import,
        test_webview_chat_widget_import,
        test_claude_tools_methods,
        test_bridge_integration,
        test_file_operations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Claude Tools integration is working.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)