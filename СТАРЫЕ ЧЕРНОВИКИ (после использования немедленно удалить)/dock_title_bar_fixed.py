"""
Модуль для создания кастомизированных заголовков QDockWidget
с поддержкой кнопок управления в зависимости от типа и состояния окна.
"""

import os
import sys
import logging
from typing import Optional

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from app.ui.i18n.translator import tr
from app.ui.icon_adapter import IconAdapter

logger = logging.getLogger(__name__)

# Импортируем ThemeManager для управления темами
imported_theme_manager = False
app_theme_manager = None

# Пытаемся импортировать ThemeManager через прокси или напрямую
try:
    # Сначала пробуем импортировать через прокси-класс
    from app.ui.theme_manager import ThemeManager as AppThemeManager
    logger.info("Импортирован ThemeManager из app.ui.theme_manager")
    imported_theme_manager = True
    app_theme_manager = AppThemeManager
except ImportError as e:
    logger.warning(f"Не удалось импортировать ThemeManager из app.ui.theme_manager: {e}")
    try:
        # Если не получилось, пробуем импортировать напрямую из simple_theme_manager
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        if root_path not in sys.path:
            sys.path.append(root_path)
        from simple_theme_manager import ThemeManager as AppThemeManager
        logger.info("Импортирован ThemeManager из simple_theme_manager")
        imported_theme_manager = True
        app_theme_manager = AppThemeManager
    except ImportError as e:
        logger.error(f"Ошибка импорта ThemeManager: {e}")
        # Определим заглушку ThemeManager далее

# Определяем фоллбек-класс ThemeManager, если не удалось импортировать
class ThemeManager:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def get_current_visual_theme(self):
        return "dark"  # По умолчанию тёмная тема

    def get_color(self, key, default_value):
        # Простой словарь цветов для базовой функциональности
        colors = {
            "dock_title_background": "#3C3C3C",
            "border": "#444444",
            "dock_title_foreground": "#EAEAEA",
            "dock_title_button_hover_background_color": "rgba(255, 255, 255, 0.2)",
            "dock_title_button_pressed_background_color": "rgba(255, 255, 255, 0.1)",
            "custom_dock_title_bar_close_button_hover_background_color": "rgba(232, 17, 35, 0.7)",
            "custom_dock_title_bar_close_button_pressed_background_color": "rgba(232, 17, 35, 0.9)",
            "accent": "#1E90FF"
        }
        return colors.get(key, default_value)

# Функция для получения правильного экземпляра ThemeManager
def get_theme_manager():
    """
    Получает экземпляр ThemeManager из импортированного модуля или фоллбек-реализацию
    """
    if imported_theme_manager and app_theme_manager:
        return app_theme_manager.instance()
    else:
        return ThemeManager.instance()

