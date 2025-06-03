#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Пример использования компонента MyComponent.
"""

import sys
from PySide6.QtWidgets import QApplication
from gopiai.app.ui.my_component import MyComponent

def main():
    """Запускает пример компонента."""
    app = QApplication(sys.argv)
    component = MyComponent()
    component.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
