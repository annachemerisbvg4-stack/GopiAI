"""
Реализация streamable HTTP клиента для MCP.
Эмулирует функциональность официального клиента mcp.client.streamable_http.
"""

import json
import httpx
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union, Tuple, AsyncGenerator

from ..types import JSONRPCRequest, JSONRPCResponse, JSONRPCNotification

logger = logging.getLogger(__name__)


class MessageStreamReader:
    """Класс для чтения сообщений из потока."""
    
    def __init__(self, response_data: Dict[str, Any] = None):
        """Инициализирует объект для чтения сообщений."""
        self.response_data = response_data or {}
        
    async def receive(self) -> Any:
        """Получает сообщение из потока."""
        try:
            # Эмулируем ответ в формате, который ожидает клиент
            id_value = self.response_data.get("id", "unknown")
            result = self.response_data.get("result", {})
            
            response = JSONRPCResponse(id=id_value, result=result)
            
            return type("MessageContainer", (), {
                "message": response,
                "metadata": {}
            })
        except Exception as e:
            logger.error(f"Ошибка при получении сообщения: {e}")
            raise


class MessageStreamWriter:
    """Класс для отправки сообщений в поток."""
    
    def __init__(self, url: str, headers: Dict[str, str], response_callback=None):
        """Инициализирует объект для отправки сообщений."""
        self.url = url
        self.headers = headers
        self.response_callback = response_callback
    
    async def send(self, message: Dict[str, Any]) -> None:
        """Отправляет сообщение в поток."""
        try:
            # В реальном клиенте здесь был бы запрос к серверу
            # Но в mock-версии мы просто логируем сообщение
            request_message = message.get("message", {})
            logger.debug(f"Отправлено сообщение на {self.url}: {request_message}")
            
            # Если это запрос list_resources, возвращаем стандартный ответ
            if isinstance(request_message, JSONRPCRequest) and request_message.method == "mcp/resources/list":
                # Эмулируем запрос к API с инструментами
                self.response_callback({
                    "id": request_message.id,
                    "result": {
                        "resources": [
                            {
                                "id": "mcp0_brave_web_search",
                                "name": "brave_web_search",
                                "description": "Поиск в интернете с помощью Brave Search API"
                            },
                            {
                                "id": "mcp0_brave_local_search",
                                "name": "brave_local_search",
                                "description": "Поиск местных компаний и мест с помощью Brave Search API"
                            },
                            {
                                "id": "mcp1_playwright_navigate",
                                "name": "playwright_navigate",
                                "description": "Перейти по URL в браузере Playwright"
                            },
                            {
                                "id": "mcp1_playwright_get_visible_html",
                                "name": "playwright_get_visible_html",
                                "description": "Получить видимый HTML-контент текущей страницы"
                            }
                        ]
                    }
                })
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")
            raise


def streamablehttp_client(url: str, headers: Dict[str, str] = None, timeout: int = 30) -> Any:
    """
    Создает контекстный менеджер для работы со streamable HTTP клиентом.
    
    Args:
        url: URL сервера MCP.
        headers: Заголовки HTTP запроса.
        timeout: Таймаут запроса в секундах.
        
    Returns:
        Асинхронный контекстный менеджер для работы с потоками чтения и записи.
    """
    headers = headers or {}
    response_data = {}
    
    def update_response(data):
        """Обновляет данные ответа."""
        nonlocal response_data
        response_data.update(data)
    
    @asynccontextmanager
    async def client_context() -> AsyncGenerator[Tuple[MessageStreamReader, MessageStreamWriter, Any], None]:
        """Контекстный менеджер для работы с клиентом."""
        reader = MessageStreamReader(response_data)
        writer = MessageStreamWriter(url, headers, update_response)
        
        try:
            # В реальном клиенте здесь был бы запрос к серверу
            logger.debug(f"Открывается соединение к {url}")
            yield reader, writer, None
        finally:
            # Закрываем соединение
            logger.debug(f"Закрывается соединение к {url}")
    
    return client_context