class DockTitleBar(QWidget):
    """
    Кастомный заголовок для QDockWidget с кнопками и стилизацией.
    """

    # Сигналы для обработки действий пользователя
    close_clicked = Signal()
    float_clicked = Signal()
    maximize_clicked = Signal()
    
    def __init__(
        self, title="", icon_manager: Optional[IconAdapter] = None, parent=None
    ):  # Добавлен icon_manager
        """
        Инициализирует панель заголовка с заданным текстом и родителем.

        Args:
            title (str): Текст заголовка.
            icon_manager (IconAdapter): Экземпляр менеджера иконок.
            parent (QWidget): Родительский виджет.
        """
        super().__init__(parent)
        self.title = title
        self.icon_manager = (
            icon_manager if icon_manager else IconAdapter.instance()
        )  # Для обратной совместимости, если не передан
        self._setup_ui()
        self._setup_styles()

    def _setup_ui(self):
        """Настраивает UI компоненты заголовка."""
        # Создаем горизонтальный макет для заголовка
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)  # Устанавливаем минимальные отступы
        layout.setSpacing(3)  # Минимальный промежуток между элементами

        # Создаем и настраиваем иконку заголовка
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(16, 16)
        self.icon_label.setObjectName("dockTitleIcon")

        # Создаем и настраиваем текст заголовка
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("dockTitleText")
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Кнопка плавающего режима
        self.float_button = QPushButton()
        self.float_button.setObjectName("dockFloatButton")
        self.float_button.setToolTip(tr("dock_title_bar.float", "Undock panel"))
        self.float_button.setFixedSize(16, 16)
        self.float_button.setFlat(True)
        self.float_button.clicked.connect(self.float_clicked)

        # Кнопка максимизации
        self.maximize_button = QPushButton()
        self.maximize_button.setObjectName("dockMaximizeButton")
        self.maximize_button.setToolTip(tr("dock_title_bar.maximize", "Maximize panel"))
        self.maximize_button.setFixedSize(16, 16)
        self.maximize_button.setFlat(True)
        self.maximize_button.clicked.connect(self.maximize_clicked)

        # Кнопка закрытия
        self.close_button = QPushButton()
        self.close_button.setObjectName("dockCloseButton")
        self.close_button.setToolTip(tr("dock_title_bar.close", "Close panel"))
        self.close_button.setFixedSize(16, 16)
        self.close_button.setFlat(True)
        self.close_button.clicked.connect(self.close_clicked)

        # Добавляем все элементы в макет
        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.float_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)

        # Устанавливаем макет
        self.setLayout(layout)
        
        # Применяем иконки для кнопок и заголовка
        self._update_icons()

    def _setup_styles(self):
        """Настраивает стили для компонентов заголовка."""
        # Получаем менеджер тем
        theme_manager = get_theme_manager()

        # Определяем, является ли родительский виджет плавающим
        is_floating = False
        if self.parent() and isinstance(self.parent(), QDockWidget):
            is_floating = self.parent().isFloating()

        # Получаем цвета из темы
        if is_floating:
            # Современные стили для плавающего окна (как сейчас)
            bg_color = theme_manager.get_color("window_background", "#2D2D2D")
            border_color = theme_manager.get_color("border", "#444444")
        else:
            # Современные стили для закрепленного дока (вместо серого)
            bg_color = theme_manager.get_color("window_background", "#2D2D2D")
            border_color = theme_manager.get_color("border", "#444444")

        text_color = theme_manager.get_color("dock_title_foreground", "#EAEAEA")
        button_hover_bg = theme_manager.get_color(
            "dock_title_button_hover_background_color", "rgba(255, 255, 255, 0.2)"
        )
        button_pressed_bg = theme_manager.get_color(
            "dock_title_button_pressed_background_color", "rgba(255, 255, 255, 0.1)"
        )
        close_hover_bg = theme_manager.get_color(
            "custom_dock_title_bar_close_button_hover_background_color",
            "rgba(232, 17, 35, 0.7)",
        )
        close_pressed_bg = theme_manager.get_color(
            "custom_dock_title_bar_close_button_pressed_background_color",
            "rgba(232, 17, 35, 0.9)",
        )

        # Применяем стили
        # Получаем акцентный цвет из темы
        accent_color = theme_manager.get_color("accent", "#1E90FF")

        # Применяем стили  
        self.setStyleSheet(
            f"""
            /* Заголовок DockWidget */
            DockTitleBar {{
            background-color: {bg_color};
            border-bottom: 1px solid {border_color};
            border-top-left-radius: 14px;
            border-top-right-radius: 14px;
            min-height: 28px;
            max-height: 28px;
            padding-left: 8px;
            padding-right: 8px;
            box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
            }}

            /* Текст заголовка */
            DockTitleBar QLabel#dockTitleText {{
            font-weight: 600;
            color: {text_color};
            font-size: 15px;
            letter-spacing: 0.5px;
            }}

            /* Кнопки управления */
            DockTitleBar QPushButton {{
            background-color: transparent;
            border: none;
            color: {text_color};
            border-radius: 8px;
            min-width: 24px;
            min-height: 24px;
            font-size: 15px;
            transition: background 0.2s;
            }}

            /* Hover-эффекты */
            DockTitleBar QPushButton:hover {{
            background-color: {button_hover_bg};
            color: {accent_color};
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }}

            DockTitleBar QPushButton:pressed {{
            background-color: {button_pressed_bg};
            color: {accent_color};
            border-radius: 8px;
            }}

            /* Кнопка закрытия с отдельными цветами */
            DockTitleBar QPushButton#dockCloseButton {{
            color: #fff;
            background-color: transparent;
            }}
            DockTitleBar QPushButton#dockCloseButton:hover {{
            background-color: {close_hover_bg};
            color: #fff;
            border-radius: 8px;
            }}
            DockTitleBar QPushButton#dockCloseButton:pressed {{
            background-color: {close_pressed_bg};
            color: #fff;                
            border-radius: 8px;
            }}
            """
        )

    def _update_icons(self):
        """Обновляет иконки в зависимости от текущей темы."""
        try:
            # Получаем текущую тему
            theme_manager = get_theme_manager()
            current_theme = theme_manager.get_current_visual_theme()
            
            # Проверяем, является ли текущая тема темной
            is_dark_theme = current_theme == "dark"

            # Проверяем, является ли родительский виджет плавающим
            is_floating = False
            if self.parent() and isinstance(self.parent(), QDockWidget):
                is_floating = self.parent().isFloating()

            # Загрузка иконок в зависимости от темы
            icon_suffix = "white" if is_dark_theme else "black"

            self.close_button.setIcon(
                self.icon_manager.get_icon(f"close_{icon_suffix}")
            )
            self.float_button.setIcon(
                self.icon_manager.get_icon(f"float_{icon_suffix}")
            )
            self.maximize_button.setIcon(
                self.icon_manager.get_icon(f"maximize_{icon_suffix}")
            )

            # Устанавливаем размер иконки
            icon_size = QSize(12, 12)
            self.close_button.setIconSize(icon_size)
            self.float_button.setIconSize(icon_size)
            self.maximize_button.setIconSize(icon_size)

            # Установка иконки для заголовка в зависимости от типа дока
            icon_name = "app_icon"  # Иконка по умолчанию

            if self.title:
                title_lower = self.title.lower()
                if "chat" in title_lower:
                    icon_name = "chat"
                elif "terminal" in title_lower:
                    icon_name = "terminal"
                elif "browser" in title_lower:
                    icon_name = "browser"
                elif "explorer" in title_lower or "files" in title_lower:
                    icon_name = "folder"
                    
            # Устанавливаем иконку заголовка
            self.icon_label.setPixmap(
                self.icon_manager.get_icon(icon_name).pixmap(16, 16)
            )

            # Обновляем стили в соответствии с цветовой схемой
            text_color = theme_manager.get_color(
                "dock_title_foreground", "#EAEAEA" if is_dark_theme else "#333333"
            )

            # Используем современный стиль фона как для плавающего, так и для закрепленного режима
            bg_color = theme_manager.get_color(
                "window_background", "#2D2D2D" if is_dark_theme else "#F0F0F0"
            )

            hover_bg = theme_manager.get_color(
                "dock_title_button_hover_background_color",
                "rgba(255, 255, 255, 0.2)" if is_dark_theme else "rgba(0, 0, 0, 0.1)",
            )
            pressed_bg = theme_manager.get_color(
                "dock_title_button_pressed_background_color",
                "rgba(255, 255, 255, 0.1)" if is_dark_theme else "rgba(0, 0, 0, 0.05)",
            )
            close_hover_bg = theme_manager.get_color(
                "custom_dock_title_bar_close_button_hover_background_color",
                "rgba(232, 17, 35, 0.7)",
            )

            # Получаем цвет границы
            border_color = theme_manager.get_color("border", "#444444" if is_dark_theme else "#E0E0E0")

            # Применяем современный стиль к заголовку с тенями и скруглением
            self.setStyleSheet(
                f"""
                background-color: {bg_color};
                border-bottom: 1px solid {border_color};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
                """
            )

            # Устанавливаем цвет текста
            self.title_label.setStyleSheet(f"color: {text_color};")

            # Создаем стиль для кнопок с использованием переменных
            button_style = f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_bg};
                }}
            """

            # Отдельный стиль для кнопки закрытия
            close_button_style = f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {close_hover_bg};
                }}
                QPushButton:pressed {{
                    background-color: rgba(232, 17, 35, 0.9);
                }}
            """
            
            self.close_button.setStyleSheet(close_button_style)
            self.float_button.setStyleSheet(button_style)
            self.maximize_button.setStyleSheet(button_style)
        except Exception as e:
            logger.error(f"Ошибка при обновлении иконок заголовка: {str(e)}")

    def refresh_theme(self):
        """Обновляет стили в соответствии с текущей темой."""
        # Вызываем приватные методы для обновления стилей и иконок
        try:
            self._setup_styles()
            self._update_icons()
        except Exception as e:
            logger.error(f"Ошибка при обновлении стилей: {e}")

    def update_floating_style(self, is_floating):
        """Обновляет стили в зависимости от плавающего состояния."""
        try:
            # Вызываем обновление темы, которое применит правильные стили
            self.refresh_theme()
        except Exception as e:
            logger.error(f"Ошибка при обновлении стилей плавающего режима: {e}")
            
    # Сохраняем оригинальный метод update_theme для совместимости
    def update_theme(self):
        """Обновляет стили для совместимости с предыдущим кодом."""
        self.refresh_theme()

    # Переопределяем метод update с правильной сигнатурой
    def update(self, *args, **kwargs):
        """
        Переопределение встроенного метода update для виджета.

        Вызывает родительскую реализацию для обеспечения правильного обновления виджета.
        """
        # Вызываем оригинальный метод update родительского класса
        super().update(*args, **kwargs)

    def set_title(self, title):
        """Устанавливает текст заголовка."""
        self.title = title
        self.title_label.setText(title)
        self._update_icons()  # Обновляем иконки, так как они могут зависеть от заголовка

