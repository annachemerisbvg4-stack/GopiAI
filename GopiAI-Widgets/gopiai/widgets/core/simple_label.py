#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Простой виджет метки с дополнительными возможностями.
"""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, Signal, QTimer

class SimpleLabel(QLabel):
    """
    Простой виджет метки с дополнительными возможностями.
    
    Возможности:
    - Автоматическое обновление текста
    - Сигнал при клике
    - Настраиваемый стиль
    """
    
    clicked = Signal()  # Сигнал, который испускается при клике на метку
    
    def __init__(self, text="", parent=None):
        """
        Инициализирует виджет метки.
        
        Args:
            text (str): Начальный текст метки
            parent: Родительский виджет
        """
        super().__init__(text, parent)
        self._timer = None
        self._update_function = None
        self._update_interval = 1000  # мс
        
        # Настройка стиля по умолчанию
        self.setStyleSheet("""
            QLabel {
                padding: 5px;
                border-radius: 3px;
            }
        """)
    
    def mousePressEvent(self, event):
        """Обрабатывает нажатие кнопки мыши."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def set_auto_update(self, update_function, interval=1000):
        """
        Устанавливает функцию для автоматического обновления текста.
        
        Args:
            update_function: Функция, которая возвращает новый текст
            interval (int): Интервал обновления в миллисекундах
        """
        self._update_function = update_function
        self._update_interval = interval
        
        if self._timer is None:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._update_text)
        
        self._timer.start(self._update_interval)
    
    def stop_auto_update(self):
        """Останавливает автоматическое обновление текста."""
        if self._timer is not None:
            self._timer.stop()
    
    def _update_text(self):
        """Обновляет текст метки."""
        if self._update_function is not None:
            new_text = self._update_function()
            self.setText(new_text)
    
    def set_style(self, background_color=None, text_color=None, border=None):
        """
        Устанавливает стиль метки.
        
        Args:
            background_color (str): Цвет фона
            text_color (str): Цвет текста
            border (str): Стиль границы
        """
        style = "QLabel { padding: 5px; border-radius: 3px; "
        
        if background_color:
            style += f"background-color: {background_color}; "
        
        if text_color:
            style += f"color: {text_color}; "
        
        if border:
            style += f"border: {border}; "
        
        style += "}"
        
        self.setStyleSheet(style)
