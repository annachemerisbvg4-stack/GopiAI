# --- START OF FILE chat_browser_handler.py ---

import logging
import re
from typing import Optional
from PySide6.QtCore import QObject, QUrl
from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)

class ChatBrowserHandler(QObject):
    """
    Handles all browser-related commands originating from the chat.
    Finds the browser widget and executes actions like navigation, search, etc.
    """
    def __init__(self, parent_widget: QWidget):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget

    def handle_command(self, command: str) -> str:
        """
        Public method to process a browser command. It finds the browser
        and executes the requested action.
        """
        logger.info(f"🌐 [BROWSER HANDLER] Received command: '{command}'")
        
        browser_components = self._get_browser_components()
        if not browser_components:
            logger.warning("Browser widget not found. Cannot execute command.")
            return "❌ Не удалось найти активную вкладку браузера."

        return self._execute_browser_action(browser_components, command)

    def _get_browser_components(self) -> dict | None:
        """Finds the active browser tab and its components within the main window."""
        try:
            # Ищем родительский виджет, который содержит Tab-ы
            main_window = self.parent_widget.window()
            if not main_window or not hasattr(main_window, 'tab_document'):
                logger.warning("Main window or 'tab_document' not found.")
                return None
            
            tab_widget = main_window.tab_document.tab_widget
            current_widget = tab_widget.currentWidget()

            if not current_widget or not hasattr(current_widget, 'property'):
                logger.warning("No active widget or it does not support properties.")
                return None
            
            # Проверяем, является ли текущая вкладка браузером
            web_view = current_widget.property('_web_view')
            if web_view:
                logger.info("✅ Active browser tab found.")
                return {
                    'web_view': web_view,
                    'address_bar': current_widget.property('_address_bar'),
                    'widget': current_widget
                }
            
            logger.warning("Active tab is not a browser widget.")
            return None
        except Exception as e:
            logger.error(f"❌ Error getting browser components: {e}", exc_info=True)
            return None

    def _execute_browser_action(self, components: dict, command: str) -> str:
        """Executes a specific action based on the parsed command."""
        web_view = components['web_view']
        address_bar = components['address_bar']
        command_lower = command.lower()

        try:
            # Навигация
            if any(word in command_lower for word in ['открой', 'перейди', 'зайди']):
                url = self._extract_url_from_command(command)
                if url:
                    if address_bar: address_bar.setText(url)
                    web_view.load(QUrl(url))
                    return f"Перехожу по адресу: {url}"
                return "❌ Не удалось извлечь URL из команды."

            # Поиск
            elif 'google' in command_lower or 'поиск' in command_lower or 'найди' in command_lower:
                query = self._extract_search_query(command)
                url = f"https://www.google.com/search?q={query}"
                if address_bar: address_bar.setText(url)
                web_view.load(QUrl(url))
                return f"Ищу в Google: '{query}'"

            # Другие команды
            elif 'назад' in command_lower:
                web_view.back()
                return "Перехожу назад."
            elif 'вперед' in command_lower:
                web_view.forward()
                return "Перехожу вперед."
            elif 'обнови' in command_lower:
                web_view.reload()
                return "Страница обновлена."

            else:
                return f"Неизвестная команда для браузера: '{command}'"
        except Exception as e:
            logger.error(f"❌ Error executing browser action: {e}", exc_info=True)
            return f"Ошибка при выполнении команды: {e}"

    def _extract_url_from_command(self, command: str) -> Optional[str]:
        """Extracts a URL from a command string."""
        match = re.search(r'https?://[^\s/$.?#].[^\s]*', command, re.IGNORECASE)
        if match:
            return match.group(0)
        # Простой поиск доменных имен
        match = re.search(r'([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}', command, re.IGNORECASE)
        if match:
            return "https://" + match.group(0)
        return None

    def _extract_search_query(self, command: str) -> str:
        """Extracts the search query from a command string."""
        # Удаляем ключевые слова, оставляя только суть запроса
        keywords = ['google', 'поиск', 'найди', 'в']
        query = command
        for keyword in keywords:
            query = re.sub(r'\b' + re.escape(keyword) + r'\b', '', query, flags=re.IGNORECASE)
        return query.strip()

# --- КОНЕЦ ФАЙЛА chat_browser_handler.py ---