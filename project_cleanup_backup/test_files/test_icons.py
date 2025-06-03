#!/usr/bin/env python3
"""
GopiAI Standalone Interface - тестовая версия для исправления иконок
=====================================

Минимальная версия для тестирования системы иконок LucideIconManager
"""

import sys
import os
import warnings
from pathlib import Path

# Добавляем пути к модулям GopiAI в sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
module_paths = [
    os.path.join(script_dir, "GopiAI-Core"),
    os.path.join(script_dir, "GopiAI-Widgets"),
    os.path.join(script_dir, "GopiAI-App"),
    os.path.join(script_dir, "GopiAI-Extensions"),
    os.path.join(script_dir, "rag_memory_system"),
]

for path in module_paths:
    if path not in sys.path:
        sys.path.insert(0, path)

print("Добавленные пути в sys.path:")
for p in module_paths:
    print(f"- {p} (существует: {os.path.exists(p)})")

# Простые импорты
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

# =============================================================================
# Менеджер иконок LucideIconManager
# =============================================================================

class LucideIconManager:
    _instance = None
    
    def __init__(self):
        self.icons_path = Path(__file__).parent / "node_modules" / "lucide-static" / "icons"
        self._icon_cache = {}
        print(f"🔍 LucideIconManager: ищем иконки в {self.icons_path}")
        print(f"📂 Путь существует: {self.icons_path.exists()}")
        if self.icons_path.exists():
            icon_files = list(self.icons_path.glob("*.svg"))
            print(f"📊 Найдено {len(icon_files)} SVG файлов")
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def get_icon(self, icon_name: str, color_override=None, size=None):
        """Получить иконку по имени"""
        if icon_name in self._icon_cache:
            return self._icon_cache[icon_name]
        
        # Ищем SVG файл
        svg_path = self.icons_path / f"{icon_name}.svg"
        
        if svg_path.exists():
            # Создаем QIcon из SVG файла
            icon = QIcon(str(svg_path))
            self._icon_cache[icon_name] = icon
            print(f"✅ Загружена иконка: {icon_name}")
            return icon
        else:
            print(f"❌ Иконка не найдена: {icon_name} (путь: {svg_path})")
            # Возвращаем пустую иконку
            empty_icon = QIcon()
            self._icon_cache[icon_name] = empty_icon
            return empty_icon

# =============================================================================
# Импорт маппинга иконок
# =============================================================================

try:
    from icon_mapping import get_lucide_name
    print("✅ Модуль icon_mapping импортирован")
except ImportError as e:
    print(f"⚠ Модуль icon_mapping недоступен: {e}")
    def get_lucide_name(original_name):
        return original_name

# =============================================================================
# Тестовое окно
# =============================================================================

class IconTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест системы иконок LucideIconManager")
        self.setGeometry(100, 100, 600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Заголовок
        title = QLabel("🧪 Тест системы иконок LucideIconManager")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Инициализируем менеджер иконок
        self.icon_manager = LucideIconManager.instance()
        
        # Тестируем иконки из маппинга
        test_icons = [
            ("file-plus", "Новый файл"),
            ("folder-open", "Открыть папку"),  
            ("save", "Сохранить"),
            ("wrench", "Инструменты"),
            ("mic", "Микрофон"),
            ("cpu", "Процессор"),
            ("settings", "Настройки"),
            ("search", "Поиск"),
            ("download", "Скачать"),
            ("upload", "Загрузить")
        ]
        
        for icon_name, description in test_icons:
            # Получаем маппинг
            lucide_name = get_lucide_name(icon_name)
            print(f"🔍 Маппинг иконки: {icon_name} -> {lucide_name}")
            
            # Получаем иконку
            icon = self.icon_manager.get_icon(lucide_name)
            
            # Создаем кнопку с иконкой
            button = QPushButton(f"{description} ({icon_name})")
            button.setIcon(icon)
            button.setStyleSheet("QPushButton { padding: 8px; margin: 2px; text-align: left; }")
            
            # Проверяем что иконка загружена
            is_loaded = not icon.isNull()
            if is_loaded:
                button.setStyleSheet(button.styleSheet() + "background-color: #e8f5e8;")
                print(f"✅ Установлена иконка {icon_name}: True")
            else:
                button.setStyleSheet(button.styleSheet() + "background-color: #ffe8e8;")
                print(f"❌ Установлена иконка {icon_name}: False")
            
            layout.addWidget(button)
        
        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

def main():
    app = QApplication(sys.argv)
    
    # Создаем и показываем тестовое окно
    window = IconTestWindow()
    window.show()
    
    print("🚀 Тестовое окно иконок запущено!")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())