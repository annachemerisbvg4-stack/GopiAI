#!/usr/bin/env python3
"""
Тест маппинга иконок
"""
import sys
import os

# Добавляем пути к модулям
script_dir = os.path.dirname(os.path.abspath(__file__))
gopiai_modules_root = os.path.abspath(script_dir)

module_paths = [
    os.path.join(gopiai_modules_root, "GopiAI-Core"),
    os.path.join(gopiai_modules_root, "GopiAI-Widgets"),
    os.path.join(gopiai_modules_root, "GopiAI-App"),
    os.path.join(gopiai_modules_root, "GopiAI-Extensions"),
    os.path.join(gopiai_modules_root, "rag_memory_system"),
]

for path in module_paths:
    if path not in sys.path:
        sys.path.insert(0, path)

print("Добавленные пути:")
for path in module_paths:
    print(f"  {path} - {'✓' if os.path.exists(path) else '✗'}")

# Импорт маппинга
try:
    from icon_mapping import get_lucide_name, ICON_NAME_MAPPING
    print("✓ Маппинг импортирован успешно")
    print(f"Размер маппинга: {len(ICON_NAME_MAPPING)} иконок")
    
    # Тестируем несколько ключевых маппингов
    test_icons = ["home", "tools", "folder_open", "save", "settings"]
    print("\nТестирование маппинга:")
    for icon in test_icons:
        mapped = get_lucide_name(icon)
        print(f"  {icon} -> {mapped}")
        
    # Тестируем иконки из интерфейса
    interface_icons = ["file-plus", "save-all", "wrench"]  
    print("\nТестирование иконок интерфейса:")
    for icon in interface_icons:
        mapped = get_lucide_name(icon)
        print(f"  {icon} -> {mapped}")
        
except ImportError as e:
    print(f"❌ Ошибка импорта маппинга: {e}")

# Тестируем LucideIconManager
try:
    from gopiai.widgets.managers.lucide_icon_manager import LucideIconManager
    print("\n✓ LucideIconManager импортирован")
    
    icon_manager = LucideIconManager.instance()
    print(f"Статистика LucideIconManager: {icon_manager.get_icon_count()} иконок")
    
    # Тестируем получение иконок через маппинг
    from PySide6.QtCore import QSize
    test_icons = ["home", "tools", "save"]
    print("\nТестирование получения иконок через маппинг:")
    for icon_name in test_icons:
        mapped_name = get_lucide_name(icon_name)
        icon = icon_manager.get_icon(mapped_name, size=QSize(24, 24))
        print(f"  {icon_name} -> {mapped_name}: {'✓ получена' if not icon.isNull() else '✗ пустая'}")
        
except ImportError as e:
    print(f"❌ LucideIconManager недоступен: {e}")

print("\n✅ Тест завершён")
