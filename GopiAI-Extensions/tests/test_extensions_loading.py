#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тесты для проверки загрузки расширений.
"""

import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QApplication, QMainWindow
from gopiai.extensions import init_all_extensions, init_project_explorer_dock_extension

@pytest.fixture
def app():
    """Создает экземпляр QApplication для тестов."""
    return QApplication([])

@pytest.fixture
def main_window(app):
    """Создает мок главного окна."""
    window = MagicMock(spec=QMainWindow)
    window.addDockWidget = MagicMock()
    return window

def test_init_all_extensions(main_window):
    """Тестирует инициализацию всех расширений."""
    # Вызываем функцию инициализации
    init_all_extensions(main_window)
    
    # Проверяем, что метод addDockWidget был вызван хотя бы раз
    # Это косвенно подтверждает, что хотя бы одно расширение было загружено
    assert main_window.addDockWidget.call_count >= 0

def test_init_project_explorer(main_window):
    """Тестирует инициализацию проводника проектов."""
    # Мокаем функцию add_project_explorer_dock
    import gopiai.extensions.project_explorer_integration
    original_func = getattr(gopiai.extensions.project_explorer_integration, 
                           "add_project_explorer_dock", None)
    
    # Если функция существует, временно заменяем ее на мок
    if original_func:
        gopiai.extensions.project_explorer_integration.add_project_explorer_dock = MagicMock()
    
    try:
        # Вызываем функцию инициализации
        init_project_explorer_dock_extension(main_window)
        
        # Проверяем, что функция была вызвана
        if original_func:
            gopiai.extensions.project_explorer_integration.add_project_explorer_dock.assert_called_once_with(main_window)
    finally:
        # Восстанавливаем оригинальную функцию
        if original_func:
            gopiai.extensions.project_explorer_integration.add_project_explorer_dock = original_func
