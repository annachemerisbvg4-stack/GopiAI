"""
Временный модуль для прямого импорта IconAdapter.
Обходит проблему с циклическими зависимостями gopiai.app.
"""

from gopiai.widgets.core.icon_adapter import IconAdapter

__all__ = ['IconAdapter']
