#!/usr/bin/env python3
"""
GopiAI Standalone Interface - исправленная версия
=====================================

Модульный интерфейс GopiAI с полностью встроенными компонентами:
- Frameless окно с профессиональным дизайном
- Левая панель: проводник файлов 
- Центральная область: система вкладок для документов
- Правая панель: чат с ИИ

Версия: 0.2.0
Дата: 2025-01-12
"""

import sys
import os
import warnings
from pathlib import Path

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
            sys.path.insert(0, path)
            
    # Импортируем НАСТОЯЩИЕ функции из GopiAI Core
    from gopiai.core.simple_theme_manager import (
        load_theme, apply_theme, save_theme,
        MATERIAL_SKY_THEME, EMERALD_GARDEN_THEME, 
        CRIMSON_RELIC_THEME, GOLDEN_EMBER_THEME
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
                from PySide6.QtGui import QIcon
                icon = QIcon(str(svg_path))
                self._icon_cache[icon_name] = icon
                print(f"✅ Загружена иконка: {icon_name}")
                return icon
            else:
                print(f"❌ Иконка не найдена: {icon_name} (путь: {svg_path})")
                # Возвращаем пустую иконку
                from PySide6.QtGui import QIcon
                empty_icon = QIcon()
                self._icon_cache[icon_name] = empty_icon
                return empty_icon
    
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
    
    # STUB: Заглушка для LucideIconManager
    class FakeLucideManager:
        def get_icon(self, icon_name, **kwargs):
            from PySide6.QtGui import QIcon
            return QIcon()
    
    LucideIconManager = type('LucideIconManager', (), {
        'instance': lambda: FakeLucideManager()
    })
    
    # STUB: Заглушка для маппинга иконок
    def get_lucide_name(original_name):
        return original_name

# Основные импорты PySide6
from PySide6.QtCore import Qt, Signal, QPoint, QSize, QRect, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QMenuBar, QMenu, QFrame, QLabel, QPushButton, QSplitter,
    QTreeView, QFileSystemModel, QTabWidget, QTextEdit, QFileDialog,
    QMessageBox
)
from PySide6.QtGui import QIcon, QFont, QPalette, QMouseEvent, QAction, QResizeEvent


def main():
    """Основная функция запуска"""
    app = QApplication(sys.argv)
    
    print("🚀 GopiAI Standalone Interface запущен!")
    
    # Применяем стили
    apply_simple_theme(app)
    
    # Создаем основное окно
    window = FramelessWindow()
    window.setGeometry(100, 100, 1200, 800)
    
    # Показываем окно
    window.show()
    
    return app.exec()


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
        
        # Установка иконок
        self._set_menu_icons()
    
    def _set_menu_icons(self):
        """Установка иконок для меню"""
        try:
            icon_manager = LucideIconManager.instance()
            
            # Маппинг иконок для меню
            icon_mappings = {
                'new_action': 'file-plus',
                'open_action': 'folder-open', 
                'save_action': 'save',
            }
            
            for action_name, icon_name in icon_mappings.items():
                if hasattr(self, action_name):
                    # Получаем иконку через маппинг
                    lucide_name = get_lucide_name(icon_name)
                    print(f"🔍 Маппинг иконки: {icon_name} -> {lucide_name}")
                    
                    icon = icon_manager.get_icon(lucide_name)
                    
                    # Проверяем системные иконки как fallback
                    if icon.isNull():
                        if icon_name == 'folder-open':
                            style = self.style()
                            icon = style.standardIcon(style.StandardPixmap.SP_DirOpenIcon)
                            if not icon.isNull():
                                print(f"✓ Системная иконка {icon_name} найдена")
                    
                    action = getattr(self, action_name)
                    action.setIcon(icon)
                    
                    success = not icon.isNull()
                    print(f"✓ Установлена иконка {action_name}: {success}")
                    
        except Exception as e:
            print(f"⚠ Ошибка установки иконок меню: {e}")
            
        print("✓ Иконки меню установлены")


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
        self.tree_view.setRootIndex(self.file_model.index(""))
        self.tree_view.hideColumn(1)  # Размер
        self.tree_view.hideColumn(2)  # Тип
        self.tree_view.hideColumn(3)  # Дата изменения
        
        layout.addWidget(self.tree_view)


