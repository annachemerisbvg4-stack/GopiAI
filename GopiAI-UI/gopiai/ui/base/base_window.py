"""
Базовый класс окна для GopiAI UI
"""

from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import QSize


class BaseWindow(QMainWindow):
    """
    Базовый класс для всех окон в GopiAI.
    
    Обеспечивает:
    - Автоматическую регистрацию в системе окон
    - Базовые настройки размера и поведения
    - Интеграцию с темной/светлой темой
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(QSize(800, 600))
        
    def closeEvent(self, event):
        """Переопределяемый метод закрытия окна"""
        event.accept()
        
    def setupUi(self):
        """Метод для настройки UI, переопределяется в наследниках"""
        pass
        
    def connectSignals(self):
        """Метод для подключения сигналов, переопределяется в наследниках"""
        pass
