#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест интеграции browser-use с чатом.

Запускает чат и проверяет, что браузерные команды распознаются.
"""

import sys
import os
from pathlib import Path

# Добавляем пути
script_dir = os.path.dirname(os.path.abspath(__file__))
gopiai_modules_root = os.path.dirname(script_dir)

module_paths = [
    os.path.join(gopiai_modules_root, "GopiAI-App"),
    os.path.join(gopiai_modules_root, "GopiAI-Core"),
    os.path.join(gopiai_modules_root, "GopiAI-UI"),
    gopiai_modules_root,
]

for path in module_paths:
    if path not in sys.path:
        sys.path.insert(0, path)

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

def main():
    print("🧪 Тестирование интеграции browser-use с чатом...")
    
    # Проверяем browser-use
    try:
        import browser_use
        print(f"✅ browser-use найден: версия {getattr(browser_use, '__version__', 'неизвестно')}")
    except ImportError:
        print("❌ browser-use не установлен!")
        return 1
    
    # Проверяем компоненты GopiAI
    try:
        from gopiai.ui.components.chat_widget import ChatWidget
        print("✅ ChatWidget импортирован")
    except ImportError as e:
        print(f"❌ Не удалось импортировать ChatWidget: {e}")
        return 1
    
    try:
        from gopiai.ui.components.crewai_client import CrewAIClient
        print("✅ CrewAIClient импортирован")
    except ImportError as e:
        print(f"❌ Не удалось импортировать CrewAIClient: {e}")
        return 1
    
    # Проверяем browser адаптеры
    try:
        from gopiai.app.utils.browser_adapters import get_browser_adapter
        print("✅ Browser адаптеры доступны")
    except Exception as e:
        print(f"⚠️ Browser адаптеры недоступны: {e}")
        # Это не критично для основной функциональности
    
    # Тестируем распознавание браузерных команд
    try:
        client = CrewAIClient()
        test_commands = [
            "Открой сайт google.com",
            "Перейди на github.com",
            "Найди кнопку входа",
            "Привет, как дела?",  # Обычная команда
        ]
        
        print("\n🔍 Тестирование распознавания команд:")
        for cmd in test_commands:
            result = client.process_request(cmd)
            is_browser = isinstance(result, dict) and result.get("impl") == "browser-use"
            status = "🌐 БРАУЗЕР" if is_browser else "💬 ОБЫЧНЫЙ"
            print(f"  {status}: {cmd}")
            
    except Exception as e:
        print(f"⚠️ Ошибка при тестировании команд: {e}")
    
    print("\n✅ Базовые проверки завершены!")
    print("\n🎯 Для полного тестирования:")
    print("   1. Запустите основное UI: python gopiai/ui/main.py")
    print("   2. В чате попробуйте команды:")
    print("      • 'Открой сайт google.com'")
    print("      • 'Перейди на github.com'")
    print("      • 'Найди на странице кнопку входа'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
