"""
Базовые классы для UI компонентов GopiAI
=======================================

Содержит базовые классы окон и реестр окон.
"""

from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt


class WindowRegistry:
    """Реестр окон приложения"""
    
    _windows = {}
    
    @classmethod
    def register(cls, window_name, window):
        """Регистрация окна"""
        cls._windows[window_name] = window
        
    @classmethod
    def get(cls, window_name):
        """Получение окна по имени"""
        return cls._windows.get(window_name)
        
    @classmethod
    def remove(cls, window_name):
        """Удаление окна из реестра"""
        if window_name in cls._windows:
            del cls._windows[window_name]


class BaseWindow(QMainWindow):
    """Базовое окно приложения"""
    
    def __init__(self, parent=None, window_name="main"):
        super().__init__(parent)
        self.window_name = window_name
        self._init_window()
        WindowRegistry.register(window_name, self)
        
    def _init_window(self):
        """Инициализация окна"""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        WindowRegistry.remove(self.window_name)
        super().closeEvent(event)
