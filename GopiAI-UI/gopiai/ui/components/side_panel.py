# --- START OF FILE side_panel.py (ФИНАЛЬНАЯ ВЕРСИЯ) ---

import logging
import json
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QTabWidget
from PySide6.QtCore import QRect, QPoint, Qt, Signal

# Импортируем менеджер инструментов
from gopiai.ui.components.tools_panel_utils import get_tools_manager

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
        
        # Создаем вкладки для разных типов инструментов
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("background-color: transparent;")
        
        # Вкладка стандартных инструментов
        self.standard_tools_tab = QWidget()
        self.standard_tools_tab.setStyleSheet("background-color: transparent;")
        self.standard_tools_layout = QVBoxLayout(self.standard_tools_tab)
        self.standard_tools_layout.setContentsMargins(0, 0, 0, 0)
        self.standard_tools_layout.setSpacing(5)
        
        # Создаем область прокрутки для стандартных инструментов
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background-color: transparent;")
        
        # Контейнер для карточек инструментов
        self.tools_container = QWidget()
        self.tools_container.setStyleSheet("background-color: transparent;")
        self.content_layout = QVBoxLayout(self.tools_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        self.content_layout.addStretch()
        
        self.scroll_area.setWidget(self.tools_container)
        self.standard_tools_layout.addWidget(self.scroll_area)
        
        self.tabs.addTab(self.standard_tools_tab, "Стандартные")
        
        self.main_layout.addWidget(self.tabs, 1)
        
        # Загружаем и отображаем инструменты
        self._load_tools()
        
        self.main_layout.addStretch()

    def add_button(self, button: QPushButton):
        """Добавляет кнопку в панель."""
        # Вставляем перед растягивающим элементом (stretch)
        self.content_layout.insertWidget(self.content_layout.count() - 1, button)
        
    def add_widget(self, widget: QWidget):
        """Добавляет виджет в панель."""
        # Вставляем перед растягивающим элементом (stretch)
        self.content_layout.insertWidget(self.content_layout.count() - 1, widget)
        
    def toggle_visibility(self):
        """Переключает видимость панели."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_() # Поднимаем панель наверх
            
    def _load_tools(self):
        """Загружает и отображает инструменты на панели."""
        try:
            # Получаем менеджер инструментов
            tools_manager = get_tools_manager()
            
            if not tools_manager:
                return
            
            # Для каждой категории создаем заголовок и добавляем инструменты
            for category in tools_manager.get_tools_categories():
                # Заголовок категории
                category_label = QLabel(category)
                category_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #ff79c6; padding-top: 10px;")
                self.add_widget(category_label)
                
                # Инструменты в категории
                tools = tools_manager.get_tools_in_category(category)
                for tool_id, tool_info in tools:
                    if tool_info.get("available", True):  # Пропускаем недоступные инструменты
                        tool_card = tools_manager.create_tool_card(tool_id, tool_info)
                        self.add_widget(tool_card)
                        
            # Подключаем сигнал выбора инструмента
            tools_manager.tool_selected.connect(self._on_tool_selected)
            
        except Exception as e:
            logging.error(f"Ошибка при загрузке инструментов: {e}")
            
    def _on_tool_selected(self, tool_id: str, tool_data: dict):
        """
        Обрабатывает выбор стандартного инструмента пользователем.
        Скрывает панель и отправляет сигнал родительскому виджету.
        
        Args:
            tool_id: Идентификатор выбранного инструмента
            tool_data: Данные выбранного инструмента
        """
        # Скрываем панель после выбора
        self.hide()
        
        # Отправляем сигнал родительскому виджету
        parent_widget = self.parent()
        if hasattr(parent_widget, "on_tool_selected"):
            parent_widget.on_tool_selected(tool_id, tool_data)

class SidePanelContainer(QWidget):
    """
    Контейнер, который содержит кнопку-триггер и управляет SlidingPanel.
    Этот виджет НЕ добавляется в layout, а позиционируется вручную.
    """
    # Сигнал, отправляемый при выборе инструмента
    tool_selected = Signal(str, dict)
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
            parent_widget = self.parent()
            if parent_widget:
                parent_rect = parent_widget.geometry()
                panel_width = 350
                panel_height = parent_rect.height() - 20
                x = parent_rect.width() - panel_width - 10
                y = 10
                self.panel.setGeometry(x, y, panel_width, panel_height)
        
        self.panel.toggle_visibility()
        
    def update_trigger_position(self):
        """Обновляет позицию кнопки-триггера. Вызывается из ChatWidget.resizeEvent."""
        parent_widget = self.parent()
        if parent_widget:
            parent_size = parent_widget.size()
            button_size = self.trigger_button.size()
            x = parent_size.width() - button_size.width() - 15
            y = parent_size.height() - button_size.height() - 15
            self.trigger_button.move(x, y)
            
    def on_tool_selected(self, tool_id: str, tool_data: dict):
        """
        Обрабатывает выбор инструмента на панели и отправляет сигнал.
        
        Args:
            tool_id: Идентификатор выбранного инструмента
            tool_data: Данные выбранного инструмента
        """
        # Отправляем сигнал наружу (в ChatWidget)
        self.tool_selected.emit(tool_id, tool_data)

# --- КОНЕЦ ФАЙЛА side_panel.py ---