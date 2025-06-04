#!/usr/bin/env python3
"""
GopiAI Standalone Interface - полностью автономный интерфейс
=====================================

Модульный интерфейс GopiAI с полностью встроенными компонентами:
- Frameless окно с профессиональным дизайном
- Левая панель: проводник файлов 
- Центральная область: система вкладок для документов
- Правая панель: чат с ИИ
- Нижняя панель: терминал
- Верхнее меню: полный набор команд

Автор: Crazy Coder
Версия: 0.2.0
Дата: 2025-01-12
"""

import sys
import os
import warnings
from pathlib import Path
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Добавляем пути к модулям GopiAI в sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
gopiai_modules_root = os.path.abspath(script_dir) # GOPI_AI_MODULES

module_paths = [
    os.path.join(gopiai_modules_root, "GopiAI-Core"),
    os.path.join(gopiai_modules_root, "GopiAI-Widgets"),
    os.path.join(gopiai_modules_root, "GopiAI-App"),
    os.path.join(gopiai_modules_root, "GopiAI-Extensions"),
    os.path.join(gopiai_modules_root, "rag_memory_system"),
]

for path in module_paths:
    if path not in sys.path:
        sys.path.insert(0, path)

print("Добавленные пути в sys.path:")
for p in module_paths:
    print(f"- {p} (существует: {os.path.exists(p)})")

# Импорт существующих систем иконок и тем
try:
    # Добавляем пути к модулям GopiAI используя архитектуру из minimal_app.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    gopi_modules_dir = current_dir  # Мы уже в корне модулей
    
    # Добавляем пути как в minimal_app.py
    app_path = os.path.join(gopi_modules_dir, "GopiAI-App")
    core_path = os.path.join(gopi_modules_dir, "GopiAI-Core")
    assets_path = os.path.join(gopi_modules_dir, "GopiAI-Assets")
    widgets_path = os.path.join(gopi_modules_dir, "GopiAI-Widgets")
    
    for path in [app_path, core_path, assets_path, widgets_path]:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)      # Импортируем НАСТОЯЩИЕ функции из GopiAI Core
    from gopiai.core.simple_theme_manager import (
        load_theme, apply_theme, save_theme,
        MATERIAL_SKY_THEME, EMERALD_GARDEN_THEME,        CRIMSON_RELIC_THEME, GOLDEN_EMBER_THEME
    )
    
    # Импортируем ThemeManager из GopiAI-Widgets
    from gopiai.widgets.managers.theme_manager import ThemeManager
      
    # Создаем простой локальный менеджер иконок
    class LucideIconManager:
        _instance = None
        
        def __init__(self):
            self.icons_path = Path(__file__).parent / "node_modules" / "lucide-static" / "icons"
            self._icon_cache = {}
            print(f"🔍 LucideIconManager: ищем иконки в {self.icons_path}")
            print(f"📂 Путь существует: {self.icons_path.exists()}")
        
        @classmethod
        def instance(cls):
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
            
        def get_icon(self, icon_name: str, color_override=None, size=None):
            """Получить иконку по имени"""
            if icon_name in self._icon_cache:
                return self._icon_cache[icon_name]
            
            # Ищем SVG файл
            svg_path = self.icons_path / f"{icon_name}.svg"
            
            if svg_path.exists():
                # Создаем QIcon из SVG файла
                icon = QIcon(str(svg_path))
                self._icon_cache[icon_name] = icon
                print(f"✅ Загружена иконка: {icon_name}")
                return icon
            else:
                print(f"❌ Иконка не найдена: {icon_name} (путь: {svg_path})")
                # Возвращаем пустую иконку
                empty_icon = QIcon()
                self._icon_cache[icon_name] = empty_icon
                return empty_icon
    
    ICON_MANAGER_AVAILABLE = True# Заглушки для недостающих модулей
    THEME_FILE = None
    
    # Импорт маппинга иконок
    from icon_mapping import get_lucide_name
    
    THEMES_AVAILABLE = True
    ICON_MANAGER_AVAILABLE = True
    print("✓ НАСТОЯЩИЕ системы тем и иконок GopiAI загружены!")
    
