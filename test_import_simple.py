#!/usr/bin/env python3
"""
Простой тест импорта gopiai_integration после исправлений
"""

import sys
import os

# Добавляем путь к tools как в main.py
tools_path = r"c:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\tools"
if tools_path not in sys.path:
    sys.path.insert(0, tools_path)

print(f"✅ Добавлен путь к tools: {tools_path}")
print(f"📁 Путь существует: {os.path.exists(tools_path)}")

try:
    from gopiai_integration.terminal_tool import set_terminal_widget
    print("🎉 УСПЕХ! Импорт gopiai_integration.terminal_tool работает!")
    print(f"📋 Функция set_terminal_widget: {set_terminal_widget}")
except Exception as e:
    print(f"❌ ОШИБКА импорта: {e}")
    
    # Дополнительная диагностика
    try:
        import gopiai_integration
        print(f"✅ Модуль gopiai_integration найден: {gopiai_integration}")
        print(f"📁 Путь к модулю: {gopiai_integration.__file__}")
    except Exception as e2:
        print(f"❌ Модуль gopiai_integration не найден: {e2}")
