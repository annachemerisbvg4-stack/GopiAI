"""
Прямой тест LucideIconManager без IconAdapter.
"""

# Настройка путей
import sys
import os

# Добавляем пути к GopiAI модулям
gopiai_paths = [
    r"C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Core",
    r"C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Widgets", 
    r"C:\Users\crazy\GOPI_AI_MODULES\GopiAI-App",
    r"C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Extensions",
    r"C:\Users\crazy\GOPI_AI_MODULES\rag_memory_system"
]

for path in gopiai_paths:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)
        print(f"✓ Добавлен путь: {path}")

# Импорт PySide6
try:
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication
    print("✓ PySide6 импортирован")
except ImportError as e:
    print(f"❌ PySide6 недоступен: {e}")
    exit(1)

# Инициализация GopiAI
import gopiai
print(f"🚀 GopiAI v{gopiai.__version__} загружен!")

# ПРЯМОЙ импорт LucideIconManager
try:
    from gopiai.widgets.managers.lucide_icon_manager import LucideIconManager
    print("✓ LucideIconManager импортирован напрямую!")
    
    # Создаём QApplication (нужно для QIcon)
    app = QApplication([])
    
    # Тестируем LucideIconManager
    manager = LucideIconManager.instance()
    print(f"✓ LucideIconManager создан: {manager}")
    print(f"✓ Путь к иконкам: {manager.icons_dir}")
    print(f"✓ Найдено иконок: {len(manager.available_icons)}")
    
    # Тестируем получение иконки
    test_icon = manager.get_icon("home", size=QSize(24, 24))
    print(f"✓ Тест иконка 'home': {test_icon}")
    print(f"✓ Иконка пустая: {test_icon.isNull()}")
    
    print("🎉 LucideIconManager работает!")
    
except ImportError as e:
    print(f"❌ LucideIconManager недоступен: {e}")
except Exception as e:
    print(f"❌ Ошибка тестирования LucideIconManager: {e}")

print("🚀 Тест завершён!")
