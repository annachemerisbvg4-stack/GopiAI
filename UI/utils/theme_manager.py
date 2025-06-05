"""
GopiAI Theme Manager - Система управления темами
===============================================

Модульная система тем для GopiAI интерфейса.
Поддерживает несколько встроенных тем и загрузку пользовательских.

Автор: Crazy Coder
Версия: 1.0.0
"""

from PySide6.QtWidgets import QApplication
from typing import Optional, cast


def apply_simple_theme(app: Optional[QApplication] = None):
    """Применить простую современную тему"""
    if app is None:
        app = cast(Optional[QApplication], QApplication.instance())
        if not isinstance(app, QApplication):
            return False

    if app is None:
        return False

    simple_theme = """
    /* Главное окно */
    QMainWindow {
        background-color: #2b2b2b;
        color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
    }
    
    /* Меню */
    QMenuBar {
        background-color: #3c3c3c;
        color: #ffffff;
        border: none;
        padding: 4px;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 6px 12px;
        border-radius: 4px;
        margin: 2px;
    }
    
    QMenuBar::item:selected {
        background-color: #028795;
    }
    
    QMenuBar::item:pressed {
        background-color: #028795;
    }
    
    QMenu {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 6px;
        padding: 4px;
    }
    
    QMenu::item {
        padding: 8px 32px 8px 32px;
        border-radius: 4px;
        margin: 1px;
    }
    
    QMenu::item:selected {
        background-color: #028795;
    }
    
    QMenu::icon {
        padding-left: 8px;
        width: 16px;
        height: 16px;
    }
    
    /* Панели и разделители */
    QSplitter::handle {
        background-color: #555555;
        width: 2px;
        height: 2px;
    }
    
    QSplitter::handle:hover {
        background-color: #028795;
    }
    
    /* Дока и панели */
    QDockWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        titlebar-close-icon: none;
        titlebar-normal-icon: none;
    }
    
    QDockWidget::title {
        background-color: #3c3c3c;
        padding: 8px;
        text-align: center;
        border-bottom: 1px solid #555555;
    }
    
    /* Виджеты */
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        selection-background-color: #028795;
    }
    
    /* Текстовые поля */
    QTextEdit, QPlainTextEdit {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 8px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 10pt;
    }
    
    QLineEdit {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 6px;
    }
    
    QLineEdit:focus {
        border-color: #028795;
    }
    
    /* Кнопки */
    QPushButton {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #4a4a4a;
        border-color: #028795;
    }
    
    QPushButton:pressed {
        background-color: #028795;
    }
    
    /* Скроллбары */
    QScrollBar:vertical {
        background-color: #2b2b2b;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #555555;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #666666;
    }
    
    QScrollBar:horizontal {
        background-color: #2b2b2b;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #555555;
        border-radius: 6px;
        min-width: 20px;
    }
    
    /* Табы */
    QTabWidget::pane {
        border: 1px solid #555555;
        background-color: #2b2b2b;
    }
    
    QTabBar::tab {
        background-color: #404040;
        color: #ffffff;
        padding: 8px 16px;
        margin: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }
    
    QTabBar::tab:selected {
        background-color: #028795;
    }
    
    QTabBar::tab:hover {
        background-color: #4a4a4a;
    }
    """

    try:
        app.setStyleSheet(simple_theme)
        print("✓ Простая тема применена")
        return True
    except Exception as e:
        print(f"⚠ Ошибка применения темы: {e}")
        return False


# Попытка импорта расширенной системы тем GopiAI
import sys
import os
from pathlib import Path

# Определяем пути к нужным модулям
# Используем абсолютные пути для большей надёжности
project_root = Path(__file__).parent.parent.parent.absolute()  # Поднимаемся на уровень выше (из UI в корень)
core_path = project_root / "GopiAI-Core"
widgets_path = project_root / "GopiAI-Widgets"

