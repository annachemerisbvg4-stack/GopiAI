"""
UI Components для GopiAI
========================

Основные компоненты пользовательского интерфейса.
"""

from .chat_widget import ChatWidget
from .tab_widget import TabDocumentWidget
from .terminal_widget import TerminalWidget
from .titlebar import StandaloneTitlebar, StandaloneTitlebarWithMenu, CustomGrip
from .menu_bar import StandaloneMenuBar
from .file_type_detector import FileTypeDetector
from .icon_file_system_model import IconFileSystemModel

# Попытка импорта file_explorer (может быть перегенерирован)
try:
    from .file_explorer_old import FileExplorerWidget
except ImportError:
    try:
        from .file_explorer import FileExplorerWidget
    except ImportError:
        print("⚠️ FileExplorerWidget не найден, требуется восстановление")

__all__ = [
    'ChatWidget',
    'TabDocumentWidget', 
    'TerminalWidget',
    'StandaloneTitlebar',
    'StandaloneTitlebarWithMenu',
    'CustomGrip',
    'StandaloneMenuBar',
    'FileExplorerWidget',
    'FileTypeDetector',
    'IconFileSystemModel'
]
