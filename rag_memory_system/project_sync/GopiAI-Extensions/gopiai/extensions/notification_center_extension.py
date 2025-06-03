#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Расширение центра уведомлений для GopiAI.

Это расширение добавляет центр уведомлений, который позволяет отображать
системные уведомления, сообщения от различных компонентов приложения
и информировать пользователя о важных событиях.
"""

import datetime
import uuid
from enum import Enum
from typing import List, Dict, Callable, Optional, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QDockWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QPen, QBrush

try:
    # Пытаемся импортировать SimpleLabel из модуля widgets
    from gopiai.widgets import SimpleLabel
    HAS_SIMPLE_LABEL = True
except ImportError:
    # Если не удалось, используем обычный QLabel
    from PySide6.QtWidgets import QLabel as SimpleLabel
    HAS_SIMPLE_LABEL = False

try:
    # Пытаемся импортировать CardWidget из модуля widgets
    from gopiai.widgets import CardWidget
    HAS_CARD_WIDGET = True
except ImportError:
    # Если не удалось, используем базовый QFrame
    HAS_CARD_WIDGET = False
    
    # Создаем простую замену для CardWidget
    class CardWidget(QFrame):
        """Простая замена для CardWidget, если он недоступен."""
        
        clicked = Signal()
        
        def __init__(self, title="", content="", parent=None):
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
            """)
            
            # Создаем лейаут
            self.layout = QVBoxLayout(self)
            self.layout.setContentsMargins(12, 12, 12, 12)
            self.layout.setSpacing(8)
            
            # Заголовок
            self.title_label = QLabel(title)
            self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            self.layout.addWidget(self.title_label)
            
            # Содержимое
            self.content_label = QLabel(content)
            self.content_label.setWordWrap(True)
            self.layout.addWidget(self.content_label)
            
            # Контейнер для кнопок
            self.buttons_container = QWidget()
            self.buttons_layout = QHBoxLayout(self.buttons_container)
            self.buttons_layout.setContentsMargins(0, 8, 0, 0)
            self.buttons_layout.setSpacing(8)
            self.buttons_layout.setAlignment(Qt.AlignRight)
            self.layout.addWidget(self.buttons_container)
        
        def add_button(self, text, callback=None):
            """Добавляет кнопку в карточку."""
            button = QPushButton(text)
            self.buttons_layout.addWidget(button)
            
            if callback:
                button.clicked.connect(callback)
            
            return button
        
        def set_content(self, content):
            """Устанавливает содержимое карточки."""
            self.content_label.setText(content)
        
        def set_title(self, title):
            """Устанавливает заголовок карточки."""
            self.title_label.setText(title)


