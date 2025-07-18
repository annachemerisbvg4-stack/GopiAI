#!/usr/bin/env python3
"""
GopiAI Standalone Interface - Модульная версия с централизованной системой тем
=====================================================================

Основной файл для запуска модульного интерфейса GopiAI.
Использует централизованную систему управления темами через ThemeManager.

Автор: Crazy Coder
Версия: 0.3.2 (Модульная с централизованной системой тем)
Дата: 2025-06-03
"""

import sys
import os
import warnings
from pathlib import Path
from datetime import datetime

# Исправляем конфликт OpenMP библиотек
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Собственная функция для загрузки переменных окружения из .env файла
def load_env_file():
    try:
        # Список возможных путей для поиска .env файла
        possible_paths = [
            Path('.') / '.env',                                  # Текущая директория
            Path('..') / '.env',                                # Родительская директория
            Path('..') / '..' / '.env',                         # Родительская директория родительской директории
            Path('..') / '..' / '..' / '.env',                  # Корень проекта (если запуск из gopiai/ui)
            Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))) / '.env'  # Абсолютный путь к корню проекта
        ]
        
        # Добавляем путь к корню проекта GOPI_AI_MODULES
        root_path = Path('C:/Users/crazy/GOPI_AI_MODULES/.env')
        if root_path not in possible_paths:
            possible_paths.append(root_path)
        
        # Ищем .env файл в возможных местах
        env_loaded = False
        for env_path in possible_paths:
            if env_path.exists():
                print(f"Загрузка .env файла из {env_path}...")
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            try:
                                key, value = line.split('=', 1)
                                os.environ[key.strip()] = value.strip().strip('"\'')
                            except ValueError:
                                # Пропускаем строки, которые не соответствуют формату key=value
                                continue
                print(f"[OK] .env файл загружен из {env_path}")
                env_loaded = True
                break
        
        if not env_loaded:
            print("[ИНФО] .env файл не найден в известных местах, продолжаем без него")
            
    except Exception as e:
        print(f"[ПРЕДУПРЕЖДЕНИЕ] Ошибка при загрузке .env файла: {e}")

# Загружаем переменные окружения из .env файла
load_env_file()

# Настройка WebEngine для предотвращения графических ошибок


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
    QDockWidget,
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

print("Модульная версия GopiAI v0.3.2 с централизованной системой тем")
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
        ChatWidget,
        TerminalWidget,
    )

    print("[OK] Все основные модули UI загружены успешно")
    
    # Инициализация системы памяти GopiAI
    try:
        from gopiai.ui.memory import get_memory_manager
        memory_manager = get_memory_manager()
        print("[MEMORY] Инициализирован MemoryManager")
        
        # Простой тест работы памяти
        try:
            test_session = "test_session_" + str(hash('test'))
            test_msg = "Тестовая запись от " + str(datetime.now())
            memory_manager.add_message(
                session_id=test_session,
                role="system",
                content=test_msg
            )
            print("[MEMORY] Тестовая запись успешно добавлена")
        except Exception as test_err:
            print(f"[WARNING] Предупреждение при тестировании памяти: {test_err}")
            
    except Exception as e:
        print(f"[ERROR] Ошибка при инициализации памяти: {e}")
        print("[WARNING] Приложение продолжит работу с ограниченной функциональностью памяти")
    
    MODULES_LOADED = True

except ImportError as e:
    print(f"[WARNING] Ошибка импорта UI модулей: {e}")
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
            
            # Create dummy signals for file explorer compatibility
            from PySide6.QtCore import Signal
            self.file_double_clicked = Signal(str)
            self.file_selected = Signal(str)

        def add_new_tab(self, title, content):
            print(f"Fallback: add_new_tab({title})")

        def add_notebook_tab(self, title, content, menu_bar=None):
            print(f"Fallback: add_notebook_tab({title})")

        def get_current_text(self):
            return "Fallback content"

        def set_window(self, window):
            pass

        def add_browser_tab(self, url="about:blank", title="Браузер"):
            print(f"Fallback: add_browser_tab({url}, {title}) - Browser not available")

        def open_file_in_tab(self, file_path):
            print(f"Fallback: open_file_in_tab({file_path})")

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

    class GlobalFallbackThemeManager:
        def __init__(self):
            self.current_theme = "default"
        
        def apply_theme(self, app_or_theme):
            print(f"Fallback: apply_theme({app_or_theme})")
            return False
        


    if 'ThemeManager' not in globals() or ThemeManager is None:
        ThemeManager = GlobalFallbackThemeManager

