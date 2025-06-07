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

# Импорт компонентов тем
from gopiai.ui.utils.theme_manager import ThemeManager
from gopiai.ui.dialogs.settings_dialog import GopiAISettingsDialog

# Настройка путей для импорта модулей GopiAI
script_dir = os.path.dirname(os.path.abspath(__file__))
# Поднимаемся на 3 уровня: ui -> gopiai -> GopiAI-UI -> корень проекта
gopiai_modules_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))

module_paths = [
    os.path.join(gopiai_modules_root, "GopiAI-Core"),
    os.path.join(gopiai_modules_root, "GopiAI-Widgets"), 
    os.path.join(gopiai_modules_root, "GopiAI-App"),
    os.path.join(gopiai_modules_root, "GopiAI-Extensions"),
    os.path.join(gopiai_modules_root, "rag_memory_system"),
    gopiai_modules_root,  # Для корневых модулей
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

# Глобальные переменные для систем
AutoIconSystem = None
ThemeManagerClass = None  # Переименовано чтобы избежать конфликта с импортом
GopiAIThemeManager = None
apply_theme = None
load_theme = None
save_theme = None
MATERIAL_SKY_THEME = {"name": "Material Sky", "primary": "#2196F3"}


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
        # Импорт системы иконок
        try:
            import qtawesome as qta
            class SimpleIconManager:
                def __init__(self):
                    self.qta = qta
                def get_icon(self, name):
                    return self.qta.icon('fa.' + name)
            
            self.icon_manager = SimpleIconManager()
            print("✅ Система иконок SimpleIconManager инициализирована")
        except ImportError:
            self.icon_manager = None
            print("⚠️ Система иконок недоступна")
        except Exception as e:
            print(f"⚠️ Ошибка инициализации иконок: {e}")
            self.icon_manager = None
              # Инициализация системы тем
        try:
            self.theme_manager = ThemeManager()
            if self.theme_manager:
                print("✅ Менеджер тем инициализирован")
                # Применяем тему по умолчанию - используем конкретную тему вместо "simple",
                # чтобы избежать появления диалога выбора темы при запуске
                self.theme_manager.apply_theme("Material Sky")
            else:
                print("⚠️ Не удалось создать менеджер тем")
        except Exception as e:
            print(f"⚠️ Ошибка инициализации менеджера тем: {e}")
            self.theme_manager = None

    def _apply_default_styles(self):
        """Применение стилей по умолчанию"""        # Пытаемся применить систему тем через theme_manager
        try:
            if self.theme_manager and hasattr(self.theme_manager, 'apply_theme'):
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                print(f"🔍 main.py: QApplication.instance() = {app}")
                if app:
                    print(f"🔍 main.py: Вызываем self.theme_manager.apply_theme({app})")
                    result = self.theme_manager.apply_theme(app)
                    print(f"🔍 main.py: Результат apply_theme = {result}")
                    if result:
                        print("✅ Система тем применена через theme_manager")
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
        }        """
        self.setStyleSheet(fallback_style)
        
    def _connect_menu_signals(self):
        """Подключение сигналов меню"""
        try:
            menu_bar = getattr(self.titlebar_with_menu, 'menu_bar', None)
            if not menu_bar:
                print("⚠️ Меню недоступно")
                return
            
            # Подключаем новые сигналы
            if hasattr(menu_bar, 'openSettingsRequested'):
                menu_bar.openSettingsRequested.connect(self._open_settings)
                print("✅ Сигнал openSettingsRequested подключен")
            
            if hasattr(menu_bar, 'changeThemeRequested'):
                menu_bar.changeThemeRequested.connect(self.on_change_theme)
                print("✅ Сигнал changeThemeRequested подключен")
                
            # Подключаем остальные сигналы файлового меню
            if hasattr(menu_bar, 'newFileRequested'):
                menu_bar.newFileRequested.connect(self._on_new_file)
            if hasattr(menu_bar, 'openFileRequested'):
                menu_bar.openFileRequested.connect(self._on_open_file)
            if hasattr(menu_bar, 'saveRequested'):
                menu_bar.saveRequested.connect(self._on_save_file)
            if hasattr(menu_bar, 'exitRequested'):
                menu_bar.exitRequested.connect(self.close)
                
            # Подключаем сигналы меню вида
            if hasattr(menu_bar, 'openChatRequested'):
                menu_bar.openChatRequested.connect(self._toggle_chat)
            if hasattr(menu_bar, 'openTerminalRequested'):
                menu_bar.openTerminalRequested.connect(self._toggle_terminal)
            
            print("✅ Сигналы меню подключены успешно")
        except Exception as e:
            print(f"⚠️ Ошибка подключения сигналов меню: {e}")

    def _open_settings(self):
        """Открыть диалог настроек"""
        try:
            # Удаляем вызов старого диалога настроек
            from gopiai.ui.dialogs.settings_dialog import GopiAISettingsDialog
            settings_dialog = GopiAISettingsDialog(self.theme_manager, self)
            
            # Подключаем сигналы диалога настроек
            if hasattr(settings_dialog, 'themeChanged'):
                settings_dialog.themeChanged.connect(self.on_change_theme)
            if hasattr(settings_dialog, 'settings_applied'):
                settings_dialog.settings_applied.connect(self._on_settings_changed)
            
            # Показываем диалог
            result = settings_dialog.exec()
            if result == settings_dialog.DialogCode.Accepted:
                print("✅ Настройки применены")
            else:
                print("⚠️ Настройки отменены")
                
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
            if 'font_size' in settings_dict:
                font_size = settings_dict['font_size']
                font = self.font()
                font.setPointSize(font_size)
                self.setFont(font)
                print(f"✅ Размер шрифта изменен на {font_size}")
            
            # Применяем изменения темы и тёмного режима
            # Примечание: переключатель тёмного режима уже обработан в settings_dialog.py
            # и применён к theme_manager._current_variant
            if 'theme' in settings_dict:
                # Используем имя темы напрямую, а не маппинг, так как теперь
                # настройка темного режима обрабатывается отдельно
                theme_name = settings_dict['theme']
                self.on_change_theme(theme_name)
            
            # Показать/скрыть панели
            if 'show_panels' in settings_dict:
                panels = settings_dict['show_panels']
                if 'file_explorer' in panels:
                    self.file_explorer.setVisible(panels['file_explorer'])
                if 'terminal' in panels:
                    self.terminal_widget.setVisible(panels['terminal'])
                if 'chat' in panels:
                    self.chat_widget.setVisible(panels['chat'])
                print("✅ Видимость панелей обновлена")            # Применяем настройки расширений
            if 'extensions' in settings_dict:
                extensions = settings_dict['extensions']
                print(f"🔌 Настройки расширений: {extensions}")
                # Здесь можно добавить логику включения/отключения расширений                
        except Exception as e:
            print(f"⚠️ Ошибка применения настроек: {e}")

    def _show_settings(self):
        """Показать диалог настроек"""
        try:
            settings_dialog = GopiAISettingsDialog(self.theme_manager, self)
              # Подключаем сигнал для применения настроек
            settings_dialog.settings_applied.connect(self._on_settings_changed)
            
            # Показываем диалог
            if settings_dialog.exec() == settings_dialog.DialogCode.Accepted:
                print("✅ Настройки применены")
                
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

    def on_change_theme(self, theme_name):
        """Обработчик смены темы"""
        try:
            print(f"🎨 Запрос смены темы: {theme_name}")
            
            # Пытаемся применить тему через theme_manager            
            if self.theme_manager and hasattr(self.theme_manager, 'apply_theme'):
                try:
                    self.theme_manager.apply_theme(theme_name)
                    print(f"✅ Тема '{theme_name}' применена через theme_manager")
                    return
                except Exception as e:
                    print(f"⚠️ Ошибка применения темы через theme_manager: {e}")
            
            print(f"⚠️ Не удалось применить тему: {theme_name}")
                
        except Exception as e:
            print(f"⚠️ Ошибка смены темы: {e}")        # Fallback - применяем простую тему
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



