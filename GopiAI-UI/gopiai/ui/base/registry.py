"""
Система регистрации окон для GopiAI UI
"""

import importlib
import inspect
from typing import Dict, Type, Optional
from .base_window import BaseWindow


class WindowRegistry:
    """Реестр окон приложения"""
    
    def __init__(self):
        self._windows: Dict[str, Type[BaseWindow]] = {}
        
    def register(self, window_class: Type[BaseWindow]) -> None:
        """Регистрация нового класса окна"""
        name = window_class.__name__
        if name in self._windows:
            raise ValueError(f"Окно с именем {name} уже зарегистрировано")
        self._windows[name] = window_class
        
    def get_window(self, name: str) -> Optional[Type[BaseWindow]]:
        """Получение класса окна по имени"""
        return self._windows.get(name)
        
    def list_windows(self) -> list:
        """Список всех зарегистрированных окон"""
        return list(self._windows.keys())


# Глобальный реестр окон
_registry = WindowRegistry()


def get_registry() -> WindowRegistry:
    """Получение глобального реестра окон"""
    return _registry


def auto_discover_windows(module_path: str) -> None:
    """
    Автоматическое обнаружение и регистрация окон в указанном модуле
    
    Args:
        module_path: Путь к модулю для сканирования (например 'gopiai.ui.windows')
    """
    try:
        module = importlib.import_module(module_path)
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseWindow) and 
                obj != BaseWindow):
                _registry.register(obj)
    except ImportError as e:
        print(f"Ошибка при автообнаружении окон: {e}")
