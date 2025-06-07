"""
GopiAI UI Package
=================

Пакет пользовательского интерфейса GopiAI.
"""

# Версия UI
__version__ = "0.3.0"

# Экспортируем основные компоненты
from . import components
from . import base
from . import utils
from . import dialogs
from . import windows

__all__ = [
    'components',
    'base', 
    'utils',
    'dialogs',
    'windows',
]
