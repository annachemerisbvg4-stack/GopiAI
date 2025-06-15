#!/usr/bin/env python3
"""
GopiAI Standalone Interface - Модульная версия с динамическими цветами
=====================================================================

Основной файл для запуска модульного интерфейса GopiAI.
Все цвета теперь динамически привязаны к текущей теме.

Автор: Crazy Coder
Версия: 0.3.1 (Модульная с динамическими цветами)
Дата: 2025-06-03
"""

import sys
import os
import warnings
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка WebEngine для предотвращения графических ошибок
os.environ.setdefault(
    "QTWEBENGINE_CHROMIUM_FLAGS",
    "--disable-gpu --disable-software-rasterizer --disable-3d-apis --disable-accelerated-2d-canvas --no-sandbox --disable-dev-shm-usage --disable-gpu-sandbox --disable-gpu-compositing --disable-webgl --disable-webgl2",
)
os.environ.setdefault("QT_OPENGL", "software")
os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QMenuBar,
    QLabel,
    QFileDialog,
    QMessageBox,
    QTabWidget,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QPalette

# Импорт компонентов тем
from gopiai.ui.utils.theme_manager import ThemeManager
from gopiai.ui.dialogs.settings_dialog import GopiAISettingsDialog

# Настройка путей для импорта модулей GopiAI
script_dir = os.path.dirname(os.path.abspath(__file__))
gopiai_modules_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))

module_paths = [
    os.path.join(gopiai_modules_root, "GopiAI-Core"),
    os.path.join(gopiai_modules_root, "GopiAI-Widgets"),
    os.path.join(gopiai_modules_root, "GopiAI-App"),
    os.path.join(gopiai_modules_root, "GopiAI-Extensions"),
    os.path.join(gopiai_modules_root, "rag_memory_system"),
    gopiai_modules_root,
]

for path in module_paths:
    if path not in sys.path:
        sys.path.insert(0, path)

print("📦 Модульная версия GopiAI v0.3.1 с динамическими цветами")
print("Добавленные пути для модулей:")
for p in module_paths:
    print(f"- {p} (существует: {os.path.exists(p)})")

# Импорт модульных компонентов UI
try:
    from gopiai.ui.components import (
        StandaloneMenuBar,
        StandaloneTitlebar,
        StandaloneTitlebarWithMenu,
        CustomGrip,
        FileExplorerWidget,
        TabDocumentWidget,
        WebViewChatWidget,
        TerminalWidget,
    )

    print("✅ Все основные модули UI загружены успешно")
    MODULES_LOADED = True

except ImportError as e:
    print(f"⚠️ Ошибка импорта UI модулей: {e}")
    print("Запускаем в fallback режиме...")
    MODULES_LOADED = False

    # Fallback - создаём простые заглушки
    class SimpleWidget(QWidget):
        def __init__(self, name="Widget"):
            super().__init__()
            self.setFixedSize(200, 100)
            layout = QVBoxLayout()
            layout.addWidget(QLabel(f"Fallback: {name}"))
            self.setLayout(layout)

        def add_new_tab(self, title, content):
            print(f"Fallback: add_new_tab({title})")

        def get_current_text(self):
            return "Fallback content"

        def set_window(self, window):
            pass

        def add_browser_tab(self, url="about:blank", title="Браузер"):
            print(f"Fallback: add_browser_tab({url}, {title}) - Browser not available")

    class SimpleMenuBar(QMenuBar):
        def refresh_icons(self):
            pass

    StandaloneMenuBar = SimpleMenuBar
    StandaloneTitlebar = lambda parent=None: SimpleWidget("Titlebar")
    StandaloneTitlebarWithMenu = lambda parent=None: SimpleWidget("TitlebarWithMenu")
    CustomGrip = lambda parent, direction: QWidget()
    FileExplorerWidget = lambda parent=None, icon_manager=None: SimpleWidget("FileExplorer")
    TabDocumentWidget = lambda parent=None: SimpleWidget("TabDocument")
    TerminalWidget = lambda parent=None: SimpleWidget("Terminal")

    class FallbackThemeManager:
        def __init__(self):
            self.current_theme = "default"
        
        def apply_theme(self, app_or_theme):
            print(f"Fallback: apply_theme({app_or_theme})")
            return False
        
        def get_theme_colors(self):
            """Возвращает базовые цвета для fallback режима"""
            return {
                'background': '#2d2d30',
                'foreground': '#ffffff',
                'accent': '#007acc',
                'border': '#3e3e42',
                'hover': '#404040',
                'selected': '#094771',
                'text': '#cccccc',
                'disabled': '#666666'
            }

    if 'ThemeManager' not in globals() or ThemeManager is None:
        ThemeManager = FallbackThemeManager

# Глобальные переменные для систем
AutoIconSystem = None
ThemeManagerClass = None
GopiAIThemeManager = None
apply_theme = None
load_theme = None
save_theme = None
MATERIAL_SKY_THEME = {"name": "Material Sky", "primary": "#2196F3"}
EXTENSIONS_AVAILABLE = True