except ImportError as e:
    THEMES_AVAILABLE = False
    ICON_MANAGER_AVAILABLE = False
    print(f"⚠ Система тем/иконок недоступна: {e}")
      # STUB: Создаём заглушки для функций GopiAI
    def load_theme():
        print("⚠ STUB: попытка загрузить тему")
        return None
    
    def apply_theme(app):
        print("⚠ STUB: попытка применить тему")
        return False
    
    def save_theme(theme_data):
        print("⚠ STUB: попытка сохранить тему")
        return False
    
    # STUB: Заглушки тем
    MATERIAL_SKY_THEME = {"name": "Material Sky", "light": {}, "dark": {}}
    EMERALD_GARDEN_THEME = {"name": "Emerald Garden", "light": {}, "dark": {}}
    CRIMSON_RELIC_THEME = {"name": "Crimson Relic", "light": {}, "dark": {}}
    GOLDEN_EMBER_THEME = {"name": "Golden Ember", "light": {}, "dark": {}}
      # Удалено: конфликтующая заглушка LucideIconManager
    
    THEME_FILE = None  # STUB: заглушка пути к файлу темы
    
    class ThemeManager:  # STUB: заглушка ThemeManager
        def __init__(self):
            pass
    
    class icons_rc:
        pass
    def show_theme_dialog(parent=None):
        """Простой диалог смены темы"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        
        dialog = QDialog(parent)
        dialog.setWindowTitle("Выбор темы")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Выберите тему:"))
        
        # Кнопки тем
        button_layout = QHBoxLayout()
        
        light_btn = QPushButton("Светлая тема")
        dark_btn = QPushButton("Тёмная тема")
        
        button_layout.addWidget(light_btn)
        button_layout.addWidget(dark_btn)
        layout.addLayout(button_layout)
        
        # Кнопки ОК/Отмена
        ok_cancel_layout = QHBoxLayout()
        ok_btn = QPushButton("ОК")
        cancel_btn = QPushButton("Отмена")
        
        ok_cancel_layout.addWidget(ok_btn)
        ok_cancel_layout.addWidget(cancel_btn)
        layout.addLayout(ok_cancel_layout)
        
        # Подключение сигналов
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Показать диалог
        return dialog.exec() == QDialog.DialogCode.Accepted
    
    def apply_theme(*args, **kwargs):        pass


# Основные импорты PySide6
from PySide6.QtCore import Qt, Signal, QPoint, QSize, QRect, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QMenuBar, QMenu, QFrame, QLabel, QPushButton, QSplitter,
    QTreeView, QFileSystemModel, QTabWidget, QTextEdit, QFileDialog,
    QMessageBox
)
from PySide6.QtGui import QIcon, QFont, QPalette, QMouseEvent, QAction, QResizeEvent

# =============================================================================
# Встроенные компоненты интерфейса
# =============================================================================

class StandaloneMenuBar(QMenuBar):
    """Автономное меню с полным набором сигналов"""
    
    # Сигналы файлового меню
    newFileRequested = Signal()
    openFileRequested = Signal()
    openFolderRequested = Signal()
    saveRequested = Signal()
    saveAsRequested = Signal()
    exitRequested = Signal()
    
    # Сигналы меню вида
    openTextEditorRequested = Signal()
    openProjectExplorerRequested = Signal()
    openChatRequested = Signal()
    openBrowserRequested = Signal()
    openTerminalRequested = Signal()
      # Сигналы расширений
    toggleProductivityExtension = Signal()
    toggleVoiceExtension = Signal()
    toggleAiToolsExtension = Signal()
      # Сигналы темы
    changeThemeRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_menu()

    def _build_menu(self):
        """Создание структуры меню"""
        # Файловое меню
        file_menu = self.addMenu("Файл")
        self.new_action = file_menu.addAction("Создать новый")
        self.open_action = file_menu.addAction("Открыть файл")
        self.open_folder_action = file_menu.addAction("Открыть папку")
        file_menu.addSeparator()
        self.save_action = file_menu.addAction("Сохранить")
        self.save_as_action = file_menu.addAction("Сохранить как")
        file_menu.addSeparator()
        self.exit_action = file_menu.addAction("Выход")
        
        # Подключение сигналов
        self.new_action.triggered.connect(self.newFileRequested.emit)
        self.open_action.triggered.connect(self.openFileRequested.emit)
        self.open_folder_action.triggered.connect(self.openFolderRequested.emit)
        self.save_action.triggered.connect(self.saveRequested.emit)
        self.save_as_action.triggered.connect(self.saveAsRequested.emit)
        self.exit_action.triggered.connect(self.exitRequested.emit)
        
        # Меню правки
        edit_menu = self.addMenu("Правка")
        self.undo_action = edit_menu.addAction("Отмена")
        self.redo_action = edit_menu.addAction("Повтор")
        edit_menu.addSeparator()
        self.cut_action = edit_menu.addAction("Вырезать")
        self.copy_action = edit_menu.addAction("Копировать")
        self.paste_action = edit_menu.addAction("Вставить")
        self.delete_action = edit_menu.addAction("Удалить")
        edit_menu.addSeparator()
        self.select_all_action = edit_menu.addAction("Выделить всё")
          # Меню вида
        view_menu = self.addMenu("Вид")
        project_explorer_action = view_menu.addAction("Файловый проводник")
        chat_action = view_menu.addAction("ИИ чат")
        browser_action = view_menu.addAction("Браузер")
        terminal_action = view_menu.addAction("Терминал")
        text_editor_action = view_menu.addAction("Редактор")
        
        view_menu.addSeparator()
          # Подменю расширений
        extensions_menu = view_menu.addMenu("🔌 Расширения")
        self.productivity_action = extensions_menu.addAction("📝 Инструменты продуктивности")
        self.voice_action = extensions_menu.addAction("🎤 Голосовое управление")
        self.ai_tools_action = extensions_menu.addAction("🤖 ИИ инструменты")
        
        # Подменю настроек темы
        view_menu.addSeparator()
        theme_menu = view_menu.addMenu("🎨 Тема")
        change_theme_action = theme_menu.addAction("Изменить тему...")
        change_theme_action.triggered.connect(self.changeThemeRequested.emit)
        
        # Делаем действия checkable (можно включать/выключать)
        self.productivity_action.setCheckable(True)
        self.voice_action.setCheckable(True)
        self.ai_tools_action.setCheckable(True)
        
        # По умолчанию продуктивность включена
        self.productivity_action.setChecked(True)
        
        # Подключение сигналов вида
        project_explorer_action.triggered.connect(self.openProjectExplorerRequested.emit)
        chat_action.triggered.connect(self.openChatRequested.emit)
        browser_action.triggered.connect(self.openBrowserRequested.emit)
        terminal_action.triggered.connect(self.openTerminalRequested.emit)
        text_editor_action.triggered.connect(self.openTextEditorRequested.emit)
        
        # Подключение сигналов расширений
        self.productivity_action.triggered.connect(self.toggleProductivityExtension.emit)
        self.voice_action.triggered.connect(self.toggleVoiceExtension.emit)
        self.ai_tools_action.triggered.connect(self.toggleAiToolsExtension.emit)


class StandaloneTitlebar(QWidget):
    """Автономный titlebar с кнопками управления окном"""
    
    minimizeClicked = Signal()
    maximizeClicked = Signal()
    restoreClicked = Signal()
    closeClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titlebarWidget")
        self.setFixedHeight(40)
        self._drag_active = False
        self._drag_pos = QPoint()
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса titlebar"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        
        # Заголовок окна
        self.window_title = QLabel("🚀 GopiAI v0.2.0", self)
        self.window_title.setObjectName("windowTitle")
        self.window_title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.window_title, 1)
        
        # Кнопки управления окном
        self.minimize_button = QPushButton("—", self)
        self.minimize_button.setObjectName("minimizeButton")
        self.minimize_button.setFixedSize(40, 40)
        self.minimize_button.clicked.connect(self.minimizeClicked.emit)
        layout.addWidget(self.minimize_button)
        
        self.restore_button = QPushButton("❐", self)
        self.restore_button.setObjectName("restoreButton")
        self.restore_button.setFixedSize(40, 40)
        self.restore_button.setVisible(False)
        self.restore_button.clicked.connect(self.restoreClicked.emit)
        layout.addWidget(self.restore_button)
        
        self.maximize_button = QPushButton("□", self)
        self.maximize_button.setObjectName("maximizeButton")
        self.maximize_button.setFixedSize(40, 40)
        self.maximize_button.clicked.connect(self.maximizeClicked.emit)
        layout.addWidget(self.maximize_button)
        
        self.close_button = QPushButton("×", self)
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedSize(40, 40)
        self.close_button.clicked.connect(self.closeClicked.emit)
        layout.addWidget(self.close_button)

    def set_title(self, text: str):
        """Установка заголовка окна"""
        self.window_title.setText(text)

    def mousePressEvent(self, event: QMouseEvent):
        """Обработка нажатия мыши для перетаскивания"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Обработка перемещения мыши для перетаскивания"""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_active:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Обработка отпускания мыши"""
        self._drag_active = False


class StandaloneTitlebarWithMenu(QWidget):
    """Комбинированный titlebar с меню"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titlebarWithMenu")
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Titlebar
        self.titlebar = StandaloneTitlebar(self)
        layout.addWidget(self.titlebar)
        
        # Меню
        self.menu_bar = StandaloneMenuBar(self)
        layout.addWidget(self.menu_bar)

    def set_window(self, window):
        """Подключение к окну"""
        self.window_ref = window
        # Подключение сигналов titlebar к окну
        self.titlebar.minimizeClicked.connect(window.showMinimized)
        self.titlebar.maximizeClicked.connect(self._toggle_maximize)
        self.titlebar.restoreClicked.connect(self._toggle_maximize)
        self.titlebar.closeClicked.connect(window.close)

    def _toggle_maximize(self):
        """Переключение между развернутым и обычным состоянием"""
        if hasattr(self, 'window_ref'):
            if self.window_ref.isMaximized():
                self.window_ref.showNormal()
                self.titlebar.maximize_button.setVisible(True)
                self.titlebar.restore_button.setVisible(False)
            else:
                self.window_ref.showMaximized()
                self.titlebar.maximize_button.setVisible(False)
                self.titlebar.restore_button.setVisible(True)


