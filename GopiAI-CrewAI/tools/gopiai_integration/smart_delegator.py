# --- START OF FILE smart_delegator.py (ВОССТАНОВЛЕННАЯ ЛОГИКА) ---

import logging
import json
import time
import traceback
import sys
import os
from typing import Dict, List, Any, Optional

# Импортируем модуль ротации моделей
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm_rotation_config import select_llm_model_safe, rate_limit_monitor

# Импортируем наш модуль системных промптов
from .system_prompts import get_system_prompts
from .mcp_integration_fixed import SmitheryMCPManager, get_smithery_mcp_manager
from .local_mcp_tools import get_local_mcp_tools

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
        
        # Инициализируем локальные MCP инструменты
        try:
            self.local_tools = get_local_mcp_tools()
            self.local_tools_available = True
            local_tools_count = len(self.local_tools.get_available_tools())
            logger.info(f"[OK] Локальные MCP инструменты инициализированы. Доступно: {local_tools_count}")
        except Exception as e:
            self.local_tools = None
            self.local_tools_available = False
            logger.warning(f"[WARNING] Не удалось инициализировать локальные MCP инструменты: {str(e)}")
        
        # Инициализируем SmitheryMCPManager для доступа к внешним MCP инструментам
        try:
            self.mcp_manager = get_smithery_mcp_manager()
            self.mcp_available = True
            # Пробуем получить инструменты для проверки работоспособности
            try:
                import asyncio
                # Инициализируем менеджер
                asyncio.run(self.mcp_manager.initialize())
                mcp_tools = asyncio.run(self.mcp_manager.get_all_tools())
                mcp_tools_count = len(mcp_tools) if mcp_tools else 0
            except Exception as async_e:
                logger.warning(f"[WARNING] Не удалось получить внешние MCP инструменты: {str(async_e)}")
                mcp_tools_count = 0
            logger.info(f"[OK] Внешние MCP интеграция инициализирована. Доступно инструментов: {mcp_tools_count}")
        except Exception as e:
            self.mcp_manager = None
            self.mcp_available = False
            logger.warning(f"[WARNING] Не удалось инициализировать внешние MCP интеграцию: {str(e)}")
        
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
        
        if tool_request and (self.mcp_available or self.local_tools_available):
            logger.info(f"Обнаружен запрос на использование MCP инструмента: {tool_request['tool_name']} (сервер: {tool_request['server_name']})")
            
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
                server_name = tool_info.get('server_name', 'local')  # По умолчанию локальный
                params = tool_info.get('params', {})
                
                if tool_name:
                    return {
                        'tool_name': tool_name,
                        'server_name': server_name,
                        'params': params
                    }
        
        # Проверяем простые команды в тексте сообщения
        message_lower = message.lower()
        
        # Проверяем запросы на системную информацию
        if any(keyword in message_lower for keyword in ['системная информация', 'info', 'статус системы', 'system info']):
            return {
                'tool_name': 'system_info',
                'server_name': 'local',
                'params': {}
            }
        
        # Проверяем запросы на время
        if any(keyword in message_lower for keyword in ['время', 'текущее время', 'current time', 'сейчас времени']):
            return {
                'tool_name': 'time_helper',
                'server_name': 'local',
                'params': {'operation': 'current_time'}
            }
        
        # Проверяем запросы на статус проекта
        if any(keyword in message_lower for keyword in ['статус проекта', 'здоровье системы', 'project status', 'health check']):
            return {
                'tool_name': 'project_helper',
                'server_name': 'local',
                'params': {'action': 'health_check'}
            }
        
        return None
        
    def _call_mcp_tool(self, tool_name: str, server_name: str, params: Dict) -> Dict:
        """
        Вызывает MCP инструмент через MCPToolsManager или локальные инструменты.
        """
        logger.info(f"Вызов MCP инструмента {tool_name} на сервере {server_name} с параметрами: {params}")
        
        # Если это локальный инструмент
        if server_name == 'local':
            if not self.local_tools_available or not self.local_tools:
                raise Exception("Локальные MCP инструменты не инициализированы или недоступны")
            
            # Вызываем локальный инструмент
            result = self.local_tools.call_tool(tool_name, params)
            logger.info(f"Получен результат от локального инструмента: {str(result)[:200]}...")
            return result
        
        # Если это внешний инструмент
        else:
            if not self.mcp_available or not self.mcp_manager:
                raise Exception("Внешний MCP менеджер не инициализирован или недоступен")
            
            # Находим инструмент по имени
            tool = self.mcp_manager.get_tool_by_name(tool_name)
            if not tool:
                raise Exception(f"Внешний инструмент {tool_name} не найден")
            
            # Вызываем инструмент через MCPToolsManager
            result = self.mcp_manager.execute_tool(tool, **params)
            logger.info(f"Получен результат от внешнего MCP инструмента: {str(result)[:200]}...")
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
        Вызывает языковую модель, используя litellm и систему ротации моделей.
        """
        try:
            # Выводим длину системного промпта для диагностики
            system_prompt_len = len(messages[0]['content']) if messages and messages[0]['role'] == 'system' else 0
            logger.info(f"[LLM] Длина системного промпта: {system_prompt_len} символов")
            
            # Оценка количества токенов (примерно)
            total_text = '\n'.join([msg.get('content', '') for msg in messages])
            estimated_tokens = len(total_text) // 4  # Примерная оценка: 4 символа на токен
            
            # Выбор модели с использованием ротации
            model_id = select_llm_model_safe("dialog", tokens=estimated_tokens)
            if not model_id:
                # Если не удалось выбрать модель, пробуем другие типы задач
                model_id = select_llm_model_safe("code", tokens=estimated_tokens)
            if not model_id:
                # Если всё ещё нет модели, используем резервную
                model_id = "gemini/gemini-1.5-flash"
                logger.warning(f"[LLM] Не удалось выбрать модель через ротацию, используем резервную: {model_id}")
            else:
                logger.info(f"[LLM] Выбрана модель через ротацию: {model_id}")
            
            # Регистрируем использование модели
            if model_id in rate_limit_monitor.models:
                rate_limit_monitor.register_use(model_id, estimated_tokens)
            
            # Вызов LLM через litellm
            logger.info(f"[LLM] Отправляем запрос в модель {model_id}...")
            response = litellm.completion(
                model=model_id,
                messages=messages,
                temperature=0.2,
                max_tokens=2000
            )
            
            logger.info(f"[LLM] Получен ответ от LLM: {str(response)[:200]}...")
            
            # Извлекаем текст ответа
            if response and response.choices and len(response.choices) > 0:
                response_text = response.choices[0].message.content
                logger.info(f"[LLM] Извлеченный текст: {response_text[:100]}...")
                return response_text if response_text else "Пустой ответ от модели"
            else:
                logger.error("[LLM] Пустой ответ от модели")
                return "Пустой ответ от модели"
            
        except Exception as e:
            error_msg = f"Ошибка при вызове LLM: {str(e)}"
            logger.error(f"[LLM] {error_msg}")
            logger.error(f"[LLM] Traceback: {traceback.format_exc()}")
            
            # Если ошибка связана с моделью, помечаем её как недоступную
            if model_id and "rate limit" in str(e).lower() or "quota exceeded" in str(e).lower():
                logger.warning(f"[LLM] Модель {model_id} превысила лимиты, блокируем на 10 минут")
                rate_limit_monitor.mark_model_unavailable(model_id, duration=600)  # 10 минут
                
                # Пробуем другую модель
                fallback_model = select_llm_model_safe("dialog", tokens=estimated_tokens, exclude_models=[model_id])
                if fallback_model:
                    logger.info(f"[LLM] Пробуем запасную модель: {fallback_model}")
                    try:
                        response = litellm.completion(
                            model=fallback_model,
                            messages=messages,
                            temperature=0.2,
                            max_tokens=2000
                        )
                        if response and response.choices and len(response.choices) > 0:
                            return response.choices[0].message.content
                    except Exception as fallback_error:
                        logger.error(f"[LLM] Ошибка при использовании запасной модели: {fallback_error}")
            
            return f"Произошла ошибка при обработке запроса: {str(e)}"

# --- END OF FILE smart_delegator.py ---