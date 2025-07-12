#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тесты для компонента MyComponent.
"""

import pytest
from PySide6.QtWidgets import QApplication
from gopiai.app.ui.my_component import MyComponent

def test_my_component():
    """Тестирует создание компонента."""
    app = QApplication([])
    component = MyComponent()
    assert component is not None

def test_my_component_title():
    app = QApplication([])
    component = MyComponent()
    assert component.windowTitle() == "MyComponent"

def test_my_component_visible():
    app = QApplication([])
    component = MyComponent()
    assert component.isVisible() == False

def test_my_component_show():
    app = QApplication([])
    component = MyComponent()
    component.show()
    assert component.isVisible() == True

def test_my_component_close():
    app = QApplication([])
    component = MyComponent()
    component.show()
    component.close()
    assert component.isVisible() == False