#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тесты для виджета CardWidget.
"""

import sys
import os
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Добавляем корневую папку проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gopiai.widgets.card_widget import CardWidget


@pytest.fixture
def app():
    """Создает экземпляр QApplication для тестов."""
    return QApplication([])


@pytest.fixture
def card_widget(app):
    """Создает экземпляр CardWidget для тестов."""
    return CardWidget("Тестовый заголовок", "Тестовое содержимое")


def test_card_widget_creation(card_widget):
    """Тестирует создание CardWidget."""
    assert card_widget is not None
    assert card_widget.title_label.text() == "Тестовый заголовок"
    assert card_widget.content_label.text() == "Тестовое содержимое"


def test_card_widget_set_content(card_widget):
    """Тестирует установку содержимого."""
    card_widget.set_content("Новое содержимое")
    assert card_widget.content_label.text() == "Новое содержимое"


def test_card_widget_set_title(card_widget):
    """Тестирует установку заголовка."""
    card_widget.set_title("Новый заголовок")
    assert card_widget.title_label.text() == "Новый заголовок"


def test_card_widget_add_button(card_widget, qtbot):
    """Тестирует добавление кнопки."""
    # Счетчик для проверки вызова callback
    counter = [0]
    
    def button_callback():
        counter[0] += 1
    
    # Добавляем кнопку
    button = card_widget.add_button("Тестовая кнопка", button_callback)
    
    # Проверяем, что кнопка добавлена
    assert button is not None
    assert button.text() == "Тестовая кнопка"
    
    # Проверяем, что callback вызывается при клике
    qtbot.mouseClick(button, Qt.LeftButton)
    assert counter[0] == 1


def test_card_widget_clear_buttons(card_widget):
    """Тестирует очистку кнопок."""
    # Добавляем несколько кнопок
    card_widget.add_button("Кнопка 1")
    card_widget.add_button("Кнопка 2")
    card_widget.add_button("Кнопка 3")
    
    # Проверяем, что кнопки добавлены
    assert card_widget.buttons_layout.count() == 3
    
    # Очищаем кнопки
    card_widget.clear_buttons()
    
    # Проверяем, что кнопки удалены
    assert card_widget.buttons_layout.count() == 0


def test_card_widget_clicked_signal(card_widget, qtbot):
    """Тестирует сигнал clicked."""
    # Счетчик для проверки вызова сигнала
    counter = [0]
    
    def on_clicked():
        counter[0] += 1
    
    # Подключаем сигнал
    card_widget.clicked.connect(on_clicked)
    
    # Эмулируем клик по карточке
    qtbot.mouseClick(card_widget, Qt.LeftButton)
    
    # Проверяем, что сигнал был вызван
    assert counter[0] == 1


def test_card_widget_set_style(card_widget):
    """Тестирует установку стиля."""
    # Устанавливаем стиль
    card_widget.set_style(
        background="#f0f0f0",
        border_color="#cccccc",
        border_radius=10,
        title_color="#0066cc",
        content_color="#333333",
        title_size=16
    )
    
    # Проверяем, что стиль установлен
    style = card_widget.styleSheet()
    assert "background-color: #f0f0f0" in style
    assert "border: 1px solid #cccccc" in style
    assert "border-radius: 10px" in style
    assert "color: #0066cc" in style
    assert "color: #333333" in style
    assert "font-size: 16px" in style