class CustomGrip(QWidget):
    """Элемент для изменения размера окна"""
    
    def __init__(self, parent, direction):
        super().__init__(parent)
        self.direction = direction
        self._setup_cursor()

    def _setup_cursor(self):
        """Настройка курсора для грипа"""
        if self.direction in ['top', 'bottom']:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif self.direction in ['left', 'right']:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif self.direction in ['top-left', 'bottom-right']:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif self.direction in ['top-right', 'bottom-left']:
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)

    def mousePressEvent(self, event):
        """Начало изменения размера"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()
            self.start_geometry = self.window().geometry()

    def mouseMoveEvent(self, event):
        """Изменение размера окна"""
        if hasattr(self, 'start_pos'):
            delta = event.globalPosition().toPoint() - self.start_pos
            self._resize_window(delta)

    def _resize_window(self, delta):
        """Изменение размера окна в зависимости от направления"""
        geo = self.start_geometry
        new_geo = QRect(geo)
        
        if 'top' in self.direction:
            new_geo.setTop(geo.top() + delta.y())
        if 'bottom' in self.direction:
            new_geo.setBottom(geo.bottom() + delta.y())
        if 'left' in self.direction:
            new_geo.setLeft(geo.left() + delta.x())
        if 'right' in self.direction:
            new_geo.setRight(geo.right() + delta.x())
        
        # Минимальные размеры
        if new_geo.width() < 600:
            new_geo.setWidth(600)
        if new_geo.height() < 400:
            new_geo.setHeight(400)
        
        self.window().setGeometry(new_geo)


# =============================================================================
# Компоненты интерфейса
# =============================================================================

class FileExplorerWidget(QWidget):
    """Проводник файлов с деревом папок"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("fileExplorer")
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса проводника"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Заголовок
        header = QLabel("📁 Проводник")
        header.setObjectName("panelHeader")
        header.setFixedHeight(30)
        layout.addWidget(header)
        
        # Дерево файлов
        self.tree_view = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.tree_view.setModel(self.file_model)
        
        # Настройка отображения
        self.tree_view.setRootIndex(self.file_model.index(os.path.expanduser("~")))
        self.tree_view.hideColumn(1)  # Размер
        self.tree_view.hideColumn(2)  # Тип
        self.tree_view.hideColumn(3)  # Дата изменения
        
        layout.addWidget(self.tree_view)


class TabDocumentWidget(QWidget):
    """Центральная область с вкладками документов"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tabDocument")
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса вкладок"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Виджет вкладок
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        
        # Добавляем стартовую вкладку
        welcome_tab = QTextEdit()
        welcome_tab.setPlainText("""
🚀 Добро пожаловать в GopiAI v0.2.0!

Это модульный интерфейс для работы с ИИ ассистентом.

Основные возможности:
• 📁 Проводник файлов (левая панель)
• 📝 Редактор кода с вкладками (центральная область)
• 🤖 ИИ чат ассистент (правая панель)  
• 💻 Встроенный терминал (нижняя панель)
• 🎨 Современный дизайн с темной темой

Используйте меню "Файл" для открытия документов или "Вид" для управления панелями.

Создано с ❤️ командой GopiAI
        """)
        welcome_tab.setReadOnly(True)
        
        self.tab_widget.addTab(welcome_tab, "🏠 Добро пожаловать")
        layout.addWidget(self.tab_widget)

    def add_new_tab(self, title="Новый документ", content=""):
        """Добавление новой вкладки"""
        editor = QTextEdit()
        editor.setPlainText(content)
        index = self.tab_widget.addTab(editor, title)
        self.tab_widget.setCurrentIndex(index)
        return editor


class ChatWidget(QWidget):
    """Чат с ИИ ассистентом"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatWidget")
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса чата"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Заголовок
        header = QLabel("🤖 ИИ Ассистент")
        header.setObjectName("panelHeader")
        header.setFixedHeight(30)
        layout.addWidget(header)
        
        # Область чата
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setPlainText("""
🤖 GopiAI: Привет! Я ваш ИИ ассистент.

Я могу помочь с:
• Анализом кода
• Написанием документации  
• Решением задач программирования
• Объяснением сложных концепций
• Оптимизацией алгоритмов

Напишите ваш вопрос ниже и нажмите Enter!
        """)
        layout.addWidget(self.chat_area, 1)
        
        # Поле ввода
        input_layout = QHBoxLayout()
        self.input_field = QTextEdit()
        self.input_field.setFixedHeight(60)
        self.input_field.setPlaceholderText("Введите ваш вопрос...")
        
        self.send_button = QPushButton("➤ Отправить")
        self.send_button.setFixedSize(100, 60)
        self.send_button.clicked.connect(self._send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

    def _send_message(self):
        """Отправка сообщения в чат"""
        message = self.input_field.toPlainText().strip()
        if message:
            # Добавляем сообщение пользователя
            current_text = self.chat_area.toPlainText()
            new_text = f"{current_text}\n\n👤 Вы: {message}\n\n🤖 GopiAI: Спасибо за ваш вопрос! В данный момент я работаю в режиме заглушки. Полная интеграция с ИИ будет добавлена в следующих версиях."
            self.chat_area.setPlainText(new_text)
            
            # Прокручиваем вниз
            cursor = self.chat_area.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.chat_area.setTextCursor(cursor)
            
            # Очищаем поле ввода
            self.input_field.clear()


class TerminalWidget(QWidget):
    """Виджет терминала с вкладками"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("terminalWidget")
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса терминала"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Заголовок с кнопками
        header_layout = QHBoxLayout()
        header_label = QLabel("💻 Терминал")
        header_label.setObjectName("panelHeader")
        
        new_tab_btn = QPushButton("+ Новая вкладка")
        new_tab_btn.setFixedHeight(25)
        new_tab_btn.clicked.connect(self._add_terminal_tab)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(new_tab_btn)
        layout.addLayout(header_layout)
        
        # Вкладки терминала
        self.terminal_tabs = QTabWidget()
        self.terminal_tabs.setTabsClosable(True)
        self.terminal_tabs.tabCloseRequested.connect(self._close_terminal_tab)
        
        # Добавляем первую вкладку
        self._add_terminal_tab()
        layout.addWidget(self.terminal_tabs)

    def _add_terminal_tab(self):
        """Добавление новой вкладки терминала"""
        terminal = QTextEdit()
        terminal.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border: none;
            }
        """)
        
        terminal.setPlainText("""
Microsoft Windows PowerShell
Copyright (C) Microsoft Corporation. Все права защищены.

PS C:\\Users\\crazy\\GOPI_AI_MODULES> # Готов к работе!
PS C:\\Users\\crazy\\GOPI_AI_MODULES> 
        """)
        
        tab_index = self.terminal_tabs.addTab(terminal, f"Терминал {self.terminal_tabs.count() + 1}")
        self.terminal_tabs.setCurrentIndex(tab_index)

    def _close_terminal_tab(self, index):
        """Закрытие вкладки терминала"""
        if self.terminal_tabs.count() > 1:
            self.terminal_tabs.removeTab(index)