def apply_custom_title_bar(
    dock_widget, icon_manager: Optional[IconAdapter], is_docked_permanent=False
):  # Добавлен icon_manager
    """
    Применяет кастомный заголовок к QDockWidget.

    Args:
        dock_widget (QDockWidget): Док-виджет, к которому применяется заголовок.
        icon_manager (IconAdapter): Экземпляр менеджера иконок.
        is_docked_permanent (bool): Является ли док постоянно закрепленным.

    Returns:
        DockTitleBar: Созданный заголовок
    """
    # Создаем кастомный заголовок с текущим названием дока
    title_bar = DockTitleBar(
        dock_widget.windowTitle(), icon_manager, dock_widget
    )  # Передаем icon_manager

    # Устанавливаем современные стили для заголовка
    # Они будут применены в _setup_styles и _update_icons внутри DockTitleBar

    # Подключаем сигналы для управления доком
    title_bar.close_clicked.connect(dock_widget.close)
    title_bar.float_clicked.connect(lambda: dock_widget.setFloating(True))
    title_bar.maximize_clicked.connect(
        lambda: dock_widget.setFloating(not dock_widget.isFloating())
    )

    # Следим за изменением состояния окна и обновляем стили при изменении
    def on_floating_changed(floating):
        # Обновляем заголовок
        title_bar.set_title(dock_widget.windowTitle())
        # Важно: обновляем стили при изменении состояния плавающего режима
        title_bar.refresh_theme()  # Вызываем наш безопасный метод для обновления темы

    dock_widget.topLevelChanged.connect(on_floating_changed)

    # Настраиваем обработку изменения заголовка
    dock_widget.windowTitleChanged.connect(title_bar.set_title)

    # Применяем заголовок к dock_widget
    dock_widget.setTitleBarWidget(title_bar)

    return title_bar
