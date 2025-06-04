#!/usr/bin/env python3
"""
GopiAI Standalone Interface - Модульная версия
=============================================

Основной файл для запуска модульного интерфейса GopiAI.

Автор: Crazy Coder
Версия: 0.3.0 (Модульная)
Дата: 2025-06-03
"""

import sys
import os
import warnings
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QMenuBar, QLabel, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

# Настройка путей для импорта модулей GopiAI
script_dir = os.path.dirname(os.path.abspath(__file__))
gopiai_modules_root = os.path.abspath(script_dir)

module_paths = [
    os.path.join(gopiai_modules_root, "GopiAI-Core"),
    os.path.join(gopiai_modules_root, "GopiAI-Widgets"), 
    os.path.join(gopiai_modules_root, "GopiAI-App"),
    os.path.join(gopiai_modules_root, "GopiAI-Extensions"),
    os.path.join(gopiai_modules_root, "rag_memory_system"),
    gopiai_modules_root,  # Для ui_components
]

for path in module_paths:
    if path not in sys.path:
        sys.path.insert(0, path)

print("📦 Модульная версия GopiAI v0.3.0")
print("Добавленные пути для модулей:")
for p in module_paths:
    print(f"- {p} (существует: {os.path.exists(p)})")

# Импорт модульных компонентов UI
try:
    from ui_components import (
        StandaloneMenuBar,
        StandaloneTitlebar, 
        StandaloneTitlebarWithMenu,
        CustomGrip,
        FileExplorerWidget,
        TabDocumentWidget,
        ChatWidget,
        TerminalWidget,
    )      # Попробуем импортировать дополнительные системы
    try:
        from ui_components import AutoIconSystem
        print("✅ Система иконок AutoIconSystem загружена")
    except ImportError:
        AutoIconSystem = None
        print("⚠️ Система иконок недоступна")
          # Импорт локальной системы тем
    try:
        from ui_components import ThemeManager
        print("✅ Локальная система тем загружена")
    except ImportError:
        ThemeManager = None
        print("⚠️ Локальная система тем недоступна")
        
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
            pass  # Fallback заглушка
    
    class SimpleMenuBar(QMenuBar):
        def refresh_icons(self):
            pass
    
    StandaloneMenuBar = SimpleMenuBar
    StandaloneTitlebar = lambda parent=None: SimpleWidget("Titlebar")
    StandaloneTitlebarWithMenu = lambda parent=None: SimpleWidget("TitlebarWithMenu")
    CustomGrip = lambda parent, direction: QWidget()
    FileExplorerWidget = lambda parent=None, icon_manager=None: SimpleWidget("FileExplorer") 
    TabDocumentWidget = lambda parent=None: SimpleWidget("TabDocument")
    ChatWidget = lambda parent=None: SimpleWidget("Chat")
    TerminalWidget = lambda parent=None: SimpleWidget("Terminal")
    ThemeManager = None
    AutoIconSystem = None

# Импорт системы тем
try:
    from gopiai.core.simple_theme_manager import (
        load_theme, apply_theme, save_theme,
        MATERIAL_SKY_THEME, EMERALD_GARDEN_THEME,
        CRIMSON_RELIC_THEME, GOLDEN_EMBER_THEME
    )
    from gopiai.widgets.managers.theme_manager import ThemeManager as GopiAIThemeManager
    print("✅ Системы тем загружены")
except ImportError as e:
    print(f"⚠️ Системы тем недоступны: {e}")
    # Fallback темы
    MATERIAL_SKY_THEME = {"name": "Material Sky", "primary": "#2196F3"}
    load_theme = lambda: MATERIAL_SKY_THEME
    apply_theme = lambda app: None
    save_theme = lambda theme: None
    GopiAIThemeManager = None


