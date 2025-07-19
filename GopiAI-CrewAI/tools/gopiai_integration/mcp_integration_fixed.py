"""
Исправленная MCP Tools Integration для GopiAI

Этот модуль обеспечивает интеграцию с инструментами MCP (Model Context Protocol)
через Smithery Registry API согласно официальной документации.
"""

import os
import logging
import asyncio
import json
import httpx
from typing import Dict, List, Any, Optional, Set, Union
from dotenv import load_dotenv

# Инициализируем логгер
logger = logging.getLogger(__name__)

class SmitheryMCPManager:
    """
    Менеджер инструментов MCP для интеграции с CrewAI через Smithery Registry API.
    """
    
    def __init__(self):
        """Инициализация менеджера MCP инструментов."""
        # Загружаем переменные окружения из .env файла
        load_dotenv(r"C:\Users\crazy\GOPI_AI_MODULES\.env")
        
        self.api_key = os.environ.get("SMITHERY_API_KEY")
        if not self.api_key:
            logger.warning("SMITHERY_API_KEY не найден в переменных окружения")
        else:
            logger.info(f"SMITHERY_API_KEY загружен: {self.api_key[:8]}...{self.api_key[-4:]}")
        
        self.registry_url = "https://registry.smithery.ai"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        self.deployed_servers = {}  # Кэш развернутых серверов
        self.server_tools = {}      # Кэш инструментов по серверам
        self.server_clients = {}    # HTTP клиенты для серверов
        self.initialized = False
    
    async def initialize(self):
        """Инициализация - получение информации о конкретных серверах"""
        if self.initialized:
            return
            
        # --- ИСПРАВЛЕНО: Загружаем только нужные серверы ---
        target_servers = [
            "@flight505/mcp-think-tank",
            "@smithery-ai/agentic-control-framework" # Предполагаемое имя
        ]

        try:
            for server_name in target_servers:
                server_info = await self.get_server_info_direct(server_name)
                if server_info and server_info.get('deploymentUrl'):
                    self.deployed_servers[server_name] = server_info
                    logger.info(f"Найден и добавлен целевой сервер: {server_name} -> {server_info.get('deploymentUrl')}")
                else:
                    logger.warning(f"Не удалось найти или проверить целевой сервер: {server_name}")

            logger.info(f"Инициализация завершена. Загружено {len(self.deployed_servers)} целевых серверов.")
            self.initialized = True

        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
    
    async def get_server_info_direct(self, qualified_name: str) -> Optional[Dict]:
        """Получает детальную информацию о сервере напрямую (используется внутри initialize)"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.registry_url}/servers/{qualified_name}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Не удалось получить информацию о сервере {qualified_name}: {response.status_code}")
                    return None
        except Exception as e:
            logger.warning(f"Ошибка при получении информации о сервере {qualified_name}: {e}")
            return None

    async def get_server_info(self, qualified_name: str) -> Optional[Dict]:
        """Получает детальную информацию о сервере по его qualified name"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.registry_url}/servers/{qualified_name}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Ошибка получения информации о сервере {qualified_name}: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Ошибка при получении информации о сервере {qualified_name}: {e}")
            return None
    
    async def get_server_tools(self, qualified_name: str) -> List[Dict]:
        """Получает инструменты для конкретного сервера"""
        if qualified_name in self.server_tools:
            return self.server_tools[qualified_name]
        
        # Сначала проверяем кэш развернутых серверов
        server_info = self.deployed_servers.get(qualified_name)
        if not server_info:
            # Если нет в кэше, получаем информацию о сервере
            server_info = await self.get_server_info(qualified_name)
            if not server_info:
                return []
        
        # Извлекаем инструменты из информации о сервере
        tools = server_info.get('tools', [])
        if tools:
            # Преобразуем инструменты в удобный формат
            formatted_tools = []
            for tool in tools:
                formatted_tools.append({
                    "id": tool.get("name", ""),
                    "name": tool.get("name", ""),
                    "description": tool.get("description", ""),
                    "server_name": qualified_name,
                    "server_info": server_info,
                    "schema": tool.get("inputSchema", {})
                })
            
            # Кэшируем инструменты
            self.server_tools[qualified_name] = formatted_tools
            logger.info(f"Получено {len(formatted_tools)} инструментов для сервера {qualified_name}")
            return formatted_tools
        
        return []
    
    async def get_all_tools(self) -> List[Dict]:
        """Получает все инструменты со всех развернутых серверов"""
        if not self.initialized:
            await self.initialize()
        
        all_tools = []
        
        for qualified_name in self.deployed_servers:
            tools = await self.get_server_tools(qualified_name)
            all_tools.extend(tools)
        
        logger.info(f"Всего доступно {len(all_tools)} инструментов")
        return all_tools
    
    def get_tool_by_name(self, tool_name: str) -> Optional[Dict]:
        """Находит инструмент по его имени"""
        try:
            async def search_tool():
                tools = await self.get_all_tools()
                for tool in tools:
                    if tool["name"].lower() == tool_name.lower():
                        return tool
                return None
            
            # Запускаем поиск
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
        """Выполняет инструмент через deployment URL сервера"""
        server_info = tool.get("server_info")
        if not server_info:
            return {"error": "Отсутствует информация о сервере"}
        
        # Получаем URL для подключения
        deployment_url = server_info.get("deploymentUrl")
        if not deployment_url:
            return {"error": "Сервер не развернут или отсутствует deployment URL"}
        
        tool_name = tool.get("name")
        if not tool_name:
            return {"error": "Отсутствует имя инструмента"}
        
        try:
            # Создаем HTTP клиент для подключения к deployment URL
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Формируем JSON-RPC запрос
                request_data = {
                    "jsonrpc": "2.0",
                    "id": f"execute_{tool_name}",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": kwargs
                    }
                }
                
                # Отправляем запрос к deployment URL
                response = await client.post(
                    deployment_url,
                    json=request_data,
                    headers=self.headers
                )
                
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
            logger.error(f"Ошибка при выполнении инструмента {tool_name}: {e}")
            return {"error": str(e)}
    
    def execute_tool(self, tool: Dict, **kwargs) -> Dict:
        """Синхронная обертка для выполнения инструмента"""
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(self.execute_tool_async(tool, **kwargs))
        except Exception as e:
            logger.error(f"Ошибка при выполнении инструмента: {e}")
            return {"error": str(e)}

