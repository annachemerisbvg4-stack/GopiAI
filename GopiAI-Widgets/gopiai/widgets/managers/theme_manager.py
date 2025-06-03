 # Прокси-файл для обеспечения обратной совместимости
# Перенаправляет импорт на новый simple_theme_manager

from gopiai.core.logging import get_logger
logger = get_logger().logger
import os
import sys

from PySide6.QtCore import Signal, QObject

# Удостоверимся, что путь к простому менеджеру тем находится в sys.path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if root_path not in sys.path:
    sys.path.append(root_path)

# Импортируем ThemeManager из simple_theme_manager
try:
    from gopiai.core.simple_theme_manager import load_theme
except ImportError as e:
    logger = get_logger().logger
    logger.error(f"Ошибка импорта ThemeManager: {e}")
    raise

# Настройка логирования
logger = get_logger().logger
logger.info("Используется прокси theme_manager.py для перенаправления на simple_theme_manager")

# Создаем класс-обертку с тем же именем
class ThemeManager(QObject):
    """
    Класс-обертка для обеспечения обратной совместимости.
    Перенаправляет все вызовы на load_theme из simple_theme_manager.
    """
    # Добавляем сигналы в класс
    visualThemeChanged = Signal(str)
    themeChanged = Signal(str)

    def __init__(self, *args, **kwargs):
        logger.info("Создан экземпляр ThemeManager через прокси")
        super().__init__()

    def switch_visual_theme(self, theme_name, force_apply=False):
        # Используем функцию load_theme вместо класса
        try:
            load_theme()
            self.visualThemeChanged.emit(theme_name)
            self.themeChanged.emit(theme_name)
            return True
        except Exception as e:
            logger.error(f"Ошибка смены темы: {e}")
            return False

    def get_color(self, color_key, default_value="#000000"):
        """Получить цвет из темы по ключу."""
        try:
            theme_data = load_theme()
            # Если theme_data это словарь цветов, ищем ключ
            if isinstance(theme_data, dict):
                return theme_data.get(color_key, default_value)
            else:
                logger.warning(f"Неожиданный формат данных темы: {type(theme_data)}")
                return default_value
        except Exception as e:
            logger.error(f"Ошибка получения цвета {color_key}: {e}")
            return default_value

    @staticmethod
    def instance():
        """Singleton-паттерн для совместимости."""
        if not hasattr(ThemeManager, '_instance'):
            ThemeManager._instance = ThemeManager()
        return ThemeManager._instance

    def get_current_visual_theme(self):
        """Получить текущую визуальную тему."""
        return "default"  # Упрощенная реализация
