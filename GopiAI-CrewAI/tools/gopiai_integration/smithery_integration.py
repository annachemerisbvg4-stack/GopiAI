"""
Интеграция Smithery MCP с ассистентом GopiAI

Этот модуль предоставляет интеграцию Smithery MCP с ассистентом GopiAI,
позволяя использовать MCP инструменты в чате с ассистентом.
"""

import logging
import json
from typing import Dict, List, Any, Optional

from .smithery_tools import get_smithery_tools_adapter
from .system_prompts import get_system_prompts

# Инициализируем логгер
logger = logging.getLogger(__name__)

class SmitheryIntegration:
    """
    Интеграция Smithery MCP с ассистентом GopiAI.
    
    Обеспечивает интеграцию MCP инструментов с системой промптов и обработчиками запросов.
    """
    
    def __init__(self):
        """Инициализация интеграции Smithery MCP."""
        self.tools_adapter = get_smithery_tools_adapter()
        self.prompts_manager = get_system_prompts()
        self.available_tools = {}
        
    def initialize(self):
        """Загружает доступные серверы и инструменты MCP."""
        try:
            logger.info("Инициализация интеграции Smithery MCP...")
            
            # Проверяем, что адаптер существует
            if self.tools_adapter is None:
                logger.warning("Адаптер Smithery MCP не создан. Создаем заглушки инструментов.")
                # Создаем заглушки для известных серверов и инструментов
                self.available_tools = {
                    "brave-search": [
                        {"name": "brave_web_search", "description": "Поиск в интернете с помощью Brave Search API"},
                        {"name": "brave_local_search", "description": "Поиск локальных мест и бизнесов"}
                    ],
                    "mcp-playwright": [
                        {"name": "playwright_navigate", "description": "Открыть URL в браузере"},
                        {"name": "playwright_click", "description": "Кликнуть по элементу на странице"},
                        {"name": "playwright_screenshot", "description": "Сделать скриншот страницы"}
                    ],
                    "puppeteer": [
                        {"name": "puppeteer_navigate", "description": "Открыть URL в браузере Puppeteer"},
                        {"name": "puppeteer_screenshot", "description": "Сделать скриншот в Puppeteer"}
                    ],
                    "serena": [
                        {"name": "activate_project", "description": "Активировать проект в Serena"},
                        {"name": "read_file", "description": "Прочитать содержимое файла"},
                        {"name": "create_text_file", "description": "Создать новый файл"}
                    ]
                }
                total_tools = sum(len(tools) for tools in self.available_tools.values())
                logger.info(f"Создано {total_tools} заглушек инструментов для {len(self.available_tools)} известных серверов")
                return True
            
            # Если адаптер существует, попытаемся загрузить инструменты
            self.available_tools = self.tools_adapter.get_all_available_tools()
            logger.info(f"Загружено {sum(len(tools) for tools in self.available_tools.values())} инструментов из {len(self.available_tools)} серверов")
            return True
        except Exception as e:
            logger.error(f"Ошибка при инициализации Smithery MCP: {e}")
            # Если произошла ошибка, создаем пустой словарь
            self.available_tools = {}
            return False
        
    def get_available_tools_for_ui(self) -> List[Dict]:
        """
        Получает список доступных MCP инструментов для отображения в UI.
        
        Returns:
            Список словарей с описаниями инструментов.
        """
        try:
            # Если инструменты уже загружены, используем их
            if self.available_tools:
                # Формируем список описаний инструментов для UI
                tools = []
                for server_name, server_tools in self.available_tools.items():
                    for tool in server_tools:
                        tools.append({
                            'id': f"mcp_{server_name}_{tool['name']}",
                            'name': tool.get('name', 'Неизвестный инструмент'),
                            'description': tool.get('description', 'Описание отсутствует'),
                            'server_name': server_name
                        })
                return tools
            # Иначе получаем описания через адаптер
            return self.tools_adapter.get_tool_descriptions()
        except Exception as e:
            logger.error(f"Ошибка при получении списка MCP инструментов: {e}")
            return []
    
    def handle_mcp_tool_request(self, message: str, tool_data: Dict) -> Dict:
        """
        Обрабатывает запрос пользователя к MCP инструменту.
        
        Args:
            message: Текст запроса пользователя.
            tool_data: Данные о выбранном инструменте.
            
        Returns:
            Результат выполнения инструмента или сообщение об ошибке.
        """
        try:
            # Проверяем, что у нас есть все необходимые данные
            if not tool_data or 'id' not in tool_data:
                return {"response": "Ошибка: Неверные данные инструмента"}
            
            tool_id = tool_data.get('id')
            
            # Проверяем, что это MCP инструмент
            if not tool_id.startswith("mcp_"):
                return {"response": "Ошибка: Указан не MCP инструмент"}
                
            # Выполняем запрос к инструменту
            result = self.tools_adapter.process_mcp_tool_request(tool_id, message)
            
            # Форматируем ответ для ассистента
            if result.get('success', False):
                tool_result = result.get('result', {})
                
                # Пытаемся форматировать результат для более читаемого вывода
                formatted_result = self._format_tool_result(tool_result)
                
                return {
                    "response": formatted_result,
                    "mcp_result": tool_result  # Сохраняем оригинальный результат
                }
            else:
                error = result.get('error', 'Неизвестная ошибка')
                return {"response": f"Ошибка при выполнении MCP инструмента: {error}"}
                
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса к MCP инструменту: {e}")
            return {"response": f"Произошла ошибка при обработке запроса: {str(e)}"}
    
    def _format_tool_result(self, result: Any) -> str:
        """
        Форматирует результат выполнения инструмента для ответа пользователю.
        
        Args:
            result: Результат выполнения инструмента.
            
        Returns:
            Отформатированный текст ответа.
        """
        try:
            # Если результат - строка, возвращаем её
            if isinstance(result, str):
                return result
                
            # Если результат - словарь или список, форматируем его для вывода
            if isinstance(result, (dict, list)):
                # Проверяем наличие специальных полей для форматирования
                if isinstance(result, dict):
                    # Приоритетные поля, которые могут содержать основной результат
                    for key in ['content', 'text', 'answer', 'result', 'message', 'response']:
                        if key in result and isinstance(result[key], str):
                            return result[key]
                
                # Если специальных полей нет, возвращаем весь результат как JSON
                return json.dumps(result, ensure_ascii=False, indent=2)
                
            # Для остальных типов просто преобразуем в строку
            return str(result)
            
        except Exception as e:
            logger.error(f"Ошибка при форматировании результата инструмента: {e}")
            return str(result)  # Возвращаем результат как есть в случае ошибки
    
    def get_mcp_tool_prompt(self, tool_data: Dict) -> str:
        """
        Получает промпт для работы с MCP инструментом.
        
        Args:
            tool_data: Данные о выбранном инструменте.
            
        Returns:
            Текст промпта для инструмента.
        """
        try:
            tool_name = tool_data.get('name', 'Неизвестный инструмент')
            description = tool_data.get('description', '')
            server = tool_data.get('server', '')
            
            # Пытаемся получить больше информации об инструменте
            original_info = tool_data.get('original_info', {})
            parameters = original_info.get('parameters', {})
            
            # Формируем промпт
            prompt = f"## MCP Инструмент: {tool_name}\n\n"
            
            if description:
                prompt += f"{description}\n\n"
                
            if server:
                prompt += f"Сервер: {server}\n\n"
                
            # Добавляем информацию о параметрах, если она есть
            if parameters:
                prompt += "### Параметры:\n"
                for param_name, param_info in parameters.items():
                    param_desc = param_info.get('description', 'Нет описания')
                    prompt += f"- `{param_name}`: {param_desc}\n"
                    
            # Добавляем инструкцию по использованию
            prompt += "\n### Как использовать:\n"
            prompt += "Отправь свой запрос, и он будет обработан этим инструментом. "
            prompt += "Старайся формулировать запросы четко и конкретно для получения наилучших результатов."
            
            return prompt
            
        except Exception as e:
            logger.error(f"Ошибка при формировании промпта для MCP инструмента: {e}")
            return "MCP инструмент активирован. Отправьте ваш запрос для обработки."

# Синглтон для повторного использования интеграции
_smithery_integration_instance = None

def get_smithery_integration() -> Optional[SmitheryIntegration]:
    """
    Возвращает экземпляр интеграции Smithery.
    Инициализация выполняется с обработкой ошибок.
    
    Returns:
        Экземпляр интеграции Smithery или None, если инициализация невозможна.
    """
    global _smithery_integration_instance
    try:
        if _smithery_integration_instance is None:
            # Для работы интеграции нужен рабочий tools_adapter
            tools_adapter = get_smithery_tools_adapter()
            if not tools_adapter:
                logger.warning("Адаптер инструментов Smithery не инициализирован. Интеграция недоступна.")
                return None
                
            _smithery_integration_instance = SmitheryIntegration()
            logger.info("Интеграция Smithery MCP успешно инициализирована")
        return _smithery_integration_instance
    except Exception as e:
        logger.error(f"Ошибка при инициализации интеграции Smithery: {e}")
        return None
