"""
GopiAI UI Components Package
============================

Компоненты пользовательского интерфейса GopiAI.
"""

from .titlebar import StandaloneTitlebar, StandaloneTitlebarWithMenu, CustomGrip
from .menu_bar import StandaloneMenuBar
from .file_explorer import FileExplorerWidget
from .tab_widget import TabDocumentWidget
from .chat_widget import ChatWidget
from .terminal_widget import TerminalWidget

__all__ = [
    'StandaloneTitlebar',
    'StandaloneTitlebarWithMenu', 
    'CustomGrip',
    'StandaloneMenuBar',
    'FileExplorerWidget',
    'TabDocumentWidget',
    'ChatWidget',
    'TerminalWidget',
]
