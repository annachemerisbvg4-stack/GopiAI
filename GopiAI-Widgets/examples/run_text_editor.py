#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестовое приложение для демонстрации работы TextEditorWidget.
"""

import sys
import os

# Добавляем корневую папку проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from gopiai.widgets.text_editor import TextEditorWidget

def main():
    """Основная функция тестового приложения."""
    app = QApplication(sys.argv)
    
    # Создаем главное окно
    main_window = QMainWindow()
    main_window.setWindowTitle("Тестовый редактор текста")
    main_window.resize(800, 600)
    
    # Создаем центральный виджет
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    
    # Создаем layout
    layout = QVBoxLayout(central_widget)
    
    # Создаем редактор текста
    editor = TextEditorWidget()
    layout.addWidget(editor)
    
    # Показываем окно
    main_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
