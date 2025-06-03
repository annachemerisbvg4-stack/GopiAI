#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тесты для расширения NotificationCenter.
"""

import sys
import os
import pytest
from PySide6.QtWidgets import QApplication, QMainWindow

# Добавляем корневую папку проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from gopiai.extensions.notification_center_extension import (
    NotificationCenterExtension, Notification, NotificationType
)


@pytest.fixture
def app():
    """Создает экземпляр QApplication для тестов."""
    return QApplication([])


@pytest.fixture
def main_window(app):
    """Создает экземпляр QMainWindow для тестов."""
    return QMainWindow()


@pytest.fixture
def notification_center_extension(main_window):
    """Создает экземпляр NotificationCenterExtension для тестов."""
    return NotificationCenterExtension(main_window)


def test_notification_center_creation(notification_center_extension):
    """Тестирует создание NotificationCenterExtension."""
    assert notification_center_extension is not None
    assert notification_center_extension.notification_center is not None
    assert notification_center_extension.dock is not None
    assert hasattr(notification_center_extension.main_window, "notification_center_extension")
    assert hasattr(notification_center_extension.main_window, "add_notification")


def test_add_notification(notification_center_extension):
    """Тестирует добавление уведомления."""
    # Добавляем уведомление
    notification_id = notification_center_extension.add_notification(
        "Тестовое уведомление",
        "Это тестовое уведомление",
        NotificationType.INFO
    )
    
    # Проверяем, что уведомление добавлено
    assert notification_id in notification_center_extension.notification_center.notifications
    
    # Проверяем свойства уведомления
    notification = notification_center_extension.notification_center.notifications[notification_id]
    assert notification.title == "Тестовое уведомление"
    assert notification.message == "Это тестовое уведомление"
    assert notification.type == NotificationType.INFO


def test_notification_types(notification_center_extension):
    """Тестирует различные типы уведомлений."""
    # Добавляем уведомления разных типов
    info_id = notification_center_extension.add_notification(
        "Информация", "Информационное сообщение", NotificationType.INFO
    )
    success_id = notification_center_extension.add_notification(
        "Успех", "Операция выполнена успешно", NotificationType.SUCCESS
    )
    warning_id = notification_center_extension.add_notification(
        "Предупреждение", "Обратите внимание", NotificationType.WARNING
    )
    error_id = notification_center_extension.add_notification(
        "Ошибка", "Произошла ошибка", NotificationType.ERROR
    )
    
    # Проверяем цвета уведомлений
    info = notification_center_extension.notification_center.notifications[info_id]
    success = notification_center_extension.notification_center.notifications[success_id]
    warning = notification_center_extension.notification_center.notifications[warning_id]
    error = notification_center_extension.notification_center.notifications[error_id]
    
    assert info.get_color() == "#2196F3"  # Синий
    assert success.get_color() == "#4CAF50"  # Зеленый
    assert warning.get_color() == "#FFC107"  # Желтый
    assert error.get_color() == "#F44336"  # Красный


def test_notification_actions(notification_center_extension):
    """Тестирует действия уведомлений."""
    # Счетчик для проверки вызова callback
    counter = [0]
    
    def action_callback():
        counter[0] += 1
    
    # Добавляем уведомление с действием
    notification_id = notification_center_extension.add_notification(
        "Уведомление с действием",
        "Это уведомление содержит действие",
        NotificationType.INFO,
        actions=[
            {
                "text": "Выполнить",
                "callback": action_callback
            }
        ]
    )
    
    # Проверяем, что уведомление добавлено
    assert notification_id in notification_center_extension.notification_center.notifications
    
    # Проверяем, что действие добавлено
    notification = notification_center_extension.notification_center.notifications[notification_id]
    assert len(notification.actions) == 1
    assert notification.actions[0]["text"] == "Выполнить"
    
    # Эмулируем вызов действия
    notification_center_extension.notification_center.on_action_triggered(
        notification_id, "Выполнить"
    )
    
    # Проверяем, что callback был вызван
    assert counter[0] == 1


def test_toggle_notification_center(notification_center_extension):
    """Тестирует переключение видимости центра уведомлений."""
    # Изначально центр уведомлений скрыт
    assert not notification_center_extension.dock.isVisible()
    
    # Показываем центр уведомлений
    notification_center_extension.show_notification_center()
    assert notification_center_extension.dock.isVisible()
    
    # Скрываем центр уведомлений
    notification_center_extension.hide_notification_center()
    assert not notification_center_extension.dock.isVisible()
    
    # Переключаем видимость
    notification_center_extension.toggle_notification_center()
    assert notification_center_extension.dock.isVisible()
    
    # Переключаем видимость еще раз
    notification_center_extension.toggle_notification_center()
    assert not notification_center_extension.dock.isVisible()
