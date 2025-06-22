#!/usr/bin/env python3
"""
Тест импорта namespace-пакета gopiai.ui
"""

import sys
import os

# Добавляем GopiAI-UI в Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
gopiai_ui_path = os.path.join(current_dir, "GopiAI-UI")
if gopiai_ui_path not in sys.path:
    sys.path.insert(0, gopiai_ui_path)

print("Тестируем импорт namespace-пакета gopiai.ui...")
print(f"PYTHONPATH содержит: {gopiai_ui_path}")

try:
    # Базовый импорт
    import gopiai.ui
    print("✓ Успешно импортирован gopiai.ui")
      # Импорт базовых компонентов
    from gopiai.ui.base import BaseWindow, WindowRegistry
    print("✓ Успешно импортированы базовые компоненты")
    
    # Импорт утилит
    from gopiai.ui.utils import UniversalIconManager
    print("✓ Успешно импортированы утилиты")
    
    # Импорт компонентов
    from gopiai.ui.components import MainMenuWidget
    print("✓ Успешно импортированы компоненты")
    
    # Проверим пути
    import os
    ui_path = gopiai.ui.__path__[0] if hasattr(gopiai.ui, '__path__') else "не найден"
    print(f"Путь к gopiai.ui: {ui_path}")
    
    # Проверим, что это действительно символическая ссылка
    if os.path.islink(ui_path):
        target = os.readlink(ui_path)
        print(f"Символическая ссылка указывает на: {target}")
    
    print("\n🎉 Все импорты прошли успешно! Namespace-пакет работает корректно.")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")
