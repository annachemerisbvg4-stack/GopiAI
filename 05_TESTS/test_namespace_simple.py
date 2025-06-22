#!/usr/bin/env python3
"""
Простой тест импорта namespace-пакета gopiai.ui
"""

import sys
import os

# Добавляем GopiAI-UI в Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
gopiai_ui_path = os.path.join(current_dir, "GopiAI-UI")
if gopiai_ui_path not in sys.path:
    sys.path.insert(0, gopiai_ui_path)

print("Тестируем базовый импорт namespace-пакета gopiai.ui...")

try:
    # Базовый импорт
    import gopiai
    print("✓ Успешно импортирован gopiai")
    
    # Проверим структуру пакета
    print(f"gopiai.__path__: {getattr(gopiai, '__path__', 'не найден')}")
    
    # Импорт UI
    import gopiai.ui
    print("✓ Успешно импортирован gopiai.ui")
    
    # Проверим пути
    ui_path = gopiai.ui.__path__[0] if hasattr(gopiai.ui, '__path__') else "не найден"
    print(f"Путь к gopiai.ui: {ui_path}")
    
    # Проверим, что это действительно символическая ссылка
    if os.path.islink(ui_path):
        target = os.readlink(ui_path)
        print(f"Символическая ссылка указывает на: {target}")
    
    # Проверим содержимое
    import os
    if os.path.exists(ui_path):
        files = os.listdir(ui_path)
        print(f"Содержимое gopiai.ui: {files[:5]}...")  # первые 5 файлов
    
    print("\n🎉 Базовый импорт прошел успешно!")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")
    import traceback
    traceback.print_exc()
