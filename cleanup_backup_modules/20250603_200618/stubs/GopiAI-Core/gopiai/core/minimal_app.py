посмотри,#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 📅 TODO_STUB_SEARCH: найти командой grep -r 'TODO_STUB' .

###############################################################
#                                                           #
#   ВНИМАНИЕ!                                               #
#   Это минимальный main window приложения GopiAI!           #
#   НЕ ДОБАВЛЯТЬ сюда никакие визуальные эффекты,            #
#   декорации, рамки, анимации, плавающие окна и т.д.!       #
#   Всё красивое — только в отдельные модули!                #
#   Здесь — только базовая логика и минимум UI!              #
#                                                           #
#   Если хочется добавить красоту — см. assets/decorative_layers.py #
#                                                           #
#   Нарушение этого правила = 🐰 будет грустить!              #
###############################################################

"""
Минимальная версия приложения GopiAI.
Содержит только главное окно, текстовый редактор и меню Файл с пунктами Открыть и Сохранить.
Использует frameless окно со своей панелью заголовка.

Модульная версия с исправленными импортами для GopiAI-Core.
"""

from gopiai.core.logging import get_logger
logger = get_logger().logger
import sys
import os

# Добавляем пути к другим модулям GopiAI
current_dir = os.path.dirname(os.path.abspath(__file__))
gopi_modules_dir = os.path.join(current_dir, "..", "..", "..", "..")
assets_path = os.path.join(gopi_modules_dir, "GopiAI-Assets")
widgets_path = os.path.join(gopi_modules_dir, "GopiAI-Widgets")

if os.path.exists(assets_path) and assets_path not in sys.path:
    sys.path.insert(0, assets_path)
if os.path.exists(widgets_path) and widgets_path not in sys.path:
    sys.path.insert(0, widgets_path)

from PySide6.QtCore import Qt, QEvent, Signal
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QMenu,
    QSizePolicy,
    QDialog,
    QColorDialog,
    QTabWidget,
)

# Настройка логирования уже происходит через unified logging system
logger = get_logger().logger

# 🚧 ЗАГЛУШКА! TODO_STUB: Требует реализации
# Функция-заглушка для иконок
def get_icon_placeholder(icon_name):
    # 🚧 ЗАГЛУШКА! TODO_STUB: Документированная заглушка
    """Заглушка для загрузки иконок."""
    logger.info(f"Запрошена иконка: {icon_name}")
    return QIcon()

ICONS_AVAILABLE = False
get_icon = get_icon_placeholder

# Импортируем функционал тем с корректными модульными путями
try:
    from gopiai.core.simple_theme_manager import (
        choose_theme_dialog,
        apply_theme,
        load_theme,
        _is_light,
    )
    logger.info("Загружен ThemeManager из gopiai.core.simple_theme_manager")
except ImportError as e:
    logger.warning(f"Не удалось загрузить ThemeManager: {e}")
    # Заглушки для функций тем
    def choose_theme_dialog(app):
        return None
    def apply_theme(app):
        pass
    def load_theme():
        return {}
    def _is_light(color):
        return True

try:
    # Пытаемся импортировать из модуля assets
    sys.path.insert(0, os.path.join(gopi_modules_dir, "GopiAI-Assets"))
    from gopiai.assets.titlebar_with_menu import TitlebarWithMenu
    logger.info("Загружен TitlebarWithMenu из gopiai.assets")
