#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Пример использования расширения статусной строки.
"""

import sys
import os

# Добавляем корневую папку проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from gopiai.extensions.status_bar_extension import add_status_bar

class DemoWindow(QMainWindow):
    """Демонстрационное окно для статусной строки."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Демо статусной строки")
        self.resize(600, 400)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем layout
        layout = QVBoxLayout(central_widget)
        
        # Создаем кнопки для обновления статусной строки
        self.info_button = QPushButton("Информационное сообщение")
        self.info_button.clicked.connect(lambda: self.update_status_message("Информационное сообщение"))
        layout.addWidget(self.info_button)
        
        self.warning_button = QPushButton("Предупреждение")
        self.warning_button.clicked.connect(lambda: self.update_status_message("Предупреждение!"))
        layout.addWidget(self.warning_button)
        
        self.error_button = QPushButton("Ошибка")
        self.error_button.clicked.connect(lambda: self.update_status_message("Ошибка!!!"))
        layout.addWidget(self.error_button)
        
        # Добавляем статусную строку
        add_status_bar(self)
        
        # Устанавливаем начальное сообщение
        self.update_status_message("Готово")

def main():
    """Основная функция."""
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