# =============================================================================
# Главное окно
# =============================================================================

class FramelessGopiAIStandaloneWindow(QMainWindow):
    """Основное frameless окно GopiAI с автономными компонентами"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GopiAI v0.2.0 - Модульный ИИ Интерфейс")
        self.setMinimumSize(1000, 700)
        self.resize(1400, 900)
          # Frameless окно
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        # Константы
        self.TITLEBAR_HEIGHT = 40
        self.GRIP_SIZE = 10
        
        self._setup_ui()
        self._init_grips()
        self._init_themes_and_icons()
        self._apply_styles()
        self._connect_signals()
        self._setup_menu_icons()
        
        print("✓ FramelessGopiAIStandaloneWindow инициализировано")

    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Titlebar с меню
        self.titlebar_with_menu = StandaloneTitlebarWithMenu(self)
        self.titlebar_with_menu.set_window(self)
        self.titlebar_with_menu.setFixedHeight(self.TITLEBAR_HEIGHT * 2)  # Место для меню и titlebar
        main_layout.addWidget(self.titlebar_with_menu)
        
        # Основной сплиттер (горизонтальный для панелей)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter, 1)
        
        # Левая панель (проводник файлов)
        self.file_explorer = FileExplorerWidget()
        main_splitter.addWidget(self.file_explorer)
        
        # Правый сплиттер (вертикальный для центра и низа)
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(right_splitter)
        
        # Центральный сплиттер (для документов и чата)
        center_splitter = QSplitter(Qt.Orientation.Horizontal)
        right_splitter.addWidget(center_splitter)
        
        # Центральная область (вкладки документов)
        self.tab_document = TabDocumentWidget()
        center_splitter.addWidget(self.tab_document)
        
        # Правая панель (чат с ИИ)
        self.chat_widget = ChatWidget()
        center_splitter.addWidget(self.chat_widget)
        
        # Нижняя панель (терминал)
        self.terminal_widget = TerminalWidget()
        right_splitter.addWidget(self.terminal_widget)
        
        # Настройка пропорций
        main_splitter.setSizes([250, 1150])  # Левая панель : Остальное
        center_splitter.setSizes([800, 350])  # Документы : Чат
        right_splitter.setSizes([700, 200])   # Верх : Терминал

    def _init_grips(self):
        """Инициализация грипов для изменения размера"""
        self.grips = {}
        directions = ['top', 'bottom', 'left', 'right', 'top-left', 'top-right', 'bottom-left', 'bottom-right']
        
        for direction in directions:
            grip = CustomGrip(self, direction)
            self.grips[direction] = grip
        
        self._update_grips()
        print("✓ Грипы для изменения размера инициализированы")

    def _update_grips(self):
        """Обновление позиций грипов"""
        rect = self.rect()
        grip_size = self.GRIP_SIZE
        
        # Угловые грипы
        self.grips['top-left'].setGeometry(0, 0, grip_size, grip_size)
        self.grips['top-right'].setGeometry(rect.width() - grip_size, 0, grip_size, grip_size)
        self.grips['bottom-left'].setGeometry(0, rect.height() - grip_size, grip_size, grip_size)
        self.grips['bottom-right'].setGeometry(rect.width() - grip_size, rect.height() - grip_size, grip_size, grip_size)
        
        # Боковые грипы
        self.grips['top'].setGeometry(grip_size, 0, rect.width() - 2 * grip_size, grip_size)
        self.grips['bottom'].setGeometry(grip_size, rect.height() - grip_size, rect.width() - 2 * grip_size, grip_size)
        self.grips['left'].setGeometry(0, grip_size, grip_size, rect.height() - 2 * grip_size)
        self.grips['right'].setGeometry(rect.width() - grip_size, grip_size, grip_size, rect.height() - 2 * grip_size)

    def _apply_styles(self):
        """Применение стилей Material Sky"""
        self.setStyleSheet("""
            /* Основные стили окна */
            QMainWindow {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333333;
            }
            
            /* Заголовки панелей */
            QLabel[objectName="panelHeader"] {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 5px 10px;
                font-weight: bold;
                border-bottom: 1px solid #444444;
            }
            
            /* Titlebar */
            QWidget[objectName="titlebarWidget"] {
                background-color: #2d2d2d;
                border-bottom: 1px solid #444444;
            }
            
            QLabel[objectName="windowTitle"] {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            
            /* Кнопки titlebar */
            QPushButton[objectName="minimizeButton"], 
            QPushButton[objectName="maximizeButton"],
            QPushButton[objectName="restoreButton"] {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 16px;
            }
            
            QPushButton[objectName="minimizeButton"]:hover,
            QPushButton[objectName="maximizeButton"]:hover,
            QPushButton[objectName="restoreButton"]:hover {
                background-color: #404040;
            }
            
            QPushButton[objectName="closeButton"] {
                background-color: transparent;
                color: #ffffff;
                border: none;
                font-size: 16px;
            }
            
            QPushButton[objectName="closeButton"]:hover {
                background-color: #e74c3c;
            }
            
            /* Меню */
            QMenuBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border: none;
                padding: 2px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
                margin: 0px;
            }
            
            QMenuBar::item:selected {
                background-color: #404040;
            }
            
            QMenuBar::item:pressed {
                background-color: #505050;
            }
            
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
            }
            
            QMenu::item {
                padding: 5px 20px;
            }
            
            QMenu::item:selected {
                background-color: #404040;
            }
            
            /* Виджеты панелей */
            QWidget[objectName="fileExplorer"],
            QWidget[objectName="chatWidget"],
            QWidget[objectName="terminalWidget"] {
                background-color: #1e1e1e;
                border: 1px solid #333333;
            }
            
            QWidget[objectName="tabDocument"] {
                background-color: #1e1e1e;
            }
            
            /* Дерево файлов */
            QTreeView {
                background-color: #1e1e1e;
                color: #ffffff;
                border: none;
                selection-background-color: #404040;
            }
            
            QTreeView::item:hover {
                background-color: #333333;
            }
            
            /* Вкладки */
            QTabWidget::pane {
                background-color: #1e1e1e;
                border: 1px solid #333333;
            }
            
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #404040;
            }
            
            QTabBar::tab:hover {
                background-color: #505050;
            }
            
            /* Текстовые области */
            QTextEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333333;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                selection-background-color: #404040;
            }
            
            /* Кнопки */
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px 10px;
                border-radius: 3px;
            }
            
            QPushButton:hover {
                background-color: #505050;
            }
            
            QPushButton:pressed {
                background-color: #606060;
            }
            
            /* Сплиттеры */
            QSplitter::handle {
                background-color: #333333;
            }
            
            QSplitter::handle:horizontal {
                width: 3px;
            }
            
            QSplitter::handle:vertical {
                height: 3px;
            }
        """)
        print("✓ Темы применены")

    def _connect_signals(self):
        """Подключение сигналов меню"""
        menu_bar = self.titlebar_with_menu.menu_bar
        
        # Файловые операции
        menu_bar.newFileRequested.connect(self._handle_new_file)
        menu_bar.openFileRequested.connect(self._handle_open_file)
        menu_bar.openFolderRequested.connect(self._handle_open_folder)
        menu_bar.saveRequested.connect(self._handle_save)
        menu_bar.saveAsRequested.connect(self._handle_save_as)
        menu_bar.exitRequested.connect(self.close)
          # Управление расширениями
        menu_bar.toggleProductivityExtension.connect(self._toggle_productivity_extension)
        menu_bar.toggleVoiceExtension.connect(self._toggle_voice_extension)
        menu_bar.toggleAiToolsExtension.connect(self._toggle_ai_tools_extension)
        
        # Управление темами
        menu_bar.changeThemeRequested.connect(self._handle_change_theme)
        
        print("✓ Меню подключены")
        
        # Инициализация расширений
        self._init_extensions()

    def _init_extensions(self):
        """Инициализация системы расширений"""
        try:
            # Добавляем пути к модулям расширений
            import sys
            import os
            current_dir = os.path.dirname(__file__)
            extensions_path = os.path.join(current_dir, 'GopiAI-Extensions')
            
            if os.path.exists(extensions_path) and extensions_path not in sys.path:
                sys.path.insert(0, extensions_path)
            
            # Пытаемся загрузить расширения
            from gopiai.extensions import init_all_extensions
            init_all_extensions(self)
            print("✓ Расширения загружены")
            
        except ImportError as e:
            print(f"⚠ Расширения недоступны: {e}")
            # Используем встроенные компоненты
            self._init_builtin_extensions()
        except Exception as e:
            print(f"⚠ Ошибка при загрузке расширений: {e}")
            self._init_builtin_extensions()

    def _init_builtin_extensions(self):
        """Инициализация встроенных расширений-заглушек"""
        # Добавляем возможность подключения dock-виджетов
        self._register_dock_handlers()
        
        # Загружаем локальные расширения
        self._load_local_extensions()
        
        print("✓ Встроенные расширения инициализированы")

    def _load_local_extensions(self):
        """Загрузка локальных расширений"""
        # Добавляем путь к расширениям в sys.path
        extensions_path = os.path.join(os.path.dirname(__file__), "GopiAI-Extensions", "gopiai", "extensions")
        if os.path.exists(extensions_path) and extensions_path not in sys.path:
            sys.path.insert(0, extensions_path)
            print(f"✓ Добавлен путь к расширениям: {extensions_path}")
        
        # Загружаем расширение продуктивности
        try:
            import productivity_extension
            productivity_extension.auto_init(self)
        except ImportError as e:
            print(f"⚠ Расширение продуктивности не найдено: {e}")
        except Exception as e:
            print(f"⚠ Ошибка при загрузке расширения продуктивности: {e}")
            
        # Загружаем голосовое расширение
        try:
            # Create a placeholder for voice extension since it's not available yet
            class VoicePlaceholder(QWidget):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    layout = QVBoxLayout(self)
                    label = QLabel("🎤 Голосовое расширение будет доступно в следующих версиях")
                    layout.addWidget(label)
            
            # Register placeholder instead of real extension
            self.add_dock_widget("voice2text", VoicePlaceholder(self), "right")
            print("✓ Зарегистрирован placeholder для голосового расширения")
            
        except Exception as e:
            print(f"⚠ Ошибка при создании placeholder для голосового расширения: {e}")

    def _register_dock_handlers(self):
        """Регистрация обработчиков для dock-виджетов"""
        # Это позволит расширениям добавлять новые панели
        self.dock_widgets = {}
        
    def add_dock_widget(self, name, widget, area='left'):
        """Добавление нового dock-виджета"""
        # Если виджет уже зарегистрирован, просто показываем его
        if name in self.dock_widgets:
            existing = self.dock_widgets[name]
            existing.show()
            return existing

        self.dock_widgets[name] = widget

        # Добавляем виджет в соответствующую область интерфейса
        if area == 'left':
            self._add_to_left_panel(widget)
        elif area == 'right':
            self._add_to_right_panel(widget)
        elif area == 'bottom':
            self._add_to_bottom_panel(widget)
        else:
            # Если область не распознана, добавляем в правую по умолчанию
            self._add_to_right_panel(widget)

        widget.show()
        print(f"✓ Добавлен dock-виджет: {name} в область {area}")
        
    def _add_to_left_panel(self, widget):
        """Добавление виджета в левую панель"""
        # Находим левую панель и добавляем виджет
        file_explorer_parent = self.file_explorer.parent()
        if hasattr(file_explorer_parent, 'addWidget'):
            file_explorer_parent.addWidget(widget)

    def _add_to_right_panel(self, widget):
        """Добавление виджета в правую панель"""
        # Находим правую панель и добавляем виджет под чатом
        chat_parent = self.chat_widget.parent()
        if hasattr(chat_parent, 'addWidget'):
            chat_parent.addWidget(widget)

    def _add_to_bottom_panel(self, widget):
        """Добавление виджета в нижнюю панель"""        # Добавляем как новую вкладку в терминал
        if hasattr(self.terminal_widget, 'terminal_tabs'):
            tab_name = getattr(widget, 'objectName', lambda: 'Новая вкладка')()
            self.terminal_widget.terminal_tabs.addTab(widget, tab_name)
        
    def get_dock_widget(self, name):
        """Получение dock-виджета по имени"""
        return self.dock_widgets.get(name)

    def _handle_new_file(self):
        """Обработка создания нового файла"""
        self.tab_document.add_new_tab("Новый файл.txt", "# Новый файл\n\nВведите содержимое...")

    def _handle_open_file(self):
        """Обработка открытия файла"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Все файлы (*.*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                file_name = os.path.basename(file_path)
                self.tab_document.add_new_tab(file_name, content)
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл:\n{e}")

    def _handle_open_folder(self):
        """Обработка открытия папки"""
        folder_path = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder_path:
            # Устанавливаем корневую папку в проводнике
            index = self.file_explorer.file_model.index(folder_path)
            self.file_explorer.tree_view.setRootIndex(index)

    def _handle_save(self):
        """Обработка сохранения"""
        QMessageBox.information(self, "Сохранение", "Функция сохранения будет реализована в следующих версиях.")
    
    def _handle_save_as(self):
        """Обработка сохранения как"""
        QMessageBox.information(self, "Сохранение как", "Функция 'Сохранить как' будет реализована в следующих версиях.")

    def _handle_change_theme(self):
        """Обработка смены темы через НАСТОЯЩУЮ систему GopiAI"""
        if THEMES_AVAILABLE:
            # Показываем диалог выбора из НАСТОЯЩИХ тем GopiAI
            self._show_theme_selection_dialog()
        else:
            # Fallback диалог для случая когда GopiAI недоступен
            self._show_fallback_theme_dialog()

    def _show_theme_selection_dialog(self):
        """Показать диалог выбора из настоящих тем GopiAI"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор темы GopiAI")
        dialog.setModal(True)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Выберите тему из коллекции GopiAI:"))
        
        # Комбобокс с НАСТОЯЩИМИ темами
        theme_combo = QComboBox()
        theme_combo.addItem("Material Sky", MATERIAL_SKY_THEME)
        theme_combo.addItem("Emerald Garden", EMERALD_GARDEN_THEME)
        theme_combo.addItem("Crimson Relic", CRIMSON_RELIC_THEME)
        theme_combo.addItem("Golden Ember", GOLDEN_EMBER_THEME)
        layout.addWidget(theme_combo)
        
        # Кнопки выбора режима
        mode_layout = QHBoxLayout()
        light_btn = QPushButton("Светлая")
        dark_btn = QPushButton("Тёмная")
        mode_layout.addWidget(QLabel("Режим:"))
        mode_layout.addWidget(light_btn)
        mode_layout.addWidget(dark_btn)
        layout.addLayout(mode_layout)
        
        # Кнопки действий
        button_layout = QHBoxLayout()
        apply_btn = QPushButton("Применить тему")
        cancel_btn = QPushButton("Отмена")
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Переменная для хранения режима
        selected_mode = {"mode": "light"}
        
        def set_light():
            selected_mode["mode"] = "light"
            light_btn.setStyleSheet("background-color: #0078d4; color: white;")
            dark_btn.setStyleSheet("")
            
        def set_dark():
            selected_mode["mode"] = "dark"
            dark_btn.setStyleSheet("background-color: #0078d4; color: white;")
            light_btn.setStyleSheet("")
        
        light_btn.clicked.connect(set_light)
        dark_btn.clicked.connect(set_dark)
        apply_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        # По умолчанию светлая тема
        set_light()
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Применяем выбранную тему
            selected_theme = theme_combo.currentData()
            self._apply_gopi_theme(selected_theme, selected_mode["mode"])
    
    def _apply_gopi_theme(self, theme_data, mode="light"):
        """Применить настоящую тему GopiAI"""
        try:
            if theme_data and mode in theme_data:
                # Извлекаем цвета для выбранного режима
                colors = theme_data[mode]
                
                # Создаём CSS стиль на основе цветов GopiAI темы
                style = f"""
                QMainWindow {{
                    background-color: {colors.get('main_color', '#ffffff')};
                    color: {colors.get('text_color', '#000000')};
                }}
                QMenuBar {{
                    background-color: {colors.get('header_color', '#f0f0f0')};
                    color: {colors.get('titlebar_text', '#000000')};
                    border: 1px solid {colors.get('border_color', '#cccccc')};
                }}
                QMenu {{
                    background-color: {colors.get('header_color', '#f0f0f0')};
                    color: {colors.get('text_color', '#000000')};
                    border: 1px solid {colors.get('border_color', '#cccccc')};
                }}
                QPushButton {{
                    background-color: {colors.get('button_color', '#0078d4')};
                    color: {colors.get('text_color', '#ffffff')};
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {colors.get('button_hover_color', '#106ebe')};
                }}
                QTextEdit {{
                    background-color: {colors.get('main_color', '#ffffff')};
                    color: {colors.get('text_color', '#000000')};
                    border: 1px solid {colors.get('border_color', '#cccccc')};
                }}
                QTreeView {{
                    background-color: {colors.get('main_color', '#ffffff')};
                    color: {colors.get('text_color', '#000000')};
                    border: 1px solid {colors.get('border_color', '#cccccc')};
                }}
                """
                
                # Применяем стиль
                app = QApplication.instance()
                if app and hasattr(app, 'setStyleSheet'):
                    app.setStyleSheet(style)
                    
                    # Сохраняем выбранную тему в файл настроек
                    if save_theme({"selected_theme": theme_data["name"], "mode": mode, **colors}):
                        print(f"✓ Применена тема GopiAI: {theme_data['name']} ({mode})")
                        QMessageBox.information(self, "Тема", 
                            f"Тема '{theme_data['name']}' ({mode}) успешно применена!")
                    else:
                        print("⚠ Тема применена, но не сохранена")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось применить тему")
            else:
                QMessageBox.warning(self, "Ошибка", "Некорректные данные темы")
                
        except Exception as e:
            print(f"⚠ Ошибка применения темы GopiAI: {e}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка применения темы:\n{e}")
            
    def _show_fallback_theme_dialog(self):
        """Показать простой диалог для случая когда GopiAI недоступен"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Смена темы")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Система тем GopiAI недоступна.\nВы можете применить базовую тему:"))
        
        # Кнопки
        button_layout = QHBoxLayout()
        apply_btn = QPushButton("Применить базовую тему")
        cancel_btn = QPushButton("Отмена")
        
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        apply_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._apply_simple_theme()

    def _apply_simple_theme(self):
        """Применение простой встроенной темы"""
        app = QApplication.instance()
        if app and hasattr(app, 'setStyleSheet'):
            simple_theme = """
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            QMenuBar {
                background-color: #3c3c3c;
                color: #ffffff;
                border: none;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            """
            app.setStyleSheet(simple_theme)
            print("✓ Простая тема применена")
        else:
            print("⚠ Не удалось применить тему - QApplication недоступно")

    def _toggle_productivity_extension(self):
        """Переключение расширения продуктивности"""
        widget_name = "productivity"
        if widget_name in self.dock_widgets:
            # Скрываем/показываем виджет
            widget = self.dock_widgets[widget_name]
            if widget.isVisible():
                widget.hide()
                print("📝 Расширение продуктивности скрыто")
            else:
                widget.show()
                print("📝 Расширение продуктивности показано")
        else:
            print("⚠ Расширение продуктивности не загружено")

    def _toggle_voice_extension(self):
        """Переключение голосового расширения"""
        widget_name = "voice2text"
        if widget_name in self.dock_widgets:
            # Скрываем/показываем виджет
            widget = self.dock_widgets[widget_name]
            if widget.isVisible():
                widget.hide()
                print("🎤 Голосовое расширение скрыто")
            else:
                widget.show()
                print("🎤 Голосовое расширение показано")
        else:
            print("⚠ Голосовое расширение не загружено")

    def _toggle_ai_tools_extension(self):
        """Переключение ИИ инструментов"""
        widget_name = "ai_tools"

        # Если панель уже загружена, просто переключаем видимость
        if widget_name in self.dock_widgets:
            widget = self.dock_widgets[widget_name]
            widget.setVisible(not widget.isVisible())
            return

        # Пытаемся динамически загрузить расширение через систему gopiai.extensions
        try:
            from gopiai.extensions import _safely_import
            module = _safely_import("gopiai.extensions.ai_tools_extension")
            if module and hasattr(module, "init_extension"):
                module.init_extension(self)
                # После инициализации панель должна быть зарегистрирована
                if widget_name in self.dock_widgets:
                    self.dock_widgets[widget_name].show()
                    return
            QMessageBox.warning(self, "ИИ инструменты", "Расширение ai_tools_extension не найдено")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить ИИ инструменты: {e}")

    def resizeEvent(self, event: QResizeEvent):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        self._update_grips()

    def showEvent(self, event):
        """Обработка показа окна"""
        super().showEvent(event)
        self._update_grips()

    def _init_themes_and_icons(self):
        """Инициализация системы тем и иконок"""
        # Инициализируем состояние для работы с темами и иконками
        self.theme_applied = False
        
        if ICON_MANAGER_AVAILABLE:
            try:
                # Используем прямой доступ к ресурсам иконок как в GopiAI-App
                print("✓ Система иконок доступна через LucideIconManager")
            except Exception as e:
                print(f"⚠ Ошибка инициализации иконок: {e}")
                
        if THEMES_AVAILABLE:
            try:
                # Применяем тему при запуске используя НАСТОЯЩУЮ систему GopiAI
                app = QApplication.instance()
                if apply_theme(app):
                    self.theme_applied = True
                    print("✓ Тема применена из настроек GopiAI")
                print("✓ Система тем доступна")
            except Exception as e:
                print(f"⚠ Ошибка инициализации тем: {e}")

    def get_icon(self, icon_name: str, size: QSize = QSize(24, 24)) -> QIcon:
        """Получение иконки через LucideIconManager"""
        try:
            # Используем рабочую LucideIconManager
            icon_manager = LucideIconManager.instance()
            icon = icon_manager.get_icon(icon_name, size=size)
            
            if not icon.isNull():
                print(f"✓ Иконка {icon_name} загружена через LucideIconManager")
                return icon
            else:
                print(f"⚠ Иконка {icon_name} не найдена в LucideIconManager")
        except Exception as e:
            print(f"⚠ Ошибка получения иконки {icon_name} через LucideIconManager: {e}")
        
        # Fallback: пытаемся использовать системные иконки Qt
        try:
            theme_icon = QIcon.fromTheme(icon_name)
            if not theme_icon.isNull():
                print(f"✓ Системная иконка {icon_name} найдена")
                return theme_icon
        except Exception as e:
            print(f"⚠ Системная иконка {icon_name} недоступна: {e}")
        
        # Возвращаем пустую иконку если ничего не найдено
        print(f"❌ Иконка {icon_name} не найдена нигде")
        return QIcon()
        print(f"⚠ Иконка {icon_name} не найдена, используется пустая")
        return QIcon()

    def _setup_menu_icons(self):
        """Установка иконок для пунктов меню"""
        if not ICON_MANAGER_AVAILABLE:
            return
            
        try:
            # Получаем ссылку на меню через titlebar
            menu_bar = self.titlebar_with_menu.menu_bar
            
            # Добавляем иконки к существующим действиям меню (увеличенный размер)
            icon_size = QSize(24, 24)  # Увеличиваем размер иконок
            
            if hasattr(menu_bar, 'new_action'):
                icon = self.get_icon("file-plus", icon_size)
                menu_bar.new_action.setIcon(icon)
                menu_bar.new_action.setIconVisibleInMenu(True)
                print(f"✓ Установлена иконка new_action: {not icon.isNull()}, размер: {icon.actualSize(icon_size)}")
                
            if hasattr(menu_bar, 'open_action'):
                icon = self.get_icon("folder-open", icon_size)
                menu_bar.open_action.setIcon(icon)
                menu_bar.open_action.setIconVisibleInMenu(True)
                print(f"✓ Установлена иконка open_action: {not icon.isNull()}, размер: {icon.actualSize(icon_size)}")
                
            if hasattr(menu_bar, 'save_action'):
                icon = self.get_icon("save", icon_size)
                menu_bar.save_action.setIcon(icon)
                menu_bar.save_action.setIconVisibleInMenu(True)
                print(f"✓ Установлена иконка save_action: {not icon.isNull()}, размер: {icon.actualSize(icon_size)}")
                
            if hasattr(menu_bar, 'productivity_action'):
                icon = self.get_icon("wrench", icon_size)
                menu_bar.productivity_action.setIcon(icon)
                menu_bar.productivity_action.setIconVisibleInMenu(True)
                print(f"✓ Установлена иконка productivity_action: {not icon.isNull()}, размер: {icon.actualSize(icon_size)}")
                
            if hasattr(menu_bar, 'voice_action'):
                icon = self.get_icon("mic", icon_size)
                menu_bar.voice_action.setIcon(icon)
                menu_bar.voice_action.setIconVisibleInMenu(True)
                print(f"✓ Установлена иконка voice_action: {not icon.isNull()}, размер: {icon.actualSize(icon_size)}")
                
            if hasattr(menu_bar, 'ai_tools_action'):
                icon = self.get_icon("cpu", icon_size)
                menu_bar.ai_tools_action.setIcon(icon)
                menu_bar.ai_tools_action.setIconVisibleInMenu(True)
                print(f"✓ Установлена иконка ai_tools_action: {not icon.isNull()}, размер: {icon.actualSize(icon_size)}")
            
            # Принудительно обновляем отображение меню
            menu_bar.update()
            self.titlebar_with_menu.update()
            
            # Дополнительное принудительное обновление через таймер
            QTimer.singleShot(100, lambda: self._force_menu_update(menu_bar))
            
            print("🎨 Установка иконок меню завершена!")
            
        except Exception as e:
            print(f"⚠ Ошибка установки иконок меню: {e}")

    def _force_menu_update(self, menu_bar):
        """Принудительное обновление меню с задержкой"""
        try:
            menu_bar.repaint()
            self.titlebar_with_menu.repaint()
            print("🔄 Принудительное обновление меню выполнено")
        except Exception as e:
            print(f"⚠ Ошибка при принудительном обновлении: {e}")

