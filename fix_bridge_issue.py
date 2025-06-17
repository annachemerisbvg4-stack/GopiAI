#!/usr/bin/env python3
"""
🔧 Исправление проблемы bridge в GopiAI
=======================================

Обнаружена проблема: в webview_chat_widget.py создается отдельный WebViewChatBridge,
вместо использования JavaScriptBridge из js_bridge.py, что приводит к дублированию
и потенциальным конфликтам.

Это исправление:
1. Удаляет дублирующий WebViewChatBridge
2. Использует JavaScriptBridge из js_bridge.py
3. Обеспечивает правильную связь между компонентами
"""

import os
import shutil
from pathlib import Path

def fix_bridge_issue():
    """Исправляет проблему с дублированием bridge"""
    
    print("🔧 Fixing bridge duplication issue...")
    
    # Путь к проблемному файлу
    widget_file = Path("GopiAI-UI/gopiai/ui/components/webview_chat_widget.py")
    
    if not widget_file.exists():
        print(f"❌ File not found: {widget_file}")
        return False
    
    # Создаем резервную копию
    backup_file = widget_file.with_suffix('.py.backup')
    shutil.copy2(widget_file, backup_file)
    print(f"📂 Backup created: {backup_file}")
    
    # Читаем содержимое
    with open(widget_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем импорт на правильный JavaScriptBridge
    new_content = content.replace(
        "class WebViewChatBridge(QObject):",
        "# WebViewChatBridge удален - используем JavaScriptBridge\n# from gopiai.webview.js_bridge import JavaScriptBridge"
    )
    
    # Добавляем правильный импорт в начало файла
    import_section = """
# Импорт JavaScriptBridge
try:
    import sys
    webview_path = Path(__file__).parent.parent.parent.parent / "GopiAI-WebView"
    if webview_path.exists():
        sys.path.insert(0, str(webview_path))
    from gopiai.webview.js_bridge import JavaScriptBridge
    JAVASCRIPT_BRIDGE_AVAILABLE = True
    print("✅ JavaScriptBridge imported successfully")
except ImportError as e:
    JAVASCRIPT_BRIDGE_AVAILABLE = False
    print(f"⚠️ JavaScriptBridge not available: {e}")
"""
    
    # Вставляем импорт после существующих импортов
    lines = new_content.split('\n')
    import_end_index = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            import_end_index = i
    
    lines.insert(import_end_index + 1, import_section)
    
    # Заменяем создание WebViewChatBridge на JavaScriptBridge
    new_content = '\n'.join(lines)
    new_content = new_content.replace(
        "self.bridge = WebViewChatBridge(self)",
        "self.bridge = JavaScriptBridge(self) if JAVASCRIPT_BRIDGE_AVAILABLE else None"
    )
    
    # Сохраняем исправленный файл
    with open(widget_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Fixed: {widget_file}")
    return True

def fix_imports_in_diagnostic_files():
    """Исправляет пути импорта в диагностических файлах"""
    
    files_to_fix = [
        "analyze_problems.py",
        "diagnostic.py", 
        "interaction_debug_logger.py"
    ]
    
    for file_path in files_to_fix:
        if not Path(file_path).exists():
            continue
            
        print(f"🔧 Fixing imports in {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Исправляем пути
        content = content.replace(
            'GopiAI-WebView/gopiai/webview/webview_bridge.py',
            'GopiAI-WebView/gopiai/webview/js_bridge.py'
        )
        content = content.replace(
            'GopiAI-Extensions/claude_tools/claude_tools_handler.py',
            'GopiAI-UI/gopiai/ui/components/claude_tools_handler.py'
        )
        content = content.replace(
            'GopiAI.GopiAI-WebView.gopiai.webview.webview_bridge',
            'gopiai.webview.js_bridge'
        )
        content = content.replace(
            'GopiAI.GopiAI-Extensions.claude_tools.claude_tools_handler',
            'gopiai.ui.components.claude_tools_handler'
        )
        content = content.replace(
            'from GopiAI.GopiAI-WebView.gopiai.webview.webview_bridge import WebViewBridge',
            'from gopiai.webview.js_bridge import JavaScriptBridge'
        )
        content = content.replace(
            'from GopiAI.GopiAI-Extensions.claude_tools.claude_tools_handler import ClaudeToolsHandler',
            'from gopiai.ui.components.claude_tools_handler import ClaudeToolsHandler'
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed imports in {file_path}")

def create_fixed_diagnostic():
    """Создает исправленный diagnostic.py"""
    
    content = '''#!/usr/bin/env python3
"""
🩺 Исправленная диагностика GopiAI
==================================

Диагностирует проблемы с правильными путями к файлам.
"""

import sys
import os
from pathlib import Path

def main():
    print("🩺 GopiAI System Diagnostic (Fixed)")
    print("=" * 60)
    
    # 1. Python paths
    print("📂 Python paths:")
    for path in sys.path:
        print(f"  {path}")
    
    # 2. Проверка импортов с правильными путями
    modules_to_check = [
        'gopiai.webview.js_bridge',  # Исправлено
        'gopiai.ui.components.claude_tools_handler',  # Исправлено
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
    
    # 3. Проверка файлов с правильными путями
    files_to_check = [
        'GopiAI-UI/gopiai/ui/main.py',
        'GopiAI-WebView/gopiai/webview/js_bridge.py',  # Исправлено
        'GopiAI-WebView/gopiai/webview/assets/chat.js',
        'GopiAI-UI/gopiai/ui/components/claude_tools_handler.py'  # Исправлено
    ]
    
    print("\\n📄 File existence:")
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
    
    # 4. Environment variables
    print("\\n🌍 Environment variables:")
    env_vars = ['PYTHONPATH', 'QT_LOGGING_RULES', 'PATH']
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"  {var}: {value}")
    
    # 5. Qt components
    print("\\n🔧 Qt Components:")
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        print("  🌐 QtWebEngine: ✅ Available")
    except ImportError:
        print("  🌐 QtWebEngine: ❌ Not available")
    
    try:
        from PySide6.QtWebChannel import QWebChannel
        print("  🌉 WebChannel: ✅ Available")
    except ImportError:
        print("  🌉 WebChannel: ❌ Not available")

if __name__ == "__main__":
    main()
'''
    
    with open("diagnostic_fixed.py", 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Created: diagnostic_fixed.py")

def main():
    """Основная функция исправления"""
    
    print("🚀 GopiAI Bridge Fix Utility")
    print("=" * 60)
    
    try:
        # 1. Исправляем проблему с дублированием bridge
        if fix_bridge_issue():
            print("✅ Bridge issue fixed")
        
        # 2. Исправляем импорты в диагностических файлах 
        fix_imports_in_diagnostic_files()
        
        # 3. Создаем исправленную диагностику
        create_fixed_diagnostic()
        
        print("\\n🎉 ALL FIXES APPLIED!")
        print("\\n📋 NEXT STEPS:")
        print("1. Run: python diagnostic_fixed.py")
        print("2. Run: python GopiAI-UI/gopiai/ui/main.py")
        print("3. Test chat functionality")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
'''