"""
Menu Bar Component для GopiAI Standalone Interface
============================================

Автономное меню с полным набором команд и сигналов.
"""

from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from pathlib import Path

# Импорт системы иконок
try:
    from .icon_file_system_model import UniversalIconManager as AutoIconSystem
except ImportError:
    AutoIconSystem = None


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
    openChatRequested = Signal()
    openBrowserRequested = Signal()
    openTerminalRequested = Signal()
    
    # Сигналы расширений
    toggleProductivityExtension = Signal()
    toggleVoiceExtension = Signal()
    toggleAiToolsExtension = Signal()
    
    # Сигналы настроек
    openSettingsRequested = Signal()
    changeThemeRequested = Signal(str)  # Передаем название темы

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Инициализируем систему иконок
        self._setup_icon_system()
        
        # Создаём меню
        self._build_menu()

    def _setup_icon_system(self):
        """Настройка системы иконок"""
        if AutoIconSystem:
            self.icon_system = AutoIconSystem()
        else:
            # Fallback - простой менеджер иконок
            self.icon_system = self._create_simple_icon_manager()

    def _create_simple_icon_manager(self):
        """Создание простого менеджера иконок как fallback"""
        class SimpleIconManager:
            def __init__(self):
                self.icons_path = Path(__file__).parent.parent / "assets" / "icons" / "lucide"
                self._icon_cache = {}
                
            def get_icon(self, icon_name: str):
                """Получить иконку по имени"""
                if icon_name in self._icon_cache:
                    return self._icon_cache[icon_name]
                
                svg_path = self.icons_path / f"{icon_name}.svg"
                print(f"🔍 Ищем иконку: {svg_path}")
                if svg_path.exists():
                    icon = QIcon(str(svg_path))
                    self._icon_cache[icon_name] = icon
                    print(f"✅ Иконка загружена: {icon_name}")
                    return icon
                else:
                    print(f"❌ Иконка не найдена: {svg_path}")
                
                return QIcon()  # Пустая иконка
            
            def get_icon_for_action_name(self, action_name: str):
                """Получить иконку по имени действия"""
                # Простое преобразование имени действия в имя иконки
                icon_name = action_name.replace('_action', '')
                return self.get_icon(icon_name)
                
        return SimpleIconManager()

    def _build_menu(self):
        """Создание структуры меню"""
        # Файловое меню
        file_menu = self.addMenu("Файл")
        self._setup_file_menu(file_menu)
        
        # Меню правки
        edit_menu = self.addMenu("Правка")
        self._setup_edit_menu(edit_menu)
        
        # Меню вида
        view_menu = self.addMenu("Вид")
        self._setup_view_menu(view_menu)
        
        # Меню настроек
        settings_menu = self.addMenu("Настройки")
        self._setup_settings_menu(settings_menu)
        
        # Сохраняем ссылки на меню для установки иконок
        self.file_menu = file_menu
        self.edit_menu = edit_menu
        self.view_menu = view_menu
        self.settings_menu = settings_menu
        
        # Обновляем иконки меню
        self._update_menu_icons()
        self._update_menu_bar_icons()

    def _setup_file_menu(self, file_menu):
        """Настройка файлового меню"""
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

    def _setup_edit_menu(self, edit_menu):
        """Настройка меню правки"""
        self.undo_action = edit_menu.addAction("Отмена")
        self.redo_action = edit_menu.addAction("Повтор")
        edit_menu.addSeparator()
        self.cut_action = edit_menu.addAction("Вырезать")
        self.copy_action = edit_menu.addAction("Копировать")
        self.paste_action = edit_menu.addAction("Вставить")
        self.delete_action = edit_menu.addAction("Удалить")
        edit_menu.addSeparator()
        self.select_all_action = edit_menu.addAction("Выделить всё")

    def _setup_view_menu(self, view_menu):
        """Настройка меню вида (без файлового проводника)"""
        # Основные панели (без проводника)
        self.chat_action = view_menu.addAction("ИИ чат")
        self.browser_action = view_menu.addAction("Браузер")
        self.terminal_action = view_menu.addAction("Терминал")
        self.text_editor_action = view_menu.addAction("Редактор")

        view_menu.addSeparator()

        # Подменю расширений
        extensions_menu = view_menu.addMenu("Расширения")
        self.extensions_menu = extensions_menu  # Сохраняем для установки иконки

        self.productivity_action = extensions_menu.addAction("Инструменты продуктивности")
        self.voice_action = extensions_menu.addAction("Голосовое управление")
        self.ai_tools_action = extensions_menu.addAction("ИИ инструменты")

        # Делаем действия расширений checkable
        self.productivity_action.setCheckable(True)
        self.voice_action.setCheckable(True)
        self.ai_tools_action.setCheckable(True)

        # По умолчанию продуктивность включена
        self.productivity_action.setChecked(True)

        # Подключение сигналов вида
        self.chat_action.triggered.connect(self.openChatRequested.emit)
        self.browser_action.triggered.connect(self.openBrowserRequested.emit)
        self.terminal_action.triggered.connect(self.openTerminalRequested.emit)
        self.text_editor_action.triggered.connect(self._on_text_editor_toggle)

    def _on_text_editor_toggle(self):
        """Обработчик для показа/скрытия всех вкладок редактора или сообщения об их отсутствии"""
        # Поиск главного окна с tab_document
        main_window = self.parent()
        while main_window is not None and not hasattr(main_window, 'tab_document'):
            main_window = main_window.parent() if hasattr(main_window, 'parent') else None
        def show_frameless_message(parent, title, text):
            from PySide6.QtWidgets import QMessageBox
            from PySide6.QtCore import Qt
            box = QMessageBox(parent)
            box.setWindowTitle(title)
            box.setText(text)
            # Используем WindowType для PySide6
            flags = box.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
            box.setWindowFlags(flags)
            box.exec()

        if main_window is not None and hasattr(main_window, 'tab_document'):
            tab_document = getattr(main_window, 'tab_document', None)
            tab_widget = getattr(tab_document, 'tab_widget', None) if tab_document else None
            if tab_widget and tab_widget.count() > 0:
                # Скрыть/показать все вкладки
                visible = any(tab_widget.isTabVisible(i) if hasattr(tab_widget, 'isTabVisible') else tab_widget.widget(i).isVisible() for i in range(tab_widget.count()))
                for i in range(tab_widget.count()):
                    widget = tab_widget.widget(i)
                    widget.setVisible(not visible)
            else:
                show_frameless_message(self, "Нет открытых вкладок", "Нет активных вкладок редактора. Воспользуйтесь меню 'Файл' для создания нового документа.")
        else:
            show_frameless_message(self, "Нет редактора", "Редактор не найден в главном окне.")

        # Подключение сигналов расширений
        self.productivity_action.triggered.connect(self.toggleProductivityExtension.emit)
        self.voice_action.triggered.connect(self.toggleVoiceExtension.emit)
        self.ai_tools_action.triggered.connect(self.toggleAiToolsExtension.emit)

    def _setup_settings_menu(self, settings_menu):
        """Настройка меню настроек"""
        # Основные настройки
        self.settings_action = settings_menu.addAction("Настройки приложения")
        self.settings_action.triggered.connect(self.openSettingsRequested.emit)

    def _update_menu_icons(self):
        """Обновление иконок в меню"""
        # Маппинг действий к иконкам
        icon_mapping = {
            # Файловое меню
            'new_action': 'file-plus',
            'open_action': 'folder-open',
            'open_folder_action': 'folder-open',
            'save_action': 'save',
            'save_as_action': 'save-all',
            'exit_action': 'x',
            
            # Меню правки
            'undo_action': 'undo',
            'redo_action': 'redo',
            'cut_action': 'scissors',
            'copy_action': 'copy',
            'paste_action': 'clipboard',
            'delete_action': 'trash-2',
            'select_all_action': 'text-select',
            
            # Меню вида
            'chat_action': 'message-circle',
            'browser_action': 'globe',
            'terminal_action': 'terminal',
            'text_editor_action': 'file-text',
            
            # Меню настроек
            'settings_action': 'settings',
            'change_theme_action': 'palette',
            
            # Расширения
            'productivity_action': 'briefcase',
            'voice_action': 'mic',
            'ai_tools_action': 'cpu',
        }

        # Применяем иконки к действиям
        for action_name, icon_name in icon_mapping.items():
            if hasattr(self, action_name):
                action = getattr(self, action_name)
                
                try:
                    # Получаем иконку методом get_icon
                    if hasattr(self.icon_system, 'get_icon'):
                        icon = self.icon_system.get_icon(icon_name)
                    else:
                        print(f"⚠️ Неизвестный тип icon_system: {type(self.icon_system)}")
                        continue
                        
                    if not icon.isNull():
                        action.setIcon(icon)
                except Exception as e:
                    print(f"⚠️ Ошибка получения иконки для {action_name}: {e}")

    def _update_menu_bar_icons(self):
        """Обновление иконок для самих пунктов меню (File, Edit, View, Settings)"""
        try:
            # Иконки для главных меню
            menu_icons = {
                'file_menu': 'folder',
                'edit_menu': 'pencil',
                'view_menu': 'eye',
                'settings_menu': 'settings',
            }
            
            for menu_name, icon_name in menu_icons.items():
                if hasattr(self, menu_name):
                    menu = getattr(self, menu_name)
                    if hasattr(self.icon_system, 'get_icon'):
                        icon = self.icon_system.get_icon(icon_name)
                        if not icon.isNull():
                            menu.setIcon(icon)
            
            # Иконка для подменю расширений
            if hasattr(self, 'extensions_menu') and hasattr(self.icon_system, 'get_icon'):
                extensions_icon = self.icon_system.get_icon('puzzle')
                if not extensions_icon.isNull():
                    self.extensions_menu.setIcon(extensions_icon)
                    
        except Exception as e:
            print(f"⚠️ Ошибка установки иконок меню: {e}")

    def refresh_icons(self):
        """Принудительное обновление всех иконок в меню"""
        self._update_menu_icons()
        self._update_menu_bar_icons()
        print("🔄 Иконки меню обновлены")