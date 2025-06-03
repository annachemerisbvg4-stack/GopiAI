#!/usr/bin/env python3
"""
Тест IconAdapter для проверки работы иконок GopiAI
"""

import sys
import os
from pathlib import Path

# Добавляем пути к модулям GopiAI
current_dir = Path(__file__).parent
module_paths = [
    current_dir / "GopiAI-Core",
    current_dir / "GopiAI-Widgets", 
    current_dir / "GopiAI-App",
    current_dir / "GopiAI-Extensions",
    current_dir / "rag_memory_system"
]

for path in module_paths:
    if path.exists():
        sys.path.insert(0, str(path))
        print(f"✓ Добавлен путь: {path}")

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QIcon
    print("✓ PySide6 импортирован")
except ImportError as e:
    print(f"❌ Ошибка импорта PySide6: {e}")
    sys.exit(1)

try:
    from gopiai.widgets.core.icon_adapter import IconAdapter
    print("✓ IconAdapter импортирован")
    ICONS_AVAILABLE = True
except ImportError as e:
    print(f"❌ IconAdapter недоступен: {e}")
    ICONS_AVAILABLE = False

class IconTestWindow(QMainWindow):
    """Окно для тестирования иконок"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест GopiAI IconAdapter")
        self.setMinimumSize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Заголовок
        title = QLabel("Тест иконок GopiAI IconAdapter")
        layout.addWidget(title)
        
        if not ICONS_AVAILABLE:
            error_label = QLabel("❌ IconAdapter недоступен!")
            layout.addWidget(error_label)
            return
            
        # Тестируем различные иконки
        icon_names = [
            "file-plus",  # новый файл
            "folder",     # папка
            "save",       # сохранить
            "settings",   # настройки
            "terminal",   # терминал
            "code",       # код
            "search",     # поиск
            "home",       # домой
            "mic",        # микрофон
            "cpu",        # процессор
            "tool",       # инструмент
            "edit",       # редактировать
            "check",      # галочка
            "x",          # крестик
        ]
        
        icon_adapter = IconAdapter.instance()
        
        for icon_name in icon_names:
            try:
                # Создаем кнопку с иконкой
                button = QPushButton(f"Иконка: {icon_name}")
                icon = icon_adapter.get_icon(icon_name, size=QSize(24, 24))
                
                if not icon.isNull():
                    button.setIcon(icon)
                    print(f"✓ Иконка {icon_name} загружена")
                else:
                    print(f"⚠ Иконка {icon_name} не найдена")
                    
                layout.addWidget(button)
                
            except Exception as e:
                print(f"❌ Ошибка загрузки иконки {icon_name}: {e}")
                error_button = QPushButton(f"ОШИБКА: {icon_name}")
                layout.addWidget(error_button)

def main():
    """Главная функция"""
    app = QApplication(sys.argv)
    
    window = IconTestWindow()
    window.show()
    
    print("🚀 Тест иконок запущен!")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
