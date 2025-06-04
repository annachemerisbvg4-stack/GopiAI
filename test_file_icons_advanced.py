#!/usr/bin/env python3
"""
Тест иконок файлового проводника
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QMainWindow, QTreeView, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from ui_components.icon_file_system_model import IconFileSystemModel

def test_file_explorer_icons():
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Тест иконок файлового проводника")
    window.resize(400, 600)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Создаём дерево с нашей моделью
    tree_view = QTreeView()
    file_model = IconFileSystemModel(icon_manager=None)  # Без менеджера иконок для теста
    file_model.setRootPath("")
    tree_view.setModel(file_model)
    
    # Настройка отображения
    current_path = os.path.dirname(os.path.abspath(__file__))
    tree_view.setRootIndex(file_model.index(current_path))
    tree_view.hideColumn(1)  # Размер
    tree_view.hideColumn(2)  # Тип
    tree_view.hideColumn(3)  # Дата изменения
    
    # Включаем полосатость для проверки
    tree_view.setAlternatingRowColors(True)
    
    layout.addWidget(tree_view)
    
    window.show()
    
    print("🔍 Тест иконок запущен")
    print("Проверьте отображение иконок в проводнике")
    
    return app.exec()

if __name__ == "__main__":
    test_file_explorer_icons()