# Синглтон для повторного использования менеджера
_smithery_manager_instance = None

def get_smithery_mcp_manager() -> Optional[SmitheryMCPManager]:
    """Возвращает экземпляр менеджера Smithery MCP"""
    global _smithery_manager_instance
    try:
        if _smithery_manager_instance is None:
            _smithery_manager_instance = SmitheryMCPManager()
        return _smithery_manager_instance
    except Exception as e:
        logger.error(f"Ошибка при создании менеджера Smithery MCP: {e}")
        return None

def get_mcp_tools_info() -> str:
    """Получает информацию о доступных инструментах MCP"""
    manager = get_smithery_mcp_manager()
    if not manager or not manager.api_key:
        return "MCP серверы недоступны (отсутствует API ключ)"
    
    try:
        # Синхронная обертка для получения инструментов
        async def get_tools_info():
            tools = await manager.get_all_tools()
            if not tools:
                return "MCP серверы доступны, но инструменты не найдены"
            
            tools_info = []
            for tool in tools:
                tools_info.append(f"- {tool['name']} (сервер: {tool['server_name']}): {tool['description']}")
            
            return f"""Доступны следующие MCP инструменты:
{chr(10).join(tools_info)}
"""
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(get_tools_info())
    except Exception as e:
        logger.error(f"Ошибка при получении информации об инструментах MCP: {e}")
        return f"Ошибка при получении информации об инструментах MCP: {e}"