# Проверяем наличие файлов
theme_manager_path = core_path / "gopiai" / "core" / "simple_theme_manager.py"
widget_theme_path = widgets_path / "gopiai" / "widgets" / "managers" / "theme_manager.py"

# Добавляем пути к sys.path для корректных импортов
if str(core_path) not in sys.path:
    sys.path.insert(0, str(core_path))

if str(widgets_path) not in sys.path:
    sys.path.insert(0, str(widgets_path))

# Отладочная информация только для разработки
# print(f"Путь к теме: {theme_manager_path}, существует: {theme_manager_path.exists()}")
# print(f"Путь к виджетам тем: {widget_theme_path}, существует: {widget_theme_path.exists()}")


# Сначала объявим заглушки на случай, если импорт не получится
def load_theme(*args, **kwargs):
    return None


def apply_theme(*args, **kwargs):
    return False


def save_theme(*args, **kwargs):
    return False


# Заглушки для тем
MATERIAL_SKY_THEME = {"name": "Material Sky"}
EMERALD_GARDEN_THEME = {"name": "Emerald Garden"}
CRIMSON_RELIC_THEME = {"name": "Crimson Relic"}
GOLDEN_EMBER_THEME = {"name": "Golden Ember"}


# Реальный ThemeManager с поддержкой тем
class ThemeManager:
    def __init__(self):
        self.current_theme = None
        # Импортируем темы из simple_theme_manager
        try:
            from .simple_theme_manager import (
                MATERIAL_SKY_THEME, EMERALD_GARDEN_THEME,
                CRIMSON_RELIC_THEME, GOLDEN_EMBER_THEME,
                apply_theme, load_theme, save_theme
            )
            self.themes = {
                "Material Sky": MATERIAL_SKY_THEME,
                "Emerald Garden": EMERALD_GARDEN_THEME,
                "Crimson Relic": CRIMSON_RELIC_THEME,
                "Golden Ember": GOLDEN_EMBER_THEME
            }
            self.apply_theme_func = apply_theme
            self.load_theme_func = load_theme
            self.save_theme_func = save_theme
            print("✅ ThemeManager инициализирован с реальными темами")
        except ImportError as e:
            print(f"⚠️ Ошибка импорта тем: {e}")
            self.themes = {}
            self.apply_theme_func = None
            self.load_theme_func = None
            self.save_theme_func = None

    def apply_theme(self, app):
        """Применение текущей темы"""
        if self.apply_theme_func:
            try:
                self.apply_theme_func(app)
                print("✅ Реальная тема применена через ThemeManager")
                return True
            except Exception as e:
                print(f"⚠️ Ошибка применения реальной темы: {e}")
        
        # Fallback
        print("⚠️ Fallback к простой теме")
        return apply_simple_theme(app)

    def apply_theme_by_name(self, theme_name):
        """Применение темы по имени"""
        if theme_name in self.themes and self.save_theme_func and self.apply_theme_func:
            try:
                theme = self.themes[theme_name]
                # Используем тёмный вариант по умолчанию
                theme_colors = theme.get('dark', theme.get('light', {}))
                self.save_theme_func(theme_colors)
                
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    self.apply_theme_func(app)
                    self.current_theme = theme_name
                    print(f"✅ Тема '{theme_name}' применена")
                    return True
            except Exception as e:
                print(f"⚠️ Ошибка применения темы '{theme_name}': {e}")
        
        print(f"⚠️ Тема '{theme_name}' недоступна")
        return False

    def load_theme(self, theme_name):
        """Загрузка темы"""
        if self.load_theme_func:
            return self.load_theme_func()
        print(f"⚠️ Используется заглушка ThemeManager.load_theme: {theme_name}")
        return None

    def get_available_themes(self):
        """Получить список доступных тем"""
        return list(self.themes.keys())


THEMES_AVAILABLE = False

