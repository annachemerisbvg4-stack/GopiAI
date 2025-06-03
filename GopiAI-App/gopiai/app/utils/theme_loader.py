import json
from gopiai.core.logging import get_logger
logger = get_logger().logger
import os

logger = get_logger().logger

def apply_theme_from_json(qapp, theme_path):
    """
    Применяет тему из JSON-файла к приложению.

    Args:
        qapp: Экземпляр QApplication
        theme_path: Путь к JSON-файлу с темой

    Returns:
        bool: True в случае успеха, False в случае ошибки
    """
    if not os.path.exists(theme_path):
        logger.error(f"Файл темы не найден: {theme_path}")
        return False

    try:
        with open(theme_path, 'r', encoding='utf-8') as f:
            theme = json.load(f)

        # Генерируем QSS
        qss = f"""
        QWidget {{
            background-color: {theme['main_color']};
            color: {theme['text_color']};
            font-family: Segoe UI, Inter, Arial, sans-serif;
        }}
        QMainWindow, QDialog, QFrame {{
            background-color: {theme['main_color']};
            border: none;
        }}
        QMenuBar {{
            background-color: {theme['header_color']};
            color: {theme['titlebar_text']};
            font-weight: bold;
            border: none;
        }}
        QPushButton {{
            background-color: {theme['button_color']};
            color: {theme['text_color']};
            border-radius: 10px;
            padding: 8px 18px;
            font-weight: bold;
            border: 1px solid {theme['border_color']};
        }}
        QPushButton:hover {{
            background: {theme['button_hover_color']};
            color: {theme['accent_color']};
        }}
        QPushButton:pressed {{
            background: {theme['button_active_color']};
            color: {theme['accent_color']};
        }}
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background: {theme['header_color']};
            color: {theme['text_color']};
            border-radius: 8px;
            border: 1px solid {theme['border_color']};
            padding: 6px;
        }}
        QListWidget, QTreeWidget {{
            background: {theme['main_color']};
            color: {theme['text_color']};
            border-radius: 8px;
            border: 1px solid {theme['border_color']};
        }}
        QTabWidget::pane {{
            background: {theme['main_color']};
            border: none;
            border-radius: 12px;
        }}
        QTabBar::tab {{
            background: {theme['button_color']};
            color: {theme['text_color']};
            border-radius: 12px 12px 0 0;
            padding: 6px 18px;
            margin: 1px;
        }}
        QTabBar::tab:selected, QTabBar::tab:hover {{
            background: {theme['button_hover_color']};
            color: {theme['accent_color']};
        }}
        QScrollBar:vertical, QScrollBar:horizontal {{
            background: {theme['header_color']};
            border-radius: 8px;
            width: 10px;
        }}
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
            background: {theme['accent_color']};
            border-radius: 8px;
        }}
        """

        qapp.setStyleSheet(qss)
        logger.info(f"Тема успешно применена из файла: {theme_path}")
        return True

    except Exception as e:
        logger.error(f"Ошибка при применении темы: {e}")
        return False
