#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Пример использования виджета CardWidget.
"""

import sys
import os
import datetime

# Добавляем корневую папку проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from gopiai.widgets.card_widget import CardWidget
from gopiai.widgets.simple_label import SimpleLabel


class MainWindow(QMainWindow):
    """Главное окно для демонстрации CardWidget."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Демонстрация CardWidget")
        self.setGeometry(100, 100, 800, 600)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем основной лейаут
        main_layout = QVBoxLayout(central_widget)
        
        # Добавляем заголовок
        title_label = SimpleLabel("Демонстрация CardWidget")
        title_label.set_style(font_size=18, bold=True, color="#0066cc")
        main_layout.addWidget(title_label)
        
        # Добавляем описание
        description_label = QLabel(
            "CardWidget - это виджет для отображения информации в виде карточек. "
            "Каждая карточка имеет заголовок, содержимое и может содержать кнопки действий."
        )
        description_label.setWordWrap(True)
        main_layout.addWidget(description_label)
        
        # Создаем область прокрутки для карточек
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        main_layout.addWidget(scroll_area, 1)  # 1 = растягивается
        
        # Создаем контейнер для карточек
        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setContentsMargins(10, 10, 10, 10)
        cards_layout.setSpacing(15)
        scroll_area.setWidget(cards_container)
        
        # Добавляем карточки
        self.add_basic_card(cards_layout)
        self.add_styled_card(cards_layout)
        self.add_card_with_buttons(cards_layout)
        self.add_card_with_time(cards_layout)
        self.add_card_with_counter(cards_layout)
        
        # Добавляем информацию о времени
        time_label = SimpleLabel()
        time_label.set_update_function(lambda: f"Текущее время: {datetime.datetime.now().strftime('%H:%M:%S')}")
        time_label.set_update_interval(1000)  # Обновление каждую секунду
        main_layout.addWidget(time_label)
    
    def add_basic_card(self, layout):
        """Добавляет базовую карточку."""
        card = CardWidget(
            "Базовая карточка",
            "Это базовая карточка без дополнительных настроек. "
            "Она имеет заголовок и содержимое."
        )
        layout.addWidget(card)
    
    def add_styled_card(self, layout):
        """Добавляет стилизованную карточку."""
        card = CardWidget(
            "Стилизованная карточка",
            "Эта карточка имеет настроенный стиль с другими цветами и радиусом скругления."
        )
        card.set_style(
            background="#f0f8ff",
            border_color="#b0c4de",
            border_radius=12,
            title_color="#0066cc",
            content_color="#333333",
            title_size=16
        )
        layout.addWidget(card)
    
    def add_card_with_buttons(self, layout):
        """Добавляет карточку с кнопками."""
        card = CardWidget(
            "Карточка с кнопками",
            "Эта карточка содержит кнопки действий, которые можно нажимать."
        )
        
        # Добавляем кнопки
        card.add_button("Подробнее", lambda: self.show_message(card, "Нажата кнопка 'Подробнее'"))
        card.add_button("Удалить", lambda: self.show_message(card, "Нажата кнопка 'Удалить'"))
        card.add_button("Отмена", lambda: self.show_message(card, "Нажата кнопка 'Отмена'"))
        
        layout.addWidget(card)
    
    def add_card_with_time(self, layout):
        """Добавляет карточку с автообновляемым временем."""
        card = CardWidget(
            "Карточка с временем",
            "Эта карточка автоматически обновляет свое содержимое, показывая текущее время."
        )
        
        # Создаем SimpleLabel для отображения времени
        time_label = SimpleLabel()
        time_label.set_update_function(lambda: f"Текущее время: {datetime.datetime.now().strftime('%H:%M:%S')}")
        time_label.set_update_interval(1000)  # Обновление каждую секунду
        time_label.set_style(font_size=14, bold=True, color="#0066cc")
        
        # Добавляем SimpleLabel в карточку
        card.layout.addWidget(time_label)
        
        layout.addWidget(card)
    
    def add_card_with_counter(self, layout):
        """Добавляет карточку со счетчиком."""
        card = CardWidget(
            "Карточка со счетчиком",
            "Эта карточка содержит счетчик, который можно увеличивать и уменьшать."
        )
        
        # Создаем контейнер для счетчика
        counter_container = QWidget()
        counter_layout = QHBoxLayout(counter_container)
        counter_layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем кнопку уменьшения
        decrease_button = card.add_button("-", None)
        counter_layout.addWidget(decrease_button)
        
        # Создаем метку счетчика
        counter_label = QLabel("0")
        counter_label.setAlignment(Qt.AlignCenter)
        counter_label.setMinimumWidth(50)
        counter_layout.addWidget(counter_label)
        
        # Создаем кнопку увеличения
        increase_button = card.add_button("+", None)
        counter_layout.addWidget(increase_button)
        
        # Удаляем кнопки из контейнера кнопок карточки
        card.clear_buttons()
        
        # Добавляем контейнер счетчика в карточку
        card.layout.addWidget(counter_container)
        
        # Добавляем функциональность кнопкам
        def decrease_counter():
            value = int(counter_label.text())
            counter_label.setText(str(max(0, value - 1)))
        
        def increase_counter():
            value = int(counter_label.text())
            counter_label.setText(str(value + 1))
        
        decrease_button.clicked.connect(decrease_counter)
        increase_button.clicked.connect(increase_counter)
        
        layout.addWidget(card)
    
    def show_message(self, card, message):
        """Показывает сообщение в карточке."""
        card.set_content(message)


def main():
    """Основная функция примера."""
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
