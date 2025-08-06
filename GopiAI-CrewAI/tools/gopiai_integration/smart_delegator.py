# --- START OF FILE smart_delegator.py (ВОССТАНОВЛЕННАЯ ЛОГИКА) ---

import logging
import json
import time
import traceback
import sys
import os
from typing import Dict, List, Any, Optional
import re # Added for command extraction

# Импортируем модуль ротации моделей
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from llm_rotation_config import select_llm_model_safe, rate_limit_monitor

# Импортируем RAGSystem
from typing import Any as _Any, Optional as _Optional  # aliases for protocol hints
try:
    from rag_system import RAGSystem as ExternalRAGSystem  # type: ignore
except ImportError:
    ExternalRAGSystem = None  # type: ignore

class RAGSystemProtocol:  # typing helper; not used for runtime isinstance
    embeddings: _Any
    def get_context_for_prompt(self, message: str) -> _Optional[str]: ...
# Keep local RAGSystem stub purely for fallback type
class RAGSystem:  # runtime stub
    pass

# Импортируем litellm
try:
    import litellm
except ImportError:
    litellm = None  # заглушка, чтобы избежать NameError
    logging.getLogger(__name__).warning("litellm не установлен, используем заглушку")
    # Можно добавить заглушку позже

# Импортируем наш модуль системных промптов
from .system_prompts import get_system_prompts

# Импорт для типов безопасности (используются ниже) с мягким fallback
try:
    from google.generativeai.types.safety_types import HarmCategory, HarmBlockThreshold  # type: ignore
except Exception:
    HarmCategory = None  # type: ignore
    HarmBlockThreshold = None  # type: ignore
# Старый MCP импорт удален, используем новую систему инструкций
# from tools.gopiai_integration.mcp_integration_fixed import get_mcp_tools_manager
from .local_mcp_tools import get_local_mcp_tools
from .command_executor import CommandExecutor
from .response_formatter import ResponseFormatter
from .openrouter_client import get_openrouter_client
from .model_config_manager import get_model_config_manager, ModelProvider

