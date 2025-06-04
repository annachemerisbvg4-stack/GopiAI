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
    from .icon_system import AutoIconSystem
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
    openProjectExplorerRequested = Signal()
    openChatRequested = Signal()
    openBrowserRequested = Signal()
    openTerminalRequested = Signal()
    
    # Сигналы расширений
    toggleProductivityExtension = Signal()
    toggleVoiceExtension = Signal()
    toggleAiToolsExtension = Signal()
      # Сигналы темы
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
                self.icons_path = Path(__file__).parent.parent / "node_modules" / "lucide-static" / "icons"
                self._icon_cache = {}
                
            def get_icon(self, icon_name: str):
                """Получить иконку по имени"""
                if icon_name in self._icon_cache:
                    return self._icon_cache[icon_name]
                
                svg_path = self.icons_path / f"{icon_name}.svg"
                if svg_path.exists():
                    icon = QIcon(str(svg_path))
                    self._icon_cache[icon_name] = icon
                    return icon
                
                return QIcon()  # Пустая иконка
                
        return SimpleIconManager()

    def _build_menu(self):
        """Создание структуры меню"""
        # Файловое меню
        file_menu = self.addMenu("📁 Файл")
        self._setup_file_menu(file_menu)
        
        # Меню правки
        edit_menu = self.addMenu("✏️ Правка")
        self._setup_edit_menu(edit_menu)
        
        # Меню вида
        view_menu = self.addMenu("👁️ Вид")
        self._setup_view_menu(view_menu)
        
        # Обновляем иконки меню
        self._update_menu_icons()

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
        """Настройка меню вида"""        # Основные панели
        self.project_explorer_action = view_menu.addAction("Файловый проводник")
        self.chat_action = view_menu.addAction("ИИ чат")
        self.browser_action = view_menu.addAction("Браузер")
        self.terminal_action = view_menu.addAction("Терминал")
        self.text_editor_action = view_menu.addAction("Редактор")
        
        view_menu.addSeparator()
        
        # Подменю расширений
        extensions_menu = view_menu.addMenu("🔌 Расширения")
        self.productivity_action = extensions_menu.addAction("📝 Инструменты продуктивности")
        self.voice_action = extensions_menu.addAction("🎤 Голосовое управление")
        self.ai_tools_action = extensions_menu.addAction("🤖 ИИ инструменты")
          # Подменю настроек темы
        view_menu.addSeparator()
        theme_menu = view_menu.addMenu("🎨 Тема")
        
        # Отдельные действия для каждой темы
        material_sky_action = theme_menu.addAction("🌊 Material Sky")
        emerald_garden_action = theme_menu.addAction("🌿 Emerald Garden")
        crimson_relic_action = theme_menu.addAction("🔥 Crimson Relic")
        golden_ember_action = theme_menu.addAction("⭐ Golden Ember")
        
        theme_menu.addSeparator()
        change_theme_action = theme_menu.addAction("🎨 Настроить тему...")
        
        # Подключение сигналов тем
        material_sky_action.triggered.connect(lambda: self.changeThemeRequested.emit("Material Sky"))
        emerald_garden_action.triggered.connect(lambda: self.changeThemeRequested.emit("Emerald Garden"))
        crimson_relic_action.triggered.connect(lambda: self.changeThemeRequested.emit("Crimson Relic"))
        golden_ember_action.triggered.connect(lambda: self.changeThemeRequested.emit("Golden Ember"))
        change_theme_action.triggered.connect(lambda: self.changeThemeRequested.emit("dialog"))
        
        # Делаем действия расширений checkable
        self.productivity_action.setCheckable(True)
        self.voice_action.setCheckable(True)
        self.ai_tools_action.setCheckable(True)
        
        # По умолчанию продуктивность включена
        self.productivity_action.setChecked(True)
          # Подключение сигналов вида
        self.project_explorer_action.triggered.connect(self.openProjectExplorerRequested.emit)
        self.chat_action.triggered.connect(self.openChatRequested.emit)
        self.browser_action.triggered.connect(self.openBrowserRequested.emit)
        self.terminal_action.triggered.connect(self.openTerminalRequested.emit)
        self.text_editor_action.triggered.connect(self.openTextEditorRequested.emit)
        
        # Подключение сигналов расширений
        self.productivity_action.triggered.connect(self.toggleProductivityExtension.emit)
        self.voice_action.triggered.connect(self.toggleVoiceExtension.emit)
        self.ai_tools_action.triggered.connect(self.toggleAiToolsExtension.emit)

    def _update_menu_icons(self):
        """Обновление иконок в меню"""
        # Маппинг действий к иконкам
        icon_mapping = {
            # Файловое меню
            'new_action': 'file-plus',
            'open_action': 'file-open',
            'open_folder_action': 'folder-open',
            'save_action': 'save',
            'save_as_action': 'save-as',
            'exit_action': 'x',            # Меню правки
            'undo_action': 'undo',
            'redo_action': 'redo',
            'cut_action': 'scissors',
            'copy_action': 'copy',
            'paste_action': 'clipboard',
            'delete_action': 'trash-2',
            'select_all_action': 'text-select',
            
            # Меню вида
            'project_explorer_action': 'folder-open',
            'chat_action': 'message-circle',
            'browser_action': 'globe',
            'terminal_action': 'terminal',
            'text_editor_action': 'file-text',
        }        # Применяем иконки
        for action_name, icon_name in icon_mapping.items():
            if hasattr(self, action_name):
                action = getattr(self, action_name)
                
                # Проверяем тип icon_system и используем соответствующий метод
                try:
                    if hasattr(self.icon_system, 'get_icon_for_action_name'):
                        # AutoIconSystem
                        icon = self.icon_system.get_icon_for_action_name(action_name)
                    elif hasattr(self.icon_system, 'get_icon'):
                        # SimpleIconManager
                        icon = self.icon_system.get_icon(icon_name)
                    else:
                        print(f"⚠️ Неизвестный тип icon_system: {type(self.icon_system)}")
                        continue
                        
                    if not icon.isNull():
                        action.setIcon(icon)
                except Exception as e:
                    print(f"⚠️ Ошибка получения иконки для {action_name}: {e}")

    def refresh_icons(self):
        """Принудительное обновление всех иконок в меню"""
        self._update_menu_icons()
        print("🔄 Иконки меню обновлены")
