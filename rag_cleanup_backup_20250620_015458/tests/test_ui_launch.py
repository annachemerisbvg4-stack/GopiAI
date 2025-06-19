#!/usr/bin/env python3
"""
Тест запуска UI через namespace-пакет gopiai.ui
"""

import sys
import os

# Добавляем GopiAI-UI в Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
gopiai_ui_path = os.path.join(current_dir, "GopiAI-UI")
if gopiai_ui_path not in sys.path:
    sys.path.insert(0, gopiai_ui_path)

print("Тестируем запуск UI через namespace-пакет...")

try:
    # Импортируем UI модуль
    import gopiai.ui
    print("✓ gopiai.ui импортирован")
    
    # Проверим, что main.py доступен
    import gopiai.ui.main
    print("✓ gopiai.ui.main импортирован")
    
    # Импортируем базовые компоненты
    from gopiai.ui.base import BaseWindow
    print("✓ BaseWindow доступен")
    
    # Импортируем иконки
    from gopiai.ui.utils import UniversalIconManager
    print("✓ UniversalIconManager доступен")
    
    print("\n🎉 Все компоненты namespace-пакета доступны для запуска!")
    print("Для полного тестирования запустите: python -m gopiai.ui.main")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")
    import traceback
    traceback.print_exc()
