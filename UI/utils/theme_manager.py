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
        padding: 4px;
    }
      QMenu::item {
        padding: 8px 32px 8px 32px;
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
    
    /* Текстовые поля */    QTextEdit, QPlainTextEdit {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #555555;
        padding: 8px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 10pt;
    }
      QLineEdit {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #555555;
        padding: 6px;
    }
    
    QLineEdit:focus {
        border-color: #028795;
    }
    
    /* Кнопки */    QPushButton {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
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
    
    /* Скроллбары */    QScrollBar:vertical {
        background-color: #2b2b2b;
        width: 12px;
    }
      QScrollBar::handle:vertical {
        background-color: #555555;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #666666;
    }
      QScrollBar:horizontal {
        background-color: #2b2b2b;
        height: 12px;
    }
      QScrollBar::handle:horizontal {
        background-color: #555555;
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
        self.themes = {}
        self.apply_theme_func = None
        self.load_theme_func = None
        self.save_theme_func = None
        
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
            print("✅ ThemeManager: реальные темы загружены")
        except ImportError as e:
            print(f"⚠️ ThemeManager: ошибка импорта тем: {e}")

    def apply_theme(self, app=None):
        """Применение текущей темы"""
        from PySide6.QtWidgets import QApplication
        
        if app is None:
            app = QApplication.instance()
            
        if not app or not isinstance(app, QApplication):
            print("⚠️ ThemeManager: QApplication недоступен")
            return False
            
        if self.apply_theme_func:
            try:
                result = self.apply_theme_func(app)
                if result:
                    print("✅ ThemeManager: реальная тема применена")
                    return True
                else:
                    print("⚠️ ThemeManager: apply_theme вернул False")
            except Exception as e:
                print(f"⚠️ ThemeManager: ошибка применения реальной темы: {e}")
        
        # Fallback к простой теме
        print("⚠️ ThemeManager: fallback к простой теме")
        return apply_simple_theme(cast(Optional[QApplication], app) if isinstance(app, QApplication) else None)

    def apply_theme_by_name(self, theme_name, is_dark=True):
        """Применение темы по имени"""
        if not theme_name in self.themes:
            print(f"⚠️ ThemeManager: тема '{theme_name}' недоступна")
            return False
            
        if not (self.save_theme_func and self.apply_theme_func):
            print("⚠️ ThemeManager: функции тем недоступны")
            return False
            
        try:
            theme = self.themes[theme_name]
            # Выбираем тёмный или светлый вариант
            variant = 'dark' if is_dark else 'light'
            theme_colors = theme.get(variant, theme.get('dark', theme.get('light', {})))
            
            if not theme_colors:
                print(f"⚠️ ThemeManager: нет данных для темы '{theme_name}' вариант {variant}")
                return False
                
            # Сохраняем цвета темы
            save_result = self.save_theme_func(theme_colors)
            if not save_result:
                print(f"⚠️ ThemeManager: не удалось сохранить тему '{theme_name}'")
                return False
            
            # Применяем тему
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app and isinstance(app, QApplication):
                apply_result = self.apply_theme_func(app)
                if apply_result:
                    self.current_theme = theme_name
                    print(f"✅ ThemeManager: тема '{theme_name}' ({variant}) применена")
                    return True
                else:
                    print(f"⚠️ ThemeManager: не удалось применить тему '{theme_name}'")
            else:
                print("⚠️ ThemeManager: QApplication недоступен")
        except Exception as e:
            print(f"⚠️ ThemeManager: ошибка применения темы '{theme_name}': {e}")
        
        return False

    def load_current_theme(self):
        """Загрузка текущей сохранённой темы"""
        if self.load_theme_func:
            try:
                return self.load_theme_func()
            except Exception as e:
                print(f"⚠️ ThemeManager: ошибка загрузки темы: {e}")        
                return None

    def get_available_themes(self):
        """Получить список доступных тем"""
        return list(self.themes.keys())
        
    def get_theme_variants(self, theme_name):
        """Получить варианты темы (light/dark)"""
        if theme_name in self.themes:
            theme = self.themes[theme_name]
            variants = []
            if 'light' in theme:
                variants.append('light')
            if 'dark' in theme:
                variants.append('dark')
            return variants
        return []


# Создаём глобальный экземпляр менеджера тем
theme_manager_instance = ThemeManager()


def initialize_theme_system(app=None):
    """Инициализирует и применяет систему тем

    Args:
        app: QApplication инстанс для применения темы. По умолчанию None (будет использован QApplication.instance()).    Returns:
        bool: True если тема была успешно применена, False в противном случае.
    """
    if app is None:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()

    if not app or not isinstance(app, QApplication):
        print("⚠ initialize_theme_system: Не удалось получить экземпляр QApplication")
        return False

    # Инициализируем новый ThemeManager
    try:
        theme_manager = ThemeManager()
        
        # Попробуем применить сохранённую тему
        current_theme = theme_manager.load_current_theme()
        if current_theme:
            print(f"✓ Загружена сохранённая тема: {current_theme.get('name', 'Без названия')}")
            success = theme_manager.apply_theme(app)
            if success:
                return True
        
        # Если сохранённой темы нет, применим Material Sky по умолчанию
        if len(theme_manager.get_available_themes()) > 0:
            default_theme = "Material Sky"
            print(f"✓ Применяем тему по умолчанию: {default_theme}")
            success = theme_manager.apply_theme_by_name(default_theme, is_dark=True)
            if success:
                return True        # Если ничего не получилось, применим простую тему
        print("⚠ Fallback к простой встроенной теме")
        return apply_simple_theme(cast(Optional[QApplication], app) if isinstance(app, QApplication) else None)
        
    except Exception as e:
        print(f"⚠ Ошибка при инициализации системы тем: {e}")
        return apply_simple_theme(cast(Optional[QApplication], app) if isinstance(app, QApplication) else None)
