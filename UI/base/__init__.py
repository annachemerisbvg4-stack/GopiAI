"""
UI Base для GopiAI
==================

Базовые классы и система автоматической регистрации.
"""

from .base_window import BaseWindow
from .registry import WindowRegistry, get_registry, auto_discover_windows

__all__ = [
    'BaseWindow',
    'WindowRegistry',
    'get_registry',
    'auto_discover_windows'
]
