"""
GopiAI UI Components Package
============================

Компоненты пользовательского интерфейса GopiAI.
"""

from .titlebar import StandaloneTitlebar, StandaloneTitlebarWithMenu, CustomGrip
from .menu_bar import StandaloneMenuBar
from .file_explorer import FileExplorerWidget
# Исправляем импорт для TabDocumentWidget
from .tab_widget import TabDocumentWidget
from .webview_chat_widget import WebViewChatWidget
from .terminal_widget import TerminalWidget

__all__ = [
    'StandaloneTitlebar',
    'StandaloneTitlebarWithMenu', 
    'CustomGrip',
    'StandaloneMenuBar',
    'FileExplorerWidget',
    'TabDocumentWidget',
    'WebViewChatWidget',
    'TerminalWidget',
]
