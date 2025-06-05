"""
GopiAI UI Package
=================

Пакет пользовательского интерфейса GopiAI.
"""

__path__ = __import__('pkgutil').extend_path(__path__, __name__)
__version__ = "0.3.0"

# Экспортируем основные компоненты
from . import components
from . import base
from . import utils
from . import dialogs
from .base import auto_discover_windows

# Автоматически обнаруживаем окна 
try:
    auto_discover_windows('gopiai.ui.windows')
except ImportError:
    print("⚠️ Модуль windows не найден. Пропускаем автообнаружение окон.")

__all__ = [
    'components',
    'base', 
    'utils',
    'dialogs',
    'auto_discover_windows'
]
