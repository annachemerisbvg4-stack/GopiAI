#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестовое приложение для демонстрации работы расширения Project Explorer.
"""

import sys
import os

# Добавляем корневую папку проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PySide6.QtWidgets import QApplication
from gopiai.core.minimal_app import FramelessMainWindow
from gopiai.extensions.project_explorer_integration import add_project_explorer_dock

def main():
    """Основная функция тестового приложения."""
    app = QApplication(sys.argv)
    
    # Создаем главное окно
    main_window = FramelessMainWindow()
    main_window.show()
    
    # Добавляем расширение
    add_project_explorer_dock(main_window)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
