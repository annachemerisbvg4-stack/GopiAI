"""
Главное окно приложения GopiAI
"""

from ..base import BaseWindow
from ..components import (
    StandaloneMenuBar,
    StandaloneTitlebar,
    FileExplorerWidget,
    TabDocumentWidget,
    ChatWidget,
    TerminalWidget
)
from PySide6.QtWidgets import QVBoxLayout, QWidget, QSplitter
from PySide6.QtCore import Qt


class MainWindow(BaseWindow):
    """Главное окно приложения GopiAI"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GopiAI")
        self.setupUi()
        self.connectSignals()
        
    def setupUi(self):
        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        
        # Основной layout
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Заголовок с меню
        self.titlebar = StandaloneTitlebar(self)
        self.menu_bar = StandaloneMenuBar(self)
        layout.addWidget(self.titlebar)
        layout.addWidget(self.menu_bar)
          # Основной сплиттер
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.main_splitter)
        
        # Левая панель - проводник
        self.file_explorer = FileExplorerWidget(self)
        self.main_splitter.addWidget(self.file_explorer)
        
        # Центральная часть
        center_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.addWidget(center_splitter)
        
        # Редактор
        self.editor = TabDocumentWidget(self)
        center_splitter.addWidget(self.editor)
        
        # Нижняя панель
        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        center_splitter.addWidget(bottom_splitter)
        
        # Чат
        self.chat = ChatWidget(self)
        bottom_splitter.addWidget(self.chat)
        
        # Терминал
        self.terminal = TerminalWidget(self)
        bottom_splitter.addWidget(self.terminal)
        
        # Настройка размеров сплиттеров
        self.main_splitter.setStretchFactor(0, 0)  # Фиксированный размер проводника
        self.main_splitter.setStretchFactor(1, 1)  # Растягиваемая центральная часть
        
        center_splitter.setStretchFactor(0, 2)  # Редактор получает больше места
        center_splitter.setStretchFactor(1, 1)  # Нижняя панель поменьше
        
        bottom_splitter.setSizes([400, 400])  # Равное разделение чата и терминала
        
    def connectSignals(self):
        """Подключение сигналов"""
        # Подключаем сигналы между компонентами по необходимости
        pass
