"""
Smithery MCP Client для GopiAI

Этот модуль предоставляет минимальный клиент для работы с Smithery MCP API,
позволяющий интегрировать инструменты MCP в ассистента GopiAI.
"""

import os
import json
import requests
import logging
from typing import Dict, List, Any, Optional, Union

# Инициализируем логгер
logger = logging.getLogger(__name__)

class SmitheryClient:
    """
    Минимальный клиент для взаимодействия с Smithery MCP API.
    
    Позволяет получать список доступных серверов, инструментов и вызывать их.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализирует клиент Smithery.
        
        Args:
            api_key: API ключ для Smithery. Если не указан, пытается получить из переменной среды SMITHERY_API_KEY.
        """
        self.api_key = api_key or os.environ.get("SMITHERY_API_KEY")
        if not self.api_key:
            logger.warning("Smithery API key не найден. Некоторые функции могут быть недоступны.")
        
        self.base_url = "https://api.smithery.ai"
        self.servers_cache = {}
        self.tools_cache = {}
    
    def list_servers(self, refresh: bool = False) -> List[Dict]:
        """
        Получает список доступных MCP серверов.
        
        Args:
            refresh: Принудительно обновить кеш серверов.
            
        Returns:
            Список словарей с информацией о серверах.
        """
        if not self.api_key:
            return []
        
        if self.servers_cache and not refresh:
            return self.servers_cache
        
        try:
            response = requests.get(
                f"{self.base_url}/servers",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            self.servers_cache = response.json()
            return self.servers_cache
        except Exception as e:
            logger.error(f"Ошибка при получении списка MCP серверов: {e}")
            return []
    
    def list_server_tools(self, server_name: str, refresh: bool = False) -> List[Dict]:
        """
        Получает список доступных инструментов для указанного сервера.
        
        Args:
            server_name: Имя MCP сервера.
            refresh: Принудительно обновить кеш инструментов.
            
        Returns:
            Список словарей с информацией об инструментах.
        """
        if not self.api_key:
            return []
        
        cache_key = f"tools_{server_name}"
        if cache_key in self.tools_cache and not refresh:
            return self.tools_cache[cache_key]
        
        try:
            response = requests.get(
                f"{self.base_url}/servers/{server_name}/tools",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            self.tools_cache[cache_key] = response.json()
            return self.tools_cache[cache_key]
        except Exception as e:
            logger.error(f"Ошибка при получении инструментов для сервера {server_name}: {e}")
            return []
    
    def call_tool(self, server_name: str, tool_name: str, params: Dict) -> Any:
        """
        Вызывает инструмент MCP с указанными параметрами.
        
        Args:
            server_name: Имя MCP сервера.
            tool_name: Имя инструмента.
            params: Параметры для вызова инструмента.
            
        Returns:
            Результат выполнения инструмента.
        """
        if not self.api_key:
            return {"error": "API key не настроен"}
        
        try:
            response = requests.post(
                f"{self.base_url}/servers/{server_name}/tools/{tool_name}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка при вызове инструмента {tool_name} на сервере {server_name}: {e}")
            return {"error": str(e)}

# Синглтон для повторного использования клиента
_smithery_client_instance = None

def get_smithery_client() -> Optional[SmitheryClient]:
    """
    Возвращает экземпляр клиента Smithery.
    Инициализация выполняется строго по официальной документации Smithery SDK.
    
    Returns:
        Экземпляр клиента Smithery или None, если инициализация невозможна.
    """
    global _smithery_client_instance
    try:
        if _smithery_client_instance is None:
            api_key = os.environ.get("SMITHERY_API_KEY")
            if not api_key:
                logger.warning("SMITHERY_API_KEY не найден в переменных среды. Клиент не инициализирован.")
                return None
            _smithery_client_instance = SmitheryClient(api_key=api_key)
            logger.info("Клиент Smithery MCP успешно инициализирован")
        return _smithery_client_instance
    except Exception as e:
        logger.error(f"Ошибка при инициализации клиента Smithery: {e}")
        return None
