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
        
        # Используем актуальные адреса вместо устаревшего api.smithery.ai
        self.registry_url = "https://registry.smithery.ai"
        self.server_base_url = "https://server.smithery.ai"
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
                f"{self.registry_url}/servers",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            
            # Добавляем диагностический вывод
            logger.debug("--- DEBUG SMITHY RESPONSE (list_servers) ---")
            logger.debug(f"URL запроса: {self.registry_url}/servers")
            logger.debug(f"Код ответа: {response.status_code}")
            logger.debug(f"Заголовки ответа: {response.headers}")
            logger.debug(f"Тип ответа до парсинга: {type(response.text)}")
            logger.debug(f"Первые 200 символов ответа: {response.text[:200]}..." if len(response.text) > 200 else f"Ответ целиком: {response.text}")
            
            # Парсим JSON и добавляем информацию о результате
            try:
                parsed_data = response.json()
                logger.debug(f"Тип данных после парсинга: {type(parsed_data)}")
                if isinstance(parsed_data, list):
                    logger.debug(f"Количество элементов в списке: {len(parsed_data)}")
                    if parsed_data:
                        logger.debug(f"Пример первого элемента: {parsed_data[0]}")
                elif isinstance(parsed_data, dict):
                    logger.debug(f"Ключи в словаре: {parsed_data.keys()}")
                logger.debug("--- КОНЕЦ DEBUG SMITHY RESPONSE ---")
                
                self.servers_cache = parsed_data
                return self.servers_cache
            except json.JSONDecodeError as json_err:
                logger.error(f"Ошибка декодирования JSON: {json_err}")
                logger.error(f"Содержимое ответа: {response.text}")
                return []
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
            logger.warning(f"Невозможно получить инструменты для сервера {server_name}: API ключ отсутствует")
            return []
        
        # Расширенная диагностика - проверяем формат server_name
        logger.info(f"Запрос инструментов для сервера: '{server_name}' (тип: {type(server_name)})")
        if not server_name or not isinstance(server_name, str):
            logger.error(f"Некорректное имя сервера: {server_name}. Должно быть непустой строкой.")
            return []
        
        cache_key = f"tools_{server_name}"
        if cache_key in self.tools_cache and not refresh:
            cached_tools = self.tools_cache[cache_key]
            logger.info(f"Получено {len(cached_tools)} инструментов из кеша для сервера {server_name}")
            return cached_tools
        
        try:
            # Проверим список доступных серверов для диагностики
            servers = self.list_servers(refresh=False)
            server_names = []
            for server in servers:
                if isinstance(server, dict):
                    # Логируем все возможные ключи, которые могут содержать имя сервера
                    name_value = server.get("name")
                    display_name = server.get("displayName")
                    server_id = server.get("id")
                    if name_value:
                        server_names.append(name_value)
                    logger.debug(f"Сервер: name={name_value}, displayName={display_name}, id={server_id}")
                    
            logger.info(f"Доступные серверы: {server_names}")
            
            # Проверка, существует ли сервер в списке доступных
            if server_names and server_name not in server_names:
                logger.warning(f"Сервер '{server_name}' не найден в списке доступных серверов: {server_names}")
                # Проверим, не нужно ли использовать другой ключ вместо 'name'
                for server in servers:
                    if isinstance(server, dict):
                        display_name = server.get("displayName")
                        server_id = server.get("id")
                        if display_name == server_name or server_id == server_name:
                            logger.info(f"Найдено соответствие: displayName={display_name} или id={server_id}")
            
            # Построение URL для запроса
            tools_url = f"{self.server_base_url}/{server_name}/tools"
            logger.info(f"Отправка запроса на получение инструментов: {tools_url}")
            response = requests.get(
                tools_url,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            
            # Расширенная диагностика ответа
            logger.debug(f"--- DEBUG SMITHY RESPONSE (list_server_tools для {server_name}) ---")
            logger.debug(f"URL запроса: {tools_url}")
            logger.debug(f"Код ответа: {response.status_code}")
            logger.debug(f"Заголовки ответа: {response.headers}")
            logger.debug(f"Тип ответа до парсинга: {type(response.text)}")
            logger.debug(f"Первые 200 символов ответа: {response.text[:200]}..." if len(response.text) > 200 else f"Ответ целиком: {response.text}")
            
            # Парсим JSON и добавляем информацию о результате
            try:
                parsed_data = response.json()
                logger.debug(f"Тип данных после парсинга: {type(parsed_data)}")
                
                # Проверка и анализ структуры полученных данных
                if isinstance(parsed_data, list):
                    logger.info(f"Получен список инструментов, количество: {len(parsed_data)}")
                    if parsed_data:
                        logger.debug(f"Пример первого инструмента: {parsed_data[0]}")
                        # Если есть инструменты, проверяем наличие необходимых полей
                        if isinstance(parsed_data[0], dict):
                            required_fields = ["name", "description"]
                            has_fields = all(field in parsed_data[0] for field in required_fields)
                            logger.debug(f"Первый инструмент содержит необходимые поля (name, description): {has_fields}")
                elif isinstance(parsed_data, dict):
                    logger.debug(f"Получен словарь с ключами: {parsed_data.keys()}")
                    # Проверяем, нет ли инструментов под ключом "tools"
                    tools_list = parsed_data.get("tools", [])
                    if tools_list:
                        logger.info(f"Извлечено {len(tools_list)} инструментов из ключа 'tools'")
                        parsed_data = tools_list
                        
                logger.debug("--- КОНЕЦ DEBUG SMITHY RESPONSE ---")
                
                # Возвращаем результат, поддерживая как прямой список, так и ключ "tools"
                result_tools = parsed_data if isinstance(parsed_data, list) else parsed_data.get("tools", [])
                logger.info(f"Итоговое количество инструментов для сервера {server_name}: {len(result_tools)}")
                self.tools_cache[cache_key] = result_tools
                return result_tools
            except json.JSONDecodeError as json_err:
                logger.error(f"Ошибка декодирования JSON в list_server_tools: {json_err}")
                logger.error(f"Содержимое ответа: {response.text}")
                return []
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP ошибка при получении инструментов для сервера {server_name}: {http_err}")
            if hasattr(http_err, "response") and hasattr(http_err.response, "text"):
                logger.error(f"Ответ сервера: {http_err.response.text}")
            return []
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
                f"{self.server_base_url}/{server_name}/tools/{tool_name}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=params
            )
            response.raise_for_status()
            
            # Добавляем диагностический вывод
            logger.debug(f"--- DEBUG SMITHY RESPONSE (call_tool для {server_name}/{tool_name}) ---")
            logger.debug(f"URL запроса: {self.server_base_url}/{server_name}/tools/{tool_name}")
            logger.debug(f"Код ответа: {response.status_code}")
            logger.debug(f"Заголовки ответа: {response.headers}")
            logger.debug(f"Параметры запроса: {params}")
            logger.debug(f"Тип ответа до парсинга: {type(response.text)}")
            logger.debug(f"Первые 200 символов ответа: {response.text[:200]}..." if len(response.text) > 200 else f"Ответ целиком: {response.text}")
            
            # Парсим JSON и добавляем информацию о результате
            try:
                parsed_data = response.json()
                logger.debug(f"Тип данных после парсинга: {type(parsed_data)}")
                if isinstance(parsed_data, dict):
                    logger.debug(f"Ключи в словаре: {parsed_data.keys()}")
                elif isinstance(parsed_data, list):
                    logger.debug(f"Количество элементов в списке: {len(parsed_data)}")
                logger.debug("--- КОНЕЦ DEBUG SMITHY RESPONSE ---")
                
                return parsed_data
            except json.JSONDecodeError as json_err:
                logger.error(f"Ошибка декодирования JSON в call_tool: {json_err}")
                logger.error(f"Содержимое ответа: {response.text}")
                return {"error": f"Ошибка парсинга JSON: {json_err}"}
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