class DynamicColorManager:
    """Менеджер динамических цветов для интерфейса"""
    
    def __init__(self, theme_manager=None):
        self.theme_manager = theme_manager
        self._theme_colors = {}
        self._update_colors()
    
    def _update_colors(self):
        """Обновляет цвета на основе текущей темы"""
        if self.theme_manager and hasattr(self.theme_manager, 'get_theme_colors'):
            try:
                self._theme_colors = self.theme_manager.get_theme_colors()
                print(f"✅ Цвета темы обновлены: {list(self._theme_colors.keys())}")
            except Exception as e:
                print(f"⚠️ Ошибка получения цветов темы: {e}")
                self._use_fallback_colors()
        else:
            self._use_fallback_colors()
    
    def _use_fallback_colors(self):
        """Использует базовые цвета в качестве запасного варианта"""
        app = QApplication.instance()
        if app and isinstance(app, QApplication):
            palette = app.palette()
            self._theme_colors = {
                'background': palette.color(QPalette.ColorRole.Window).name(),
                'foreground': palette.color(QPalette.ColorRole.WindowText).name(),
                'accent': palette.color(QPalette.ColorRole.Highlight).name(),
                'border': palette.color(QPalette.ColorRole.Mid).name(),
                'hover': palette.color(QPalette.ColorRole.AlternateBase).name(),
                'selected': palette.color(QPalette.ColorRole.Highlight).name(),
                'text': palette.color(QPalette.ColorRole.Text).name(),
                'disabled': palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text).name()
            }
        else:
            # Последний fallback
            self._theme_colors = {
                'background': '#2d2d30',
                'foreground': '#ffffff',
                'accent': '#007acc',
                'border': '#3e3e42',
                'hover': '#404040',
                'selected': '#094771',
                'text': '#cccccc',
                'disabled': '#666666'
            }
        print("✅ Используются fallback цвета")
    
    def get_color(self, color_name, fallback=None):
        """Получает цвет по имени с возможностью fallback"""
        color = self._theme_colors.get(color_name, fallback)
        if color is None:
            color = self._theme_colors.get('foreground', '#ffffff')
        return color
    
    def get_all_colors(self):
        """Возвращает все доступные цвета"""
        return self._theme_colors.copy()
    
    def refresh_colors(self):
        """Обновляет цвета при смене темы"""
        self._update_colors()
    
    def generate_dynamic_stylesheet(self):
        """Генерирует динамический stylesheet на основе цветов темы"""
        colors = self._theme_colors
        
        return f"""
        /* Основные стили окна */
        QMainWindow {{
            background-color: {colors.get('background', '#2d2d30')};
            color: {colors.get('foreground', '#ffffff')};
            border: none;
        }}
        
        QWidget {{
            background-color: {colors.get('background', '#2d2d30')};
            color: {colors.get('text', '#cccccc')};
            border: none;
        }}
        
        /* Меню */
        QMenuBar {{
            background-color: {colors.get('background', '#2d2d30')};
            color: {colors.get('text', '#cccccc')};
            padding: 4px;
            border-bottom: 1px solid {colors.get('border', '#3e3e42')};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 12px;
            color: {colors.get('text', '#cccccc')};
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors.get('accent', '#007acc')};
            color: {colors.get('foreground', '#ffffff')};
        }}
        
        QMenuBar::item:pressed {{
            background-color: {colors.get('selected', '#094771')};
        }}
        
        QMenu {{
            background-color: {colors.get('background', '#2d2d30')};
            color: {colors.get('text', '#cccccc')};
            border: 1px solid {colors.get('border', '#3e3e42')};
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 6px 24px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors.get('accent', '#007acc')};
            color: {colors.get('foreground', '#ffffff')};
        }}
        
        /* Сплиттеры */
        QSplitter::handle {{
            background-color: {colors.get('border', '#3e3e42')};
            border: 1px solid {colors.get('border', '#3e3e42')};
        }}
        
        QSplitter::handle:horizontal {{
            width: 3px;
            background-color: {colors.get('border', '#3e3e42')};
        }}
        
        QSplitter::handle:vertical {{
            height: 3px;
            background-color: {colors.get('border', '#3e3e42')};
        }}
        
        QSplitter::handle:hover {{
            background-color: {colors.get('accent', '#007acc')};
        }}
        
        QSplitter::handle:pressed {{
            background-color: {colors.get('selected', '#094771')};
        }}
        
        /* Вкладки */
        QTabWidget::pane {{
            border: 1px solid {colors.get('border', '#3e3e42')};
            background-color: {colors.get('background', '#2d2d30')};
            border-top: none;
        }}
        
        QTabBar::tab {{
            background-color: {colors.get('hover', '#404040')};
            color: {colors.get('text', '#cccccc')};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            min-width: 80px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors.get('accent', '#007acc')};
            color: {colors.get('foreground', '#ffffff')};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {colors.get('hover', '#404040')};
        }}
        
        QTabBar::tab:disabled {{
            color: {colors.get('disabled', '#666666')};
            background-color: {colors.get('background', '#2d2d30')};
        }}
        
        /* Кнопки */
        QPushButton {{
            background-color: {colors.get('hover', '#404040')};
            color: {colors.get('text', '#cccccc')};
            border: 1px solid {colors.get('border', '#3e3e42')};
            padding: 6px 12px;
            min-width: 80px;
        }}
        
        QPushButton:hover {{
            background-color: {colors.get('accent', '#007acc')};
            color: {colors.get('foreground', '#ffffff')};
            border-color: {colors.get('accent', '#007acc')};
        }}
        
        QPushButton:pressed {{
            background-color: {colors.get('selected', '#094771')};
        }}
        
        QPushButton:disabled {{
            background-color: {colors.get('background', '#2d2d30')};
            color: {colors.get('disabled', '#666666')};
            border-color: {colors.get('disabled', '#666666')};
        }}
        
        /* Поля ввода */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors.get('background', '#2d2d30')};
            color: {colors.get('text', '#cccccc')};
            border: 1px solid {colors.get('border', '#3e3e42')};
            padding: 4px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {colors.get('accent', '#007acc')};
        }}
        
        /* Скроллбары */
        QScrollBar:vertical {{
            background-color: {colors.get('background', '#2d2d30')};
            width: 12px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors.get('hover', '#404040')};
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors.get('accent', '#007acc')};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        
        QScrollBar:horizontal {{
            background-color: {colors.get('background', '#2d2d30')};
            height: 12px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors.get('hover', '#404040')};
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors.get('accent', '#007acc')};
        }}
        
        /* Группы виджетов */
        QGroupBox {{
            color: {colors.get('text', '#cccccc')};
            border: 1px solid {colors.get('border', '#3e3e42')};
            padding-top: 16px;
            margin-top: 8px;
        }}
        
        QGroupBox::title {{
            color: {colors.get('accent', '#007acc')};
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 8px 0 8px;
        }}
        
        /* Списки */
        QListWidget, QTreeWidget {{
            background-color: {colors.get('background', '#2d2d30')};
            color: {colors.get('text', '#cccccc')};
            border: 1px solid {colors.get('border', '#3e3e42')};
            alternate-background-color: {colors.get('hover', '#404040')};
        }}
        
        QListWidget::item:selected, QTreeWidget::item:selected {{
            background-color: {colors.get('accent', '#007acc')};
            color: {colors.get('foreground', '#ffffff')};
        }}
        
        QListWidget::item:hover, QTreeWidget::item:hover {{
            background-color: {colors.get('hover', '#404040')};
        }}
        
        /* Статусная строка */
        QStatusBar {{
            background-color: {colors.get('background', '#2d2d30')};
            color: {colors.get('text', '#cccccc')};
            border-top: 1px solid {colors.get('border', '#3e3e42')};
        }}
        
        /* Прогресс-бары */
        QProgressBar {{
            background-color: {colors.get('background', '#2d2d30')};
            border: 1px solid {colors.get('border', '#3e3e42')};
            text-align: center;
            color: {colors.get('text', '#cccccc')};
        }}
        
        QProgressBar::chunk {{
            background-color: {colors.get('accent', '#007acc')};
        }}
        """


