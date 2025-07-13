# --- START OF FILE side_panel.py (ФИНАЛЬНАЯ ВЕРСИЯ) ---

import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QRect, QPoint, Qt

logger = logging.getLogger(__name__)

class SlidingPanel(QWidget):
    """Сама выезжающая панель с полупрозрачным фоном."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.hide() # Панель по умолчанию скрыта

    def setup_ui(self):
        # # Стиль для полупрозрачности и внешнего вида
        # self.setStyleSheet("""
            # SlidingPanel {
                # background-color: rgba(40, 42, 54, 0.50); /* 50% непрозрачный темный фон */
                # border: 1px solid rgba(255, 255, 255, 0.1);
                # border-radius: 12px;
            # }
            # QLabel { 
                # color: #f8f8f2; /* Светлый текст */
                # background-color: transparent;
            # }
            # QPushButton { 
                # border: none;
                # padding: 8px;
                # border-radius: 6px;
                # text-align: left; /* Выравнивание текста на кнопках по левому краю */
            # }
            # QPushButton#closeButton { /* Особый стиль для кнопки закрытия */
            # }
        # """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 10, 15, 15)
        self.main_layout.setSpacing(15)
        
        # Заголовок с кнопкой закрытия
        header_layout = QHBoxLayout()
        self.title_label = QLabel("Инструменты")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; background-color: transparent;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeButton")
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.hide) # Просто скрываем панель
        header_layout.addWidget(close_btn)
        
        self.main_layout.addLayout(header_layout)
        
        # Контейнер для кнопок, которые будут добавлены извне
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        self.main_layout.addLayout(self.content_layout)
        
        self.main_layout.addStretch()

    def add_button(self, button: QPushButton):
        """Добавляет кнопку в панель."""
        self.content_layout.addWidget(button)
        
    def toggle_visibility(self):
        """Переключает видимость панели."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_() # Поднимаем панель наверх

class SidePanelContainer(QWidget):
    """
    Контейнер, который содержит кнопку-триггер и управляет SlidingPanel.
    Этот виджет НЕ добавляется в layout, а позиционируется вручную.
    """
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        # Делаем сам контейнер невидимым, нам нужна только его кнопка
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Создаем панель, ее родителем будет родитель этого контейнера (т.е. chat_area_widget)
        self.panel = SlidingPanel(parent)
        
        # Создаем кнопку-триггер
        # UniversalIconManager должен быть доступен, т.к. инициализируется раньше
        from gopiai.ui.components.icon_file_system_model import UniversalIconManager
        icon_mgr = UniversalIconManager.instance()
        
        self.trigger_button = QPushButton(icon_mgr.get_icon("settings-2"), "", self) # Иконка шестеренки
        self.trigger_button.setToolTip("Показать/скрыть панель инструментов")
        self.trigger_button.setFixedSize(32, 32)
        self.trigger_button.setStyleSheet("""
            QPushButton { 
                background-color: rgba(40, 42, 54, 0.7); 
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px; /* Делаем ее круглой */
            }
            QPushButton:hover { background-color: rgba(68, 71, 90, 0.8); }
        """)
        self.trigger_button.clicked.connect(self.toggle_panel)
        
    def add_button_to_panel(self, button: QPushButton):
        """Прокси-метод для добавления кнопки в саму выезжающую панель."""
        self.panel.add_button(button)
        
    def toggle_panel(self):
        """Показывает или скрывает панель в правильном месте."""
        if not self.panel.isVisible():
            # Позиционируем панель относительно родителя контейнера
            parent_rect = self.parent().geometry()
            panel_width = 250
            panel_height = parent_rect.height() - 20
            x = parent_rect.width() - panel_width - 10
            y = 10
            self.panel.setGeometry(x, y, panel_width, panel_height)
        
        self.panel.toggle_visibility()
        
    def update_trigger_position(self):
        """Обновляет позицию кнопки-триггера. Вызывается из ChatWidget.resizeEvent."""
        if self.parent():
            parent_size = self.parent().size()
            button_size = self.trigger_button.size()
            x = parent_size.width() - button_size.width() - 15
            y = parent_size.height() - button_size.height() - 15
            self.trigger_button.move(x, y)

# --- КОНЕЦ ФАЙЛА side_panel.py ---