class SimpleChatWidget(QWidget):
    """Простой виджет чата"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatWidget")
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса чата"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Заголовок
        header = QLabel("💬 Чат с ИИ")
        header.setObjectName("panelHeader")
        header.setFixedHeight(30)
        layout.addWidget(header)
        
        # Область сообщений
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        self.messages_area.append("Добро пожаловать в GopiAI! 🤖")
        layout.addWidget(self.messages_area)
        
        # Поле ввода
        input_layout = QHBoxLayout()
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(60)
        self.input_field.setPlaceholderText("Введите сообщение...")
        
        self.send_button = QPushButton("Отправить")
        self.send_button.setMaximumWidth(100)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)


class FramelessWindow(QMainWindow):
    """Окно без рамки с поддержкой изменения размера"""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Параметры изменения размера
        self.border_width = 8
        self.corner_width = 16
        self.is_resizing = False
        self.resize_direction = None
        
        # Для перемещения окна
        self.dragging = False
        self.drag_position = QPoint()
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Настройка интерфейса frameless окна"""
        # Главный контейнер
        main_container = QWidget()
        main_container.setObjectName("mainContainer")
        self.setCentralWidget(main_container)
        
        # Основной layout
        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем заголовочную панель
        self._create_title_bar(layout)
        
        # Создаем основной контент
        self._create_main_content(layout)
        
        # Применяем стили
        self._apply_styles()
    
    def _create_title_bar(self, parent_layout):
        """Создание заголовочной панели"""
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(40)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 5, 0)
        
        # Заголовок
        self.title_label = QLabel("GopiAI Standalone Interface")
        self.title_label.setObjectName("titleLabel")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Кнопки управления окном
        self.minimize_btn = QPushButton("_")
        self.maximize_btn = QPushButton("□")
        self.close_btn = QPushButton("×")
        
        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            btn.setFixedSize(30, 30)
            btn.setObjectName("windowControl")
            title_layout.addWidget(btn)
        
        # Подключение сигналов
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        self.close_btn.clicked.connect(self.close)
        
        # Делаем title_bar перетаскиваемым
        title_bar.mousePressEvent = self._title_bar_press
        title_bar.mouseMoveEvent = self._title_bar_move
        title_bar.mouseReleaseEvent = self._title_bar_release
        
        parent_layout.addWidget(title_bar)
    
    def _create_main_content(self, parent_layout):
        """Создание основного контента"""
        # Меню
        self.menu_bar = StandaloneMenuBar(self)
        parent_layout.addWidget(self.menu_bar)
        
        # Основной сплиттер
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель - проводник
        self.file_explorer = FileExplorerWidget()
        main_splitter.addWidget(self.file_explorer)
        
        # Центральная область - вкладки
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(QTextEdit(), "Новый документ")
        main_splitter.addWidget(self.tab_widget)
        
        # Правая панель - чат
        self.chat_widget = SimpleChatWidget()
        main_splitter.addWidget(self.chat_widget)
        
        # Настройка пропорций
        main_splitter.setSizes([250, 400, 300])
        
        parent_layout.addWidget(main_splitter)
    
    def _apply_styles(self):
        """Применение стилей"""
        style = """
        #mainContainer {
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 8px;
        }
        
        #titleBar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #e0e0e0, stop:1 #d0d0d0);
            border-bottom: 1px solid #bbb;
            border-radius: 8px 8px 0px 0px;
        }
        
        #titleLabel {
            font-weight: bold;
            color: #333;
            font-size: 14px;
        }
        
        #windowControl {
            border: 1px solid #bbb;
            background-color: #e8e8e8;
            border-radius: 4px;
            font-weight: bold;
        }
        
        #windowControl:hover {
            background-color: #d0d0d0;
        }
        
        #windowControl:pressed {
            background-color: #c0c0c0;
        }
        
        #panelHeader {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f8f8f8, stop:1 #e8e8e8);
            border-bottom: 1px solid #ddd;
            font-weight: bold;
            padding: 5px;
        }
        """
        
        self.setStyleSheet(style)
    
    def _toggle_maximize(self):
        """Переключение между обычным и максимальным размером"""
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.showMaximized() 
            self.maximize_btn.setText("❐")
    
    def _title_bar_press(self, event):
        """Обработка нажатия на заголовочную панель"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def _title_bar_move(self, event):
        """Обработка перемещения заголовочной панели"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def _title_bar_release(self, event):
        """Обработка отпускания заголовочной панели"""
        self.dragging = False


def apply_simple_theme(app):
    """Применение простой темы"""
    simple_theme = """
    QApplication {
        background-color: #f5f5f5;
        color: #333;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
    }
    
    QMainWindow {
        background-color: #ffffff;
    }
    
    QMenuBar {
        background-color: #f0f0f0;
        border-bottom: 1px solid #ddd;
        padding: 2px;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 4px 8px;
        margin: 1px;
        border-radius: 3px;
    }
    
    QMenuBar::item:selected {
        background-color: #e0e0e0;
    }
    
    QTabWidget::pane {
        border: 1px solid #c0c0c0;
        top: -1px;
        background-color: white;
    }
    
    QTabBar::tab {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #f0f0f0, stop:1 #e0e0e0);
        border: 1px solid #c0c0c0;
        padding: 6px 12px;
        margin-right: -1px;
    }
    
    QTabBar::tab:selected {
        background: white;
        border-bottom-color: white;
    }
    
    QTextEdit {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 4px;
    }
    
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #f8f8f8, stop:1 #e8e8e8);
        border: 1px solid #c0c0c0;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #f0f0f0, stop:1 #e0e0e0);
    }
    
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #e0e0e0, stop:1 #d0d0d0);
    }
    """
    
    app.setStyleSheet(simple_theme)


if __name__ == "__main__":
    sys.exit(main())

