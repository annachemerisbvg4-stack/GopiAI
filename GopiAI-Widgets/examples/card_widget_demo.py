#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Демонстрация CardWidget без зависимостей от других модулей.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal


class CardWidget(QFrame):
    """
    Виджет в стиле карточки с заголовком, содержимым и действиями.
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
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
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


class TestWindow(QMainWindow):
    """Тестовое окно для CardWidget."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Демонстрация CardWidget")
        self.setGeometry(100, 100, 500, 400)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем лейаут
        layout = QVBoxLayout(central_widget)
        
        # Создаем CardWidget
        card = CardWidget("Тестовая карточка", "Это тестовая карточка для проверки работы CardWidget.")
        card.clicked.connect(lambda: self.show_message(card, "Карточка нажата"))
        card.add_button("Кнопка 1", lambda: self.show_message(card, "Нажата кнопка 1"))
        card.add_button("Кнопка 2", lambda: self.show_message(card, "Нажата кнопка 2"))
        
        layout.addWidget(card)
        
        # Создаем стилизованную карточку
        styled_card = CardWidget("Стилизованная карточка", "Эта карточка имеет настроенный стиль.")
        styled_card.set_style(
            background="#f0f8ff",
            border_color="#b0c4de",
            border_radius=12,
            title_color="#0066cc",
            content_color="#333333",
            title_size=16
        )
        styled_card.add_button("Действие", lambda: self.show_message(styled_card, "Выполнено действие"))
        
        layout.addWidget(styled_card)
    
    def show_message(self, card, message):
        """Показывает сообщение в карточке."""
        card.set_content(message)


def main():
    """Основная функция демонстрации."""
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
