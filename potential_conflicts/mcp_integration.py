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
        {"name": "mcp-think-tank", "url": "https://server.smithery.ai/@flight505/mcp-think-tank/mcp"},
        {"name": "agentic-control", "url": "https://server.smithery.ai/@FutureAtoms/agentic-control-framework/mcp"},
    ]
    
    def __init__(self):
        """Инициализация менеджера MCP инструментов."""
        self.api_key = os.environ.get("SMITHERY_API_KEY")
        if not self.api_key:
            logger.warning("SMITHERY_API_KEY не найден в переменных окружения")
        else:
            logger.info(f"SMITHERY_API_KEY загружен: {self.api_key[:8]}...{self.api_key[-4:]}")
        self.server_clients = {}  # Словарь клиентов streamable_http для серверов
        self.server_tools = {}    # Словарь инструментов, доступных на каждом сервере
        self.initialized_servers = set()  # Множество инициализированных серверов
        self.all_tools = []  # Список всех инструментов со всех серверов
        self.tools_by_server = {}  # Словарь инструментов по серверам
        self.connected_servers = set()  # Множество подключенных серверов
    
    async def connect_to_server(self, server_url: str) -> bool:
        """
        Подключается к MCP серверу через Smithery API.
        
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
            # Создаем HTTP клиент для работы с Smithery API
            self.server_clients[server_url] = httpx.AsyncClient(
                headers=headers,
                timeout=30.0
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
        Получает список инструментов с указанного MCP сервера через Smithery API.
        
        Args:
            server_url: URL сервера.
            
        Returns:
            Список инструментов сервера или пустой список, если сервер недоступен.
        """
        if server_url not in self.server_clients:
            if not await self.connect_to_server(server_url):
                return []
                
        try:
            # Создаем JSON-RPC запрос для получения списка инструментов
            request_data = {
                "jsonrpc": "2.0",
                "id": "list_tools_request",
                "method": "tools/list",
                "params": {}
            }
            
            # Отправляем POST запрос к Smithery API
            client = self.server_clients[server_url]
            response = await client.post(server_url, json=request_data)
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "result" in response_data and "tools" in response_data["result"]:
                    # Преобразуем информацию об инструментах в более удобный формат
                    tools = []
                    for tool in response_data["result"]["tools"]:
                        tools.append({
                            "id": tool.get("name", ""),
                            "name": tool.get("name", ""),
                            "description": tool.get("description", ""),
                            "server_url": server_url,
                            "schema": tool.get("inputSchema", {})
                        })
                    
                    # Сохраняем список инструментов для сервера
                    self.server_tools[server_url] = tools
                    return tools
                
                return []
            else:
                logger.warning(f"Получен статус {response.status_code} от сервера {server_url}")
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
        try:
            # Метод поиска через асинхронные операции
            async def search_tool() -> Optional[Dict]:
                tools = await self.get_all_tools()
                for tool in tools:
                    if tool["name"].lower() == tool_name.lower():
                        return tool
                return None
            
            # Запускаем поиск в асинхронном режиме
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(search_tool())
        except Exception as e:
            logger.error(f"Ошибка при поиске инструмента {tool_name}: {e}")
            return None
        
    async def execute_tool_async(self, tool: Dict, **kwargs) -> Dict:
        """
        Выполняет вызов инструмента MCP с заданными параметрами через Smithery API.
        
        Args:
            tool: Информация об инструменте MCP для выполнения.
            **kwargs: Параметры для вызова инструмента.
            
        Returns:
            Результат выполнения инструмента.
        """
        server_url = tool.get("server_url")
        tool_name = tool.get("name")
        
        if not server_url or not tool_name:
            logger.error("Неверная информация об инструменте")
            return {"error": "Неверная информация об инструменте"}
            
        if server_url not in self.server_clients:
            if not await self.connect_to_server(server_url):
                return {"error": f"Не удалось подключиться к серверу {server_url}"}
                
        try:
            # Создаем JSON-RPC запрос для выполнения инструмента
            request_data = {
                "jsonrpc": "2.0",
                "id": f"execute_{tool_name}",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": kwargs
                }
            }
            
            # Отправляем POST запрос к Smithery API
            client = self.server_clients[server_url]
            response = await client.post(server_url, json=request_data)
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "result" in response_data:
                    return response_data["result"]
                elif "error" in response_data:
                    return {"error": response_data["error"]}
                else:
                    return {"error": "Неожиданный формат ответа"}
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
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
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
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