except ImportError as e:
    logger.warning(f"Не удалось загрузить TitlebarWithMenu: {e}")
    # Создаем простую заглушку для titlebar
    from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenuBar
    
    class TitlebarWithMenu(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            # Заглушка для titlebar
            layout = QHBoxLayout()
            title_label = QLabel("GopiAI v0.2.0")
            layout.addWidget(title_label)
            layout.addStretch()
            self.setLayout(layout)
            # Создаем простой menubar
            self.menubar = QMenuBar(self)
            
        def set_window(self, window):
            # Заглушка для set_window
            pass

try:
    from gopiai.widgets.custom_grips.custom_grips import CustomGrip
    logger.info("Загружены CustomGrip из gopiai.widgets")
except ImportError as e:
    logger.warning(f"Не удалось загрузить CustomGrip: {e}")
    # 🚧 ЗАГЛУШКА! TODO_STUB: Требует реализации
    # Заглушка для грипов
    class CustomGrip:
        def __init__(self, parent, edge):
            pass
        def setGeometry(self, x, y, w, h):
            pass
        def raise_(self):
            pass

try:
    from gopiai.widgets.core.text_editor import TextEditorWidget
    logger.info("Загружен TextEditorWidget из gopiai.widgets")
except ImportError as e:
    logger.error(f"Не удалось загрузить TextEditorWidget: {e}")
    raise

try:
    from gopiai.core.icon_adapter import IconAdapter
    logger.info("Загружен IconAdapter из gopiai.core")
except ImportError as e:
    logger.warning(f"Не удалось загрузить IconAdapter: {e}")
    # 🚧 ЗАГЛУШКА! TODO_STUB: Требует реализации
    # Заглушка для IconAdapter
    class IconAdapter:
        @staticmethod
        def instance():
            return None


# --- Функция для base64 -> QPixmap ---
def base64_to_pixmap(base64_str):
    try:
        cleaned_base64 = (
            base64_str.replace("\n", "")
            .replace("\r", "")
            .replace(" ", "")
            .replace("\t", "")
        )
        if not cleaned_base64:
            logger.error("Пустая строка base64 после очистки")
            return QPixmap()
        import base64

        image_data = base64.b64decode(cleaned_base64)
        pixmap = QPixmap()
        success = pixmap.loadFromData(image_data)
        if not success or pixmap.isNull():
            logger.error("Не удалось загрузить данные изображения в QPixmap")
            return QPixmap()
        return pixmap
    except Exception as e:
        logger.error(f"Ошибка при преобразовании base64 в QPixmap: {e}")
        return QPixmap()


# --- FramelessMainWindow ---
class FramelessMainWindow(QMainWindow):
    # Добавляем сигнал для уведомления о смене темы
    theme_changed = Signal(dict)  # Сигнал передает словарь с данными темы

    def __init__(self):
        super().__init__(None, Qt.WindowType.FramelessWindowHint)
        self.setObjectName("framelessMainWindow")
        self.setMinimumSize(700, 520)  # ещё больше
        self.resize(1200, 800)  # ещё больше
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Безопасная инициализация IconAdapter
        try:
            self.icon_manager = IconAdapter.instance()
        except Exception as e:
            logger.warning(f"Не удалось инициализировать IconAdapter: {e}")
            self.icon_manager = None
            
        self.TITLEBAR_HEIGHT = 40  # Высота заголовка в пикселях

        # --- Настраиваем главный виджет-контейнер для всего содержимого ---
        self.main_container = QWidget(self)
        self.main_container.setObjectName("mainContainer")
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(
            24, 0, 24, 24
        )  # увеличенные внешние отступы
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_container)

        # --- Titlebar вверху с приоритетом поверх всех элементов ---
        self.titlebar_with_menu = TitlebarWithMenu(self)
        self.titlebar_with_menu.set_window(self)
        self.titlebar_with_menu.setFixedHeight(self.TITLEBAR_HEIGHT)
        self.titlebar_with_menu.setObjectName("titlebarWithMenu")

        # --- Делаем заголовок отдельным виджетом для исключения перекрытия ---
        # Он не будет частью главного layout, а будет всегда поверх содержимого
        self.titlebar_with_menu.setParent(self)
        self.titlebar_with_menu.move(0, 0)
        self.titlebar_with_menu.resize(self.width(), self.TITLEBAR_HEIGHT)
        self.titlebar_with_menu.show()
        self.titlebar_with_menu.raise_()  # Поднимаем поверх остальных виджетов

        # --- Основная область приложения (занимает все место, начиная с отступа под заголовком) ---
        self.content_widget = QWidget(self.main_container)
        self.content_widget.setObjectName("contentWidget")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.main_layout.addWidget(self.content_widget, 1)  # Коэффициент растяжения 1

        # --- Tab workspace (центральный виджет) ---
        self.tab_widget = QTabWidget(self.content_widget)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.tabBar().setMovable(True)
        self.content_layout.addWidget(self.tab_widget)

        # --- Настраиваем поведение док-виджетов как в VS Code ---
        self.setDockOptions(
            QMainWindow.DockOption.AnimatedDocks
            | QMainWindow.DockOption.AllowNestedDocks
            | QMainWindow.DockOption.AllowTabbedDocks
            | QMainWindow.DockOption.GroupedDragging
        )
        # Ограничиваем возможность закрепления доков к центральному виджету
        # Это предотвращает закрепление окон к основному окну редактора
        self.setDockNestingEnabled(True)
        # Устанавливаем маржу для всех виджетов в главном окне, чтобы они не перекрывали заголовок
        self.setContentsMargins(
            20, self.TITLEBAR_HEIGHT + 8, 20, 20
        )  # увеличенные внешние отступы для всего окна
        
        # --- Открыть первую вкладку ---
        self.open_text_editor()
        
        # --- Drag support ---
        self._drag_active = False
        self._drag_pos = None
        
        # --- Меню: подключение выбора темы ---
        self._connect_theme_menu()
        self._apply_tab_theme()
        
        # --- Файл: подключение сигналов ---
        self._connect_file_menu()
        
        # --- Правка: подключение ---
        self._connect_edit_menu()
        
        # --- Resize grips ---
        self._init_grips()
        
        # --- Новые сигналы меню 'Вид' ---
        self._connect_view_menu()

    def _connect_file_menu(self):
        """Подключение сигналов меню 'Файл'."""
        try:
            menubar = self.titlebar_with_menu.menubar
            menubar.newFileRequested.connect(self._menu_new_file)
            menubar.openFileRequested.connect(self._menu_open_file)
            menubar.openFolderRequested.connect(self._menu_open_folder)
            menubar.saveRequested.connect(self._menu_save)
            menubar.saveAsRequested.connect(self._menu_save_as)
            menubar.exitRequested.connect(self.close)
            menubar.openTextEditorRequested.connect(self.open_text_editor)
            logger.info("Подключены сигналы меню 'Файл'")
        except Exception as e:
            logger.error(f"Ошибка при подключении меню 'Файл': {e}")

    def _connect_edit_menu(self):
        """Подключение сигналов меню 'Правка'."""
        try:
            menubar = self.titlebar_with_menu.menubar
            menubar.undo_action.triggered.connect(self._menu_undo)
            menubar.redo_action.triggered.connect(self._menu_redo)
            menubar.cut_action.triggered.connect(self._menu_cut)
            menubar.copy_action.triggered.connect(self._menu_copy)
            menubar.paste_action.triggered.connect(self._menu_paste)
            menubar.delete_action.triggered.connect(self._menu_delete)
            menubar.select_all_action.triggered.connect(self._menu_select_all)
            logger.info("Подключены сигналы меню 'Правка'")
        except Exception as e:
            logger.error(f"Ошибка при подключении меню 'Правка': {e}")

    def _connect_view_menu(self):
        """Подключение сигналов меню 'Вид'."""
        try:
            menubar = self.titlebar_with_menu.menubar
            menubar.openProjectExplorerRequested.connect(self._menu_open_project_explorer)
            menubar.openChatRequested.connect(self._menu_open_chat)
            menubar.openBrowserRequested.connect(self._menu_open_browser)
            menubar.openTerminalRequested.connect(self._menu_open_terminal)
            logger.info("Подключены сигналы меню 'Вид'")
        except Exception as e:
            logger.error(f"Ошибка при подключении меню 'Вид': {e}")

    def _connect_theme_menu(self):
        """Подключение диалога выбора темы."""
        try:
            # Находим пункт 'Тема' в меню 'Вид' и подключаем к нему choose_theme_dialog
            menubar = self.titlebar_with_menu.menubar
            for action in menubar.actions():
                menu = action.menu()
                if menu and isinstance(menu, QMenu) and menu.title() == "Вид":
                    for subaction in menu.actions():
                        if subaction.text() == "Тема":
                            subaction.triggered.connect(self._show_theme_dialog)
                            logger.info("Подключен диалог выбора темы")
                            return
        except Exception as e:
            logger.error(f"Ошибка при подключении диалога темы: {e}")

    def _apply_tab_theme(self):
        """Применение темы к вкладкам."""
        try:
            theme = load_theme() or {}
            tab_color = theme.get("control_color") or theme.get("header_color") or "#cccccc"
            active_color = theme.get("accent_color") or tab_color
            border_color = theme.get("border_color") or tab_color

            def get_tab_text_color(bg):
                try:
                    return "#222" if _is_light(bg) else "#fff"
                except Exception:
                    return "#222"

            text_color = get_tab_text_color(tab_color)
            active_text_color = get_tab_text_color(active_color)
            
            self.tab_widget.setStyleSheet(
                f"""
                QTabBar::tab {{
                    background: {tab_color};
                    color: {text_color};
                    border: 1px solid {border_color};
                    padding: 6px 16px;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    margin-right: 2px;
                }}
                QTabBar::tab:selected {{
                    background: {active_color};
                    color: {active_text_color};
                    border: 1px solid {border_color};
                }}
                QTabWidget::pane {{
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    top: -1px;
                }}
            """
            )
        except Exception as e:
            logger.error(f"Ошибка при применении темы к вкладкам: {e}")

    def _show_theme_dialog(self):
        """Показать диалог выбора темы."""
        try:
            app = QApplication.instance()
            theme_data = choose_theme_dialog(app)
            self._apply_tab_theme()

            # Отправляем сигнал об изменении темы всем подписчикам
            if theme_data:
                self.theme_changed.emit(theme_data)
            else:
                # Если theme_data не была возвращена, загружаем текущую тему
                current_theme = load_theme() or {}
                self.theme_changed.emit(current_theme)
        except Exception as e:
            logger.error(f"Ошибка при показе диалога темы: {e}")

    def open_text_editor(self, filename=None):
        """Открыть новый текстовый редактор в новой вкладке."""
        try:
            editor = TextEditorWidget(self)
            idx = self.tab_widget.addTab(editor, filename or "Новый файл")
            self.tab_widget.setCurrentIndex(idx)

            def update_tab_name(name):
                self.tab_widget.setTabText(idx, name)

            editor.file_name_changed.connect(update_tab_name)
            logger.info(f"Открыт новый редактор: {filename or 'Новый файл'}")
        except Exception as e:
            logger.error(f"Ошибка при открытии текстового редактора: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть текстовый редактор:\n{e}")

    def close_tab(self, index):
        """Закрыть вкладку по индексу."""
        try:
            widget = self.tab_widget.widget(index)
            self.tab_widget.removeTab(index)
            if widget:
                widget.deleteLater()
            logger.info(f"Закрыта вкладка с индексом: {index}")
        except Exception as e:
            logger.error(f"Ошибка при закрытии вкладки: {e}")

    def update_title(self, filename=None):
        """Обновить заголовок окна."""
        try:
            if filename:
                self.titlebar_with_menu.update_title(filename)
            else:
                self.titlebar_with_menu.update_title("GopiAI - Минимальная версия")
        except Exception as e:
            logger.error(f"Ошибка при обновлении заголовка: {e}")

    def maximize_window(self):
        """Развернуть окно на весь экран."""
        self.titlebar_with_menu.maximize_window()

    def restore_window(self):
        """Восстановить размер окна."""
        self.titlebar_with_menu.restore_window()

    def _init_grips(self):
        """Инициализация грипов для изменения размера окна."""
        try:
            self._grip_top = CustomGrip(self, Qt.Edge.TopEdge)
            self._grip_bottom = CustomGrip(self, Qt.Edge.BottomEdge)
            self._grip_left = CustomGrip(self, Qt.Edge.LeftEdge)
            self._grip_right = CustomGrip(self, Qt.Edge.RightEdge)
            self._update_grips()
            logger.info("Инициализированы грипы для изменения размера")
        except Exception as e:
            logger.warning(f"Ошибка при инициализации грипов: {e}")

    def _update_grips(self):
        """Обновление позиции грипов."""
        try:
            GRIP_SIZE = 10
            w, h = self.width(), self.height()
            
            self._grip_top.setGeometry(0, 0, w, GRIP_SIZE)
            self._grip_bottom.setGeometry(0, h - GRIP_SIZE, w, GRIP_SIZE)
            self._grip_left.setGeometry(0, 0, GRIP_SIZE, h)
            self._grip_right.setGeometry(w - GRIP_SIZE, 0, GRIP_SIZE, h)  # Исправлена ошибка
            
            self._grip_top.raise_()
            self._grip_bottom.raise_()
            self._grip_left.raise_()
            self._grip_right.raise_()
        except Exception as e:
            logger.warning(f"Ошибка при обновлении грипов: {e}")

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMaximized():
                self.titlebar_with_menu.maximize_window()
            else:
                self.titlebar_with_menu.restore_window()
            # При изменении состояния окна убедимся, что заголовок остаётся поверх содержимого
            self.titlebar_with_menu.raise_()
        super().changeEvent(event)

    def showEvent(self, event):
        """Обработка события показа окна."""
        super().showEvent(event)
        # При каждом показе окна поднимаем заголовок поверх всех остальных виджетов
        self.titlebar_with_menu.raise_()

    def addDockWidget(self, area, dock_widget, orientation=Qt.Orientation.Horizontal):
        """Переопределяем метод добавления dock-виджетов."""
        # Вызываем оригинальный метод
        super().addDockWidget(area, dock_widget, orientation)

        # Если добавляется виджет в верхнюю область, убедимся, что он не перекрывает заголовок
        if area == Qt.DockWidgetArea.TopDockWidgetArea:
            # Устанавливаем отступ сверху для dock-виджета, чтобы он не перекрывал заголовок
            dock_widget.setContentsMargins(0, self.TITLEBAR_HEIGHT, 0, 0)

        # Убедимся, что заголовок остаётся поверх
        self.titlebar_with_menu.raise_()

    def _menu_new_file(self):
        """Создать новый файл."""
        self.open_text_editor()

    def _menu_open_file(self):
        """Открыть файл."""
        try:
            editor = self._get_current_editor()
            if editor:
                editor.open_file()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Текущая вкладка не поддерживает открытие файла."
                )
        except Exception as e:
            logger.error(f"Ошибка при открытии файла: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии файла:\n{e}")

    def _menu_open_folder(self):
        """Открыть папку."""
        try:
            folder = QFileDialog.getExistingDirectory(self, "Открыть папку")
            if folder:
                QMessageBox.information(
                    self, "Папка выбрана", f"Вы выбрали папку:\n{folder}"
                )
        except Exception as e:
            logger.error(f"Ошибка при открытии папки: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии папки:\n{e}")

    def _menu_save(self):
        """Сохранить файл."""
        try:
            editor = self._get_current_editor()
            if editor:
                editor.save_file()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Текущая вкладка не поддерживает сохранение файла."
                )
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении файла:\n{e}")

    def _menu_save_as(self):
        """Сохранить файл как."""
        try:
            editor = self._get_current_editor()
            if editor:
                editor.save_file_as()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Текущая вкладка не поддерживает сохранение файла как."
                )
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла как: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении файла как:\n{e}")

    def _get_current_editor(self):
        """Получить текущий редактор.

        Returns:
            TextEditorWidget or None: Текущий редактор, если он поддерживает необходимые методы.
        """
        widget = self.tab_widget.currentWidget()
        if widget is not None and isinstance(widget, TextEditorWidget):
            return widget
        return None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Обновляем положение grip-виджетов для изменения размера окна
        self._update_grips()

        # Обновляем размер и положение заголовка при изменении размера окна
        self.titlebar_with_menu.resize(self.width(), self.TITLEBAR_HEIGHT)
        self.titlebar_with_menu.move(0, 0)

        # Поднимаем заголовок поверх остальных виджетов
        self.titlebar_with_menu.raise_()

    def _menu_undo(self):
        """Отменить действие."""
        try:
            editor = self._get_current_editor()
            if editor:
                editor.undo()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Текущая вкладка не поддерживает отмену действия."
                )
        except Exception as e:
            logger.error(f"Ошибка при отмене действия: {e}")

    def _menu_redo(self):
        """Повторить действие."""
        try:
            editor = self._get_current_editor()
            if editor:
                editor.redo()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Текущая вкладка не поддерживает повтор действия."
                )
        except Exception as e:
            logger.error(f"Ошибка при повторе действия: {e}")

    def _menu_cut(self):
        """Вырезать."""
        try:
            editor = self._get_current_editor()
            if editor:
                editor.cut()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Текущая вкладка не поддерживает вырезание."
                )
        except Exception as e:
            logger.error(f"Ошибка при вырезании: {e}")

    def _menu_copy(self):
        """Копировать."""
        try:
            editor = self._get_current_editor()
            if editor:
                editor.copy()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Текущая вкладка не поддерживает копирование."
                )
        except Exception as e:
            logger.error(f"Ошибка при копировании: {e}")

    def _menu_paste(self):
        """Вставить."""
        try:
            editor = self._get_current_editor()
            if editor:
                editor.paste()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Текущая вкладка не поддерживает вставку."
                )
        except Exception as e:
            logger.error(f"Ошибка при вставке: {e}")

    def _menu_delete(self):
        """Удалить."""
        try:
            editor = self._get_current_editor()
            if editor:
                editor.delete()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Текущая вкладка не поддерживает удаление."
                )
        except Exception as e:
            logger.error(f"Ошибка при удалении: {e}")

    def _menu_select_all(self):
        """Выделить всё."""
        try:
            editor = self._get_current_editor()
            if editor:
                editor.select_all()
            else:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Текущая вкладка не поддерживает выделение всего текста.",
                )
        except Exception as e:
            logger.error(f"Ошибка при выделении всего: {e}")

    def _menu_open_project_explorer(self):
        """Открыть проект-эксплорер."""
        try:
            # Импортируем и инициализируем проект-эксплорер с модульным путем
            from gopiai.extensions.project_explorer_integration import (
                add_project_explorer_dock,
            )
            add_project_explorer_dock(self)
        except ImportError as e:
            logger.warning(f"Не удалось загрузить проект-эксплорер: {e}")
            QMessageBox.warning(
                self, "Ошибка", f"Не удалось загрузить проект-эксплорер: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Ошибка при открытии проект-эксплорера: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии проект-эксплорера:\n{e}")

    def _menu_open_chat(self):
        """Открыть чат."""
        try:
            from gopiai.extensions import init_chat_extension
            init_chat_extension(self)
        except ImportError as e:
            logger.warning(f"Не удалось загрузить чат-расширение: {e}")
            QMessageBox.warning(
                self, "Ошибка", f"Не удалось загрузить чат-расширение: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Ошибка при открытии чата: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии чата:\n{e}")

    def _menu_open_browser(self):
        """Открыть браузер."""
        try:
            from gopiai.extensions import connect_browser_menu
            connect_browser_menu(self)
        except ImportError as e:
            logger.warning(f"Не удалось загрузить расширение браузера: {e}")
            QMessageBox.warning(
                self, "Ошибка", f"Не удалось загрузить расширение браузера: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Ошибка при открытии браузера: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии браузера:\n{e}")

    def _menu_open_terminal(self):
        """Открыть терминал."""
        try:
            from gopiai.extensions import init_terminal_extension
            init_terminal_extension(self)
        except ImportError as e:
            logger.warning(f"Не удалось загрузить расширение терминала: {e}")
            QMessageBox.warning(
                self, "Ошибка", f"Не удалось загрузить расширение терминала: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Ошибка при открытии терминала: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии терминала:\n{e}")


