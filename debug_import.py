#!/usr/bin/env python3
"""
Детальная диагностика проблемы с импортом gopiai_integration
"""

import os
import sys

def debug_import():
    print("🔍 === ДЕТАЛЬНАЯ ДИАГНОСТИКА ИМПОРТА ===")
    
    # Добавляем путь как в main.py
    crewai_path = r"c:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI"
    if crewai_path not in sys.path:
        sys.path.insert(0, crewai_path)
    
    print(f"📁 Добавлен путь: {crewai_path}")
    print(f"📁 Путь существует: {os.path.exists(crewai_path)}")
    
    # Проверяем содержимое GopiAI-CrewAI
    print(f"\n📋 Содержимое {crewai_path}:")
    if os.path.exists(crewai_path):
        for item in os.listdir(crewai_path):
            item_path = os.path.join(crewai_path, item)
            if os.path.isdir(item_path):
                print(f"  📁 {item}/")
            else:
                print(f"  📄 {item}")
    
    # Проверяем tools
    tools_path = os.path.join(crewai_path, 'tools')
    print(f"\n📋 Содержимое {tools_path}:")
    if os.path.exists(tools_path):
        for item in os.listdir(tools_path):
            item_path = os.path.join(tools_path, item)
            if os.path.isdir(item_path):
                print(f"  📁 {item}/")
            else:
                print(f"  📄 {item}")
    
    # Проверяем gopiai_integration
    gopiai_path = os.path.join(tools_path, 'gopiai_integration')
    print(f"\n📋 Содержимое {gopiai_path}:")
    if os.path.exists(gopiai_path):
        for item in os.listdir(gopiai_path):
            item_path = os.path.join(gopiai_path, item)
            if os.path.isdir(item_path):
                print(f"  📁 {item}/")
            else:
                print(f"  📄 {item}")
    
    # Проверяем __init__.py файлы
    print(f"\n🔍 Проверка __init__.py файлов:")
    
    init_files = [
        os.path.join(crewai_path, '__init__.py'),
        os.path.join(tools_path, '__init__.py'),
        os.path.join(gopiai_path, '__init__.py')
    ]
    
    for init_file in init_files:
        exists = os.path.exists(init_file)
        print(f"  {'✅' if exists else '❌'} {init_file}")
        if exists:
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"    📄 Размер: {len(content)} символов")
                    if content.strip():
                        print(f"    📝 Содержимое: {content[:100]}...")
                    else:
                        print(f"    📝 Пустой файл")
            except Exception as e:
                print(f"    ❌ Ошибка чтения: {e}")
    
    # Проверяем terminal_tool.py
    terminal_tool_path = os.path.join(gopiai_path, 'terminal_tool.py')
    print(f"\n🔍 Проверка terminal_tool.py:")
    exists = os.path.exists(terminal_tool_path)
    print(f"  {'✅' if exists else '❌'} {terminal_tool_path}")
    
    # Пробуем импорт поэтапно
    print(f"\n🧪 Тестирование импорта:")
    
    try:
        print("  1. Импорт tools...")
        import tools
        print("  ✅ import tools - успешно")
        print(f"     📁 tools.__file__ = {getattr(tools, '__file__', 'не определен')}")
        print(f"     📁 tools.__path__ = {getattr(tools, '__path__', 'не определен')}")
    except Exception as e:
        print(f"  ❌ import tools - ошибка: {e}")
    
    try:
        print("  2. Импорт tools.gopiai_integration...")
        from tools import gopiai_integration
        print("  ✅ from tools import gopiai_integration - успешно")
    except Exception as e:
        print(f"  ❌ from tools import gopiai_integration - ошибка: {e}")
    
    try:
        print("  3. Импорт gopiai_integration напрямую...")
        import gopiai_integration
        print("  ✅ import gopiai_integration - успешно")
    except Exception as e:
        print(f"  ❌ import gopiai_integration - ошибка: {e}")
    
    try:
        print("  4. Импорт terminal_tool...")
        from gopiai_integration.terminal_tool import set_terminal_widget
        print("  ✅ from gopiai_integration.terminal_tool import set_terminal_widget - успешно")
    except Exception as e:
        print(f"  ❌ from gopiai_integration.terminal_tool import set_terminal_widget - ошибка: {e}")
    
    print(f"\n📋 sys.path:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")

if __name__ == "__main__":
    debug_import()
