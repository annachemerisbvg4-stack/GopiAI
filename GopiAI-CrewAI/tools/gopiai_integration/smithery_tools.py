"""
Smithery MCP Tools Adapter для GopiAI

Этот модуль предоставляет адаптер для работы с инструментами Smithery MCP,
который позволяет ассистенту GopiAI использовать MCP инструменты.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable, Union

from .smithery_client import get_smithery_client, SmitheryClient

# Инициализируем логгер
logger = logging.getLogger(__name__)

class SmitheryToolsAdapter:
    """
    Адаптер для работы с инструментами Smithery MCP.
    
    Позволяет получать информацию об инструментах, вызывать их
    и форматировать результаты для ассистента.
    """
    
    def __init__(self):
        """Инициализация адаптера для инструментов Smithery MCP."""
        self.client = get_smithery_client()
        self.active_servers = []  # Список активных серверов
    
    def get_available_servers(self) -> List[Dict]:
        """
        Получает список доступных серверов Smithery MCP.
        
        Returns:
            Список словарей с информацией о серверах.
        """
        return self.client.list_servers()
    
    def get_server_tools(self, server_name: str) -> List[Dict]:
        """
        Получает список инструментов для указанного сервера.
        
        Args:
            server_name: Имя сервера MCP.
            
        Returns:
            Список словарей с информацией об инструментах.
        """
        return self.client.list_server_tools(server_name)
    
    def get_all_available_tools(self) -> Dict[str, List[Dict]]:
        """
        Получает все доступные инструменты со всех серверов.
        
        Returns:
            Словарь {имя_сервера: [инструменты]}.
        """
        servers = self.get_available_servers()
        result = {}
        
        for server in servers:
            server_name = server.get("name")
            if server_name:
                tools = self.get_server_tools(server_name)
                if tools:
                    result[server_name] = tools
        
        return result
    
    def execute_tool(self, server_name: str, tool_name: str, params: Dict) -> Dict:
        """
        Выполняет инструмент MCP с указанными параметрами.
        
        Args:
            server_name: Имя MCP сервера.
            tool_name: Имя инструмента.
            params: Параметры для вызова инструмента.
            
        Returns:
            Результат выполнения инструмента.
        """
        try:
            logger.info(f"Вызов инструмента {tool_name} на сервере {server_name} с параметрами {params}")
            result = self.client.call_tool(server_name, tool_name, params)
            logger.info(f"Результат вызова инструмента: {result}")
            return {
                "success": True,
                "result": result,
                "server": server_name,
                "tool": tool_name
            }
        except Exception as e:
            logger.error(f"Ошибка при выполнении инструмента {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "server": server_name,
                "tool": tool_name
            }
    
    def format_tool_description(self, server_name: str, tool_info: Dict) -> Dict:
        """
        Форматирует описание инструмента для отображения в UI.
        
        Args:
            server_name: Имя сервера MCP.
            tool_info: Информация об инструменте.
            
        Returns:
            Отформатированное описание инструмента.
        """
        tool_name = tool_info.get("name", "Неизвестный инструмент")
        description = tool_info.get("description", "Описание отсутствует")
        
        return {
            "id": f"mcp_{server_name}_{tool_name}",
            "name": f"{tool_name} ({server_name})",
            "description": description,
            "type": "mcp",
            "server": server_name,
            "tool": tool_name,
            "original_info": tool_info
        }
    
    def get_tool_descriptions(self) -> List[Dict]:
        """
        Получает форматированные описания всех доступных инструментов.
        
        Returns:
            Список словарей с описаниями инструментов.
        """
        all_tools = self.get_all_available_tools()
        result = []
        
        for server_name, tools in all_tools.items():
            for tool in tools:
                result.append(self.format_tool_description(server_name, tool))
        
        return result

    def process_mcp_tool_request(self, tool_id: str, message: str) -> Dict:
        """
        Обрабатывает запрос пользователя к MCP инструменту.
        
        Args:
            tool_id: Идентификатор инструмента в формате "mcp_{server}_{tool}".
            message: Текст запроса пользователя.
            
        Returns:
            Результат выполнения инструмента.
        """
        try:
            # Разбор идентификатора инструмента
            parts = tool_id.split("_", 2)
            if len(parts) != 3 or parts[0] != "mcp":
                return {"success": False, "error": "Неверный формат идентификатора инструмента"}
            
            server_name = parts[1]
            tool_name = parts[2]
            
            # Простая обработка запроса - передаем весь текст как параметр "query"
            params = {"query": message}
            
            # Выполняем инструмент
            return self.execute_tool(server_name, tool_name, params)
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса MCP: {e}")
            return {"success": False, "error": str(e)}

# Синглтон для повторного использования адаптера
_smithery_tools_adapter_instance = None

def get_smithery_tools_adapter() -> SmitheryToolsAdapter:
    """
    Возвращает экземпляр адаптера Smithery Tools.
    
    Returns:
        Экземпляр адаптера Smithery Tools.
    """
    global _smithery_tools_adapter_instance
    if _smithery_tools_adapter_instance is None:
        _smithery_tools_adapter_instance = SmitheryToolsAdapter()
    return _smithery_tools_adapter_instance