# --- UI для выбора темы и акцента ---
class FramelessColorDialog(QColorDialog):
    def __init__(self, initial, parent=None):
        super().__init__(initial, parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self._drag_active = False
        self._drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = False
        super().mouseReleaseEvent(event)


def get_frameless_color_dialog(initial, parent, title):
    """Создать диалог выбора цвета без рамки."""
    dlg = FramelessColorDialog(initial, parent)
    dlg.setWindowTitle(title)
    dlg.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, False)
    if dlg.exec() == QDialog.DialogCode.Accepted:
        return dlg.selectedColor()
    return initial


def main():
    """Основная функция программы."""
    app = QApplication(sys.argv)
    
    # Автоматически применяем тему при запуске
    try:
        apply_theme(app)
        logger.info("Применена тема при запуске")
    except Exception as e:
        logger.warning(f"Не удалось применить тему при запуске: {e}")
    
    # Создаем и отображаем главное окно
    main_window = FramelessMainWindow()
    main_window.show()
    
    # Пытаемся загрузить расширения
    try:
        from gopiai.extensions import init_all_extensions
        init_all_extensions(main_window)
        logger.info("Инициализированы все расширения")
    except ImportError as e:
        logger.warning(f"Не удалось загрузить расширения: {str(e)}")
    except Exception as e:
        logger.error(f"Ошибка при инициализации расширений: {e}")
    
    # Инициализируем переменную результата перед блоком try
    exec_result = 1
    try:
        exec_result = app.exec()
    except Exception as e:
        logger.error(f"Ошибка в цикле событий: {e}")
        exec_result = 1
    finally:
        sys.exit(exec_result)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)