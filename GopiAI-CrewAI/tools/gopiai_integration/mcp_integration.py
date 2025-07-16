"""
MCP Tools Integration для GopiAI

Этот модуль обеспечивает интеграцию с инструментами MCP (Model Context Protocol)
через модуль mcp.client.streamable_http.

Модуль предоставляет функциональность для подключения к MCP серверам
и использования их инструментов в CrewAI без зависимостей от crewai-tools.
"""

import os
import logging
import asyncio
import json
import httpx
from typing import Dict, List, Any, Optional, Set, Union, Callable, Awaitable

# Используем streamable_http для подключения к MCP серверам
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import JSONRPCRequest, JSONRPCResponse, JSONRPCNotification

# Инициализируем логгер
logger = logging.getLogger(__name__)

class MCPToolsManager:
    """
    Менеджер инструментов MCP для интеграции с CrewAI.
    
    Позволяет получать инструменты с нескольких MCP серверов
    и использовать их в CrewAI через streamable_http_client.
    """
    
    # Список доступных MCP серверов с их URL
    MCP_SERVERS = [
        {"name": "brightdata", "url": "https://server.smithery.ai/@luminati-io/brightdata-mcp/mcp"},
        {"name": "ref-tools", "url": "https://server.smithery.ai/@ref-tools/ref-tools-mcp/mcp"},
        {"name": "desktop-commander", "url": "https://server.smithery.ai/@wonderwhy-er/desktop-commander/mcp"},
        {"name": "mcp-think-tank", "url": "https://server.smithery.ai/@flight505/mcp-think-tank/mcp"},
        {"name": "agentic-control", "url": "https://server.smithery.ai/@FutureAtoms/agentic-control-framework/mcp"},
        {"name": "mem0-memory", "url": "https://server.smithery.ai/@mem0ai/mem0-memory-mcp/mcp"},
        {"name": "mcp-browser", "url": "https://server.smithery.ai/@bytedance/mcp-server-browser/mcp"},
        {"name": "toolbox", "url": "https://server.smithery.ai/@smithery/toolbox/mcp"},
        {"name": "minimax", "url": "https://server.smithery.ai/@ropon/minimax-mcp/mcp"},
        {"name": "vocr", "url": "https://server.smithery.ai/@JigsawStack/vocr/mcp"},
    ]
    
    def __init__(self):
        """Инициализация менеджера MCP инструментов."""
        self.api_key = os.environ.get("SMITHERY_API_KEY", "3efd202d-d41b-4708-b0fa-ca8b977e46ef")  # Используем API ключ из предыдущего кода
        self.server_clients = {}  # Словарь клиентов streamable_http для серверов
        self.server_tools = {}    # Словарь инструментов, доступных на каждом сервере
        self.initialized_servers = set()  # Множество инициализированных серверов
        self.all_tools = []  # Список всех инструментов со всех серверов
        self.tools_by_server = {}  # Словарь инструментов по серверам
        self.connected_servers = set()  # Множество подключенных серверов
    
    async def connect_to_server(self, server_url: str) -> bool:
        """
        Подключается к MCP серверу через streamable_http_client.
        
        Args:
            server_url: URL MCP сервера.
            
        Returns:
            True если подключение успешно, False в противном случае.
        """
        if server_url in self.server_clients:
            return True
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Используем streamable_http_client для создания клиента MCP
            self.server_clients[server_url] = streamablehttp_client(
                url=server_url,
                headers=headers,
                timeout=30
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка при подключении к MCP серверу {server_url}: {e}")
            return False
    
    async def initialize_server(self, server_url: str) -> bool:
        """
        Инициализирует подключение к серверу и получает список его инструментов.
        
        Args:
            server_url: URL MCP сервера.
            
        Returns:
            True если инициализация прошла успешно, False в противном случае.
        """
        if server_url in self.initialized_servers:
            return True
            
        try:
            if not await self.connect_to_server(server_url):
                return False
                
            # Получаем список инструментов
            tools = await self.get_server_tools_by_url(server_url)
            if tools:
                self.initialized_servers.add(server_url)
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при инициализации сервера {server_url}: {e}")
            return False
    
    async def connect_to_all_servers(self) -> Dict[str, List[Dict]]:
        """
        Подключается ко всем доступным MCP серверам и получает их инструменты.
        
        Returns:
            Словарь с названиями серверов и списками их инструментов.
        """
        result = {}
        
        for server in self.MCP_SERVERS:
            server_name = server["name"]
            server_url = server["url"]
            
            try:
                if await self.initialize_server(server_url):
                    tools = await self.get_server_tools_by_url(server_url)
                    if tools:
                        result[server_name] = tools
                        self.server_tools[server_url] = tools
            except Exception as e:
                logger.error(f"Ошибка при подключении к серверу {server_name}: {e}")
        
        return result
        
    async def get_server_tools_by_url(self, server_url: str) -> List[Dict]:
        """
        Получает список инструментов с указанного MCP сервера по его URL.
        
        Args:
            server_url: URL сервера.
            
        Returns:
            Список инструментов сервера или пустой список, если сервер недоступен.
        """
        if server_url not in self.server_clients:
            if not await self.connect_to_server(server_url):
                return []
                
        try:
            # Создаем запрос для получения списка ресурсов
            request = JSONRPCRequest(
                id="list_resources_request",
                method="mcp/resources/list",
                params={}
            )
            
            # Получаем доступ к клиенту и выполняем запрос
            client = self.server_clients[server_url]
            async with client as (read_stream, write_stream, _):
                # Отправляем запрос
                await write_stream.send({
                    "message": request,
                    "metadata": {}
                })
                
                # Ожидаем ответ
                response_message = await read_stream.receive()
                response = response_message.message
                
                if isinstance(response, JSONRPCResponse) and response.result:
                    # Преобразуем информацию об инструментах в более удобный формат
                    tools = []
                    for resource in response.result.get("resources", []):
                        tools.append({
                            "id": resource.get("id", ""),
                            "name": resource.get("name", ""),
                            "description": resource.get("description", ""),
                            "server_url": server_url
                        })
                    
                    # Сохраняем список инструментов для сервера
                    self.server_tools[server_url] = tools
                    return tools
                
                return []
        except Exception as e:
            logger.error(f"Ошибка при получении инструментов с сервера {server_url}: {e}")
            return []
    
    async def get_all_tools(self) -> List[Dict]:
        """
        Получает все инструменты со всех доступных MCP серверов.
        
        Returns:
            Список всех инструментов со всех серверов.
        """
        all_tools = []
        
        # Если еще нет подключенных серверов, подключаемся
        if not self.server_tools:
            await self.connect_to_all_servers()
            
        # Собираем инструменты со всех серверов
        for server_url, tools in self.server_tools.items():
            all_tools.extend(tools)
            
        return all_tools
        
    def get_tool_by_name(self, tool_name: str) -> Optional[Dict]:
        """
        Находит инструмент по его имени среди всех серверов.
        
        Args:
            tool_name: Имя инструмента для поиска.
            
        Returns:
            Инструмент с указанным именем или None, если не найден.
        """
        # Метод поиска через асинхронные операции
        async def search_tool() -> Optional[Dict]:
            tools = await self.get_all_tools()
            for tool in tools:
                if tool["name"].lower() == tool_name.lower():
                    return tool
            return None
        
        # Запускаем поиск в асинхронном режиме
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(search_tool())
        
    async def execute_tool_async(self, tool: Dict, **kwargs) -> Dict:
        """
        Выполняет вызов инструмента MCP с заданными параметрами асинхронно.
        
        Args:
            tool: Информация об инструменте MCP для выполнения.
            **kwargs: Параметры для вызова инструмента.
            
        Returns:
            Результат выполнения инструмента.
        """
        server_url = tool.get("server_url")
        tool_id = tool.get("id")
        
        if not server_url or not tool_id:
            logger.error("Неверная информация об инструменте")
            return {"error": "Неверная информация об инструменте"}
            
        if server_url not in self.server_clients:
            if not await self.connect_to_server(server_url):
                return {"error": f"Не удалось подключиться к серверу {server_url}"}
                
        try:
            # Создаем запрос для выполнения инструмента
            request = JSONRPCRequest(
                id=f"execute_{tool_id}",
                method="mcp/resources/invoke",
                params={
                    "uri": tool_id,
                    "args": kwargs
                }
            )
            
            # Получаем доступ к клиенту и выполняем запрос
            client = self.server_clients[server_url]
            async with client as (read_stream, write_stream, _):
                # Отправляем запрос
                await write_stream.send({
                    "message": request,
                    "metadata": {}
                })
                
                # Ожидаем ответ
                response_message = await read_stream.receive()
                response = response_message.message
                
                if isinstance(response, JSONRPCResponse):
                    return response.result or {}
                else:
                    return {"error": "Неверный формат ответа"}
        except Exception as e:
            logger.error(f"Ошибка при выполнении инструмента {tool.get('name', '')}: {e}")
            return {"error": str(e)}
            
    def execute_tool(self, tool: Dict, **kwargs) -> Dict:
        """
        Выполняет вызов инструмента MCP с заданными параметрами.
        
        Args:
            tool: Информация об инструменте MCP для выполнения.
            **kwargs: Параметры для вызова инструмента.
            
        Returns:
            Результат выполнения инструмента.
        """
        try:
            # Запускаем выполнение в асинхронном режиме
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.execute_tool_async(tool, **kwargs))
        except Exception as e:
            logger.error(f"Ошибка при выполнении инструмента {tool.get('name', '')}: {e}")
            return {"error": str(e)}
    
    def disconnect_from_all_servers(self) -> bool:
        """
        Отключается от всех серверов MCP.
        
        Returns:
            True, если все отключения успешны, иначе False.
        """
        all_success = True
        
        # Создаем копию множества, чтобы избежать ошибки при изменении во время итерации
        servers_to_disconnect = set(self.connected_servers)
        
        for server_name in servers_to_disconnect:
            success = self.disconnect_from_server(server_name)
            all_success = all_success and success
        
        if all_success:
            logger.info("Отключение от всех серверов MCP выполнено успешно")
        else:
            logger.warning("Не удалось корректно отключиться от некоторых серверов MCP")
        
        return all_success
    
    def __del__(self):
        """Деструктор для корректного закрытия всех соединений."""
        try:
            self.disconnect_from_all_servers()
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединений в деструкторе: {e}")

