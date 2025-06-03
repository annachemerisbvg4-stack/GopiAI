#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тесты для minimal_app.py
"""

import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QApplication
from gopiai.core.minimal_app import FramelessMainWindow

@pytest.fixture
def app():
    """Создает экземпляр QApplication для тестов."""
    return QApplication([])

@pytest.fixture
def main_window(app):
    """Создает экземпляр FramelessMainWindow для тестов."""
    return FramelessMainWindow()

def test_main_window_creation(main_window):
    """Тестирует создание главного окна."""
    assert main_window is not None
    assert hasattr(main_window, 'tab_widget')
    assert hasattr(main_window, 'titlebar_with_menu')

def test_main_window_methods(main_window):
    """Тестирует наличие необходимых методов."""
    assert hasattr(main_window, 'open_text_editor')
    assert hasattr(main_window, 'close_tab')
    assert hasattr(main_window, 'update_title')
    assert hasattr(main_window, 'maximize_window')
    assert hasattr(main_window, 'restore_window')

def test_open_text_editor(main_window):
    """Тестирует открытие текстового редактора."""
    # Запоминаем начальное количество вкладок
    initial_tab_count = main_window.tab_widget.count()
    
    # Открываем новый редактор
    main_window.open_text_editor()
    
    # Проверяем, что добавилась новая вкладка
    assert main_window.tab_widget.count() == initial_tab_count + 1
    
    # Проверяем, что текущая вкладка - это новая вкладка
    assert main_window.tab_widget.currentIndex() == initial_tab_count