class NotificationType(Enum):
    """Типы уведомлений."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class Notification:
    """Класс для представления уведомления."""
    
    def __init__(self, 
                 title: str, 
                 message: str, 
                 notification_type: NotificationType = NotificationType.INFO,
                 icon: Optional[QIcon] = None,
                 actions: Optional[List[Dict[str, Any]]] = None,
                 auto_close: bool = True,
                 duration: int = 5000):
        """
        Инициализирует уведомление.
        
        Args:
            title: Заголовок уведомления
            message: Текст уведомления
            notification_type: Тип уведомления (INFO, SUCCESS, WARNING, ERROR)
            icon: Иконка уведомления (опционально)
            actions: Список действий для уведомления (опционально)
                Каждое действие - словарь с ключами:
                - text: Текст кнопки
                - callback: Функция обратного вызова
            auto_close: Автоматически закрывать уведомление
            duration: Продолжительность отображения в мс (если auto_close=True)
        """
        self.id = str(uuid.uuid4())
        self.title = title
        self.message = message
        self.type = notification_type
        self.icon = icon
        self.actions = actions or []
        self.auto_close = auto_close
        self.duration = duration
        self.timestamp = datetime.datetime.now()
        self.read = False
    
    def mark_as_read(self):
        """Отмечает уведомление как прочитанное."""
        self.read = True
    
    def get_color(self) -> str:
        """Возвращает цвет для уведомления в зависимости от типа."""
        if self.type == NotificationType.INFO:
            return "#2196F3"  # Синий
        elif self.type == NotificationType.SUCCESS:
            return "#4CAF50"  # Зеленый
        elif self.type == NotificationType.WARNING:
            return "#FFC107"  # Желтый
        elif self.type == NotificationType.ERROR:
            return "#F44336"  # Красный
        return "#757575"  # Серый по умолчанию
    
    def get_icon(self) -> QIcon:
        """Возвращает иконку для уведомления."""
        if self.icon:
            return self.icon
        
        # Создаем иконку по умолчанию в зависимости от типа
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Рисуем круг с цветом типа уведомления
        color = QColor(self.get_color())
        painter.setPen(QPen(color, 2))
        painter.setBrush(QBrush(color.lighter(120)))
        painter.drawEllipse(2, 2, 20, 20)
        
        # Рисуем символ в зависимости от типа
        painter.setPen(QPen(Qt.white, 2))
        if self.type == NotificationType.INFO:
            # Рисуем "i"
            painter.drawLine(12, 8, 12, 10)
            painter.drawLine(12, 12, 12, 16)
        elif self.type == NotificationType.SUCCESS:
            # Рисуем галочку
            points = [QPoint(8, 12), QPoint(11, 16), QPoint(16, 8)]
            painter.drawPolyline(points)
        elif self.type == NotificationType.WARNING:
            # Рисуем "!"
            painter.drawLine(12, 7, 12, 13)
            painter.drawLine(12, 15, 12, 17)
        elif self.type == NotificationType.ERROR:
            # Рисуем "x"
            painter.drawLine(8, 8, 16, 16)
            painter.drawLine(16, 8, 8, 16)
        
        painter.end()
        
        return QIcon(pixmap)


class NotificationWidget(QWidget):
    """Виджет для отображения одного уведомления."""
    
    closed = Signal(str)  # Сигнал закрытия с ID уведомления
    action_triggered = Signal(str, str)  # Сигналы: ID уведомления, действие
    
    def __init__(self, notification: Notification, parent=None):
        """
        Инициализирует виджет уведомления.
        
        Args:
            notification: Объект уведомления
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.notification = notification
        self.init_ui()
        
        # Если уведомление автоматически закрывается, запускаем таймер
        if notification.auto_close:
            QTimer.singleShot(notification.duration, self.close_notification)
    
    def init_ui(self):
        """Инициализирует пользовательский интерфейс."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем карточку для уведомления
        if HAS_CARD_WIDGET:
            self.card = CardWidget(self.notification.title, self.notification.message)
            
            # Настраиваем стиль карточки
            self.card.set_style(
                border_color=self.notification.get_color(),
                border_radius=8
            )
        else:
            self.card = CardWidget(self.notification.title, self.notification.message)
            
            # Настраиваем стиль карточки
            border_color = self.notification.get_color()
            self.card.setStyleSheet(f"""
                #cardWidget {{
                    border: 2px solid {border_color};
                    border-radius: 8px;
                }}
            """)
        
        # Добавляем действия
        for action in self.notification.actions:
            self.card.add_button(
                action["text"],
                lambda action_text=action["text"]: self.trigger_action(action_text)
            )
        
        # Добавляем кнопку закрытия
        self.card.add_button("Закрыть", self.close_notification)
        
        layout.addWidget(self.card)
    
    def close_notification(self):
        """Закрывает уведомление."""
        self.notification.mark_as_read()
        self.closed.emit(self.notification.id)
        
        # Анимация исчезновения
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QSize(0, 0))
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.finished.connect(self.hide)
        self.animation.start()
    
    def trigger_action(self, action_text):
        """Вызывает действие по уведомлению."""
        self.action_triggered.emit(self.notification.id, action_text)
        
        # Находим соответствующее действие и вызываем его callback
        for action in self.notification.actions:
            if action["text"] == action_text and "callback" in action:
                action["callback"]()
                break
        
        # Закрываем уведомление после действия
        self.close_notification()


class NotificationCenter(QWidget):
    """Центр уведомлений."""
    
    def __init__(self, parent=None):
        """
        Инициализирует центр уведомлений.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.notifications = {}  # ID -> Notification
        self.notification_widgets = {}  # ID -> NotificationWidget
        self.callbacks = {}  # Тип события -> список функций
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализирует пользовательский интерфейс."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Заголовок
        header_layout = QHBoxLayout()
        
        if HAS_SIMPLE_LABEL:
            self.title_label = SimpleLabel("Центр уведомлений")
            self.title_label.set_style(font_size=16, bold=True)
        else:
            self.title_label = QLabel("Центр уведомлений")
            self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        header_layout.addWidget(self.title_label)
        
        # Кнопки управления
        self.clear_button = QPushButton("Очистить все")
        self.clear_button.clicked.connect(self.clear_all_notifications)
        header_layout.addWidget(self.clear_button)
        
        layout.addLayout(header_layout)
        
        # Область прокрутки для уведомлений
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Контейнер для уведомлений
        self.notifications_container = QWidget()
        self.notifications_layout = QVBoxLayout(self.notifications_container)
        self.notifications_layout.setContentsMargins(0, 0, 0, 0)
        self.notifications_layout.setSpacing(10)
        self.notifications_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.notifications_container)
        layout.addWidget(self.scroll_area, 1)  # 1 = растягивается
        
        # Метка с информацией
        if HAS_SIMPLE_LABEL:
            self.info_label = SimpleLabel()
            self.info_label.set_update_function(self.update_info_text)
            self.info_label.set_update_interval(1000)  # Обновление каждую секунду
        else:
            self.info_label = QLabel()
            self.update_info_timer = QTimer(self)
            self.update_info_timer.timeout.connect(
                lambda: self.info_label.setText(self.update_info_text())
            )
            self.update_info_timer.start(1000)  # Обновление каждую секунду
        
        layout.addWidget(self.info_label)
    
    def update_info_text(self):
        """Обновляет текст информационной метки."""
        count = len(self.notifications)
        unread = sum(1 for n in self.notifications.values() if not n.read)
        
        if count == 0:
            return "Нет уведомлений"
        
        return f"Всего уведомлений: {count}, непрочитанных: {unread}"
    
    def add_notification(self, notification: Notification):
        """
        Добавляет уведомление в центр уведомлений.
        
        Args:
            notification: Объект уведомления
        
        Returns:
            str: ID добавленного уведомления
        """
        # Сохраняем уведомление
        self.notifications[notification.id] = notification
        
        # Создаем виджет уведомления
        notification_widget = NotificationWidget(notification, self)
        notification_widget.closed.connect(self.on_notification_closed)
        notification_widget.action_triggered.connect(self.on_action_triggered)
        
        # Добавляем виджет в начало списка (новые уведомления сверху)
        self.notifications_layout.insertWidget(0, notification_widget)
        self.notification_widgets[notification.id] = notification_widget
        
        # Вызываем обработчики события добавления уведомления
        self.trigger_event("notification_added", notification)
        
        return notification.id
    
    def remove_notification(self, notification_id: str):
        """
        Удаляет уведомление из центра уведомлений.
        
        Args:
            notification_id: ID уведомления
        """
        if notification_id in self.notification_widgets:
            # Удаляем виджет
            widget = self.notification_widgets.pop(notification_id)
            self.notifications_layout.removeWidget(widget)
            widget.deleteLater()
        
        if notification_id in self.notifications:
            # Удаляем уведомление
            notification = self.notifications.pop(notification_id)
            
            # Вызываем обработчики события удаления уведомления
            self.trigger_event("notification_removed", notification)
    
    def clear_all_notifications(self):
        """Удаляет все уведомления."""
        # Копируем список ID, чтобы избежать изменения словаря во время итерации
        notification_ids = list(self.notifications.keys())
        
        for notification_id in notification_ids:
            self.remove_notification(notification_id)
    
    def on_notification_closed(self, notification_id: str):
        """
        Обрабатывает закрытие уведомления.
        
        Args:
            notification_id: ID закрытого уведомления
        """
        # Отмечаем уведомление как прочитанное
        if notification_id in self.notifications:
            self.notifications[notification_id].mark_as_read()
            
            # Вызываем обработчики события прочтения уведомления
            self.trigger_event("notification_read", self.notifications[notification_id])
    
    def on_action_triggered(self, notification_id: str, action_text: str):
        """
        Обрабатывает действие по уведомлению.
        
        Args:
            notification_id: ID уведомления
            action_text: Текст действия
        """
        if notification_id in self.notifications:
            # Вызываем обработчики события действия по уведомлению
            self.trigger_event(
                "notification_action",
                self.notifications[notification_id],
                action_text
            )
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Регистрирует функцию обратного вызова для события.
        
        Args:
            event_type: Тип события
            callback: Функция обратного вызова
        """
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        
        self.callbacks[event_type].append(callback)
    
    def unregister_callback(self, event_type: str, callback: Callable):
        """
        Отменяет регистрацию функции обратного вызова для события.
        
        Args:
            event_type: Тип события
            callback: Функция обратного вызова
        """
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
    
    def trigger_event(self, event_type: str, *args, **kwargs):
        """
        Вызывает обработчики события.
        
        Args:
            event_type: Тип события
            *args, **kwargs: Аргументы для передачи обработчикам
        """
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Ошибка в обработчике события {event_type}: {e}")


class NotificationCenterExtension:
    """
    Расширение центра уведомлений для GopiAI.
    
    Это расширение добавляет центр уведомлений, который позволяет отображать
    системные уведомления, сообщения от различных компонентов приложения
    и информировать пользователя о важных событиях.
    """
    
    def __init__(self, main_window):
        """
        Инициализирует расширение центра уведомлений.
        
        Args:
            main_window: Главное окно приложения
        """
        self.main_window = main_window
        
        # Создаем центр уведомлений
        self.notification_center = NotificationCenter()
        
        # Создаем док-виджет для центра уведомлений
        self.dock = QDockWidget("Центр уведомлений", main_window)
        self.dock.setObjectName("notificationCenterDock")
        self.dock.setWidget(self.notification_center)
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Добавляем док-виджет в главное окно
        main_window.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        
        # Скрываем док-виджет по умолчанию
        self.dock.hide()
        
        # Добавляем действие в меню
        self.add_menu_action()
        
        # Добавляем методы в главное окно для удобного доступа
        self.add_methods_to_main_window()
        
        # Добавляем приветственное уведомление
        self.add_welcome_notification()
    
    def add_menu_action(self):
        """Добавляет действие в меню для показа центра уведомлений."""
        # Проверяем, есть ли у главного окна метод add_menu_action
        if hasattr(self.main_window, "add_menu_action"):
            self.main_window.add_menu_action(
                "Вид",
                "Центр уведомлений",
                self.toggle_notification_center,
                shortcut="Ctrl+N"
            )
        # Иначе пробуем найти меню "Вид" и добавить действие
        elif hasattr(self.main_window, "menuBar"):
            menu_bar = self.main_window.menuBar()
            
            # Ищем меню "Вид"
            view_menu = None
            for action in menu_bar.actions():
                if action.text() == "Вид":
                    view_menu = action.menu()
                    break
            
            # Если меню "Вид" найдено, добавляем действие
            if view_menu:
                action = view_menu.addAction("Центр уведомлений")
                action.triggered.connect(self.toggle_notification_center)
    
    def add_methods_to_main_window(self):
        """Добавляет методы в главное окно для удобного доступа."""
        # Добавляем ссылку на расширение
        self.main_window.notification_center_extension = self
        
        # Добавляем методы
        self.main_window.add_notification = self.add_notification
        self.main_window.show_notification_center = self.show_notification_center
        self.main_window.hide_notification_center = self.hide_notification_center
        self.main_window.toggle_notification_center = self.toggle_notification_center
    
    def add_welcome_notification(self):
        """Добавляет приветственное уведомление."""
        self.add_notification(
            "Добро пожаловать в GopiAI",
            "Центр уведомлений успешно инициализирован. "
            "Здесь вы будете получать уведомления о важных событиях.",
            NotificationType.INFO,
            actions=[
                {
                    "text": "Подробнее",
                    "callback": lambda: self.show_notification_center()
                }
            ]
        )
    
    def add_notification(self, title, message, notification_type=NotificationType.INFO,
                        icon=None, actions=None, auto_close=True, duration=5000):
        """
        Добавляет уведомление в центр уведомлений.
        
        Args:
            title: Заголовок уведомления
            message: Текст уведомления
            notification_type: Тип уведомления (INFO, SUCCESS, WARNING, ERROR)
            icon: Иконка уведомления (опционально)
            actions: Список действий для уведомления (опционально)
                Каждое действие - словарь с ключами:
                - text: Текст кнопки
                - callback: Функция обратного вызова
            auto_close: Автоматически закрывать уведомление
            duration: Продолжительность отображения в мс (если auto_close=True)
        
        Returns:
            str: ID добавленного уведомления
        """
        notification = Notification(
            title=title,
            message=message,
            notification_type=notification_type,
            icon=icon,
            actions=actions,
            auto_close=auto_close,
            duration=duration
        )
        
        return self.notification_center.add_notification(notification)
    
    def show_notification_center(self):
        """Показывает центр уведомлений."""
        self.dock.show()
        self.dock.raise_()
    
    def hide_notification_center(self):
        """Скрывает центр уведомлений."""
        self.dock.hide()
    
    def toggle_notification_center(self):
        """Переключает видимость центра уведомлений."""
        if self.dock.isVisible():
            self.hide_notification_center()
        else:
            self.show_notification_center()


def init_extension(main_window):
    """
    Инициализирует расширение центра уведомлений.
    
    Args:
        main_window: Главное окно приложения
    
    Returns:
        NotificationCenterExtension: Экземпляр расширения
    """
    # Создаем экземпляр расширения
    extension = NotificationCenterExtension(main_window)
    
    return extension