# Автоматическая система иконок
    class AutoIconManager:
        """Автоматический менеджер иконок для всех элементов интерфейса"""
        
        # Автоматический маппинг названий действий на иконки
        AUTO_ICON_MAPPING = {
            # Файловые операции
            'new': 'file-plus', 'create': 'file-plus', 'новый': 'file-plus',
            'open': 'folder-open', 'открыть': 'folder-open',
            'save': 'save', 'сохранить': 'save', 'save_as': 'save',
            'close': 'x', 'закрыть': 'x',
            'exit': 'log-out', 'выход': 'log-out', 'quit': 'log-out',
            
            # Редактирование
            'copy': 'copy', 'копировать': 'copy',
            'paste': 'clipboard', 'вставить': 'clipboard',
            'cut': 'scissors', 'вырезать': 'scissors',
            'undo': 'undo', 'отменить': 'undo',
            'redo': 'redo', 'повторить': 'redo',
            
            # Поиск и навигация
            'search': 'search', 'поиск': 'search', 'find': 'search',
            'replace': 'replace', 'заменить': 'replace',
            'refresh': 'refresh-cw', 'обновить': 'refresh-cw',
            
            # Инструменты и настройки
            'settings': 'settings', 'настройки': 'settings', 'preferences': 'settings',
            'tools': 'wrench', 'инструменты': 'wrench', 'productivity': 'wrench',
            'help': 'help-circle', 'помощь': 'help-circle', 'about': 'info',
            
            # AI и специфические функции
            'ai': 'cpu', 'ии': 'cpu', 'ai_tools': 'cpu',
            'voice': 'mic', 'голос': 'mic', 'speech': 'mic',
            'chat': 'message-circle', 'чат': 'message-circle',
            'code': 'code', 'код': 'code', 'editor': 'code',
            'terminal': 'terminal', 'терминал': 'terminal',
            
            # Проект и файлы
            'project': 'folder', 'проект': 'folder',
            'folder': 'folder', 'папка': 'folder', 'directory': 'folder',
            'file': 'file', 'файл': 'file',
            
            # Разное
            'run': 'play', 'запустить': 'play', 'execute': 'play',
            'stop': 'square', 'остановить': 'square',
            'pause': 'pause', 'пауза': 'pause',
            'download': 'download', 'скачать': 'download',
            'upload': 'upload', 'загрузить': 'upload',
        }
        
        @classmethod
        def auto_apply_icons(cls, widget, icon_manager):
            """Автоматически применяет иконки ко всем QAction в виджете"""
            applied_count = 0
            
            # Находим все QAction в виджете
            actions = cls._find_all_actions(widget)
            
            for action in actions:
                icon_name = cls._detect_icon_for_action(action)
                if icon_name:
                    try:
                        icon = icon_manager.get_icon(icon_name, QSize(24, 24))
                        if not icon.isNull():
                            action.setIcon(icon)
                            action.setIconVisibleInMenu(True)
                            applied_count += 1
                            print(f"🎨 Автоиконка: {action.objectName() or action.text()} -> {icon_name}")
                    except Exception as e:
                        print(f"⚠ Ошибка автоиконки для {action.text()}: {e}")
            
            print(f"✨ Автоматически применено {applied_count} иконок")
            return applied_count
        
        @classmethod
        def _find_all_actions(cls, widget):
            """Рекурсивно находит все QAction в виджете и его дочерних элементах"""
            actions = []
            
            # Получаем действия самого виджета
            if hasattr(widget, 'actions'):
                actions.extend(widget.actions())
            
            # Ищем в меню
            if hasattr(widget, 'menuBar') and widget.menuBar():
                for menu in widget.menuBar().findChildren(QMenu):
                    actions.extend(menu.actions())
            
            # Ищем в тулбарах
            for toolbar in widget.findChildren(QToolBar):
                actions.extend(toolbar.actions())
            
            # Ищем в дочерних виджетах
            for child in widget.findChildren(QWidget):
                if hasattr(child, 'actions'):
                    actions.extend(child.actions())
            
            return actions
        
        @classmethod
        def _detect_icon_for_action(cls, action):
            """Определяет подходящую иконку для действия по его названию"""
            # Проверяем objectName
            if action.objectName():
                name = action.objectName().lower().replace('_action', '').replace('action', '')
                if name in cls.AUTO_ICON_MAPPING:
                    return cls.AUTO_ICON_MAPPING[name]
            
            # Проверяем текст действия
            if action.text():
                text = action.text().lower().replace('&', '').replace('...', '').strip()
                
                # Прямое совпадение
                if text in cls.AUTO_ICON_MAPPING:
                    return cls.AUTO_ICON_MAPPING[text]
                
                # Поиск по ключевым словам
                for keyword, icon in cls.AUTO_ICON_MAPPING.items():
                    if keyword in text or text in keyword:
                        return icon
            
            return None
        
        @classmethod
        def register_module_icons(cls, module_widget, icon_manager):
            """Автоматически регистрирует иконки для нового модуля"""
            print(f"🔄 Автоматическая установка иконок для модуля: {module_widget.__class__.__name__}")
            return cls.auto_apply_icons(module_widget, icon_manager)

    # ...existing code...
# Импорт маппинга иконок
from icon_mapping import get_lucide_name


# =============================================================================
# Запуск приложения
# =============================================================================

def main():
    """Главная функция запуска приложения"""
    try:
        # Создание приложения
        app = QApplication(sys.argv)
        app.setApplicationName("GopiAI")
        app.setApplicationVersion("0.2.0")
        app.setOrganizationName("GopiAI Team")
        
        # Создание и отображение главного окна
        window = FramelessGopiAIStandaloneWindow()
        window.show()
        
        print("🚀 GopiAI Standalone Interface запущен!")
        
        # Запуск главного цикла приложения
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Ошибка при запуске приложения: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