# Синглтон для повторного использования менеджера
_mcp_tools_manager_instance = None

def get_mcp_tools_manager() -> Optional[MCPToolsManager]:
    """
    Возвращает экземпляр менеджера MCP инструментов.
    
    Returns:
        Экземпляр менеджера MCP инструментов или None, если менеджер не может быть создан.
    """
    global _mcp_tools_manager_instance
    try:
        if _mcp_tools_manager_instance is None:
            _mcp_tools_manager_instance = MCPToolsManager()
        return _mcp_tools_manager_instance
    except Exception as e:
        logger.error(f"Ошибка при создании менеджера MCP инструментов: {e}")
        return None

def get_mcp_tools_info() -> str:
    """
    Получает информацию о доступных инструментах MCP для использования в промптах.
    
    Returns:
        Строка с информацией о доступных инструментах MCP.
    """
    manager = get_mcp_tools_manager()
    if not manager or not manager.api_key:
        return "MCP серверы недоступны (отсутствует API ключ)"
    
    try:
        all_tools = manager.get_all_tools()
        if not all_tools:
            return "MCP серверы доступны, но инструменты не найдены"
        
        tools_info = "\n".join([f"- {tool.name}: {tool.description}" for tool in all_tools])
        return f"""Доступны следующие MCP инструменты:
{tools_info}
"""
    except Exception as e:
        logger.error(f"Ошибка при получении информации об инструментах MCP: {e}")
        return f"Ошибка при получении информации об инструментах MCP: {e}"
