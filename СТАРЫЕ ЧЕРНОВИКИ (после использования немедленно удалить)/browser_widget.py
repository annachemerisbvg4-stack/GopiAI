"""
Модуль для создания и управления веб-браузером внутри приложения.
"""

import logging
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

logger = logging.getLogger(__name__)


def get_browser_widget(parent=None):
    """
    Создает виджет веб-браузера.

    Args:
        parent: Родительский виджет

    Returns:
        QWebEngineView: Виджет веб-браузера
    """
    try:
        web_view = QWebEngineView(parent)
        web_view.setUrl(QUrl("about:blank"))
        logger.info("Веб-браузер успешно создан")
        return web_view
    except Exception as e:
        logger.error(f"Ошибка при создании веб-браузера: {str(e)}")
        # Возвращаем заглушку в случае ошибки
        from PySide6.QtWidgets import QLabel

        return QLabel("Браузер недоступен: " + str(e), parent)
