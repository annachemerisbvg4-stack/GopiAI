#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тесты для расширения статусной строки.
"""

import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QApplication, QMainWindow
from gopiai.extensions.status_bar_extension import add_status_bar, init_status_bar_extension

@pytest.fixture
def app():
    """Создает экземпляр QApplication для тестов."""
    return QApplication([])

@pytest.fixture
def main_window(app):
    """Создает экземпляр QMainWindow для тестов."""
    return QMainWindow()

def test_add_status_bar(main_window):
    """Тестирует добавление статусной строки."""
    # Добавляем статусную строку
    status_bar = add_status_bar(main_window)
    
    # Проверяем, что статусная строка добавлена
    assert main_window.statusBar() is not None
    assert main_window.statusBar() == status_bar
    
    # Проверяем, что метод update_status_message добавлен
    assert hasattr(main_window, "update_status_message")
    
    # Проверяем, что метод update_status_message работает
    main_window.update_status_message("Test Message")
    
    # Находим метку сообщения
    message_label = None
    for widget in status_bar.findChildren(QMainWindow.findChild.__self__.__class__):
        if widget.objectName() == "statusMessageLabel":
            message_label = widget
            break
    
    # Проверяем, что сообщение обновлено
    assert message_label is not None
    assert message_label.text() == "Test Message"

def test_init_status_bar_extension(main_window):
    """Тестирует инициализацию расширения статусной строки."""
    # Мокаем метод add_status_bar
    original_add_status_bar = add_status_bar
    add_status_bar = MagicMock()
    
    try:
        # Инициализируем расширение
        init_status_bar_extension(main_window)
        
        # Проверяем, что add_status_bar был вызван
        add_status_bar.assert_called_once_with(main_window)
    finally:
        # Восстанавливаем оригинальный метод
        globals()["add_status_bar"] = original_add_status_bar
