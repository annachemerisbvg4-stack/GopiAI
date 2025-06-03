#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Расширение для добавления статусной строки.
"""

import time
from PySide6.QtWidgets import QStatusBar, QLabel, QHBoxLayout, QWidget
from PySide6.QtCore import QTimer, Qt

def add_status_bar(main_window):
    """
    Добавляет статусную строку в главное окно.
    
    Args:
        main_window: Главное окно приложения
    
    Returns:
        QStatusBar: Созданная статусная строка
    """
    # Создаем статусную строку
    status_bar = QStatusBar(main_window)
    status_bar.setObjectName("statusBar")
    
    # Создаем виджет для размещения элементов статусной строки
    status_widget = QWidget(status_bar)
    status_layout = QHBoxLayout(status_widget)
    status_layout.setContentsMargins(0, 0, 0, 0)
    status_layout.setSpacing(10)
    
    # Создаем метку для отображения сообщений
    message_label = QLabel("Готово")
    message_label.setObjectName("statusMessageLabel")
    status_layout.addWidget(message_label)
    
    # Создаем метку для отображения времени
    time_label = QLabel(time.strftime("%H:%M:%S"))
    time_label.setObjectName("statusTimeLabel")
    time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    status_layout.addWidget(time_label)
    
    # Добавляем виджет в статусную строку
    status_bar.addWidget(status_widget, 1)
    
    # Устанавливаем статусную строку в главное окно
    main_window.setStatusBar(status_bar)
    
    # Создаем таймер для обновления времени
    timer = QTimer(main_window)
    timer.timeout.connect(lambda: time_label.setText(time.strftime("%H:%M:%S")))
    timer.start(1000)
    
    # Добавляем метод для обновления сообщения
    def update_status_message(message):
        message_label.setText(message)
    
    # Добавляем метод в главное окно
    main_window.update_status_message = update_status_message
    
    return status_bar

def init_status_bar_extension(main_window):
    """
    Инициализирует расширение статусной строки.
    
    Args:
        main_window: Главное окно приложения
    """
    try:
        add_status_bar(main_window)
        main_window.update_status_message("Статусная строка инициализирована")
    except Exception as e:
        print(f"Ошибка при инициализации статусной строки: {e}")
