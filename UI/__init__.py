"""
UI Module для GopiAI
====================

Унифицированный модуль пользовательского интерфейса с поддержкой
автоматической регистрации окон и меню.

Архитектура:
- base/: Базовые классы (BaseWindow, Registry)
- components/: Основные UI компоненты (виджеты, панели)
- windows/: Окна приложения
- dialogs/: Диалоговые окна
- utils/: Утилиты (ThemeManager, IconManager и др.)

Автоматическая регистрация:
Для добавления нового окна достаточно поместить файл с классом,
наследующим BaseWindow, в папку windows/ или dialogs/.
Окно автоматически появится в меню, если указаны метаданные.

Пример создания окна:
```python
from UI.base import BaseWindow

class MyWindow(BaseWindow):
    window_metadata = {
        'window_name': 'my_window',
        'description': 'Моё окно',
        'menu_title': 'Моё окно',
        'menu_category': 'Инструменты',
        'menu_icon': 'settings',
        'menu_order': 10
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Моё окно")
```

Автор: Crazy Coder
Версия: 1.0.0
Дата: 2025-01-27
"""

# Импорт базовых классов
from .base import BaseWindow, WindowRegistry, get_registry, auto_discover_windows

# Импорт основных компонентов
from .components import (
    ChatWidget,
    TabDocumentWidget,
    TerminalWidget,
    StandaloneTitlebar,
    StandaloneTitlebarWithMenu, 
    StandaloneMenuBar
)