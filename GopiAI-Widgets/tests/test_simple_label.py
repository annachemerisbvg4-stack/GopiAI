#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тесты для SimpleLabel.
"""

import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from gopiai.widgets.simple_label import SimpleLabel

@pytest.fixture
def app():
    """Создает экземпляр QApplication для тестов."""
    return QApplication([])

@pytest.fixture
def label(app):
    """Создает экземпляр SimpleLabel для тестов."""
    return SimpleLabel("Test Label")

def test_label_creation(label):
    """Тестирует создание метки."""
    assert label is not None
    assert label.text() == "Test Label"

def test_label_click(label):
    """Тестирует сигнал clicked."""
    # Создаем мок-функцию для обработки сигнала
    callback = MagicMock()
    label.clicked.connect(callback)
    
    # Эмулируем клик на метку
    label.mousePressEvent(MagicMock(button=lambda: Qt.MouseButton.LeftButton))
    
    # Проверяем, что сигнал был вызван
    callback.assert_called_once()

def test_label_auto_update(label, app):
    """Тестирует автоматическое обновление текста."""
    # Создаем функцию для обновления текста
    update_function = MagicMock(return_value="Updated Text")
    
    # Устанавливаем автообновление
    label.set_auto_update(update_function, 100)
    
    # Проверяем, что таймер создан
    assert label._timer is not None
    
    # Останавливаем автообновление
    label.stop_auto_update()
    
    # Проверяем, что таймер остановлен
    assert not label._timer.isActive()

def test_label_style(label):
    """Тестирует установку стиля."""
    # Устанавливаем стиль
    label.set_style(
        background_color="#3498db",
        text_color="#ffffff",
        border="1px solid #2980b9"
    )
    
    # Проверяем, что стиль установлен
    style = label.styleSheet()
    assert "background-color: #3498db" in style
    assert "color: #ffffff" in style
    assert "border: 1px solid #2980b9" in style
