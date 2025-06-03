#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тесты для TextEditorWidget.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock

# Добавляем корневую папку проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PySide6.QtWidgets import QApplication
from gopiai.widgets.text_editor import TextEditorWidget

@pytest.fixture
def app():
    """Создает экземпляр QApplication для тестов."""
    return QApplication([])

@pytest.fixture
def editor(app):
    """Создает экземпляр TextEditorWidget для тестов."""
    return TextEditorWidget()

def test_editor_creation(editor):
    """Тестирует создание редактора."""
    assert editor is not None
    assert hasattr(editor, 'text_editor')
    assert editor.current_file is None
    assert editor.current_encoding == "utf-8"

def test_editor_methods(editor):
    """Тестирует наличие необходимых методов."""
    assert hasattr(editor, 'open_file')
    assert hasattr(editor, 'save_file')
    assert hasattr(editor, 'save_file_as')
    assert hasattr(editor, 'undo')
    assert hasattr(editor, 'redo')
    assert hasattr(editor, 'cut')
    assert hasattr(editor, 'copy')
    assert hasattr(editor, 'paste')
    assert hasattr(editor, 'delete')
    assert hasattr(editor, 'select_all')

def test_editor_signal(editor):
    """Тестирует сигнал file_name_changed."""
    # Создаем мок-функцию для обработки сигнала
    callback = MagicMock()
    editor.file_name_changed.connect(callback)
    
    # Эмулируем изменение имени файла
    editor.file_name_changed.emit("test.txt")
    
    # Проверяем, что сигнал был вызван с правильным аргументом
    callback.assert_called_once_with("test.txt")
