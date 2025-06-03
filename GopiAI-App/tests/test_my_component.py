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
