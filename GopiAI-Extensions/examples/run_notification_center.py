#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Пример использования расширения NotificationCenter.
"""

import sys
import os
import time

# Добавляем корневую папку проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QComboBox, QLabel, QLineEdit, QTextEdit
from PySide6.QtCore import Qt
from gopiai.extensions.notification_center_extension import NotificationCenterExtension, NotificationType


class MainWindow(QMainWindow):
    """Главное окно для демонстрации NotificationCenter."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Демонстрация NotificationCenter")
        self.setGeometry(100, 100, 800, 600)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем основной лейаут
        main_layout = QVBoxLayout(central_widget)
        
        # Добавляем заголовок
        title_label = QLabel("Демонстрация центра уведомлений")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0066cc;")
        main_layout.addWidget(title_label)
        
        # Добавляем описание
        description_label = QLabel(
            "Центр уведомлений позволяет отображать системные уведомления, "
            "сообщения от различных компонентов приложения и информировать "
            "пользователя о важных событиях."
        )
        description_label.setWordWrap(True)
        main_layout.addWidget(description_label)
        
        # Создаем форму для добавления уведомлений
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        
        # Заголовок формы
        form_title = QLabel("Создать уведомление")
        form_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        form_layout.addWidget(form_title)
        
        # Поле для заголовка уведомления
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Заголовок:"))
        self.title_input = QLineEdit()
        self.title_input.setText("Тестовое уведомление")
        title_layout.addWidget(self.title_input)
        form_layout.addLayout(title_layout)
        
        # Поле для текста уведомления
        message_layout = QHBoxLayout()
        message_layout.addWidget(QLabel("Сообщение:"))
        self.message_input = QTextEdit()
        self.message_input.setPlainText("Это тестовое уведомление для демонстрации центра уведомлений.")
        self.message_input.setMaximumHeight(100)
        message_layout.addWidget(self.message_input)
        form_layout.addLayout(message_layout)
        
        # Выбор типа уведомления
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Тип:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Информация", "Успех", "Предупреждение", "Ошибка"])
        type_layout.addWidget(self.type_combo)
        form_layout.addLayout(type_layout)
        
        # Опции уведомления
        options_layout = QHBoxLayout()
        
        # Автозакрытие
        self.auto_close_checkbox = QPushButton("Автозакрытие")
        self.auto_close_checkbox.setCheckable(True)
        self.auto_close_checkbox.setChecked(True)
        options_layout.addWidget(self.auto_close_checkbox)
        
        # Продолжительность
        options_layout.addWidget(QLabel("Продолжительность (мс):"))
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["3000", "5000", "10000", "15000"])
        self.duration_combo.setCurrentIndex(1)  # 5000 мс по умолчанию
        options_layout.addWidget(self.duration_combo)
        
        form_layout.addLayout(options_layout)
        
        # Добавление действий
        actions_layout = QHBoxLayout()
        actions_layout.addWidget(QLabel("Действия:"))
        
        self.add_action_button = QPushButton("Добавить действие 'Подробнее'")
        self.add_action_button.setCheckable(True)
        actions_layout.addWidget(self.add_action_button)
        
        form_layout.addLayout(actions_layout)
        
        # Кнопка добавления уведомления
        self.add_notification_button = QPushButton("Добавить уведомление")
        self.add_notification_button.clicked.connect(self.add_notification)
        form_layout.addWidget(self.add_notification_button)
        
        main_layout.addWidget(form_widget)
        
        # Добавляем кнопки управления центром уведомлений
        buttons_layout = QHBoxLayout()
        
        self.show_button = QPushButton("Показать центр уведомлений")
        self.show_button.clicked.connect(self.show_notification_center)
        buttons_layout.addWidget(self.show_button)
        
        self.hide_button = QPushButton("Скрыть центр уведомлений")
        self.hide_button.clicked.connect(self.hide_notification_center)
        buttons_layout.addWidget(self.hide_button)
        
        self.toggle_button = QPushButton("Переключить центр уведомлений")
        self.toggle_button.clicked.connect(self.toggle_notification_center)
        buttons_layout.addWidget(self.toggle_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Добавляем кнопки для демонстрации различных типов уведомлений
        demo_layout = QHBoxLayout()
        
        self.demo_info_button = QPushButton("Демо: Информация")
        self.demo_info_button.clicked.connect(self.demo_info_notification)
        demo_layout.addWidget(self.demo_info_button)
        
        self.demo_success_button = QPushButton("Демо: Успех")
        self.demo_success_button.clicked.connect(self.demo_success_notification)
        demo_layout.addWidget(self.demo_success_button)
        
        self.demo_warning_button = QPushButton("Демо: Предупреждение")
        self.demo_warning_button.clicked.connect(self.demo_warning_notification)
        demo_layout.addWidget(self.demo_warning_button)
        
        self.demo_error_button = QPushButton("Демо: Ошибка")
        self.demo_error_button.clicked.connect(self.demo_error_notification)
        demo_layout.addWidget(self.demo_error_button)
        
        main_layout.addLayout(demo_layout)
        
        # Добавляем кнопку для демонстрации серии уведомлений
        self.demo_series_button = QPushButton("Демо: Серия уведомлений")
        self.demo_series_button.clicked.connect(self.demo_notification_series)
        main_layout.addWidget(self.demo_series_button)
        
        # Инициализируем расширение центра уведомлений
        self.notification_center_extension = NotificationCenterExtension(self)
    
    def add_notification(self):
        """Добавляет уведомление из формы."""
        # Получаем данные из формы
        title = self.title_input.text()
        message = self.message_input.toPlainText()
        
        # Определяем тип уведомления
        type_text = self.type_combo.currentText()
        if type_text == "Информация":
            notification_type = NotificationType.INFO
        elif type_text == "Успех":
            notification_type = NotificationType.SUCCESS
        elif type_text == "Предупреждение":
            notification_type = NotificationType.WARNING
        else:
            notification_type = NotificationType.ERROR
        
        # Определяем опции
        auto_close = self.auto_close_checkbox.isChecked()
        duration = int(self.duration_combo.currentText())
        
        # Определяем действия
        actions = None
        if self.add_action_button.isChecked():
            actions = [
                {
                    "text": "Подробнее",
                    "callback": lambda: self.show_notification_center()
                }
            ]
        
        # Добавляем уведомление
        self.notification_center_extension.add_notification(
            title=title,
            message=message,
            notification_type=notification_type,
            actions=actions,
            auto_close=auto_close,
            duration=duration
        )
    
    def show_notification_center(self):
        """Показывает центр уведомлений."""
        self.notification_center_extension.show_notification_center()
    
    def hide_notification_center(self):
        """Скрывает центр уведомлений."""
        self.notification_center_extension.hide_notification_center()
    
    def toggle_notification_center(self):
        """Переключает видимость центра уведомлений."""
        self.notification_center_extension.toggle_notification_center()
    
    def demo_info_notification(self):
        """Демонстрирует информационное уведомление."""
        self.notification_center_extension.add_notification(
            title="Информационное уведомление",
            message="Это информационное уведомление для демонстрации центра уведомлений.",
            notification_type=NotificationType.INFO
        )
    
    def demo_success_notification(self):
        """Демонстрирует уведомление об успехе."""
        self.notification_center_extension.add_notification(
            title="Операция выполнена успешно",
            message="Все файлы были успешно сохранены.",
            notification_type=NotificationType.SUCCESS
        )
    
    def demo_warning_notification(self):
        """Демонстрирует предупреждающее уведомление."""
        self.notification_center_extension.add_notification(
            title="Предупреждение",
            message="Обнаружены несохраненные изменения. Пожалуйста, сохраните файлы перед выходом.",
            notification_type=NotificationType.WARNING,
            actions=[
                {
                    "text": "Сохранить",
                    "callback": lambda: self.demo_success_notification()
                },
                {
                    "text": "Игнорировать",
                    "callback": lambda: None
                }
            ]
        )
    
    def demo_error_notification(self):
        """Демонстрирует уведомление об ошибке."""
        self.notification_center_extension.add_notification(
            title="Ошибка",
            message="Не удалось подключиться к серверу. Проверьте подключение к интернету и повторите попытку.",
            notification_type=NotificationType.ERROR,
            actions=[
                {
                    "text": "Повторить",
                    "callback": lambda: self.demo_error_notification()
                }
            ],
            auto_close=False
        )
    
    def demo_notification_series(self):
        """Демонстрирует серию уведомлений."""
        # Информационное уведомление
        self.notification_center_extension.add_notification(
            title="Начало операции",
            message="Начинается выполнение длительной операции...",
            notification_type=NotificationType.INFO,
            duration=3000
        )
        
        # Имитируем задержку
        QApplication.processEvents()
        time.sleep(1)
        
        # Уведомление о прогрессе
        self.notification_center_extension.add_notification(
            title="Операция выполняется",
            message="Выполнено 25% операции...",
            notification_type=NotificationType.INFO,
            duration=3000
        )
        
        # Имитируем задержку
        QApplication.processEvents()
        time.sleep(1)
        
        # Уведомление о прогрессе
        self.notification_center_extension.add_notification(
            title="Операция выполняется",
            message="Выполнено 50% операции...",
            notification_type=NotificationType.INFO,
            duration=3000
        )
        
        # Имитируем задержку
        QApplication.processEvents()
        time.sleep(1)
        
        # Уведомление о прогрессе
        self.notification_center_extension.add_notification(
            title="Операция выполняется",
            message="Выполнено 75% операции...",
            notification_type=NotificationType.INFO,
            duration=3000
        )
        
        # Имитируем задержку
        QApplication.processEvents()
        time.sleep(1)
        
        # Уведомление об успешном завершении
        self.notification_center_extension.add_notification(
            title="Операция завершена",
            message="Операция успешно завершена!",
            notification_type=NotificationType.SUCCESS,
            actions=[
                {
                    "text": "Подробнее",
                    "callback": lambda: self.show_notification_center()
                }
            ]
        )


def main():
    """Основная функция примера."""
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