# Инициализируем логгер перед использованием
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SmartDelegator:
    def __init__(self, rag_system: Optional[RAGSystem] = None, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.rag_system = rag_system  # type: ignore[assignment]
        self.rag_available = bool(
            rag_system is not None and hasattr(rag_system, 'embeddings') and getattr(rag_system, 'embeddings', None) is not None
        )
        
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
        
        # Устаревшая внешняя MCP интеграция удалена
        # Используем только локальные инструменты и новую систему ToolsInstructionManager
        self.mcp_manager = None
        self.mcp_available = False
        logger.info("[INFO] Внешняя MCP интеграция отключена, используем локальные инструменты")
        
        # Инициализируем исполнитель команд для обработки ответов Gemini
        try:
            self.command_executor = CommandExecutor()
            logger.info("[OK] CommandExecutor инициализирован для обработки команд Gemini")
        except Exception as e:
            self.command_executor = None
            logger.warning(f"[WARNING] Не удалось инициализировать CommandExecutor: {str(e)}")
        
        # Инициализируем форматировщик ответов для чистого отображения
        try:
            self.response_formatter = ResponseFormatter()
            logger.info("[OK] ResponseFormatter инициализирован для фильтрации JSON и HTML")
        except Exception as e:
            self.response_formatter = None
            logger.warning(f"[WARNING] Не удалось инициализировать ResponseFormatter: {str(e)}")
        
        # Инициализируем менеджер конфигураций моделей
        try:
            self.model_config_manager = get_model_config_manager()
            logger.info("[OK] ModelConfigurationManager инициализирован")
        except Exception as e:
            self.model_config_manager = None
            logger.warning(f"[WARNING] Не удалось инициализировать ModelConfigurationManager: {str(e)}")
        
        # Инициализируем OpenRouter клиент
        try:
            self.openrouter_client = get_openrouter_client()
            if self.openrouter_client.test_connection():
                logger.info("[OK] OpenRouter клиент инициализирован и подключен")
                # Загружаем модели OpenRouter в фоновом режиме
                self._load_openrouter_models_async()
            else:
                logger.info("[INFO] OpenRouter клиент инициализирован, но нет подключения (возможно, нет API ключа)")
        except Exception as e:
            self.openrouter_client = None
            logger.warning(f"[WARNING] Не удалось инициализировать OpenRouter клиент: {str(e)}")
        
        if self.rag_available:
            try:
                rec_count = getattr(getattr(rag_system, 'embeddings', None), 'count', lambda: 'unknown')()
            except Exception:
                rec_count = 'unknown'
            logger.info(f"[OK] RAG system passed to SmartDelegator. Records: {rec_count}")
        else:
            logger.warning("[WARNING] RAG system not passed or not initialized.")

    def process_request(self, message: str, metadata: Dict) -> Dict:
        """
        Главный метод обработки. Анализирует, получает контекст и вызывает LLM.
        """
        start_time = time.time()
        
        # 0. Обрабатываем информацию о выбранной модели из UI
        preferred_provider = metadata.get('preferred_provider')
        preferred_model = metadata.get('preferred_model')
        model_info = metadata.get('model_info')
        
        if preferred_provider and preferred_model:
            logger.info(f"[MODEL-SELECTION] UI запросил использование {preferred_provider} модели: {preferred_model}")
            
            # Устанавливаем выбранную модель
            if preferred_provider == 'openrouter' and self.model_config_manager:
                try:
                    success = self.set_model('openrouter', preferred_model)
                    if success:
                        logger.info(f"[MODEL-SELECTION] ✅ Успешно переключились на OpenRouter модель: {preferred_model}")
                    else:
                        logger.warning(f"[MODEL-SELECTION] ⚠️ Не удалось переключиться на OpenRouter модель: {preferred_model}")
                except Exception as e:
                    logger.error(f"[MODEL-SELECTION] ❌ Ошибка переключения на OpenRouter: {e}")
            elif preferred_provider == 'gemini':
                try:
                    success = self.switch_to_provider('gemini')
                    if success:
                        logger.info(f"[MODEL-SELECTION] ✅ Успешно переключились на Gemini")
                    else:
                        logger.warning(f"[MODEL-SELECTION] ⚠️ Не удалось переключиться на Gemini")
                except Exception as e:
                    logger.error(f"[MODEL-SELECTION] ❌ Ошибка переключения на Gemini: {e}")
        else:
            logger.info("[MODEL-SELECTION] UI не указал предпочтительную модель, используем настройки по умолчанию")
        
        # 1. Анализ (пока заглушка, можно вернуть старую логику позже)
        analysis = {"type": "general", "complexity": 1, "requires_crewai": False}
        
        # 2. Получение RAG-контекста
        rag_context: Optional[str] = None
        if self.rag_available and self.rag_system:
            get_ctx = getattr(self.rag_system, 'get_context_for_prompt', None)
            if callable(get_ctx):
                try:
                    _ctx = get_ctx(message)
                    rag_context = str(_ctx) if isinstance(_ctx, (str, bytes)) else None
                except Exception as _e:
                    logger.warning(f"[RAG] Ошибка получения контекста: {_e}")
        
        # 3. Проверяем наличие запроса на вызов MCP инструмента
        tool_request = self._check_for_tool_request(message, metadata)
        
        if tool_request and self.local_tools_available:
            logger.info(f"Обнаружен запрос на использование инструмента: {tool_request['tool_name']} (сервер: {tool_request['server_name']})")
            
            # Вызываем MCP инструмент
            try:
                tool_response = self._call_tool(
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
                    tool_response,
                    metadata
                )
                
                # Вызываем LLM для формирования итогового ответа
                response_text = self._call_llm(messages)
                
            except Exception as e:
                logger.error(f"Ошибка при вызове MCP инструмента: {str(e)}")
                traceback.print_exc()
                response_text = f"Извините, произошла ошибка при использовании инструмента {tool_request['tool_name']}: {str(e)}"
        else:
            # 3. Обычное формирование промпта без инструментов
            messages = self._format_prompt(message, rag_context, metadata.get("chat_history", []), metadata)
            
            # 4. Вызов LLM
            response_text = self._call_llm(messages)
        
        # 5. Обработка команд из ответа LLM
        # СТРОГИЙ ПРОТОКОЛ: только валидный JSON { "tool": "...", "params": {...} } или массив таких объектов.
        # Любые эвристики/regex по свободному тексту отключены — защита от "lss*([^n]*)" и пр.
        if self.command_executor and response_text:
            try:
                logger.info("[COMMAND-PROCESSOR] Проверяем ответ на наличие СТРОГОГО JSON команд (strict_mode=True)...")
                # Унифицированный вызов процессора команд в строгом режиме
                updated_response, command_results = self.command_executor.process_gemini_response(
                    response_text,
                )
                # Дополнительная валидация верхнего уровня: допускаем только объекты/массивы с полями tool+params
                if command_results:
                    try:
                        parsed = json.loads(response_text)
                    except Exception:
                        parsed = None
                    def _valid_cmd(obj: Any) -> bool:
                        return isinstance(obj, dict) and "tool" in obj and "params" in obj and isinstance(obj["params"], dict)
                    is_valid_top_level = False
                    if isinstance(parsed, dict):
                        is_valid_top_level = _valid_cmd(parsed)
                    elif isinstance(parsed, list):
                        is_valid_top_level = all(_valid_cmd(x) for x in parsed)
                    # Если верхний уровень невалидный — не исполняем
                    if not is_valid_top_level:
                        logger.info("[COMMAND-PROCESSOR] Строгий JSON не валиден на верхнем уровне — команды не будут исполнены")
                    else:
                        logger.info(f"[COMMAND-PROCESSOR] Выполнено команд: {len(command_results)}")
                        response_text = updated_response
                        analysis['executed_commands'] = len(command_results)
                        analysis['command_results'] = command_results
                else:
                    logger.info("[COMMAND-PROCESSOR] Команды в ответе не найдены (строгий режим)")
            except Exception as e:
                logger.error(f"[COMMAND-PROCESSOR] Ошибка строгой обработки команд: {str(e)}")
                logger.error(f"[COMMAND-PROCESSOR] Traceback: {traceback.format_exc()}")
                # не прерываем выполнение
        
        elapsed = time.time() - start_time
        logger.info(f"[TIMING] Request processed in {elapsed:.2f} sec")
        
        # 6. Форматирование ответа для чистого отображения (НОВАЯ ФУНКЦИОНАЛЬНОСТЬ)
        analysis['analysis_time'] = elapsed
        
        # Добавляем информацию о используемой модели
        model_info = {}
        if self.model_config_manager:
            current_config = self.model_config_manager.get_current_configuration()
            if current_config:
                model_info = {
                    "provider": current_config.provider.value,
                    "model_id": current_config.model_id,
                    "display_name": current_config.display_name
                }
                logger.info(f"[RESPONSE-MODEL] Ответ сгенерирован моделью: {current_config.display_name} ({current_config.provider.value}/{current_config.model_id})")
        
        raw_response = {
            "response": response_text,
            "processed_with_crewai": False,
            "analysis": analysis,
            "model_info": model_info
        }
        
        # Применяем форматирование; гарантируем, что непустой текст не станет "Пустой ответ"
        if self.response_formatter:
            try:
                logger.info("[RESPONSE-FORMATTER] Применяем форматирование ответа...")
                formatted_response = self.response_formatter.format_for_chat(raw_response)
                
                user_content = formatted_response.get('user_content', response_text)
                if isinstance(user_content, str) and user_content.strip():
                    raw_response["response"] = user_content
                else:
                    # Если форматтер вернул пустоту — оставляем оригинальный response_text
                    raw_response["response"] = response_text
                
                raw_response["formatted"] = True
                raw_response["has_commands"] = bool(formatted_response.get('has_commands', False))
                
                logger.info(f"[RESPONSE-FORMATTER] Ответ отформатирован. Команды: {raw_response['has_commands']}")
            except Exception as e:
                logger.error(f"[RESPONSE-FORMATTER] Ошибка форматирования: {str(e)}")
                logger.error(f"[RESPONSE-FORMATTER] Traceback: {traceback.format_exc()}")
                # Не прерываем выполнение, просто логируем ошибку
        
        # 7. Возвращаем отформатированный результат
        return raw_response

    def _format_prompt(self, user_message: str, rag_context: Optional[str], chat_history: List[Dict], metadata: Dict) -> List[Dict]:
        """Формирует итоговый список сообщений для LLM."""
        
        # --- ИСПРАВЛЕНО: Добавляем проверку на None для chat_history ---
        if chat_history is None:
            chat_history = []

        # Получаем системные промпты из модуля system_prompts
        prompts_manager = get_system_prompts()
        
        # Проверяем наличие выбранного инструмента в метаданных
        tool_info = None
        for msg in chat_history[-5:]:  # Ищем в последних 5 сообщениях
            if isinstance(msg, dict) and msg.get('metadata') and msg['metadata'].get('tool'):
                tool_info = msg['metadata']['tool']
                break
        
        # Get system prompt with RAG context
        system_prompt = prompts_manager.get_assistant_prompt_with_context(rag_context)

        messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]

        # Log full prompt for debug
        logger.debug(f"DEBUG: Full prompt to LLM:\n{system_prompt}")
        
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
            
        # Add attachments handling (type-safe)
        processed_attachments = metadata.get('processed_attachments', [])
        for att in processed_attachments:
            if att.get('type') == 'image':
                # добавляем отдельно, чтобы тип контента был list[dict]
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "image_url",
                        "image_url": {"url": att.get('content', '')}
                    }]
                })
            elif att.get('type') == 'text':
                # всегда добавляем отдельным сообщением (строка)
                messages.append({
                    "role": "user",
                    "content": f"Attached file {att.get('name','file')}:\n{att.get('content','')}"
                })
        
        logger.debug(f"Итоговый промпт для LLM: {json.dumps(messages, indent=2, ensure_ascii=False)}")
        return messages

    def _check_for_tool_request(self, message: str, metadata: Dict) -> Optional[Dict]:
        """Проверяет, содержит ли сообщение запрос на использование MCP инструмента."""
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
        
        # Проверяем запросы на терминальные команды
        if any(keyword in message_lower for keyword in ['terminal', 'command', 'execute shell', 'run in terminal']):
            cmd_match = re.search(r'(?:terminal|command|execute shell|run in terminal):?\s*(.+)', message, re.IGNORECASE)
            if cmd_match:
                command = cmd_match.group(1).strip()
                return {
                    'tool_name': 'terminal',
                    'server_name': 'local',
                    'params': {'command': command}
                }
        
        return None
        
    def _call_tool(self, tool_name: str, server_name: str, params: Dict) -> Dict:
        """Вызывает MCP инструмент через MCPToolsManager или локальные инструменты."""
        logger.info(f"Вызов MCP инструмента {tool_name} на сервере {server_name} с параметрами: {params}")
        
        # Если это локальный инструмент
        if server_name == 'local':
            if not self.local_tools_available or not self.local_tools:
                raise Exception("Локальные MCP инструменты не инициализированы или недоступны")
            
            # Добавляем special handling for terminal
            if tool_name == 'terminal':
                from .terminal_tool import TerminalTool
                terminal_tool = TerminalTool()
                return terminal_tool._run(params.get('command', ''))
            
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
                                      tool_response: Dict, metadata: Dict) -> List[Dict]:
        """
        Формирует промпт с результатами выполнения инструмента.
        """
        # Получаем базовый промпт
        messages = self._format_prompt(user_message, rag_context, chat_history, metadata)
        
        # Добавляем результаты инструмента к запросу пользователя
        tool_result_message = {
            "role": "assistant",
            "content": f"Я использовал инструмент '{tool_request['tool_name']}' и получил следующий результат:\n```json\n{json.dumps(tool_response, ensure_ascii=False, indent=2)}\n```\n\nТеперь я проанализирую этот результат и отвечу на ваш запрос."
        }
        
        messages.append(tool_result_message)
        
        return messages
    
    def _convert_to_gemini_format(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        gemini_messages = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content')
            if isinstance(content, str):
                gemini_messages.append({'role': role, 'parts': [{'text': content}]})
            elif isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, str):
                        parts.append({'text': item})
                    elif isinstance(item, dict) and 'type' in item:
                        if item['type'] == 'text':
                            parts.append({'text': item.get('text', '')})
                        elif item['type'] == 'image_url':
                            url = item['image_url'].get('url', '')
                            if ',' in url:
                                mime, data = url.split(',', 1)
                                mime = mime.split(';')[0].split(':')[1]
                                parts.append({'inline_data': {'mime_type': mime, 'data': data}})
                if parts:
                    gemini_messages.append({'role': role, 'parts': parts})
            else:
                logger.warning(f"Skipping unsupported message format: {msg}")
        return gemini_messages

    def _call_llm(self, messages: List[Dict]) -> str:
        """
        Вызывает языковую модель, используя litellm и систему ротации моделей.
        """
        logger.info("[CRITICAL-DEBUG] НАЧАЛО _call_llm")
        logger.info(f"[CRITICAL-DEBUG] messages_count: {len(messages)}")
        logger.info(f"[CRITICAL-DEBUG] model_config_manager: {self.model_config_manager is not None}")
        
        # Инициализируем estimated_tokens в начале метода для использования в блоке except
        estimated_tokens = 0
        
        try:
            # Выводим длину системного промпта для диагностики
            system_prompt_len = len(messages[0]['content']) if messages and messages[0]['role'] == 'system' else 0
            logger.info(f"[LLM] Длина системного промпта: {system_prompt_len} символов")
            
            # Оценка количества токенов (примерно)
            total_text = '\n'.join([
                '\n'.join(str(item.get('text', '') if isinstance(item, dict) else str(item)) for item in msg.get('content', [])) 
                if isinstance(msg.get('content'), list) else str(msg.get('content', '')) 
                for msg in messages
            ])
            estimated_tokens = len(total_text) // 4  # Примерная оценка: 4 символа на токen
            
            # Проверяем, есть ли текущая конфигурация модели (выбранная пользователем)
            current_config = None
            if self.model_config_manager:
                current_config = self.model_config_manager.get_current_configuration()
            
            if current_config and current_config.is_available():
                # Используем выбранную пользователем модель
                model_id = current_config.model_id
                logger.info(f"[LLM] Используем выбранную пользователем модель: {model_id} ({current_config.display_name})")
                logger.info(f"[LLM] Провайдер: {current_config.provider.value}")
            else:
                # Выбор модели с использованием ротации (только если нет выбранной модели)
                has_image = any(
                    isinstance(msg.get('content'), list) and any(item.get('type') == 'image_url' for item in msg['content'])
                    for msg in messages if msg.get('role') == 'user'
                )
                task_type = 'vision' if has_image else 'dialog'
                logger.info(f"[LLM-DEBUG] Определен тип задачи: {task_type}, токенов: {estimated_tokens}")
                
                model_cfg = select_llm_model_safe(task_type, tokens=estimated_tokens)
                logger.info(f"[LLM-DEBUG] Результат select_llm_model_safe: {model_cfg}")
                model_id = None
                if isinstance(model_cfg, dict):
                    model_id = model_cfg.get('id') or model_cfg.get('model_id') or model_cfg.get('name')
                elif isinstance(model_cfg, str):
                    model_id = model_cfg
                
                if not model_id:
                    # Если не удалось выбрать модель, пробуем другие типы задач
                    logger.info(f"[LLM-DEBUG] Пробуем тип 'code'")
                    model_cfg = select_llm_model_safe("code", tokens=estimated_tokens)
                    model_id = None
                    if isinstance(model_cfg, dict):
                        model_id = model_cfg.get('id') or model_cfg.get('model_id') or model_cfg.get('name')
                    elif isinstance(model_cfg, str):
                        model_id = model_cfg
                    logger.info(f"[LLM-DEBUG] Результат для 'code': {model_id}")
                if not model_id:
                    # Если всё ещё нет модели, используем резервную
                    model_id = "gemini/gemini-1.5-flash"
                    logger.warning(f"[LLM] Не удалось выбрать модель через ротацию, используем резервную: {model_id}")
                else:
                    logger.info(f"[LLM] Выбрана модель через ротацию: {model_id}")
                
            # 🔥 ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА
            logger.info(f"[LLM-DEBUG] Финальная модель: {model_id}")
            try:
                _is_gemini = isinstance(model_id, str) and ('gemini' in model_id.lower())
            except Exception:
                _is_gemini = False
            logger.info(f"[LLM-DEBUG] Проверка 'gemini' in model_id.lower(): {_is_gemini}")
            
            # Регистрируем использование модели
            try:
                if hasattr(rate_limit_monitor, 'register_use'):
                    # мягкая попытка: если ожидается dict-конфиг, завернём id в dict
                    try:
                        rate_limit_monitor.register_use({"id": model_id}, estimated_tokens)  # type: ignore[arg-type]
                    except Exception:
                        rate_limit_monitor.register_use(model_id, estimated_tokens)  # type: ignore[arg-type]
            except Exception as _e:
                logger.debug(f"[LLM] register_use мягко пропущен: {_e}")
            
            # 🔥 СПЕЦИАЛЬНАЯ ОБРАБОТКА ДЛЯ РАЗНЫХ ПРОВАЙДЕРОВ
            
            # OpenRouter модели - проверяем и по current_config, и по имени модели
            is_openrouter = (current_config and current_config.provider.value == 'openrouter') or \
                model_id.startswith('openrouter/')
            
            if is_openrouter:
                try:
                    logger.info(f"🌐 Используем OpenRouter модель: {model_id}")
                    if litellm is None:
                        raise RuntimeError("litellm недоступен")
                    api_key = os.getenv('OPENROUTER_API_KEY')
                    logger.debug(f"[DEBUG] OPENROUTER_API_KEY найден: {'Да' if api_key else 'Нет'}")
                    if api_key:
                        logger.debug(f"[DEBUG] API ключ начинается с: {api_key[:10]}...")
                    if not api_key:
                        raise ValueError("Не найден API ключ для OpenRouter (OPENROUTER_API_KEY)")

                    final_model = model_id if str(model_id).startswith('openrouter/') else f"openrouter/{model_id}"
                    logger.info(f"[LLM-DEBUG] Отправляем запрос в OpenRouter: final_model={final_model}, messages_count={len(messages)}")

                    # Пробуем до 2-х ретраев, затем fallback на альтернативные free модели, если доступны
                    attempts = 0
                    max_attempts = 2
                    last_err: Optional[Exception] = None

                    while attempts <= max_attempts:
                        try:
                            response = litellm.completion(
                                model=str(final_model),
                                messages=messages,
                                temperature=0.2,
                                max_tokens=2000,
                                api_key=api_key,
                                api_base="https://openrouter.ai/api/v1"
                            )
                            resp_text = self._extract_text(response)
                            if isinstance(resp_text, str) and resp_text.strip():
                                logger.info(f"✅ OpenRouter вернул непустой ответ: {len(resp_text)} символов")
                                return resp_text
                            logger.error("[LLM-DEBUG] Не удалось извлечь текст из ответа OpenRouter")
                            return "Пустой ответ от OpenRouter модели"
                        except Exception as req_err:
                            last_err = req_err
                            err_str = str(req_err).lower()
                            logger.warning(f"[OpenRouter] Ошибка попытки {attempts+1}/{max_attempts+1}: {req_err}")

                            # Если это rate-limit/429 — пробуем ретрай с бэкоффом, затем fallback
                            if any(k in err_str for k in ["429", "rate limit", "too many requests", "rate_limited", "temporarily"]):
                                if attempts < max_attempts:
                                    delay = 0.3 * (attempts + 1)
                                    logger.info(f"[OpenRouter] Backoff {delay:.2f}s и повтор запроса")
                                    time.sleep(delay)
                                    attempts += 1
                                    continue
                                # fallback: попробовать альтернативную free модель через модельный менеджер, если он есть
                                alt_model = None
                                try:
                                    if self.model_config_manager:
                                        candidates = self.model_config_manager.get_configurations_by_provider(ModelProvider.OPENROUTER)
                                        # вначале free модели, отличные от текущей
                                        free_candidates = [c for c in candidates if getattr(c, "is_free", False) and c.model_id != model_id]
                                        if free_candidates:
                                            alt_model = f"openrouter/{free_candidates[0].model_id}"
                                except Exception as alt_err:
                                    logger.debug(f"[OpenRouter] Не удалось получить альтернативные модели: {alt_err}")

                                if alt_model:
                                    logger.info(f"[OpenRouter] Переключаемся на альтернативную free модель: {alt_model}")
                                    final_model = alt_model
                                    attempts = 0  # перезапускаем попытки для новой модели
                                    continue
                            # любые другие ошибки — выходим в общий обработчик
                            break

                    # если добрались сюда — не удалось получить ответ
                    if last_err:
                        logger.error(f"❌ Ошибка OpenRouter после ретраев/фолбэка: {last_err}")
                    return "Пустой ответ от OpenRouter модели"
                except Exception as e:
                    logger.error(f"❌ Ошибка OpenRouter: {str(e)}")
                    # Продолжаем со стандартным litellm
            
            # 🔥 КАСТОМНЫЙ ОБХОД ОГРАНИЧЕНИЙ GEMINI API!
            # Используем наш GeminiDirectClient вместо стандартного Google API
            elif isinstance(model_id, str) and 'gemini' in model_id.lower():
                try:
                    # Импортируем наш кастомный клиент
                    from .gemini_direct_client import GeminiDirectClient
                    
                    # Создаем кастомный клиент БЕЗ safetySettings
                    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
                    if not api_key:
                        raise ValueError("Не найден API ключ для Google/Gemini")
                    
                    client = GeminiDirectClient(
                        api_key=api_key,
                        model=model_id.split('/')[-1]  # Извлекаем имя модели
                    )
                    
                    logger.info(f"🔥 Используем GeminiDirectClient для обхода ограничений безопасности: {model_id}")
                    
                    # Преобразуем сообщения в формат, понятный нашему клиенту
                    logger.info(f"[LLM-DEBUG] Отправляем запрос в GeminiDirectClient: model={model_id}, messages_count={len(messages)}")
                    
                    response = client.generate_text(messages)
                    
                    logger.info(f"[LLM-DEBUG] Получен ответ от GeminiDirectClient: '{response[:100] if response else 'None'}...' (длина: {len(response) if response else 0})")
                    
                    if response and response.strip():
                        logger.info(f"✅ Gemini вернул непустой ответ: {len(response)} символов")
                        return response
                    else:
                        logger.error(f"[LLM-DEBUG] Gemini вернул пустой ответ: '{response}'")
                        return "Пустой ответ от Gemini"
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка кастомного GeminiDirectClient: {str(e)}")
                    # Продолжаем со стандартным litellm
            else:
                logger.info(f"[CRITICAL-DEBUG] ОБЩАЯ ВЕТКА litellm: model_id={model_id}")
                
                # Получаем API ключ для Gemini если это Gemini модель
                api_key = None
                if 'gemini' in model_id.lower():
                    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
                    logger.info(f"[CRITICAL-DEBUG] Gemini API key: {'НАЙДЕН' if api_key else 'ОТСУТСТВУЕТ'}")
                
                # Добавляем safety settings для ослабления фильтров
                safety_settings = None
                if HarmCategory is not None and HarmBlockThreshold is not None:
                    safety_settings = [
                        {
                            "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                            "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH
                        }
                    ]
                
                logger.info(f"[CRITICAL-DEBUG] Вызываем litellm.completion с model={model_id}, api_key={'ЕСТЬ' if api_key else 'НЕТ'}")
                
                completion_args = {
                    "model": str(model_id),
                    "messages": messages,
                    "temperature": 0.2,
                    "max_tokens": 2000
                }
                if safety_settings is not None:
                    completion_args["safety_settings"] = safety_settings
                
                if api_key:
                    completion_args["api_key"] = api_key
                
                if litellm is None:
                    raise RuntimeError("litellm недоступен")
                response = litellm.completion(**completion_args)
                
                logger.info(f"[LLM] Получен ответ от LLM: {str(response)[:200]}...")
                
                # Извлекаем текст ответа
                response_text = self._extract_text(response)
                if isinstance(response_text, str) and response_text.strip():
                    logger.info(f"[LLM] Извлеченный текст: {response_text[:100]}...")
                    return response_text
                    # Пустой контент считаем ошибкой провайдера → поднимем исключение
                    error_msg = "LLM вернул пустой ответ"
                    logger.error(f"[LLM] {error_msg}")
                    raise RuntimeError(error_msg)
                else:
                    error_msg = "LLM не вернул choices/текст"
                    logger.error(f"[LLM] {error_msg}")
                    raise RuntimeError(error_msg)
            
        except Exception as e:
            error_msg = f"Ошибка при вызове LLM: {str(e)}"
            logger.error(f"[CRITICAL-DEBUG] ОШИБКА в _call_llm: {error_msg}")
            logger.error(f"[LLM] Traceback: {traceback.format_exc()}")
            
            # Если ошибка связана с моделью, помечаем её как недоступную
            model_id = locals().get('model_id', None)
            if model_id and ("rate limit" in str(e).lower() or "quota exceeded" in str(e).lower()):
                logger.warning(f"[LLM] Модель {model_id} превысила лимиты (soft-handling)")
                # Мягкий fallback без прямого mark_model_unavailable
                try:
                    fb_cfg = select_llm_model_safe("dialog", tokens=estimated_tokens)
                    fb_id = None
                    if isinstance(fb_cfg, dict):
                        fb_id = fb_cfg.get('id') or fb_cfg.get('model_id') or fb_cfg.get('name')
                    elif isinstance(fb_cfg, str):
                        fb_id = fb_cfg
                    if fb_id and fb_id != model_id and litellm is not None:
                        logger.info(f"[LLM] Пробуем запасную модель: {fb_id}")
                        resp = litellm.completion(
                            model=str(fb_id),
                            messages=messages,
                            temperature=0.2,
                            max_tokens=2000
                        )
                        # попытка извлечь текст
                        fb_text = self._extract_text(resp)
                        if isinstance(fb_text, str) and fb_text.strip():
                            return fb_text
                except Exception as fallback_error:
                    logger.error(f"[LLM] Ошибка при использовании запасной модели: {fallback_error}")
            
            logger.error(f"[CRITICAL-DEBUG] ВОЗВРАЩАЕМ ОШИБКУ: {error_msg}")
            return f"Произошла ошибка при обработке запроса: {str(e)}"
        # гарантия возврата на случай непредвиденного пути
        return "Пустой ответ"
    
    def _extract_text(self, response: Any) -> Optional[str]:
        """
        Универсальное извлечение текста из ответа litellm:
        - ModelResponse с .choices
        - dict-подобные
        - стрим/кастомные обертки (если поддерживают аккумулирование)
        """
        try:
            # 1) Объекты с choices
            if hasattr(response, "choices"):
                choices = getattr(response, "choices", None)
                if choices:
                    first = choices[0]
                    msg = getattr(first, "message", None)
                    if msg is not None:
                        content = getattr(msg, "content", None)
                        if isinstance(content, str):
                            return content
            # 2) dict-подобные
            if isinstance(response, dict):
                ch = response.get("choices")
                if isinstance(ch, list) and ch:
                    msg = ch[0].get("message")
                    if isinstance(msg, dict):
                        content = msg.get("content")
                        if isinstance(content, str):
                            return content
            # 3) fallback: str
            if isinstance(response, str):
                return response
        except Exception as _e:
            logger.debug(f"[_extract_text] fallback with error: {_e}")
        return None

    def _load_openrouter_models_async(self):
        """Загружает модели OpenRouter в фоновом режиме"""
        try:
            if self.openrouter_client and self.model_config_manager:
                logger.debug("🔄 Загружаем модели OpenRouter...")
                
                # Получаем список моделей
                models = self.openrouter_client.get_models_sync()
                
                if models:
                    # Добавляем модели в менеджер конфигураций
                    self.model_config_manager.add_openrouter_models(models)
                    
                    free_count = len([m for m in models if m.is_free])
                    paid_count = len([m for m in models if not m.is_free])
                    
                    logger.debug(f"✅ Загружено {len(models)} моделей OpenRouter")
                    logger.debug(f"🆓 Бесплатных: {free_count}, 💰 Платных: {paid_count}")
                else:
                    logger.warning("⚠️ Не удалось загрузить модели OpenRouter")
                    
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки моделей OpenRouter: {e}")
    
    def switch_to_provider(self, provider: str) -> bool:
        """
        Переключается на указанного провайдера
        
        Args:
            provider: Название провайдера (gemini, openrouter)
            
        Returns:
            True, если переключение успешно
        """
        try:
            if not self.model_config_manager:
                logger.warning("⚠️ ModelConfigurationManager не инициализирован")
                return False
            
            # Преобразуем строку в ModelProvider
            provider_map = {
                'gemini': ModelProvider.GEMINI,
                'google': ModelProvider.GOOGLE,
                'openrouter': ModelProvider.OPENROUTER
            }
            
            model_provider = provider_map.get(provider.lower())
            if not model_provider:
                logger.warning(f"⚠️ Неизвестный провайдер: {provider}")
                return False
            
            success = self.model_config_manager.switch_to_provider(model_provider)
            
            if success:
                current_config = self.model_config_manager.get_current_configuration()
                logger.info(f"🎯 Переключение на {provider}: {current_config.display_name if current_config else 'неизвестная модель'}")
            else:
                logger.warning(f"⚠️ Не удалось переключиться на {provider}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Ошибка переключения провайдера: {e}")
            return False
    
    def set_model(self, provider: str, model_id: str) -> bool:
        """
        Устанавливает конкретную модель
        
        Args:
            provider: Название провайдера
            model_id: ID модели
            
        Returns:
            True, если модель установлена
        """
        try:
            if not self.model_config_manager:
                logger.warning("⚠️ ModelConfigurationManager не инициализирован")
                return False
            
            # Преобразуем строку в ModelProvider
            provider_map = {
                'gemini': ModelProvider.GEMINI,
                'google': ModelProvider.GOOGLE,
                'openrouter': ModelProvider.OPENROUTER
            }
            
            model_provider = provider_map.get(provider.lower())
            if not model_provider:
                logger.warning(f"⚠️ Неизвестный провайдер: {provider}")
                return False
            
            success = self.model_config_manager.set_current_configuration(model_provider, model_id)
            
            if success:
                logger.info(f"🎯 Установлена модель: {provider}/{model_id}")
            else:
                logger.warning(f"⚠️ Не удалось установить модель: {provider}/{model_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Ошибка установки модели: {e}")
            return False
    
    def get_current_model_info(self) -> Dict[str, Any]:
        """Возвращает информацию о текущей модели"""
        try:
            if not self.model_config_manager:
                return {"error": "ModelConfigurationManager не инициализирован"}
            
            current_config = self.model_config_manager.get_current_configuration()
            
            if current_config:
                return {
                    "provider": current_config.provider.value,
                    "model_id": current_config.model_id,
                    "display_name": current_config.display_name,
                    "is_available": current_config.is_available(),
                    "api_key_env": current_config.api_key_env,
                    "parameters": current_config.parameters
                }
            else:
                return {"error": "Нет активной конфигурации"}
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о модели: {e}")
            return {"error": str(e)}
    
    def get_available_models(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Возвращает список доступных моделей
        
        Args:
            provider: Фильтр по провайдеру (опционально)
            
        Returns:
            Список доступных моделей
        """
        try:
            if not self.model_config_manager:
                return []
            
            if provider:
                provider_map = {
                    'gemini': ModelProvider.GEMINI,
                    'google': ModelProvider.GOOGLE,
                    'openrouter': ModelProvider.OPENROUTER
                }
                
                model_provider = provider_map.get(provider.lower())
                if model_provider:
                    configs = self.model_config_manager.get_configurations_by_provider(model_provider)
                else:
                    configs = []
            else:
                configs = self.model_config_manager.get_all_configurations()
            
            # Преобразуем в словари
            models = []
            for config in configs:
                if config.is_available():  # Только доступные
                    models.append({
                        "provider": config.provider.value,
                        "model_id": config.model_id,
                        "display_name": config.display_name,
                        "is_default": config.is_default,
                        "parameters": config.parameters
                    })
            
            return models
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка моделей: {e}")
            return []
    
    def refresh_openrouter_models(self) -> bool:
        """Обновляет список моделей OpenRouter"""
        try:
            if not self.openrouter_client:
                logger.warning("⚠️ OpenRouter клиент не инициализирован")
                return False
            
            logger.debug("🔄 Обновляем список моделей OpenRouter...")
            
            # Принудительно обновляем кэш
            models = self.openrouter_client.get_models_sync(force_refresh=True)
            
            if models and self.model_config_manager:
                self.model_config_manager.add_openrouter_models(models)
                logger.debug(f"✅ Обновлено {len(models)} моделей OpenRouter")
                return True
            else:
                logger.warning("⚠️ Не удалось обновить модели OpenRouter")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления моделей OpenRouter: {e}")
            return False

# --- END OF FILE smart_delegator.py ---
