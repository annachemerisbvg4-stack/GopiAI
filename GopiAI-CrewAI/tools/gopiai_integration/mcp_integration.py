"""
MCP Tools Integration для GopiAI

Этот модуль обеспечивает интеграцию с инструментами MCP (Model Context Protocol)
через официальную библиотеку crewai_tools.MCPServerAdapter.

Модуль предоставляет функциональность для подключения к MCP серверам
и использования их инструментов в агентах CrewAI.
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Union

# Используем официальный адаптер MCP из crewai_tools
from crewai_tools import MCPServerAdapter, BaseTool

# Инициализируем логгер
logger = logging.getLogger(__name__)

class MCPToolsManager:
    """
    Менеджер инструментов MCP для интеграции с CrewAI.
    
    Позволяет получать инструменты с нескольких MCP серверов
    и использовать их в агентах CrewAI.
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
        self.api_key = os.environ.get("SMITHERY_API_KEY")
        if not self.api_key:
            logger.warning("SMITHERY_API_KEY не найден в переменных среды. Интеграция MCP будет недоступна.")
        
        self.server_adapters = {}  # Словарь активных MCP серверов
        self.all_tools = []  # Список всех инструментов со всех серверов
        self.tools_by_server = {}  # Словарь инструментов по серверам
        self.connected_servers = set()  # Множество подключенных серверов
    
    def connect_to_server(self, server_config: Dict[str, str]) -> List[BaseTool]:
        """
        Подключается к серверу MCP и получает его инструменты.
        
        Args:
            server_config: Конфигурация сервера MCP (name, url).
            
        Returns:
            Список инструментов с сервера.
        """
        if not self.api_key:
            logger.warning(f"Не удалось подключиться к серверу {server_config['name']}: отсутствует API ключ")
            return []
        
        server_name = server_config['name']
        server_url = server_config['url']
        
        try:
            # Формируем URL с API ключом
            url_with_auth = f"{server_url}?api_key={self.api_key}"
            
            logger.info(f"Подключение к MCP серверу {server_name} по URL {server_url}")
            
            # Создаем параметры для MCPServerAdapter
            server_params = {
                "url": url_with_auth,
                "transport": "streamable-http"  # Используем протокол streamable-http
            }
            
            # Создаем адаптер для сервера
            adapter = MCPServerAdapter(server_params)
            adapter.start()
            
            # Получаем инструменты
            tools = adapter.tools
            
            # Сохраняем адаптер и инструменты
            self.server_adapters[server_name] = adapter
            self.tools_by_server[server_name] = tools
            self.connected_servers.add(server_name)
            
            logger.info(f"Успешно подключен к серверу {server_name}, получено {len(tools)} инструментов")
            logger.info(f"Инструменты: {[tool.name for tool in tools]}")
            
            return tools
            
        except Exception as e:
            logger.error(f"Ошибка при подключении к серверу {server_name}: {e}")
            return []
    
    def connect_to_all_servers(self) -> List[BaseTool]:
        """
        Подключается ко всем доступным серверам MCP и получает все инструменты.
        
        Returns:
            Список всех инструментов со всех серверов.
        """
        all_tools = []
        
        for server_config in self.MCP_SERVERS:
            server_tools = self.connect_to_server(server_config)
            all_tools.extend(server_tools)
        
        self.all_tools = all_tools
        logger.info(f"Подключено к {len(self.connected_servers)} серверам, получено {len(all_tools)} инструментов")
        
        return all_tools
    
    def get_all_tools(self) -> List[BaseTool]:
        """
        Получает все инструменты со всех подключенных серверов.
        Если соединения еще нет, подключается ко всем серверам.
        
        Returns:
            Список всех инструментов со всех серверов.
        """
        if not self.all_tools:
            return self.connect_to_all_servers()
        return self.all_tools
    
    def get_server_tools(self, server_name: str) -> List[BaseTool]:
        """
        Получает инструменты с указанного сервера.
        Если соединения еще нет, подключается к серверу.
        
        Args:
            server_name: Имя сервера MCP.
            
        Returns:
            Список инструментов с указанного сервера.
        """
        # Проверяем, есть ли сервер в списке подключенных
        if server_name not in self.connected_servers:
            # Ищем конфигурацию сервера по имени
            server_config = next((s for s in self.MCP_SERVERS if s['name'] == server_name), None)
            if server_config:
                return self.connect_to_server(server_config)
            else:
                logger.warning(f"Сервер {server_name} не найден в списке доступных серверов")
                return []
        
        # Возвращаем инструменты с сервера
        return self.tools_by_server.get(server_name, [])
    
    def disconnect_from_server(self, server_name: str) -> bool:
        """
        Отключается от указанного сервера MCP.
        
        Args:
            server_name: Имя сервера MCP.
            
        Returns:
            True, если отключение успешно, иначе False.
        """
        if server_name in self.connected_servers:
            try:
                adapter = self.server_adapters.get(server_name)
                if adapter and adapter.is_connected:
                    adapter.stop()
                
                # Удаляем инструменты сервера из общего списка
                server_tools = self.tools_by_server.get(server_name, [])
                self.all_tools = [tool for tool in self.all_tools if tool not in server_tools]
                
                # Удаляем информацию о сервере
                self.connected_servers.remove(server_name)
                self.tools_by_server.pop(server_name, None)
                self.server_adapters.pop(server_name, None)
                
                logger.info(f"Отключен от сервера {server_name}")
                return True
            except Exception as e:
                logger.error(f"Ошибка при отключении от сервера {server_name}: {e}")
        
        return False
    
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
