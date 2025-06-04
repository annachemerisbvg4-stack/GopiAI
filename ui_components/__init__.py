"""
UI Components для GopiAI Standalone Interface
=========================================

Модульная система компонентов интерфейса:
- menu_bar.py - Система меню
- titlebar.py - Заголовок окна и элементы управления
- file_explorer.py - Панель файлов
- tab_widget.py - Система вкладок для документов
- chat_widget.py - Чат с ИИ
- terminal_widget.py - Терминал
- theme_manager.py - Система тем
- icon_system.py - Автоматическая система иконок
"""

from .menu_bar import StandaloneMenuBar
from .titlebar import StandaloneTitlebar, StandaloneTitlebarWithMenu, CustomGrip
from .file_explorer import FileExplorerWidget
from .tab_widget import TabDocumentWidget
from .chat_widget import ChatWidget
from .terminal_widget import TerminalWidget
from .theme_selector_dialog import ThemeSelectorDialog, show_theme_selector  # Временно отключено из-за синтаксической ошибки

# Импорт систем тем и иконок (могут быть недоступны)
try:
    from .theme_manager import ThemeManager
except ImportError:
    ThemeManager = None

try:
    from .icon_system import AutoIconSystem
except ImportError:
    AutoIconSystem = None

__all__ = [
    "StandaloneMenuBar",
    "StandaloneTitlebar",
    "StandaloneTitlebarWithMenu", 
    "CustomGrip",
    "FileExplorerWidget",
    "TabDocumentWidget",
    "ChatWidget",
    "TerminalWidget",
    "ThemeSelectorDialog",
    "show_theme_selector",
]

# Добавляем в экспорт только доступные модули
if ThemeManager:
    __all__.append("ThemeManager")
    
if AutoIconSystem:
    __all__.append("AutoIconSystem")
