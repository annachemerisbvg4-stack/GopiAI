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
        logger.info(f"Запрашиваю инструменты для сервера: '{server_name}'")
        
        # Добавляем обработку специальных серверов
        if server_name.lower() == "brave-search":
            logger.info(f"Специальная обработка для сервера {server_name} - добавляем заглушки для инструментов")
            # Для тестирования создаем заглушку с инструментами
            return [
                {
                    "name": "brave_web_search",
                    "description": "Поиск в интернете с помощью Brave Search API"
                },
                {
                    "name": "brave_local_search",
                    "description": "Поиск локальных мест и бизнесов"
                }
            ]
        
        # Для других серверов используем стандартный метод
        tools = self.client.list_server_tools(server_name)
        logger.info(f"Получено {len(tools)} инструментов для сервера '{server_name}'")
        
        return tools
    
    # Класс для ленивой загрузки инструментов Smithery MCP
    class LazySmitheryTool:
        def __init__(self, server_data, server_name):
            # Сохраняем только метаданные, никаких проверок и подключений
            self.server_name = server_name
            self.name = server_data.get('name', 'unknown_tool')
            self.description = server_data.get('description', 'Нет описания')
            self.server_info = server_data  # Сохраняем все данные на будущее
            
        def to_dict(self):
            """Преобразует инструмент в словарь для использования в API"""
            return {
                'name': self.name,
                'description': self.description
            }
    
    def get_all_available_tools(self) -> Dict[str, List[Dict]]:
        """
        Получает все доступные инструменты со всех серверов.
        Реализует "ленивую загрузку" (lazy loading) согласно Best Practices Smithery MCP.
        
        Returns:
            Словарь {имя_сервера: [инструменты]}.
        """
        servers_response = self.get_available_servers()
        result = {}
        
        # Добавляем диагностику и правильную обработку структуры ответа
        logger.debug(f"Тип ответа от get_available_servers: {type(servers_response)}")
        
        # Проверяем формат ответа, так как Smithery может вернуть словарь с ключом 'servers'
        if isinstance(servers_response, dict) and 'servers' in servers_response:
            # Если получили словарь {'servers': [...], 'pagination': ...}
            servers_list = servers_response.get('servers', [])
            logger.debug(f"Извлекли список серверов из словаря по ключу 'servers', найдено {len(servers_list)} серверов")
        else:
            # Если получили напрямую список серверов
            servers_list = servers_response
            logger.debug(f"Получили напрямую список серверов, размер: {len(servers_list) if isinstance(servers_list, list) else 'не список'}")
        
        # Проверяем, что servers_list действительно список
        if not isinstance(servers_list, list):
            logger.error(f"Ошибка: servers_list не является списком, его тип: {type(servers_list)}")
            return {}
        
        # ДИАГНОСТИКА: Выводим первый сервер полностью для анализа структуры
        if servers_list:
            logger.info("--- ДЕБАГ ПЕРВОГО СЕРВЕРА ---")
            import json
            first_server = servers_list[0]
            logger.info(json.dumps(first_server, indent=2))
            logger.info(f"Ключи первого сервера: {list(first_server.keys())}")
            logger.info("----------------------------")
        
        # Обрабатываем каждый сервер в соответствии с Best Practices (ленивая загрузка)
        for i, server in enumerate(servers_list):
            if not isinstance(server, dict):
                logger.error(f"Ошибка: элемент в servers_list не является словарём: {server}")
                continue
            
            logger.info(f"\n[DEBUG] Обрабатываю сервер {i+1}/{len(servers_list)}")
            
            # Определяем имя сервера из разных возможных ключей
            server_name = None
            for key in ["name", "displayName", "qualifiedName", "id"]:
                if key in server:
                    logger.info(f"[DEBUG] Найден ключ '{key}' со значением '{server[key]}'")
                    if not server_name:  # Берем первый найденный ключ как имя
                        server_name = server[key]
            
            # Если не удалось найти имя ни по одному из ключей
            if not server_name:
                logger.error(f"[DEBUG] Не удалось определить имя сервера, доступные ключи: {list(server.keys())}")
                continue
                
            logger.info(f"[DEBUG] Использую имя сервера: '{server_name}'")
            
            # LAZY LOADING: Создаем "заглушку" инструментов без проверки подключения
            # Инициализация произойдет только при вызове инструмента пользователем
            lazy_tools = []
            
            # Специальная обработка для известных серверов
            if server_name.lower() == "brave-search":
                # Заранее знаем инструменты для brave-search
                lazy_tools = [
                    self.LazySmitheryTool({
                        'name': 'brave_web_search',
                        'description': 'Поиск в интернете с помощью Brave Search API'
                    }, server_name),
                    self.LazySmitheryTool({
                        'name': 'brave_local_search',
                        'description': 'Поиск локальных мест и бизнесов'
                    }, server_name)
                ]
            elif 'tools' in server:
                # Если в данных сервера уже есть список инструментов
                for tool_data in server.get('tools', []):
                    lazy_tools.append(self.LazySmitheryTool(tool_data, server_name))
            else:
                # Создаем минимум один инструмент на основе данных сервера
                lazy_tools.append(self.LazySmitheryTool({
                    'name': f"tool_{server_name.lower().replace(' ', '_')}",
                    'description': f"Инструмент для сервера {server_name}"
                }, server_name))
            
            # Преобразуем LazySmitheryTool в словари для API
            result[server_name] = [tool.to_dict() for tool in lazy_tools]
            logger.info(f"[DEBUG] Добавлено {len(lazy_tools)} ленивых инструментов для сервера '{server_name}'")
        
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

def get_smithery_tools_adapter() -> Optional[SmitheryToolsAdapter]:
    """
    Возвращает экземпляр адаптера Smithery Tools.
    
    Returns:
        Экземпляр адаптера Smithery Tools или None, если адаптер не может быть создан.
    """
    global _smithery_tools_adapter_instance
    try:
        if _smithery_tools_adapter_instance is None:
            from tools.gopiai_integration.smithery_client import SmitheryClient
            # Проверяем, можно ли создать клиент
            client = SmitheryClient()
            if not client.api_key:
                logger.warning("Не удалось создать SmitheryClient: отсутствует API ключ")
                return None
                
            # Тестовый запрос для проверки работы клиента
            try:
                # Попытка выполнить запрос к реестру
                test_result = client.list_servers(refresh=True)
                if test_result is None or not isinstance(test_result, list) and not isinstance(test_result, dict):
                    logger.warning(f"Некорректный ответ от Smithery API: {type(test_result)}")
                    return None
            except Exception as e:
                logger.error(f"Ошибка при тестовом запросе к Smithery API: {e}")
                return None
            
            # Если все проверки пройдены, создаем адаптер
            _smithery_tools_adapter_instance = SmitheryToolsAdapter()
        return _smithery_tools_adapter_instance
    except Exception as e:
        logger.error(f"Ошибка при создании SmitheryToolsAdapter: {e}")
        return None
