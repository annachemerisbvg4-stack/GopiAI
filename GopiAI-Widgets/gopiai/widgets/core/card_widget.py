#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Виджет карточки для отображения информации.

Этот виджет представляет собой карточку с заголовком, содержимым и кнопками действий.
Может использоваться для отображения различной информации в виде карточек.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, Signal


class CardWidget(QFrame):
    """
    Виджет в стиле карточки с заголовком, содержимым и действиями.
    
    Особенности:
    - Настраиваемый заголовок и содержимое
    - Возможность добавления кнопок действий
    - Сигнал clicked при клике на карточку
    - Настраиваемый внешний вид через стили
    """
    
    clicked = Signal()  # Сигнал при клике на карточку
    
    def __init__(self, title="", content="", parent=None):
        """
        Инициализирует CardWidget.
        
        Args:
            title (str): Заголовок карточки
            content (str): Содержимое карточки
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("cardWidget")
        
        # Настройка внешнего вида
        self.setStyleSheet("""
            #cardWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            #cardTitle {
                font-weight: bold;
                font-size: 14px;
                color: #303030;
            }
            #cardContent {
                color: #505050;
            }
            #cardButton {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 4px 8px;
            }
            #cardButton:hover {
                background-color: #e0e0e0;
            }
            #cardButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        # Создаем лейаут
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(8)
        
        # Заголовок
        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        self.layout.addWidget(self.title_label)
        
        # Содержимое
        self.content_label = QLabel(content)
        self.content_label.setObjectName("cardContent")
        self.content_label.setWordWrap(True)
        self.layout.addWidget(self.content_label)
        
        # Контейнер для кнопок
        self.buttons_container = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(0, 8, 0, 0)
        self.buttons_layout.setSpacing(8)
        self.buttons_layout.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.buttons_container)
        
        # Делаем виджет кликабельным
        self.setMouseTracking(True)
        
        # Эффект при наведении
        self.setAutoFillBackground(True)
        self._default_style = self.styleSheet()
        self._is_hovered = False
    
    def mousePressEvent(self, event):
        """Обрабатывает клик по карточке."""
        self.clicked.emit()
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """Обрабатывает наведение курсора на карточку."""
        self._is_hovered = True
        self.setStyleSheet(self._default_style + """
            #cardWidget {
                border: 1px solid #b0b0b0;
                border_color: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
        """)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Обрабатывает уход курсора с карточки."""
        self._is_hovered = False
        self.setStyleSheet(self._default_style)
        super().leaveEvent(event)
    
    def add_button(self, text, callback=None):
        """
        Добавляет кнопку в карточку.
        
        Args:
            text (str): Текст кнопки
            callback: Функция, вызываемая при нажатии на кнопку
        
        Returns:
            QPushButton: Созданная кнопка
        """
        button = QPushButton(text)
        button.setObjectName("cardButton")
        self.buttons_layout.addWidget(button)
        
        if callback:
            button.clicked.connect(callback)
        
        return button
    
    def set_content(self, content):
        """
        Устанавливает содержимое карточки.
        
        Args:
            content (str): Новое содержимое
        """
        self.content_label.setText(content)
    
    def set_title(self, title):
        """
        Устанавливает заголовок карточки.
        
        Args:
            title (str): Новый заголовок
        """
        self.title_label.setText(title)
    
    def set_style(self, background=None, border_color=None, border_radius=None, 
                 title_color=None, content_color=None, title_size=None):
        """
        Устанавливает стиль карточки.
        
        Args:
            background (str, optional): Цвет фона (CSS-формат)
            border_color (str, optional): Цвет границы (CSS-формат)
            border_radius (int, optional): Радиус скругления углов
            title_color (str, optional): Цвет заголовка (CSS-формат)
            content_color (str, optional): Цвет содержимого (CSS-формат)
            title_size (int, optional): Размер шрифта заголовка
        """
        style = self._default_style
        
        if background:
            style += f"#cardWidget {{ background-color: {background}; }}\n"
        
        if border_color:
            style += f"#cardWidget {{ border: 1px solid {border_color}; }}\n"
        
        if border_radius is not None:
            style += f"#cardWidget {{ border-radius: {border_radius}px; }}\n"
        
        if title_color:
            style += f"#cardTitle {{ color: {title_color}; }}\n"
        
        if content_color:
            style += f"#cardContent {{ color: {content_color}; }}\n"
        
        if title_size is not None:
            style += f"#cardTitle {{ font-size: {title_size}px; }}\n"
        
        self._default_style = style
        self.setStyleSheet(style)
    
    def clear_buttons(self):
        """Удаляет все кнопки из карточки."""
        while self.buttons_layout.count():
            item = self.buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
