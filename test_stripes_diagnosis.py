#!/usr/bin/env python3
"""
Диагностика проблемы с полосами в файловом проводнике
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QMainWindow, QTreeView, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QCheckBox
from PySide6.QtCore import Qt
from ui_components.icon_file_system_model import IconFileSystemModel

def test_stripes_issue():
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Диагностика полос в проводнике")
    window.resize(600, 700)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Заголовок
    title = QLabel("Тест отображения иконок в файловом проводнике")
    title.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
    layout.addWidget(title)
    
    # Контрольная панель
    controls = QHBoxLayout()
    
    alternating_checkbox = QCheckBox("Полосатые строки")
    alternating_checkbox.setChecked(False)
    controls.addWidget(alternating_checkbox)
    
    layout.addLayout(controls)
    
    # Создаём дерево с нашей моделью
    tree_view = QTreeView()
    
    # Применяем минимальные стили
    tree_view.setStyleSheet("""
        QTreeView {
            background-color: white;
            color: black;
            border: 1px solid gray;
        }
        QTreeView::item {
            height: 20px;
            padding: 2px;
        }
        QTreeView::item:selected {
            background-color: #0078d4;
            color: white;
        }
        QTreeView::item:hover {
            background-color: #f0f0f0;
        }
        QTreeView::item:alternate {
            background-color: #f5f5f5;
        }
    """)
    
    file_model = IconFileSystemModel(icon_manager=None)  # Без менеджера иконок для теста
    file_model.setRootPath("")
    tree_view.setModel(file_model)
    
    # Настройка отображения
    current_path = os.path.dirname(os.path.abspath(__file__))
    tree_view.setRootIndex(file_model.index(current_path))
    tree_view.hideColumn(1)  # Размер
    tree_view.hideColumn(2)  # Тип
    tree_view.hideColumn(3)  # Дата изменения
    
    # Начальная настройка полос
    tree_view.setAlternatingRowColors(False)
    
    # Связываем чекбокс с полосами
    def toggle_alternating(checked):
        tree_view.setAlternatingRowColors(checked)
        print(f"Полосатые строки: {'Включены' if checked else 'Отключены'}")
    
    alternating_checkbox.toggled.connect(toggle_alternating)
    
    layout.addWidget(tree_view)
    
    # Информация
    info = QLabel("Проверьте отображение иконок. Переключайте чекбокс для тестирования полос.")
    info.setStyleSheet("margin: 10px; padding: 5px; background-color: #e6f3ff; border-radius: 3px;")
    layout.addWidget(info)
    
    window.show()
    
    print("🔍 Диагностика полос запущена")
    print("Переключайте чекбокс для проверки влияния полос на отображение")
    
    return app.exec()

if __name__ == "__main__":
    test_stripes_issue()