class FramelessGopiAIStandaloneWindow(QMainWindow):
    """Основное frameless окно GopiAI - модульная версия"""
    
    def __init__(self):
        super().__init__()
        print("🚀 Инициализация модульного интерфейса GopiAI...")
        
        # Базовые настройки окна
        self.setWindowTitle("GopiAI v0.3.0 - Модульный ИИ Интерфейс")
        self.setMinimumSize(1000, 700)
        self.resize(1400, 900)
        
        # Frameless окно
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        # Константы
        self.TITLEBAR_HEIGHT = 40
        self.GRIP_SIZE = 10
          # Инициализация
        self._init_theme_system()
        self._setup_ui()
        self._init_grips()
        self._apply_default_styles()
        self._connect_menu_signals()
        
        print("✅ FramelessGopiAIStandaloneWindow готов к работе!")

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
            if hasattr(self.titlebar_with_menu, 'set_window'):
                self.titlebar_with_menu.set_window(self)
        else:
            self.titlebar_with_menu = StandaloneTitlebarWithMenu()
        self.titlebar_with_menu.setFixedHeight(self.TITLEBAR_HEIGHT * 2)
        main_layout.addWidget(self.titlebar_with_menu)
        
        # Основной сплиттер (горизонтальный)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter, 1)        # Левая панель - файловый проводник (модульный)
        self.file_explorer = FileExplorerWidget(icon_manager=self.icon_manager)
        
        # Зафиксировать размер проводника
        from PySide6.QtWidgets import QSizePolicy
        self.file_explorer.setMinimumWidth(250)
        self.file_explorer.setMaximumWidth(400)
        self.file_explorer.resize(300, 600)
        
        # Установить политику размера - фиксированная ширина, растягиваемая высота
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
        self.chat_widget = ChatWidget()
        center_splitter.addWidget(self.chat_widget)
        
        # Нижняя панель - терминал (модульный)
        self.terminal_widget = TerminalWidget()
        right_splitter.addWidget(self.terminal_widget)        # Настройка пропорций сплиттеров
        main_splitter.setSizes([300, 1100])   # Левая панель : Остальное
        center_splitter.setSizes([800, 350])  # Документы : Чат  
        right_splitter.setSizes([700, 200])   # Верх : Терминал
        
        # Разрешаем складывание панелей, но устанавливаем стабильные размеры
        main_splitter.setChildrenCollapsible(True)
        
        # ВАЖНО: Устанавливаем стретч-факторы для предотвращения автоматического изменения размеров
        # Панель проводника (индекс 0) не растягивается, основная область (индекс 1) растягивается
        main_splitter.setStretchFactor(0, 0)  # Проводник не растягивается
        main_splitter.setStretchFactor(1, 1)  # Основная область растягивается
        
        print("✅ Модульный UI настроен")

    def _init_grips(self):
        """Инициализация грипов для изменения размера"""
        self.grips = {}
        directions = ['top', 'bottom', 'left', 'right', 'top-left', 'top-right', 'bottom-left', 'bottom-right']
        
        for direction in directions:
            grip = CustomGrip(self, direction)
            self.grips[direction] = grip
        
        self._update_grips()

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
        self.grips['top'].setGeometry(grip_size, 0, rect.width() - 2*grip_size, grip_size)
        self.grips['bottom'].setGeometry(grip_size, rect.height() - grip_size, rect.width() - 2*grip_size, grip_size)
        self.grips['left'].setGeometry(0, grip_size, grip_size, rect.height() - 2*grip_size)
        self.grips['right'].setGeometry(rect.width() - grip_size, grip_size, grip_size, rect.height() - 2*grip_size)

    def _init_theme_system(self):
        """Инициализация системы тем и иконок"""
        # Инициализация системы тем
        try:
            if GopiAIThemeManager:
                self.theme_manager = GopiAIThemeManager()
                print("✅ Расширенная система тем GopiAI инициализирована")
            elif ThemeManager:
                self.theme_manager = ThemeManager()
                print("✅ Локальная система тем инициализирована")
            else:
                self.theme_manager = None
                print("⚠️ Система тем недоступна - используем встроенные темы")
        except Exception as e:
            print(f"⚠️ Ошибка инициализации тем: {e}")
            self.theme_manager = None
            
        # Инициализация системы иконок
        try:
            if AutoIconSystem:
                self.icon_manager = AutoIconSystem()
                print("✅ Система иконок AutoIconSystem инициализирована")
            else:
                self.icon_manager = None
                print("⚠️ Система иконок недоступна")
        except Exception as e:
            print(f"⚠️ Ошибка инициализации иконок: {e}")
            self.icon_manager = None

    def _apply_default_styles(self):
        """Применение стилей по умолчанию"""
        # Пытаемся применить расширенную систему тем
        try:
            if apply_theme:
                # Загружаем сохранённую тему или тему по умолчанию
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    apply_theme(app)
                    print("✅ Расширенная система тем применена")
                    return
        except Exception as e:
            print(f"⚠️ Ошибка применения расширенной темы: {e}")
        
        # Fallback - применяем простую тему из ui_components
        try:
            if self.theme_manager:
                # Пытаемся применить простую тему
                from ui_components.theme_manager import apply_simple_theme
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                if isinstance(app, QApplication) and apply_simple_theme(app):
                    print("✅ Простая тема применена")
                    return
        except Exception as e:
            print(f"⚠️ Ошибка применения простой темы: {e}")
            
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
            background-color: #2d2d2d;
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
            border-radius: 4px;
        }
        QMenuBar::item:selected {
            background-color: #4CAF50;
        }
        QSplitter::handle {
            background-color: #404040;
        }
        QTabWidget::pane {
            border: 1px solid #404040;
            background-color: #2d2d2d;
        }
        QTabBar::tab {
            background-color: #404040;
            color: #ffffff;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #4CAF50;
        }
        """
        self.setStyleSheet(fallback_style)

    def _connect_menu_signals(self):
        """Подключение сигналов меню"""
        try:
            menu_bar = getattr(self.titlebar_with_menu, 'menu_bar', None)
            if menu_bar and hasattr(menu_bar, 'newFileRequested'):
                # Подключаем сигналы файлового меню
                menu_bar.newFileRequested.connect(self._on_new_file)
                menu_bar.openFileRequested.connect(self._on_open_file)
                menu_bar.saveRequested.connect(self._on_save_file)
                menu_bar.exitRequested.connect(self.close)                # Подключаем сигналы вида
                menu_bar.openChatRequested.connect(self._toggle_chat)
                menu_bar.openTerminalRequested.connect(self._toggle_terminal)
                
                # Подключаем сигнал смены темы
                menu_bar.changeThemeRequested.connect(self._on_change_theme)
                print("✅ Сигналы меню подключены")
        except Exception as e:
            print(f"⚠️ Ошибка подключения сигналов меню: {e}")

    def _on_new_file(self):
        """Создание нового файла"""
        if MODULES_LOADED and hasattr(self.tab_document, 'add_new_tab'):
            self.tab_document.add_new_tab("Новый документ", "# Новый документ\n\nВведите текст здесь...")
        else:
            print("📝 Новый файл создан (fallback режим)")

    def _on_open_file(self):
        """Открытие файла"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Все файлы (*.*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                filename = os.path.basename(file_path)
                if MODULES_LOADED and hasattr(self.tab_document, 'add_new_tab'):
                    self.tab_document.add_new_tab(filename, content)
                else:
                    print(f"📂 Файл открыт: {filename} (fallback режим)")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {e}")

    def _on_save_file(self):
        """Сохранение файла"""
        if hasattr(self.tab_document, 'get_current_text'):
            content = self.tab_document.get_current_text()
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Все файлы (*.*)")
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    QMessageBox.information(self, "Успех", "Файл сохранён успешно!")
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить файл: {e}")

    def _toggle_chat(self):
        """Переключение видимости чата"""
        self.chat_widget.setVisible(not self.chat_widget.isVisible())

    def _toggle_terminal(self):
        """Переключение видимости терминала"""
        self.terminal_widget.setVisible(not self.terminal_widget.isVisible())

    def _on_change_theme(self, theme_name):
        """Обработчик смены темы"""
        try:
            print(f"🎨 Запрос смены темы: {theme_name}")
            
            if theme_name == "dialog":
                # Показываем диалог выбора темы
                from gopiai.core.simple_theme_manager import choose_theme_dialog
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    choose_theme_dialog(app)
                    print("✅ Диалог выбора темы открыт")
                return
            
            # Применяем конкретную тему
            from gopiai.core.simple_theme_manager import (
                MATERIAL_SKY_THEME, EMERALD_GARDEN_THEME,
                CRIMSON_RELIC_THEME, GOLDEN_EMBER_THEME,
                apply_theme
            )
            
            # Загружаем тему по названию
            themes = {
                "Material Sky": MATERIAL_SKY_THEME,
                "Emerald Garden": EMERALD_GARDEN_THEME,
                "Crimson Relic": CRIMSON_RELIC_THEME,
                "Golden Ember": GOLDEN_EMBER_THEME
            }
            
            if theme_name in themes:
                theme = themes[theme_name]
                # Сохраняем выбранную тему для apply_theme()
                from gopiai.core.simple_theme_manager import save_theme
                
                # Извлекаем цвета темы для сохранения
                # Используем тёмный вариант по умолчанию
                theme_colors = theme.get('dark', theme.get('light', {}))
                save_theme(theme_colors)
                  # Применяем тему
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    apply_theme(app)
                    print(f"✅ Тема '{theme_name}' применена")
            else:
                print(f"⚠️ Неизвестная тема: {theme_name}")
                
        except Exception as e:
            print(f"⚠️ Ошибка смены темы: {e}")            # Fallback - применяем простую тему
            try:
                from ui_components.theme_manager import apply_simple_theme
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                if isinstance(app, QApplication):
                    apply_simple_theme(app)
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
            menu_bar = getattr(self.titlebar_with_menu, 'menu_bar', None)
            if menu_bar and hasattr(menu_bar, 'refresh_icons'):
                menu_bar.refresh_icons()
        except Exception as e:
            print(f"⚠️ Ошибка обновления иконок: {e}")


def main():
    """Основная функция запуска приложения"""
    print("🚀 Запуск модульного GopiAI...")
    
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
