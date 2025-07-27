#!/usr/bin/env python3
"""
Диагностика путей для исправления импорта gopiai_integration
"""

import os
import sys

def debug_paths():
    print("🔍 === ДИАГНОСТИКА ПУТЕЙ ===")
    
    # Эмулируем логику из main.py
    current_file = r"c:\Users\crazy\GOPI_AI_MODULES\GopiAI-UI\gopiai\ui\main.py"
    print(f"📁 Текущий файл: {current_file}")
    
    # Логика из main.py
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(current_file)))))
    print(f"📁 project_root (текущая логика): {project_root}")
    
    # Путь к GopiAI-CrewAI
    crewai_backend_path = os.path.join(project_root, 'GopiAI-CrewAI')
    print(f"📁 crewai_backend_path: {crewai_backend_path}")
    print(f"📁 Существует: {os.path.exists(crewai_backend_path)}")
    
    # Правильный путь
    correct_path = r"c:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI"
    print(f"📁 Правильный путь: {correct_path}")
    print(f"📁 Существует: {os.path.exists(correct_path)}")
    
    # Проверяем gopiai_integration
    gopiai_integration_path = os.path.join(correct_path, 'tools', 'gopiai_integration')
    print(f"📁 gopiai_integration: {gopiai_integration_path}")
    print(f"📁 Существует: {os.path.exists(gopiai_integration_path)}")
    
    # Проверяем __init__.py
    init_file = os.path.join(gopiai_integration_path, '__init__.py')
    print(f"📁 __init__.py: {init_file}")
    print(f"📁 Существует: {os.path.exists(init_file)}")
    
    # Проверяем terminal_tool.py
    terminal_tool = os.path.join(gopiai_integration_path, 'terminal_tool.py')
    print(f"📁 terminal_tool.py: {terminal_tool}")
    print(f"📁 Существует: {os.path.exists(terminal_tool)}")
    
    print("\n🔧 === ИСПРАВЛЕНИЕ ===")
    print("Нужно изменить логику формирования project_root в main.py")
    print(f"Вместо: {project_root}")
    print(f"Должно быть: c:\\Users\\crazy\\GOPI_AI_MODULES")

if __name__ == "__main__":
    debug_paths()
