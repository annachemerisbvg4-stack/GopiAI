"""
GopiAI UI Package
=================

Пакет пользовательского интерфейса GopiAI.
"""

# Версия UI
__version__ = "0.3.0"

# Экспортируем основные компоненты
from . import components
from . import utils
from . import dialogs

__all__ = [
    'components',
    'utils',
    'dialogs',
]