# Проверяем файлы и пытаемся импортировать
if theme_manager_path.exists():
    try:
        # Используем специальный импорт для загрузки модуля вручную
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "simple_theme_manager", str(theme_manager_path)
        )

        if spec and spec.loader:
            theme_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(theme_module)

            # Извлекаем нужные функции и константы из модуля
            load_theme = theme_module.load_theme
            apply_theme = theme_module.apply_theme
            save_theme = theme_module.save_theme
            MATERIAL_SKY_THEME = theme_module.MATERIAL_SKY_THEME
            EMERALD_GARDEN_THEME = theme_module.EMERALD_GARDEN_THEME
            CRIMSON_RELIC_THEME = theme_module.CRIMSON_RELIC_THEME
            GOLDEN_EMBER_THEME = theme_module.GOLDEN_EMBER_THEME

            THEMES_AVAILABLE = True
            print(f"✓ Расширенная система тем GopiAI загружена из {theme_manager_path}")

            # Пробуем импортировать ThemeManager если файл существует
            if widget_theme_path.exists():
                try:
                    widget_spec = importlib.util.spec_from_file_location(
                        "widget_theme_manager", str(widget_theme_path)
                    )

                    if widget_spec and widget_spec.loader:
                        widget_theme_module = importlib.util.module_from_spec(widget_spec)
                        widget_spec.loader.exec_module(widget_theme_module)

                        # Переопределяем класс ThemeManager
                        WidgetThemeManager = widget_theme_module.ThemeManager
                        ThemeManager = WidgetThemeManager  # Переименовываем для совместимости
                        print(f"✓ ThemeManager загружен из {widget_theme_path}")
                    else:
                        print(f"⚠ Не удалось создать спецификацию для ThemeManager")
                except Exception as e:
                    print(f"⚠ ThemeManager недоступен, используется заглушка: {e}")
        else:
            print(f"⚠ Не удалось создать спецификацию для simple_theme_manager")
    except Exception as e:
        THEMES_AVAILABLE = False
        print(f"⚠ Расширенная система тем недоступна: {e}")
        print(f"⚠ sys.path: {sys.path}")

else:
    # print(f"⚠ Файл {theme_manager_path} не существует")  # Отладка отключена
    THEMES_AVAILABLE = False

    # Заглушки функций для поддержки совместимости
    def load_theme(*args, **kwargs):
        print("⚠ Используется заглушка load_theme")
        return None

    def apply_theme(*args, **kwargs):
        print("⚠ Используется заглушка apply_theme")
        return False

    def save_theme(*args, **kwargs):
        print("⚠ Используется заглушка save_theme")
        return False


def initialize_theme_system(app=None):
    """Инициализирует и применяет систему тем

    Args:
        app: QApplication инстанс для применения темы. По умолчанию None (будет использован QApplication.instance()).

    Returns:
        bool: True если тема была успешно применена, False в противном случае.
    """
    if app is None:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()

    if not app:
        print("⚠ Не удалось получить экземпляр QApplication")
        return False

    if THEMES_AVAILABLE:
        try:
            theme_manager = ThemeManager()
            current_theme = load_theme()

            if current_theme:
                print(f"✓ Загружена тема: {current_theme.get('name', 'Без названия')}")
                success = apply_theme(current_theme, app)
                if success:
                    print(f"✓ Применена тема: {current_theme.get('name', 'Без названия')}")
                    return True
                else:
                    print(f"⚠ Не удалось применить тему, использую простую тему")
                    return apply_simple_theme(cast(QApplication, app))
            else:
                print(f"⚠ Не удалось загрузить тему, использую Material Sky")
                return apply_theme(MATERIAL_SKY_THEME, app)
        except Exception as e:
            print(f"⚠ Ошибка при инициализации системы тем: {e}")
            return apply_simple_theme(cast(QApplication, app))
    else:
        print("⚠ Расширенная система тем недоступна, использую простую тему")
        return apply_simple_theme(cast(QApplication, app))