# Глобальные переменные для систем
AutoIconSystem = None
ThemeManagerClass = None
GopiAIThemeManager = None
apply_theme = None
load_theme = None
save_theme = None
MATERIAL_SKY_THEME = {"name": "Material Sky", "primary": "#2196F3"}
EXTENSIONS_AVAILABLE = True


class FallbackThemeManager:
    """Fallback менеджер тем для случаев, когда основной ThemeManager недоступен"""
    def __init__(self):
        self.current_theme = "default"
    
    def apply_theme(self, app_or_theme):
        print(f"Fallback: apply_theme({app_or_theme})")
        return False


class FramelessGopiAIStandaloneWindow(QMainWindow):
    """Основное frameless окно GopiAI с модульной системой тем"""



    def __init__(self):
        super().__init__()
        print("[LAUNCH] Инициализация модульного интерфейса GopiAI с централизованной системой тем...")

        # Базовые настройки окна
        self.setWindowTitle("GopiAI v0.3.2 - Модульный ИИ Интерфейс")
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
        self._setup_ui()
        self._init_grips()
        self._connect_menu_signals()
        self._apply_vscode_like_layout()
        self._setup_panel_shortcuts()
        
        # Initialize AI Assistant
        self._init_ai_assistant()


        print("[OK] FramelessGopiAIStandaloneWindow готов к работе!")


    def _setup_ui(self):
        """Настройка модульного пользовательского интерфейса"""
        print("[SETUP] Настройка UI из модулей...")

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

        # --- Новый layout: горизонтальный сплиттер (проводник | центральная область | чат) ---
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter, 1)

        # Левая панель - файловый проводник (модульный)
        self.file_explorer = FileExplorerWidget(icon_manager=self.icon_manager)
        self.file_explorer.setMinimumWidth(0)
        self.file_explorer.setMaximumWidth(600)
        self.file_explorer.resize(300, 600)
        size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.file_explorer.setSizePolicy(size_policy)
        main_splitter.addWidget(self.file_explorer)

        # Центральная область: вертикальный сплиттер (TabDocumentWidget | терминал)
        center_vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(center_vertical_splitter)

        # Центральная область - система вкладок (модульная)
        self.tab_document = TabDocumentWidget()
        self.tab_document.setMinimumWidth(500)
        center_vertical_splitter.addWidget(self.tab_document)

        # Нижняя панель — терминал под TabDocumentWidget
        self.terminal_widget = TerminalWidget()
        self.terminal_widget.setMinimumHeight(150)
        self.terminal_widget.setMaximumHeight(400)
        terminal_size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.terminal_widget.setSizePolicy(terminal_size_policy)
        center_vertical_splitter.addWidget(self.terminal_widget)

        # Правая панель - табы с чатом и MCP панелью
        self.right_tabs = QTabWidget()
        self.right_tabs.setTabPosition(QTabWidget.TabPosition.South)  # Вкладки внизу
        self.right_tabs.setMinimumWidth(0)
        self.right_tabs.setMaximumWidth(800)  # Увеличено для лучшего отображения инструментов
        right_tabs_size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.right_tabs.setSizePolicy(right_tabs_size_policy)

        # Вкладка чата с ИИ (модульный)
        self.chat_widget = ChatWidget()
        print("[CHAT] ChatWidget создан успешно")
        if hasattr(self, 'theme_manager'):
            print("[CHAT] Передаем theme_manager в ChatWidget...")
            self.chat_widget.set_theme_manager(self.theme_manager)
            print("[CHAT] theme_manager передан успешно")

        # Вкладка MCP панели (новый компонент)
        try:
            from gopiai.ui.components.smithery_mcp_panel import SmitheryMcpPanel
            self.smithery_mcp_panel = SmitheryMcpPanel()
            print("[MCP] SmitheryMcpPanel создан успешно")
        except Exception as e:
            print(f"[ERROR] Ошибка создания SmitheryMcpPanel: {e}")
            self.smithery_mcp_panel = QWidget()
            error_layout = QVBoxLayout(self.smithery_mcp_panel)
            error_layout.addWidget(QLabel(f"Ошибка загрузки MCP панели:\n{str(e)}"))

        # Добавляем вкладки
        self.right_tabs.addTab(self.chat_widget, "Чат")
        self.right_tabs.addTab(self.smithery_mcp_panel, "MCP Tools")
        
        main_splitter.addWidget(self.right_tabs)

        # Настройка пропорций сплиттеров
        main_splitter.setSizes([200, 800, 350])  # Проводник | центр | чат/MCP
        center_vertical_splitter.setSizes([700, 200])  # TabDocumentWidget | терминал
        main_splitter.setCollapsible(0, True)   # Проводник можно схлопнуть
        main_splitter.setCollapsible(1, False)  # Центр нельзя схлопнуть
        main_splitter.setCollapsible(2, True)   # Чат можно схлопнуть
        center_vertical_splitter.setChildrenCollapsible(True)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 10)
        main_splitter.setStretchFactor(2, 0)
        center_vertical_splitter.setStretchFactor(0, 1)
        center_vertical_splitter.setStretchFactor(1, 0)

        self._configure_splitter_behavior()
        self._setup_splitter_constraints()  # Добавляем этот вызов
        print("[OK] Модульный UI настроен с ограничениями размеров панелей")

    def _configure_splitter_behavior(self):
        """Дополнительная настройка поведения сплиттеров с ограничениями"""
        try:
            main_splitter = self.findChild(QSplitter)
            if main_splitter:
                main_splitter.setHandleWidth(5)  # Увеличиваем ширину handle для лучшего захвата
                
                # Минимальные размеры и collapsible теперь задаются в _setup_ui
                pass
                
            print("[OK] Поведение сплиттеров настроено с ограничениями")
            
        except Exception as e:
            print(f"[WARNING] Ошибка настройки сплиттеров: {e}")
    
    def _setup_splitter_constraints(self):
        """Настройка дополнительных ограничений для сплиттеров"""
        try:
            # Находим все сплиттеры и настраиваем их
            splitters = self.findChildren(QSplitter)
            
            for splitter in splitters:
                # Увеличиваем размер handle для лучшего захвата
                splitter.setHandleWidth(6)
                
                # Подключаем сигнал для контроля перемещения
                splitter.splitterMoved.connect(self._on_splitter_moved)
            
            print("[OK] Дополнительные ограничения сплиттеров установлены")
            
        except Exception as e:
            print(f"[WARNING] Ошибка настройки ограничений сплиттеров: {e}")
    
    def _on_splitter_moved(self, pos, index):
        """Обработчик перемещения сплиттера для контроля границ"""
        try:
            splitter = self.sender()
            if not isinstance(splitter, QSplitter):
                return
            
            sizes = splitter.sizes()
            total_size = sum(sizes)
            
            # Минимальные размеры в процентах от общего размера
            min_percent = 0.05  # 5% минимум для каждой панели
            min_size = int(total_size * min_percent)
            
            # Проверяем и корректируем размеры
            adjusted = False
            for i, size in enumerate(sizes):
                if size < min_size:
                    sizes[i] = min_size
                    adjusted = True
            
            # Если были корректировки, применяем их
            if adjusted:
                # Пересчитываем размеры пропорционально
                current_total = sum(sizes)
                if current_total != total_size:
                    ratio = total_size / current_total
                    sizes = [int(size * ratio) for size in sizes]
                
                splitter.setSizes(sizes)
        
        except Exception as e:
            print(f"[WARNING] Ошибка контроля перемещения сплиттера: {e}")
    
    def _reset_panel_sizes(self):
        """Сброс размеров панелей к значениям по умолчанию"""
        try:
            main_splitter = self.findChild(QSplitter)
            if main_splitter:
                # Устанавливаем размеры по умолчанию
                main_splitter.setSizes([300, 1100])
                
                right_splitter = main_splitter.widget(1)
                if isinstance(right_splitter, QSplitter):
                    right_splitter.setSizes([900, 100])  # Чат высокий, терминал низкий по умолчанию
                    
                    center_splitter = right_splitter.widget(0)
                    if isinstance(center_splitter, QSplitter):
                        center_splitter.setSizes([700, 350])
            
            print("[OK] Размеры панелей сброшены к значениям по умолчанию")
            
        except Exception as e:
            print(f"[WARNING] Ошибка сброса размеров панелей: {e}")

    def _apply_vscode_like_layout(self):
        """Применить макет в стиле VSCode с динамическими цветами"""
        try:
            print("[OK] Применен макет в стиле VSCode с динамическими цветами")
        except Exception as e:
            print(f"[WARNING] Ошибка применения макета VSCode: {e}")

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
            
            # Ctrl+Shift+R - сброс размеров панелей
            reset_panels = QShortcut(QKeySequence("Ctrl+Shift+R"), self)
            reset_panels.activated.connect(self._reset_panel_sizes)
            
            print("[OK] Горячие клавиши для панелей настроены (включая сброс размеров)")
            
        except Exception as e:
            print(f"[WARNING] Ошибка настройки горячих клавиш: {e}")

        # Подключаем сигналы файлового проводника
        self._connect_file_explorer_signals()
        
        print("[OK] Модульный UI настроен")

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
            print("[OK] Система иконок SimpleIconManager инициализирована")
        except ImportError:
            self.icon_manager = None
            print("[WARNING] Система иконок недоступна")
        except Exception as e:
            print(f"[WARNING] Ошибка инициализации иконок: {e}")
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
            print(f"[WARNING] Ошибка инициализации менеджера тем: {e}")
            # Используем предварительно определенный LocalFallbackThemeManager в случае ошибки
            self.theme_manager = LocalFallbackThemeManager() # Создаем экземпляр

    def _apply_default_styles(self):
        """Применение стилей по умолчанию"""
        # Пытаемся применить систему тем через theme_manager
        try:
            if self.theme_manager and hasattr(self.theme_manager, "apply_theme"):
                from PySide6.QtWidgets import QApplication

                app = QApplication.instance()
                print(f"[DEBUG] main.py: QApplication.instance() = {app}")
                if app:
                    print(f"[DEBUG] main.py: Вызываем self.theme_manager.apply_theme({app})")
                    result = self.theme_manager.apply_theme(app)
                    print(f"[DEBUG] main.py: Результат apply_theme = {result}")
                    if result:
                        print("[OK] Система тем применена через theme_manager")
                        
                        return
                    else:
                        print("[WARNING] apply_theme вернул False")
                else:
                    print("[WARNING] QApplication.instance() вернул None")
        except Exception as e:
            print(f"[WARNING] Ошибка применения темы через theme_manager: {e}")
            import traceback

            traceback.print_exc()

        # Если все попытки применения темы не удались, оставляем стандартные системные стили
        print("[WARNING] Используется системная тема по умолчанию")



    def _init_ai_assistant(self):
        """Initialize the AI Assistant functionality in the main chat widget."""
        try:
            # AI Assistant functionality is now integrated into the main chat widget
            if hasattr(self, 'chat_widget') and hasattr(self.chat_widget, 'ui_assistant'):
                # Set the main window reference for the UI Assistant
                self.chat_widget.ui_assistant.set_main_window(self)
                print("[OK] AI Assistant инициализирован в основном чате")
            else:
                print("[WARNING] Основной виджет чата не найден или не содержит UI Assistant")
                
        except Exception as e:
            print(f"[ERROR] Ошибка инициализации AI Assistant: {e}")
    
    def _connect_menu_signals(self):
        """Подключение сигналов меню"""
        try:
            menu_bar = getattr(self.titlebar_with_menu, "menu_bar", None)
            if not menu_bar:
                print("[WARNING] Меню недоступно")
                return

            # Подключаем новые сигналы для создания документов
            if hasattr(menu_bar, "newCodeEditorRequested"):
                menu_bar.newCodeEditorRequested.connect(self._on_new_code_editor)
            if hasattr(menu_bar, "newNotebookRequested"):
                menu_bar.newNotebookRequested.connect(self._on_new_notebook)

            # Подключаем новые сигналы
            if hasattr(menu_bar, "openSettingsRequested"):
                menu_bar.openSettingsRequested.connect(self._open_settings)
                if self.icon_manager is not None:
                    self.icon_manager.get_icon("settings")
                print("[OK] Сигнал openSettingsRequested подключен")

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

            print("[OK] Сигналы меню подключены успешно")
        except Exception as e:
            print(f"[WARNING] Ошибка подключения сигналов меню: {e}")

    def _on_new_code_editor(self):
        """Создание новой вкладки редактора кода"""
        if MODULES_LOADED and hasattr(self.tab_document, "add_new_tab"):
            self.tab_document.add_new_tab("Новый код", "# Новый код\n\n")
        else:
            print("📝 Новый редактор кода создан (fallback режим)")

    def _on_new_notebook(self):
        """Создание новой вкладки-блокнота с форматированием"""
        if MODULES_LOADED and hasattr(self.tab_document, "add_notebook_tab"):
            menu_bar = getattr(self.titlebar_with_menu, "menu_bar", None)
            self.tab_document.add_notebook_tab("Новый блокнот", "<h2>Новая заметка</h2><p>Введите текст...</p>", menu_bar=menu_bar)
        else:
            # Fallback: создаём простую вкладку с QLabel или QTextEdit
            if hasattr(self.tab_document, "add_new_tab"):
                self.tab_document.add_new_tab("Новый блокнот (fallback)", "<h2>Новая заметка (fallback)</h2><p>Введите текст...</p>")
            else:
                print("📝 Новый блокнот не может быть создан: нет метода add_new_tab (fallback режим)")
            print("📝 Новый блокнот создан (fallback режим)")

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
                
                
                self._settings_dialog.themeChanged.connect(self.on_change_theme)
    
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
                with open(file_path, "rb") as f:
                    raw = f.read()
                encoding = chardet.detect(raw)["encoding"] or "utf-8"
                content = raw.decode(encoding, errors="replace")
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
                    


                    return
                except Exception as e:
                    print(f"[WARNING] Ошибка применения темы через theme_manager: {e}")

            print(f"⚠️ Не удалось применить тему: {theme_name}")

        except Exception as e:
            print(f"⚠️ Ошибка смены темы: {e}")

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
            print(f"[WARNING] Ошибка обновления иконок: {e}")

    def _apply_theme_to_components(self):
            """Применяет тему ко всем компонентам после смены глобальной темы"""
            try:
                print("🎨 Применяем тему к компонентам...")
                
                # Обновляем основные стили
                        
                # Обновляем titlebar если есть
                if hasattr(self, 'titlebar_with_menu'):
                    try:
                        menu_bar = getattr(self.titlebar_with_menu, 'menu_bar', None)
                        if menu_bar and hasattr(menu_bar, 'refresh_colors'):
                            menu_bar.refresh_colors()
                            print("✅ Titlebar обновлен")
                    except Exception as e:
                        print(f"⚠️ Ошибка обновления titlebar: {e}")
                
                
                
                print("[OK] Все компоненты обновлены")
                
            except Exception as e:
                print(f"[WARNING] Ошибка применения темы к компонентам: {e}")

    def _connect_file_explorer_signals(self):
        """Подключение сигналов файлового проводника"""
        try:
            # Подключаем двойной клик для открытия файлов
            if hasattr(self.file_explorer, 'file_double_clicked'):
                self.file_explorer.file_double_clicked.connect(self._open_file_in_editor)  # type: ignore
                print("[OK] Сигнал file_double_clicked подключен")
            
            # Подключаем одинарный клик для выбора файлов
            if hasattr(self.file_explorer, 'file_selected'):
                self.file_explorer.file_selected.connect(self._on_file_selected)  # type: ignore
                print("[OK] Сигнал file_selected подключен")
                
            print("[OK] Сигналы файлового проводника подключены")
            
        except Exception as e:
            print(f"[WARNING] Ошибка подключения сигналов файлового проводника: {e}")

    def _open_file_in_editor(self, file_path):
        """Открытие файла в редакторе по двойному клику"""
        try:
            print(f"📂 Открываем файл: {file_path}")
            
            # Проверяем, что это действительно файл
            import os
            if not os.path.isfile(file_path):
                print(f"⚠️ Это не файл: {file_path}")
                return
                
            # Открываем файл в новой вкладке
            if MODULES_LOADED and hasattr(self.tab_document, 'open_file_in_tab'):
                self.tab_document.open_file_in_tab(file_path)
            elif MODULES_LOADED and hasattr(self.tab_document, 'add_new_tab'):
                # Fallback - используем add_new_tab
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    filename = os.path.basename(file_path)
                    self.tab_document.add_new_tab(filename, content)
                    print(f"✅ Файл открыт (fallback): {filename}")
                except Exception as e:
                    print(f"❌ Ошибка открытия файла: {e}")
            else:
                # Полный fallback для случая, когда модули не загружены
                print(f"⚠️ Модули не загружены, открываем файл в системном редакторе: {file_path}")
                try:
                    import subprocess
                    import platform
                    if platform.system() == "Windows":
                        os.startfile(file_path)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", file_path])
                    else:  # Linux
                        subprocess.run(["xdg-open", file_path])
                    print(f"✅ Файл открыт в системном редакторе: {file_path}")
                except Exception as e:
                    print(f"❌ Не удалось открыть файл в системном редакторе: {e}")
                    
        except Exception as e:
            print(f"❌ Ошибка при открытии файла в редакторе: {e}")

    def _on_file_selected(self, file_path):
        """Обработка выбора файла в проводнике"""
        try:
            print(f"📄 Выбран файл: {file_path}")
            # Здесь можно добавить дополнительную логику при выборе файла
            # например, показать информацию о файле в статусной строке
        except Exception as e:
            print(f"[WARNING] Ошибка обработки выбора файла: {e}")


def main():
    """Основная функция запуска приложения"""
    print("[LAUNCH] Запуск модульного GopiAI...")

    

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

        print("[SUCCESS] GopiAI v0.3.0 успешно запущен!")
        print("[INFO] Модульная архитектура активна")
        print("[INFO] Размер основного файла значительно уменьшен")

        # Запуск цикла приложения
        sys.exit(app.exec())
    except Exception as e:
        print(f"[CRITICAL ERROR] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()



