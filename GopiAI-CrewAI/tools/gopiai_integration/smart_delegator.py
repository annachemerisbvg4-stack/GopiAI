# --- START OF FILE smart_delegator.py (ВОССТАНОВЛЕННАЯ ЛОГИКА) ---

import logging
import json
import time
import traceback
from typing import Dict, List, Any, Optional

# Импортируем наш модуль системных промптов
from .system_prompts import get_system_prompts
from .mcp_integration import MCPToolsManager, get_mcp_tools_manager

# Инициализируем логгер перед использованием
logger = logging.getLogger(__name__)

# Используем локальную заглушку litellm вместо реального модуля
try:
    import litellm
except ImportError:
    from .base import litellm_stub as litellm
    logger.warning("WARNING: Using litellm stub instead of actual litellm module")
from rag_system import get_rag_system, RAGSystem

class SmartDelegator:
    
    def __init__(self, rag_system: Optional[RAGSystem] = None, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.rag_system = rag_system
        self.rag_available = self.rag_system is not None and self.rag_system.embeddings is not None
        
        # Инициализируем MCPToolsManager для доступа к MCP инструментам
        try:
            import asyncio
            self.mcp_manager = get_mcp_tools_manager()
            self.mcp_available = True
            # Исправлено: правильный вызов асинхронной функции через asyncio.run
            mcp_tools = asyncio.run(self.mcp_manager.get_all_tools())
            mcp_tools_count = len(mcp_tools) if mcp_tools else 0
            logger.info(f"[OK] MCP интеграция инициализирована. Доступно инструментов: {mcp_tools_count}")
        except Exception as e:
            self.mcp_manager = None
            self.mcp_available = False
            logger.warning(f"[WARNING] Не удалось инициализировать MCP интеграцию: {str(e)}")
        
        if self.rag_available:
            logger.info(f"[OK] RAG system passed to SmartDelegator. Records: {self.rag_system.embeddings.count()}")
        else:
            logger.warning("[WARNING] RAG system not passed or not initialized.")

    def process_request(self, message: str, metadata: Dict) -> Dict:
        """
        Главный метод обработки. Анализирует, получает контекст и вызывает LLM.
        """
        start_time = time.time()
        
        # 1. Анализ (пока заглушка, можно вернуть старую логику позже)
        analysis = {"type": "general", "complexity": 1, "requires_crewai": False}
        
        # 2. Получение RAG-контекста
        rag_context = self.rag_system.get_context_for_prompt(message) if self.rag_available else None
        
        # 3. Проверяем наличие запроса на вызов MCP инструмента
        tool_request = self._check_for_tool_request(message, metadata)
        
        if tool_request and self.mcp_available:
            logger.info(f"Обнаружен запрос на использование MCP инструмента: {tool_request['tool_name']}")
            
            # Вызываем MCP инструмент
            try:
                tool_response = self._call_mcp_tool(
                    tool_request['tool_name'], 
                    tool_request['server_name'],
                    tool_request['params']
                )
                
                # Формируем ответ с результатами инструмента
                messages = self._format_prompt_with_tool_result(
                    message, 
                    rag_context, 
                    metadata.get("chat_history", []),
                    tool_request,
                    tool_response
                )
                
                # Вызываем LLM для формирования итогового ответа
                response_text = self._call_llm(messages)
                
            except Exception as e:
                logger.error(f"Ошибка при вызове MCP инструмента: {str(e)}")
                traceback.print_exc()
                response_text = f"Извините, произошла ошибка при использовании инструмента {tool_request['tool_name']}: {str(e)}"
        else:
            # 3. Обычное формирование промпта без инструментов
            messages = self._format_prompt(message, rag_context, metadata.get("chat_history", []))
            
            # 4. Вызов LLM
            response_text = self._call_llm(messages)
        
        elapsed = time.time() - start_time
        logger.info(f"[TIMING] Request processed in {elapsed:.2f} sec")
        
        # 5. Возвращаем результат в стандартном формате
        analysis['analysis_time'] = elapsed
        return {
            "response": response_text,
            "processed_with_crewai": False,
            "analysis": analysis
        }

    def _format_prompt(self, user_message: str, rag_context: Optional[str], chat_history: List[Dict]) -> List[Dict]:
        """Формирует итоговый список сообщений для LLM."""
        
        # Получаем системные промпты из модуля system_prompts
        prompts_manager = get_system_prompts()
        
        # Проверяем наличие выбранного инструмента в метаданных
        tool_info = None
        for msg in chat_history[-5:]:  # Ищем в последних 5 сообщениях
            if isinstance(msg, dict) and msg.get('metadata') and msg['metadata'].get('tool'):
                tool_info = msg['metadata']['tool']
                break
        
        # Получаем системный промпт с контекстом из RAG
        system_prompt = prompts_manager.get_assistant_prompt_with_context(rag_context)
        
        # Если есть информация об инструменте, добавляем ее в промпт
        if tool_info and isinstance(tool_info, dict):
            tool_name = tool_info.get('name', '') or tool_info.get('tool_id', '')
            tool_description = tool_info.get('description', '')
            tool_usage = tool_info.get('usage', '')
            
            if tool_name:
                system_prompt += f"\n\n## Выбранный инструмент: {tool_name}"
                if tool_description:
                    system_prompt += f"\n{tool_description}"
                if tool_usage:
                    system_prompt += f"\n\nПримеры использования:\n```\n{tool_usage}\n```"
            
        messages = [{"role": "system", "content": system_prompt}]
        
        # Добавляем краткосрочную память (историю чата)
        # Убираем системные сообщения и берем последние 20 реплик
        # Фильтруем сообщения: отсеиваем системные и служебные сообщения
        filtered_history = []
        for msg in chat_history:
            if msg.get("role") == "system":
                continue  # Пропускаем системные сообщения
                
            # Проверяем содержимое на наличие служебных сообщений
            content = msg.get("content", "")
            if content and isinstance(content, str):
                if "⏳ Обрабатываю запрос" in content:
                    continue  # Пропускаем заглушки запросов
                if "Произошла ошибка" in content:
                    continue  # Пропускаем сообщения об ошибках
            
            filtered_history.append(msg)
            
        # Берем только последние 20 сообщений после фильтрации
        history_to_add = filtered_history[-20:]  # Увеличено с 10 до 20 сообщений
        
        # Добавляем логирование размера окна кратковременной памяти
        logger.info(f"Окно кратковременной памяти: добавлено {len(history_to_add)} сообщений из {len(chat_history)} в истории")
        if len(history_to_add) > 0:
            logger.debug(f"Первое сообщение в окне: {history_to_add[0].get('role')}: {history_to_add[0].get('content')[:30]}...")
        messages.extend(history_to_add)
        
        # Добавляем текущий вопрос пользователя, если его еще нет в истории
        if not messages or messages[-1].get("content") != user_message:
            messages.append({"role": "user", "content": user_message})
            
        logger.debug(f"Итоговый промпт для LLM: {json.dumps(messages, indent=2, ensure_ascii=False)}")
        return messages

    def _check_for_tool_request(self, message: str, metadata: Dict) -> Optional[Dict]:
        """
        Проверяет, содержит ли сообщение запрос на использование MCP инструмента.
        Возвращает словарь с информацией об инструменте или None.
        """
        # Проверяем явный запрос в метаданных
        if metadata and isinstance(metadata, dict):
            tool_info = metadata.get('tool', None)
            if tool_info and isinstance(tool_info, dict):
                tool_name = tool_info.get('name', '') or tool_info.get('tool_id', '')
                server_name = tool_info.get('server_name', '')
                params = tool_info.get('params', {})
                
                if tool_name and server_name:
                    return {
                        'tool_name': tool_name,
                        'server_name': server_name,
                        'params': params
                    }
        
        # TODO: Можно добавить анализ текста сообщения для автоматического определения
        # запроса на использование инструмента
        
        return None
        
    def _call_mcp_tool(self, tool_name: str, server_name: str, params: Dict) -> Dict:
        """
        Вызывает MCP инструмент через MCPToolsManager и возвращает результат.
        """
        if not self.mcp_available or not self.mcp_manager:
            raise Exception("MCP менеджер не инициализирован или недоступен")
        
        logger.info(f"Вызов MCP инструмента {tool_name} на сервере {server_name} с параметрами: {params}")
        
        # Находим инструмент по имени
        tool = self.mcp_manager.get_tool_by_name(tool_name)
        if not tool:
            raise Exception(f"Инструмент {tool_name} не найден")
        
        # Вызываем инструмент через MCPToolsManager
        result = self.mcp_manager.execute_tool(tool, **params)
        
        logger.info(f"Получен результат от MCP инструмента: {str(result)[:200]}...")
        
        return result
    
    def _format_prompt_with_tool_result(self, user_message: str, rag_context: Optional[str], 
                                      chat_history: List[Dict], tool_request: Dict, 
                                      tool_response: Dict) -> List[Dict]:
        """
        Формирует промпт с результатами выполнения инструмента.
        """
        # Получаем базовый промпт
        messages = self._format_prompt(user_message, rag_context, chat_history)
        
        # Добавляем результаты инструмента к запросу пользователя
        tool_result_message = {
            "role": "assistant",
            "content": f"Я использовал инструмент '{tool_request['tool_name']}' и получил следующий результат:\n```json\n{json.dumps(tool_response, ensure_ascii=False, indent=2)}\n```\n\nТеперь я проанализирую этот результат и отвечу на ваш запрос."
        }
        
        messages.append(tool_result_message)
        
        return messages
    
    def _call_llm(self, messages: List[Dict]) -> str:
        """
        Вызывает языковую модель, используя litellm.
        """
        try:
            # Выводим длину системного промпта для диагностики
            system_prompt_len = len(messages[0]['content']) if messages and messages[0]['role'] == 'system' else 0
            logger.info(f"Длина системного промпта: {system_prompt_len} символов")
            
            # Вызов LLM через litellm
            response = litellm.completion(
                model="gemini/gemini-1.5-flash",
                messages=messages,
                temperature=0.2,
                max_tokens=2000
            )
            
            logger.debug(f"Получен ответ от LLM: {str(response)[:200]}...")
            
            # Извлекаем текст ответа
            response_text = response.choices[0].message.content if response and response.choices else ""
            return response_text
            
        except Exception as e:
            logger.error(f"Ошибка при вызове LLM: {str(e)}")
            traceback.print_exc()
            return f"Произошла ошибка при обработке запроса: {str(e)}"

# --- END OF FILE smart_delegator.py ---