#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Пример использования SimpleLabel.
"""

import sys
import os
import time

# Добавляем корневую папку проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from gopiai.widgets.simple_label import SimpleLabel

class DemoWindow(QMainWindow):
    """Демонстрационное окно для SimpleLabel."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Демо SimpleLabel")
        self.resize(400, 300)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем layout
        layout = QVBoxLayout(central_widget)
        
        # Создаем простую метку
        self.label = SimpleLabel("Нажмите на меня!")
        self.label.clicked.connect(self.on_label_clicked)
        layout.addWidget(self.label)
        
        # Создаем метку с автообновлением
        self.time_label = SimpleLabel("Текущее время")
        self.time_label.set_auto_update(self.get_current_time, 1000)
        layout.addWidget(self.time_label)
        
        # Создаем метку с настраиваемым стилем
        self.styled_label = SimpleLabel("Стилизованная метка")
        self.styled_label.set_style(
            background_color="#3498db",
            text_color="#ffffff",
            border="1px solid #2980b9"
        )
        layout.addWidget(self.styled_label)
        
        # Создаем кнопку для изменения стиля
        self.style_button = QPushButton("Изменить стиль")
        self.style_button.clicked.connect(self.change_style)
        layout.addWidget(self.style_button)
        
        # Флаг для отслеживания текущего стиля
        self.current_style = 0
    
    def on_label_clicked(self):
        """Обработчик клика на метку."""
        self.label.setText("Метка была нажата!")
    
    def get_current_time(self):
        """Возвращает текущее время."""
        return f"Текущее время: {time.strftime('%H:%M:%S')}"
    
    def change_style(self):
        """Изменяет стиль метки."""
        styles = [
            {
                "background_color": "#3498db",
                "text_color": "#ffffff",
                "border": "1px solid #2980b9"
            },
            {
                "background_color": "#e74c3c",
                "text_color": "#ffffff",
                "border": "1px solid #c0392b"
            },
            {
                "background_color": "#2ecc71",
                "text_color": "#ffffff",
                "border": "1px solid #27ae60"
            }
        ]
        
        # Выбираем следующий стиль
        self.current_style = (self.current_style + 1) % len(styles)
        style = styles[self.current_style]
        
        # Применяем стиль
        self.styled_label.set_style(**style)

def main():
    """Основная функция."""
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
