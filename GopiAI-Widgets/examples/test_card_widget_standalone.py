#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестирование CardWidget без зависимостей от других модулей.
"""

import sys
import os

# Добавляем путь к текущей папке
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

# Импортируем CardWidget напрямую
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gopiai.widgets.card_widget import CardWidget


class TestWindow(QMainWindow):
    """Тестовое окно для CardWidget."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Тест CardWidget")
        self.setGeometry(100, 100, 500, 400)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем лейаут
        layout = QVBoxLayout(central_widget)
        
        # Создаем CardWidget
        card = CardWidget("Тестовая карточка", "Это тестовая карточка для проверки работы CardWidget.")
        card.clicked.connect(lambda: print("Карточка нажата"))
        card.add_button("Кнопка 1", lambda: print("Нажата кнопка 1"))
        card.add_button("Кнопка 2", lambda: print("Нажата кнопка 2"))
        
        layout.addWidget(card)
        
        # Создаем стилизованную карточку
        styled_card = CardWidget("Стилизованная карточка", "Эта карточка имеет настроенный стиль.")
        styled_card.set_style(
            background="#f0f8ff",
            border_color="#b0c4de",
            border_radius=12,
            title_color="#0066cc",
            content_color="#333333",
            title_size=16
        )
        
        layout.addWidget(styled_card)


def main():
    """Основная функция тестирования."""
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