class FramelessGopiAIStandaloneWindow(QMainWindow):
    """Основное frameless окно GopiAI с динамическими цветами"""

    def _apply_dynamic_styles(self):
        """Применяет динамические стили на основе текущей темы"""
        try:
            if hasattr(self, "color_manager"):
                stylesheet = self.color_manager.generate_dynamic_stylesheet()
                self.setStyleSheet(stylesheet)
                print("✅ Динамические стили применены")
            else:
                print("⚠️ color_manager не инициализирован, стили не применены")
        except Exception as e:
            print(f"⚠️ Ошибка применения динамических стилей: {e}")

    def __init__(self):
        super().__init__()
        print("🚀 Инициализация модульного интерфейса GopiAI с динамическими цветами...")

        # Базовые настройки окна
        self.setWindowTitle("GopiAI v0.3.1 - Модульный ИИ Интерфейс")
        self.setMinimumSize(1000, 700)
        self.resize(1400, 900)

        # Frameless окно
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # Константы
        self.TITLEBAR_HEIGHT = 40
        self.GRIP_SIZE = 10
        
        # Инициализация систем
        self._init_theme_system()
        self._init_color_manager()
        self._setup_ui()
        self._init_grips()
        self._apply_dynamic_styles()
        self._connect_menu_signals()
        self._apply_vscode_like_layout()
        self._setup_panel_shortcuts()

        # Настройка автоматического обновления цветов
        self._setup_color_refresh_timer()

        print("✅ FramelessGopiAIStandaloneWindow с динамическими цветами готов к работе!")

    def _init_color_manager(self):
        """Инициализация менеджера динамических цветов"""
        try:
            self.color_manager = DynamicColorManager(self.theme_manager)
            print("✅ Менеджер динамических цветов инициализирован")
        except Exception as e:
            print(f"⚠️ Ошибка инициализации менеджера цветов: {e}")
            self.color_manager = DynamicColorManager()

    def _setup_color_refresh_timer(self):
        """Настройка таймера для обновления цветов"""
        self.color_refresh_timer = QTimer()
        self.color_refresh_timer.timeout.connect(self._refresh_colors_if_needed)
        self.color_refresh_timer.start(1000)  # Проверяем каждую секунду

    def _refresh_colors_if_needed(self):
        """Обновляет цвета при необходимости"""
        try:
            # Проверяем, изменилась ли тема
            if hasattr(self.theme_manager, 'current_theme'):
                current_theme = getattr(self.theme_manager, 'current_theme', None)
                if not hasattr(self, '_last_theme') or self._last_theme != current_theme:
                    self._last_theme = current_theme
                    self._refresh_all_colors()
        except Exception as e:
            # Тихо игнорируем ошибки обновления
            pass

    def _refresh_all_colors(self):
        """Полное обновление всех цветов интерфейса"""
        try:
            print("🎨 Обновление цветов интерфейса...")
            self.color_manager.refresh_colors()
            self._apply_dynamic_styles()
            
            # Обновляем цвета всех дочерних виджетов
            self._update_child_widgets_colors()
            
            print("✅ Цвета интерфейса обновлены")
        except Exception as e:
            print(f"⚠️ Ошибка обновления цветов: {e}")

    def _update_child_widgets_colors(self):
        """Обновляет цвета всех дочерних виджетов"""
        try:
            # Обновляем цвета меню
            if hasattr(self, 'titlebar_with_menu'):
                menu_bar = getattr(self.titlebar_with_menu, 'menu_bar', None)
                if menu_bar and hasattr(menu_bar, 'refresh_colors'):
                    menu_bar.refresh_colors()
            
            # Обновляем цвета всех виджетов, только если у них есть метод refresh_colors
            for widget in self.findChildren(QWidget):
                if hasattr(widget, 'refresh_colors') and callable(getattr(widget, 'refresh_colors', None)):
                    try:
                        widget.refresh_colors() # type: ignore
                    except Exception as widget_error:
                        print(f"⚠️ Ошибка обновления цветов виджета {type(widget).__name__}: {widget_error}")
                    
        except Exception as e:
            print(f"⚠️ Ошибка обновления цветов дочерних виджетов: {e}")

    def _setup_ui(self):
        """Настройка модульного пользовательского интерфейса"""
        print("🔧 Настройка UI из модулей...")

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Titlebar с меню (модульный)
        if MODULES_LOADED:
            self.titlebar_with_menu = StandaloneTitlebarWithMenu(self)
            if hasattr(self.titlebar_with_menu, "set_window"):
                self.titlebar_with_menu.set_window(self)
        else:
            self.titlebar_with_menu = StandaloneTitlebarWithMenu()
        self.titlebar_with_menu.setFixedHeight(self.TITLEBAR_HEIGHT * 2)
        main_layout.addWidget(self.titlebar_with_menu)

        # Основной сплиттер (горизонтальный)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter, 1)
        
        # Левая панель - файловый проводник (модульный)
        self.file_explorer = FileExplorerWidget(icon_manager=self.icon_manager)
        self.file_explorer.setMinimumWidth(250)
        self.file_explorer.setMaximumWidth(600)
        self.file_explorer.resize(300, 600)

        size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.file_explorer.setSizePolicy(size_policy)
        main_splitter.addWidget(self.file_explorer)

        # Правый сплиттер (вертикальный)
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(right_splitter)

        # Центральный сплиттер (горизонтальный)
        center_splitter = QSplitter(Qt.Orientation.Horizontal)
        right_splitter.addWidget(center_splitter)

        # Центральная область - система вкладок (модульная)
        self.tab_document = TabDocumentWidget()
        center_splitter.addWidget(self.tab_document)

        # Правая панель - чат с ИИ (модульный)
        try:
            # Пытаемся использовать WebView чат с современным интерфейсом
            self.chat_widget = WebViewChatWidget()
            # Передаем менеджер тем в WebView чат для интеграции
            if hasattr(self, 'theme_manager'):
                self.chat_widget.set_theme_manager(self.theme_manager)
            print("✅ Используется WebView чат")
        except Exception as e:
            print(f"⚠️ WebView чат недоступен, используется обычный чат: {e}")
            # Fallback - используем обычный ChatWidget из импорта
            from gopiai.ui.components.chat_widget import ChatWidget
            self.chat_widget = ChatWidget()
        self.chat_widget.setMinimumWidth(250)
        self.chat_widget.setMaximumWidth(600)
        self.chat_widget.resize(300, 600)
        
        chat_size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.chat_widget.setSizePolicy(chat_size_policy)
        center_splitter.addWidget(self.chat_widget)

        if EXTENSIONS_AVAILABLE:
            self.chat_widget.setVisible(False)

        # Нижняя панель - терминал (модульный)
        self.terminal_widget = TerminalWidget()
        self.terminal_widget.setMinimumHeight(150)
        self.terminal_widget.setMaximumHeight(400)
        
        terminal_size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.terminal_widget.setSizePolicy(terminal_size_policy)
        right_splitter.addWidget(self.terminal_widget)

        # Настройка пропорций сплиттеров
        main_splitter.setSizes([300, 1100])
        center_splitter.setSizes([700, 350])
        right_splitter.setSizes([700, 200])

        main_splitter.setChildrenCollapsible(True)
        center_splitter.setChildrenCollapsible(True)
        right_splitter.setChildrenCollapsible(False)

        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        center_splitter.setStretchFactor(0, 1)
        center_splitter.setStretchFactor(1, 0)
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 0)

        self._configure_splitter_behavior()
        print("✅ Модульный UI настроен с ограничениями размеров панелей")

    def _configure_splitter_behavior(self):
        """Дополнительная настройка поведения сплиттеров"""
        try:
            main_splitter = self.findChild(QSplitter)
            if main_splitter:
                main_splitter.setHandleWidth(3)
                
                right_splitter = main_splitter.widget(1)
                if isinstance(right_splitter, QSplitter):
                    right_splitter.setHandleWidth(3)
                    
                    center_splitter = right_splitter.widget(0)
                    if isinstance(center_splitter, QSplitter):
                        center_splitter.setHandleWidth(3)
                        center_splitter.setCollapsible(0, False)
                        center_splitter.setCollapsible(1, True)
                    
                    right_splitter.setCollapsible(0, False)
                    right_splitter.setCollapsible(1, True)
                
                main_splitter.setCollapsible(0, True)
                main_splitter.setCollapsible(1, False)
                
            print("✅ Поведение сплиттеров настроено")
            
        except Exception as e:
            print(f"⚠️ Ошибка настройки сплиттеров: {e}")

    def _apply_vscode_like_layout(self):
        """Применить макет в стиле VSCode с динамическими цветами"""
        try:
            print("✅ Применен макет в стиле VSCode с динамическими цветами")
        except Exception as e:
            print(f"⚠️ Ошибка применения макета VSCode: {e}")

    def _setup_panel_shortcuts(self):
        """Настройка горячих клавиш для управления панелями"""
        try:
            from PySide6.QtGui import QKeySequence, QShortcut
            
            toggle_explorer = QShortcut(QKeySequence("Ctrl+B"), self)
            toggle_explorer.activated.connect(
                lambda: self.file_explorer.setVisible(not self.file_explorer.isVisible())
            )
            
            toggle_terminal = QShortcut(QKeySequence("Ctrl+`"), self)
            toggle_terminal.activated.connect(
                lambda: self.terminal_widget.setVisible(not self.terminal_widget.isVisible())
            )
            
            # Ctrl+Shift+C - переключение чата
            toggle_chat = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
            toggle_chat.activated.connect(
                lambda: self.chat_widget.setVisible(not self.chat_widget.isVisible())
            )
            
            print("✅ Горячие клавиши для панелей настроены")
            
        except Exception as e:
            print(f"⚠️ Ошибка настройки горячих клавиш: {e}")

        print("✅ Модульный UI настроен")

    def _init_grips(self):
        """Инициализация грипов для изменения размера"""
        self.grips = {}
        directions = [
            "top",
            "bottom",
            "left",
            "right",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
        ]

        for direction in directions:
            grip = CustomGrip(self, direction)
            self.grips[direction] = grip

        self._update_grips()

    def _update_grips(self):
        """Обновление позиций грипов"""
        rect = self.rect()
        grip_size = self.GRIP_SIZE

        # Угловые грипы
        self.grips["top-left"].setGeometry(0, 0, grip_size, grip_size)
        self.grips["top-right"].setGeometry(
            rect.width() - grip_size, 0, grip_size, grip_size
        )
        self.grips["bottom-left"].setGeometry(
            0, rect.height() - grip_size, grip_size, grip_size
        )
        self.grips["bottom-right"].setGeometry(
            rect.width() - grip_size, rect.height() - grip_size, grip_size, grip_size
        )

        # Боковые грипы
        self.grips["top"].setGeometry(
            grip_size, 0, rect.width() - 2 * grip_size, grip_size
        )
        self.grips["bottom"].setGeometry(
            grip_size,
            rect.height() - grip_size,
            rect.width() - 2 * grip_size,
            grip_size,
        )
        self.grips["left"].setGeometry(
            0, grip_size, grip_size, rect.height() - 2 * grip_size
        )
        self.grips["right"].setGeometry(
            rect.width() - grip_size,
            grip_size,
            grip_size,
            rect.height() - 2 * grip_size,
        )

    def _init_theme_system(self):
        """Инициализация системы тем и иконок"""
        # Импорт системы иконок
        try:
            import qtawesome as qta

            class SimpleIconManager:
                def __init__(self):
                    self.qta = qta

                def get_icon(self, name):
                    # Try several icon prefixes, fallback to a default icon if not found
                    prefixes = ["fa5.", "fa.", "mdi.", "ei."]
                    for prefix in prefixes:
                        try:
                            icon = self.qta.icon(prefix + name)
                            if not icon.isNull():
                                return icon
                        except Exception:
                            continue
                    # Fallback to a default icon if all attempts fail
                    try:
                        return self.qta.icon("fa5.question")
                    except Exception:
                        return None

            self.icon_manager = SimpleIconManager()
            self.icon_manager.get_icon("example")
            print("✅ Система иконок SimpleIconManager инициализирована")
        except ImportError:
            self.icon_manager = None
            print("⚠️ Система иконок недоступна")
        except Exception as e:
            print(f"⚠️ Ошибка инициализации иконок: {e}")
            self.icon_manager = None

        # Инициализация системы тем
        
        # Определяем LocalFallbackThemeManager один раз здесь, до блока try-except
        class LocalFallbackThemeManager:
            def __init__(self):
                self.current_theme = "default"
            
            def apply_theme(self, app_or_theme):
                print(f"Fallback: apply_theme({app_or_theme})")
                return False

        try:
            if ThemeManager is not None:
                self.theme_manager = ThemeManager()
                if self.theme_manager:
                    print("✅ Менеджер тем инициализирован")
                    # Применяем тему, сохраненную в файле настроек
                    app = QApplication.instance()
                    if app:
                        self.theme_manager.apply_theme(app)
                        print("✅ Применена тема из файла настроек")
                else:
                    print("⚠️ Не удалось создать менеджер тем. Используем fallback.")
                    self.theme_manager = LocalFallbackThemeManager() # Создаем экземпляр
            else:
                print("⚠️ ThemeManager недоступен, используем fallback")
                # Используем предварительно определенный LocalFallbackThemeManager
                self.theme_manager = LocalFallbackThemeManager() # Создаем экземпляр
        except Exception as e:
            print(f"⚠️ Ошибка инициализации менеджера тем: {e}")
            # Используем предварительно определенный LocalFallbackThemeManager в случае ошибки
            self.theme_manager = LocalFallbackThemeManager() # Создаем экземпляр

    def _apply_default_styles(self):
        """Применение стилей по умолчанию"""
        # Пытаемся применить систему тем через theme_manager
        try:
            if self.theme_manager and hasattr(self.theme_manager, "apply_theme"):
                from PySide6.QtWidgets import QApplication

                app = QApplication.instance()
                print(f"🔍 main.py: QApplication.instance() = {app}")
                if app:
                    print(f"🔍 main.py: Вызываем self.theme_manager.apply_theme({app})")
                    result = self.theme_manager.apply_theme(app)
                    print(f"🔍 main.py: Результат apply_theme = {result}")
                    if result:
                        print("✅ Система тем применена через theme_manager")
                        # Обновляем тему WebView чата
                        if hasattr(self, 'chat_widget') and hasattr(self.chat_widget, '_apply_theme_to_webview'):
                            self.chat_widget._apply_theme_to_webview()
                        return
                    else:
                        print("⚠️ apply_theme вернул False")
                else:
                    print("⚠️ QApplication.instance() вернул None")
        except Exception as e:
            print(f"⚠️ Ошибка применения темы через theme_manager: {e}")
            import traceback

            traceback.print_exc()

        # Последний fallback - встроенные стили
        print("⚠️ Используем встроенные стили fallback")
        self._apply_fallback_styles()

    def _apply_fallback_styles(self):
        """Применение запасных стилей"""
        fallback_style = """
      QMainWindow {
          background-color: #1e1e1e;
          color: #ffffff;
      }
      QWidget {
          background-color: #ff0000;
          color: #ffffff;
          border: none;
      }
      QMenuBar {
          background-color: #333333;
          color: #ffffff;
          padding: 4px;
      }
      QMenuBar::item {
          background-color: transparent;
          padding: 8px 12px;
      }
      QMenuBar::item:selected {
          background-color: #4CAF50;
      }
      QSplitter::handle {
          background-color: #404040;
      }
      QTabWidget::pane {
          border: 1px solid #404040;
          background-color: #ff0000;
      }
      QTabBar::tab {
          background-color: #404040;
          color: #ffffff;
          padding: 8px 16px;
          margin-right: 2px;
      }
      QTabBar::tab:selected {
          background-color: #4CAF50;
      }        """
        self.setStyleSheet(fallback_style)

    def _connect_menu_signals(self):
        """Подключение сигналов меню"""
        try:
            menu_bar = getattr(self.titlebar_with_menu, "menu_bar", None)
            if not menu_bar:
                print("⚠️ Меню недоступно")
                return

            # Подключаем новые сигналы
            if hasattr(menu_bar, "openSettingsRequested"):
                menu_bar.openSettingsRequested.connect(self._open_settings)
                if self.icon_manager is not None:
                    self.icon_manager.get_icon("settings")
                print("✅ Сигнал openSettingsRequested подключен")

            if hasattr(menu_bar, "changeThemeRequested"):
                menu_bar.changeThemeRequested.connect(self.on_change_theme)
                if self.icon_manager is not None:
                    self.icon_manager.get_icon("theme")
                print("✅ Сигнал changeThemeRequested подключен")

            # Подключаем остальные сигналы файлового меню
            if hasattr(menu_bar, "newFileRequested"):
                menu_bar.newFileRequested.connect(self._on_new_file)
            if hasattr(menu_bar, "openFileRequested"):
                menu_bar.openFileRequested.connect(self._on_open_file)
            if hasattr(menu_bar, "saveRequested"):
                menu_bar.saveRequested.connect(self._on_save_file)
            if hasattr(menu_bar, "exitRequested"):
                menu_bar.exitRequested.connect(self.close)

            # Подключаем сигналы меню вида
            if hasattr(menu_bar, "openChatRequested"):
                menu_bar.openChatRequested.connect(self._toggle_chat)
            if hasattr(menu_bar, "openTerminalRequested"):
                menu_bar.openTerminalRequested.connect(self._toggle_terminal)
            if hasattr(menu_bar, "toggleFileExplorerRequested"):
                menu_bar.toggleFileExplorerRequested.connect(
                    lambda: self.file_explorer.setVisible(
                        not self.file_explorer.isVisible()
                    )
                )
            if hasattr(menu_bar, "togglePanelsRequested"):

                def toggle_panels():
                    self.file_explorer.setVisible(not self.file_explorer.isVisible())
                    self.chat_widget.setVisible(not self.chat_widget.isVisible())
                    self.terminal_widget.setVisible(
                        not self.terminal_widget.isVisible()
                    )

                menu_bar.togglePanelsRequested.connect(toggle_panels)

            # Подключаем сигнал открытия браузера
            if hasattr(menu_bar, "openBrowserRequested"):
                if hasattr(self.tab_document, "add_browser_tab"):
                    menu_bar.openBrowserRequested.connect(
                        self.tab_document.add_browser_tab
                    )
                    print("✅ Сигнал openBrowserRequested подключен к add_browser_tab")
                else:
                    print("⚠️ tab_document не поддерживает add_browser_tab")

            # Подключаем сигналы для обновления иконок и тем
            if hasattr(menu_bar, "refreshIconsRequested"):
                menu_bar.refreshIconsRequested.connect(menu_bar.refresh_icons)
            if hasattr(menu_bar, "refreshThemeRequested"):
                menu_bar.refreshThemeRequested.connect(
                    lambda: self.on_change_theme(
                        getattr(self.theme_manager, "current_theme", "default")
                    )
                )

            print("✅ Сигналы меню подключены успешно")
        except Exception as e:
            print(f"⚠️ Ошибка подключения сигналов меню: {e}")

    def _open_settings(self):
        """Открыть диалог настроек"""
        try:
            print("🔧 Создание диалога настроек...")
            
            # Проверяем доступность класса диалога настроек
            if GopiAISettingsDialog is None:
                print("⚠️ GopiAISettingsDialog недоступен")
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Ошибка", "Диалог настроек недоступен")
                return

            # Удаляем вызов старого диалога настроек
            print("🔧 Импорт выполнен успешно")

            # Сохраняем диалог как атрибут экземпляра, чтобы избежать удаления
            if hasattr(self, "_settings_dialog") and self._settings_dialog is not None:
                try:
                    self._settings_dialog.close()
                except Exception:
                    pass
                self._settings_dialog = None
            
            self._settings_dialog = GopiAISettingsDialog(self.theme_manager, self)
            print("🔧 Диалог настроек создан успешно")

            # Подключаем сигналы диалога настроек
            if hasattr(self._settings_dialog, "themeChanged"):
                self._settings_dialog.themeChanged.connect(self.on_change_theme)
            if hasattr(self._settings_dialog, "settings_applied"):
                self._settings_dialog.settings_applied.connect(
                    self._on_settings_changed
                )

            print("🔧 Показываем диалог настроек...")
            # Показываем диалог
            result = self._settings_dialog.exec()
            if result == self._settings_dialog.DialogCode.Accepted:
                print("✅ Настройки применены")
            else:
                print("⚠️ Настройки отменены")
            self._settings_dialog = None

        except ImportError as e:
            print(f"⚠️ Ошибка импорта диалога настроек: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Диалог настроек недоступен")
        except Exception as e:
            print(f"⚠️ Ошибка открытия настроек: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть настройки: {e}")

    def _on_settings_changed(self, settings_dict):
        """Обработка изменения настроек"""
        try:
            print(f"🔧 Настройки изменены: {settings_dict}")

            # Применяем изменения шрифта
            if "font_size" in settings_dict:
                font_size = settings_dict["font_size"]
                font = self.font()
                font.setPointSize(font_size)
                self.setFont(font)
                print(f"✅ Размер шрифта изменен на {font_size}")

            # Применяем изменения темы и тёмного режима
            # Примечание: переключатель тёмного режима уже обработан в settings_dialog.py
            # и применён к theme_manager._current_variant
            if "theme" in settings_dict:
                # Используем имя темы напрямую, а не маппинг, так как теперь
                # настройка темного режима обрабатывается отдельно
                theme_name = settings_dict["theme"]
                self.on_change_theme(theme_name)

            # Показать/скрыть панели
            # Примечание: исправлено использование переменной panels
            if "show_panels" in settings_dict:
                panels = settings_dict["show_panels"]
                if "file_explorer" in panels:
                    self.file_explorer.setVisible(panels["file_explorer"])
                if "terminal" in panels:
                    self.terminal_widget.setVisible(panels["terminal"])
                if "chat" in panels:
                    self.chat_widget.setVisible(panels["chat"])
                print(
                    "✅ Видимость панелей обновлена"
                )  # Применяем настройки расширений
            if "extensions" in settings_dict:
                extensions = settings_dict["extensions"]
                print(f"🔌 Настройки расширений: {extensions}")
                # Здесь можно добавить логику включения/отключения расширений
        except Exception as e:
            print(f"⚠️ Ошибка применения настроек: {e}")

    def _show_settings(self):
        """Показать диалог настроек"""
        try:
            # Сохраняем диалог как атрибут экземпляра, чтобы избежать удаления
            if hasattr(self, "_settings_dialog") and self._settings_dialog is not None:
                try:
                    self._settings_dialog.close()
                except Exception:
                    pass
                self._settings_dialog = None
            self._settings_dialog = GopiAISettingsDialog(self.theme_manager, self)
            # Подключаем сигнал для применения настроек
            self._settings_dialog.settings_applied.connect(self._on_settings_changed)

            # Показываем диалог
            if (
                self._settings_dialog.exec()
                == self._settings_dialog.DialogCode.Accepted
            ):
                print("✅ Настройки применены")
            self._settings_dialog = None

        except Exception as e:
            print(f"⚠️ Ошибка отображения диалога настроек: {e}")
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть настройки: {e}")

    def _apply_theme_change(self, theme_key: str):
        """Применение изменения темы"""
        try:
            if self.theme_manager and self.theme_manager.apply_theme(theme_key):
                print(f"🎨 Тема изменена на: {theme_key}")
            else:
                print(f"⚠️ Не удалось применить тему: {theme_key}")
        except Exception as e:
            print(f"⚠️ Ошибка применения темы: {e}")

    def _on_new_file(self):
        """Создание нового файла"""
        if MODULES_LOADED and hasattr(self.tab_document, "add_new_tab"):
            self.tab_document.add_new_tab(
                "Новый документ", "# Новый документ\n\nВведите текст здесь..."
            )
        else:
            print("📝 Новый файл создан (fallback режим)")

    def _on_open_file(self):
        """Открытие файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "", "Все файлы (*.*)"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                filename = os.path.basename(file_path)
                if MODULES_LOADED and hasattr(self.tab_document, "add_new_tab"):
                    self.tab_document.add_new_tab(filename, content)
                else:
                    print(f"📂 Файл открыт: {filename} (fallback режим)")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {e}")

    def _on_save_file(self):
        """Сохранение файла"""
        if hasattr(self.tab_document, "get_current_text"):
            content = self.tab_document.get_current_text()
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить файл", "", "Все файлы (*.*)"
            )
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    QMessageBox.information(self, "Успех", "Файл сохранён успешно!")
                except Exception as e:
                    QMessageBox.warning(
                        self, "Ошибка", f"Не удалось сохранить файл: {e}"
                    )

    def _toggle_chat(self):
        """Переключение видимости чата"""
        self.chat_widget.setVisible(not self.chat_widget.isVisible())

    def _toggle_terminal(self):
        """Переключение видимости терминала"""
        self.terminal_widget.setVisible(not self.terminal_widget.isVisible())

    def on_change_theme(self, theme_name):
        """Обработчик смены темы"""
        try:
            print(f"🎨 Запрос смены темы: {theme_name}")

            # Пытаемся применить тему через theme_manager
            if self.theme_manager and hasattr(self.theme_manager, "apply_theme"):
                try:
                    self.theme_manager.apply_theme(theme_name)
                    print(f"✅ Тема '{theme_name}' применена через theme_manager")
                    
                    # Обновляем все компоненты после применения глобальной темы
                    self._apply_theme_to_components()
                    
                    # Обновляем тему в WebView чате если он есть
                    if hasattr(self, 'chat_widget') and hasattr(self.chat_widget, '_apply_theme_to_webview'):
                        self.chat_widget._apply_theme_to_webview()
                        print("✅ Тема обновлена в WebView чате")
                    
                    return
                except Exception as e:
                    print(f"⚠️ Ошибка применения темы через theme_manager: {e}")

            print(f"⚠️ Не удалось применить тему: {theme_name}")

        except Exception as e:
            print(f"⚠️ Ошибка смены темы: {e}")  # Fallback - применяем простую тему
            try:
                # Применяем fallback стили
                self._apply_fallback_styles()
                print("✅ Применена простая fallback тема")
            except Exception as fallback_error:
                print(f"⚠️ Ошибка fallback темы: {fallback_error}")

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        self._update_grips()

    def showEvent(self, event):
        """Событие показа окна"""
        super().showEvent(event)
        # Обновляем иконки меню после показа
        try:
            menu_bar = getattr(self.titlebar_with_menu, "menu_bar", None)
            if menu_bar and hasattr(menu_bar, "refresh_icons"):
                menu_bar.refresh_icons()
        except Exception as e:
            print(f"⚠️ Ошибка обновления иконок: {e}")

    def _apply_theme_to_components(self):
            """Применяет тему ко всем компонентам после смены глобальной темы"""
            try:
                print("🎨 Применяем тему к компонентам...")
                
                # Обновляем основные стили
                self._apply_dynamic_styles()
                
                # Обновляем titlebar если есть
                if hasattr(self, 'titlebar_with_menu'):
                    try:
                        menu_bar = getattr(self.titlebar_with_menu, 'menu_bar', None)
                        if menu_bar and hasattr(menu_bar, 'refresh_colors'):
                            menu_bar.refresh_colors()
                            print("✅ Titlebar обновлен")
                    except Exception as e:
                        print(f"⚠️ Ошибка обновления titlebar: {e}")
                
                # Обновляем file_explorer если есть apply_theme
                if hasattr(self, 'file_explorer'):
                    try:
                        if hasattr(self.file_explorer, 'apply_theme'):
                            self.file_explorer.apply_theme()
                            print("✅ File Explorer обновлен")
                        elif hasattr(self.file_explorer, 'refresh_colors'):
                            self.file_explorer.refresh_colors()
                            print("✅ File Explorer обновлен (refresh_colors)")
                    except Exception as e:
                        print(f"⚠️ Ошибка обновления File Explorer: {e}")
                
                # Обновляем tab_document если есть apply_theme
                if hasattr(self, 'tab_document'):
                    try:
                        if hasattr(self.tab_document, 'apply_theme'):
                            self.tab_document.apply_theme()
                            print("✅ Tab Document обновлен")
                        elif hasattr(self.tab_document, 'refresh_colors'):
                            self.tab_document.refresh_colors()
                            print("✅ Tab Document обновлен (refresh_colors)")
                    except Exception as e:
                        print(f"⚠️ Ошибка обновления Tab Document: {e}")
                
                # Обновляем terminal_widget если есть apply_theme
                if hasattr(self, 'terminal_widget'):
                    try:
                        if hasattr(self.terminal_widget, 'apply_theme'):
                            self.terminal_widget.apply_theme()
                            print("✅ Terminal обновлен")
                        elif hasattr(self.terminal_widget, 'refresh_colors'):
                            self.terminal_widget.refresh_colors()
                            print("✅ Terminal обновлен (refresh_colors)")
                    except Exception as e:
                        print(f"⚠️ Ошибка обновления Terminal: {e}")
                
                # Принудительно обновляем приложение
                QApplication.instance().processEvents()
                print("✅ Все компоненты обновлены")
                
            except Exception as e:
                print(f"⚠️ Ошибка применения темы к компонентам: {e}")

def main():
    """Основная функция запуска приложения"""
    print("🚀 Запуск модульного GopiAI...")

    # Настройка WebEngine для исправления графических проблем
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--disable-gpu --disable-software-rasterizer --disable-3d-apis --disable-accelerated-2d-canvas --no-sandbox"
    )

    # Создание приложения
    app = QApplication(sys.argv)
    app.setApplicationName("GopiAI")
    app.setApplicationVersion("0.3.0")
    app.setOrganizationName("GopiAI Team")

    # Отключение предупреждений Qt
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    try:
        # Создание и показ главного окна
        window = FramelessGopiAIStandaloneWindow()
        window.show()

        print("✅ GopiAI v0.3.0 успешно запущен!")
        print("🎯 Модульная архитектура активна")
        print("📊 Размер основного файла значительно уменьшен")

        # Запуск цикла приложения
        sys.exit(app.exec())
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
