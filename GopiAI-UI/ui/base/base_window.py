"""
Базовые классы для UI компонентов GopiAI
"""

from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6.QtCore import Signal, QSize
from abc import ABC, abstractmethod


class BaseWindow(QMainWindow, ABC):
    """
    Базовый класс для всех окон GopiAI
    
    Автоматически регистрируется в системе на основе метаданных класса.
    """
      # Метаданные для автоматической регистрации (переопределяются в дочерних классах)
    window_name: str = ""                # Уникальное имя окна
    menu_title: str = ""                 # Название в меню
    menu_category: str = "tools"         # Категория меню (file, edit, view, tools, help)
    menu_icon: str = ""                  # Иконка в меню
    menu_shortcut: str = ""              # Горячая клавиша
    menu_order: int = 100                # Порядок в меню
    menu_visible: bool = True            # Видимость в меню
    
    # Сигналы
    window_closed = Signal(str)          # Окно закрыто (передаёт window_name)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Проверяем, что дочерний класс определил обязательные атрибуты
        if not self.window_name:
            raise ValueError(f"Класс {self.__class__.__name__} должен определить window_name")
        
        self.setObjectName(f"window_{self.window_name}")
        self.setup_window()
        self.setup_ui()
        self.connect_signals()
        
    def setup_window(self):
        """Базовая настройка окна"""
        if self.menu_title:
            self.setWindowTitle(self.menu_title)
        
        # Устанавливаем разумный размер по умолчанию
        self.resize(800, 600)
        
    @abstractmethod
    def setup_ui(self):
        """Настройка интерфейса (должен быть переопределён в дочерних классах)"""
        pass
        
    def connect_signals(self):
        """Подключение сигналов (может быть переопределено)"""
        pass
        
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.window_closed.emit(self.window_name)
        super().closeEvent(event)


class BaseWidget(QWidget, ABC):
    """
    Базовый класс для переиспользуемых UI компонентов
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
        
    @abstractmethod
    def setup_ui(self):
        """Настройка интерфейса"""
        pass
        
    def connect_signals(self):
        """Подключение сигналов"""
        pass
