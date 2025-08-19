import urllib.parse
import re

"""
🔌 CrewAI API Client
Клиент для интеграции с CrewAI через REST API
"""

import requests
import requests.exceptions
import threading
import time
import json
import logging
import logging.handlers
import os
import sys
from pathlib import Path
import base64
from typing import Dict, Any, List, Optional, Union

# Настройка логирования для CrewAI клиента
logger = logging.getLogger(__name__)

# Импортируем менеджер памяти для работы с историей чата
from ..memory.manager import MemoryManager

# Добавляем путь к модулю emotional_classifier
import sys
import os
print('Current working directory:', os.getcwd())
print('sys.path:', sys.path)

# Импортируем заглушки, так как gopiai_integration больше не используется
from gopiai.gopiai_integration_stub import (
    EmotionalClassifier,
    EmotionalState,
    AIRouterLLM,
    get_model_config_manager,
    get_tools_instruction_manager
)

EMOTIONAL_CLASSIFIER_AVAILABLE = False
TOOLS_INSTRUCTION_MANAGER_AVAILABLE = False

# Создаем директорию для логов, если её нет
# Используем текущую директорию или директорию приложения
try:
    # Пробуем получить путь к директории приложения
    app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    logs_dir = os.path.join(app_dir, 'logs')
    print(f"[DEBUG-LOGS-PATH] CrewAIClient пробуем путь 1: {logs_dir}")
    
    # Проверяем, что можем создать директорию по этому пути
    os.makedirs(logs_dir, exist_ok=True)
except Exception as e:
    print(f"[DEBUG-LOGS-PATH] Ошибка при создании первичного пути: {e}")
    
    # Используем текущую директорию
    logs_dir = os.path.join(os.getcwd(), 'logs')
    print(f"[DEBUG-LOGS-PATH] CrewAIClient используем текущую директорию: {logs_dir}")
    os.makedirs(logs_dir, exist_ok=True)

# Настраиваем файловый обработчик для логов CrewAI клиента
crewai_log_file = os.path.join(logs_dir, 'crewai_client.log')
file_handler = logging.FileHandler(crewai_log_file, mode='w', encoding='utf-8')  # mode='w' to overwrite

# Форматтер для логов
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# Устанавливаем уровень логирования для файла
file_handler.setLevel(logging.DEBUG)

# Добавляем обработчик к логгеру
logger.addHandler(file_handler)

# Устанавливаем уровень логирования для логгера
logger.setLevel(logging.DEBUG)

# --- NLP (spaCy) ---
try:
    import spacy
    # Загружаем обе модели (русскую и английскую)
    nlp_ru = spacy.load("ru_core_news_sm")
    nlp_en = spacy.load("en_core_web_sm")
    logger.info("✅ spaCy и языковые модели успешно загружены")
except Exception as e:
    logger.warning(f"⚠️ Не удалось загрузить spaCy или языковые модели: {e}")
    nlp_ru = None
    nlp_en = None

class CrewAIClient:
    """
    Клиент для взаимодействия с CrewAI API сервером

    Позволяет UI приложению использовать функциональность CrewAI,
    запущенного в отдельном окружении через REST API.
    """

    def __init__(self, base_url="http://127.0.0.1:5051"):  # Стандартный порт CrewAI API сервера
        self.base_url = base_url
        self.timeout = 30  # Таймаут для API запросов (в секундах)
        self._server_available = None
        self._last_check = 0

        # MCP клиент отключен по умолчанию, чтобы избежать ошибок отсутствия атрибута
        self.mcp_client = None
        
        # Инициализация эмоционального классификатора
        self.emotional_classifier = None
        if EMOTIONAL_CLASSIFIER_AVAILABLE and AIRouterLLM and EmotionalClassifier:
            try:
                # Создаем AI Router для эмоционального классификатора
                model_config_manager = None
                try:
                    from gopiai_integration.model_config_manager import get_model_config_manager
                    model_config_manager = get_model_config_manager()
                    logger.info("[INIT] ✅ ModelConfigManager успешно получен")
                except Exception as mcm_error:
                    logger.warning(f"[INIT] ⚠️ Не удалось получить ModelConfigManager: {mcm_error}")
                    logger.info("[INIT] ℹ️ Будет использована заглушка ModelConfigManager")
                
                # Создаем экземпляр AIRouterLLM с явной передачей model_config_manager
                # AIRouterLLM сам создаст заглушку, если model_config_manager=None
                ai_router = AIRouterLLM(model_config_manager=model_config_manager)
                
                # Проверяем, что model_config_manager успешно инициализирован в ai_router
                if hasattr(ai_router, 'model_config_manager') and ai_router.model_config_manager is not None:
                    self.emotional_classifier = EmotionalClassifier(ai_router)
                    logger.info("[INIT] ✅ Эмоциональный классификатор инициализирован с AI Router")
                else:
                    logger.error("[INIT] ❌ model_config_manager не инициализирован в AIRouterLLM")
                    self.emotional_classifier = None
            except Exception as e:
                logger.error(f"[INIT] ❌ Ошибка инициализации эмоционального классификатора: {e}")
                self.emotional_classifier = None
        else:
            logger.debug("[INIT] Эмоциональный классификатор недоступен или модули не импортированы")

    def brave_search_site(self, query):
        """
        Ищет сайт по запросу через Brave Search API и возвращает первый найденный url.
        """
        api_key = os.environ.get("BRAVE_API_KEY")
        if not api_key:
            logger.warning("BRAVE_API_KEY не найден в окружении!")
            return None
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
        params = {"q": query, "count": 3}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # Ищем первый внешний сайт (не brave.com)
                for item in data.get("web", {}).get("results", []):
                    link = item.get("url")
                    if link and not link.startswith("https://search.brave.com"):
                        return link
            else:
                logger.warning(f"Brave API error: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Ошибка Brave Search: {e}")
        return None

    def is_available(self, force_check=False):
        """Проверяет доступность CrewAI API сервера"""
        # Перепроверяем чаще, если предыдущая попытка показала, что сервер недоступен.
        current_time = time.time()
        cache_window = 5 if self._server_available is False else 30  # 5 сек, если сервер был оффлайн
        if (not force_check
                and self._server_available is not None
                and (current_time - self._last_check) < cache_window):
            return self._server_available

        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=self.timeout)
            self._server_available = response.status_code == 200
            self._last_check = current_time
            return self._server_available
        except requests.RequestException:
            self._server_available = False
            self._last_check = current_time
            return False

    def analyze_emotion(self, message_text, context=None):
        """
        Анализирует эмоциональное состояние сообщения
        
        Args:
            message_text: Текст сообщения для анализа
            context: Контекст диалога (список предыдущих сообщений)
            
        Returns:
            dict: Результат анализа эмоций или None, если анализ невозможен
        """
        if not self.emotional_classifier or not message_text or not isinstance(message_text, str):
            return None
            
        try:
            # Проверяем, что сообщение не является командой
            if message_text.startswith(('/', '!', '#')):
                return None
                
            # Анализируем эмоциональное состояние
            analysis = self.emotional_classifier.analyze_emotional_state(
                context or [], 
                message_text
            )
            
            # Возвращаем структурированные данные
            return {
                'primary_emotion': analysis.primary_emotion.value,
                'confidence': analysis.confidence,
                'intensity': analysis.emotional_intensity,
                'explanation': getattr(analysis, 'explanation', ''),
                'recommendations': getattr(analysis, 'recommendations', [])
            }
            
        except Exception as e:
            print(f"⚠️ Ошибка при анализе эмоций: {e}")
            return None
            
    def process_request(self, message: Union[str, Dict[str, Any]], force_crewai: bool = False, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Обработка всех типов CrewAI API и выбором оптимального обработчика
        
        Args:
            message: Входное сообщение (может быть строкой или JSON с данными)
            force_crewai: Принудительно отправить всё в CrewAI (игнорируя простые ответы)
            timeout: Таймаут ожидания в секундах
            
        Returns:
            dict: Ответ от API с полями 'response', 'command' (опционально) и 'emotion_analysis' (не всегда)
        """
        # Добавляем подробное логирование
        logger.debug(f"[REQUEST] Начало обработки сообщ. force_crewai={force_crewai}, timeout={timeout}")
        
        # Обрезаем сообщение в логах для читабельности
        if isinstance(message, dict):
            msg_text = message.get('message', '')
            msg_log = f"{msg_text[:50]}..." if len(msg_text) > 50 else msg_text
        else:
            msg_log = f"{message[:50]}..." if len(str(message)) > 50 else message
            
        logger.debug(f"[REQUEST] Сообщение: {msg_log}")
        
        if not self.is_available():
            logger.error("[REQUEST-ERROR] Сервер CrewAI недоступен")
            return {"response": "Ошибка: Сервер CrewAI недоступен", "error": "CrewAI server not available"}
            
        # Обработка JSON-строки, если она есть
        if isinstance(message, str):
            try:
                logger.debug("[REQUEST] Пробуем парсить JSON из строки")
                message_data = json.loads(message)
                if 'message' in message_data:
                    message = message_data
                    logger.debug("[REQUEST] Успешный парсинг JSON")
            except json.JSONDecodeError:
                logger.debug("[REQUEST] Не удалось парсить JSON, оборачиваем в простейший словарь")
                message = {"message": message}
        
        # Если message не словарь, делаем его словарем
        if not isinstance(message, dict):
            logger.debug("[REQUEST] Преобразуем не-словарь в словарь")
            message = {"message": str(message)}
            
        # --- ИСПРАВЛЕНО: Корректная инициализация MemoryManager и получение истории ---
        memory_manager = MemoryManager()

        # Новая обработка через MCP для инструментов
        if 'metadata' in message and 'tool' in message['metadata']:
            tool_type = message['metadata']['tool']
            args = message['metadata'].get('args', {})
            try:
                if not getattr(self, "mcp_client", None):
                    logger.warning("[MCP] mcp_client недоступен, пропускаем обработку через MCP")
                    return {"response": "", "error": "mcp_client_unavailable", "from_mcp": False}
                # Pylance: mcp_client может быть None — подсказываем типу
                mcp = self.mcp_client  # type: ignore[assignment]
                mcp_response = mcp.query({"type": tool_type, "args": args})  # type: ignore[call-arg]
                logger.info(f"[MCP] Успешный запрос: {tool_type}")
                return {"response": mcp_response.get('result', ''), "from_mcp": True, "error": None}
            except Exception as e:
                logger.error(f"[MCP-ERROR] Ошибка: {str(e)}")
                return {"response": "", "error": str(e), "from_mcp": False}

        # === ИНТЕГРАЦИЯ ДИНАМИЧЕСКИХ ИНСТРУКЦИЙ В РЕАЛЬНЫЙ UI-ЧАТ ===
        # Проверяем, нужны ли детальные инструкции для инструментов
        dynamic_instructions = self._get_dynamic_tool_instructions(message.get('message', ''))
        
        # Добавляем метаданные, если их нет
        if 'metadata' not in message:
            message['metadata'] = {}
            
        # Добавляем динамические инструкции в метаданные запроса
        if dynamic_instructions:
            message['metadata']['dynamic_tool_instructions'] = dynamic_instructions
            logger.info(f"[DYNAMIC-TOOLS] ✅ Добавлены динамические инструкции для {len(dynamic_instructions)} инструментов")
            
        try:
            # Получаем ID сессии из переданных метаданных
            session_id = message.get('metadata', {}).get('session_id', 'default_session')
            logger.debug(f"[REQUEST] Получаем историю сообщений для сессии: {session_id}")
            
            # Получаем историю сообщений (последние 20 сообщений)
            chat_history = memory_manager.get_chat_history(session_id)
            if chat_history:
                # Берем только 20 сообщений
                chat_history = chat_history[-20:]
                logger.info(f"[REQUEST] Получено {len(chat_history)} сообщений из истории для сессии {session_id}")
                
                # Добавляем историю сообщений в переданные данные
                message['metadata']['chat_history'] = chat_history
                logger.debug(f"[REQUEST] История сообщений добавлена в запрос")
            else:
                logger.debug(f"[REQUEST] История сообщений для сессии {session_id} не найдена")
        except Exception as e:
            logger.error(f"[REQUEST-ERROR] Ошибка при получении истории сообщений: {e}")
            # Устанавливаем пустую историю в случае ошибки, чтобы не падать
            message['metadata']['chat_history'] = []
            
        logger.debug(f"[REQUEST] Продолжаем с отправкой запроса к CrewAI API")
            
        # Process attachments if present
        attachments = message.get('metadata', {}).get('attachments', [])
        processed_attachments = []
        for att in attachments:
            path = att['path']
            att_type = att['type']
            name = os.path.basename(path)
            if att_type == 'image':
                with open(path, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('utf-8')
                processed_attachments.append({'type': 'image', 'content': f'data:image/{os.path.splitext(name)[1][1:]};base64,{content}', 'name': name})
            elif att_type == 'file':
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                processed_attachments.append({'type': 'text', 'content': content, 'name': name})
        if processed_attachments:
            message['metadata']['processed_attachments'] = processed_attachments

        # Извлекаем текст сообщения для анализа эмоций
        message_text = message.get('message', '')
        logger.debug(f"[REQUEST] Извлеченный текст сообщения: {message_text[:50]}..." if len(message_text) > 50 else message_text)
        
        # Анализируем эмоциональное состояние, если это не команда
        emotion_analysis = None
        if not any(message_text.startswith(prefix) for prefix in ('/', '!', '#')):
            logger.debug("[REQUEST] Анализ эмоционального состояния...")
            emotion_analysis = self.analyze_emotion(message_text)
            
            # Добавляем информацию об эмоциях в метаданные запроса
            if emotion_analysis:
                logger.debug(f"[REQUEST] Результат анализа эмоций: {emotion_analysis['primary_emotion']}")
                if 'metadata' not in message:
                    message['metadata'] = {}
                message['metadata']['emotion_analysis'] = emotion_analysis
        
        # Добавляем флаг асинхронной обработки
        message['async_processing'] = True
        logger.debug("[REQUEST] Установлен флаг async_processing=True")
        
        # Обрабатываем информацию о выбранной модели
        model_provider = message.get('metadata', {}).get('model_provider', 'gemini')
        model_id = message.get('metadata', {}).get('model_id')
        model_data = message.get('metadata', {}).get('model_data')
        
        logger.info(f"[MODEL] Запрос с провайдером: {model_provider}")
        if model_id:
            logger.info(f"[MODEL] Выбранная модель: {model_id}")
            
        # Добавляем информацию о модели в метаданные для сервера
        if model_provider == 'openrouter' and model_id:
            message['metadata']['preferred_provider'] = 'openrouter'
            message['metadata']['preferred_model'] = model_id
            if model_data:
                message['metadata']['model_info'] = {
                    'name': model_data.get('name', model_id),
                    'context_length': model_data.get('context_length', 4096),
                    'pricing': model_data.get('pricing', {})
                }
            logger.info(f"[MODEL] Настроен запрос для OpenRouter модели: {model_id}")
        else:
            message['metadata']['preferred_provider'] = 'gemini'
            logger.info(f"[MODEL] Используется провайдер по умолчанию: Gemini")
        
        # Добавляем системный промпт, если его нет
        system_prompt = (
            "Ты - полезный ассистент. "
            "Отвечай на русском языке. "
            "Будь вежливым и кратким. "
            "Если не знаешь ответа, так и скажи."
        )
        
        # Адаптируем системный промпт на основе эмоционального анализа
        if emotion_analysis:
            emotion = emotion_analysis['primary_emotion']
            logger.debug(f"[REQUEST] Адаптация системного промпта на основе эмоции: {emotion}")
            
            if emotion in ['depressed', 'sad', 'anxious']:
                system_prompt += " Пользователь выглядит расстроенным, прояви сочувствие и поддержку."
            elif emotion in ['angry', 'frustrated']:
                system_prompt += " Пользователь раздражен, сохраняй спокойствие и будь особенно вежливым."
            elif emotion == 'happy':
                system_prompt += " Пользователь в хорошем настроении, можно быть немного более неформальным."
        
        # Перемещаем system_prompt в metadata вместо корня запроса, так как сервер ожидает только message и metadata
        if 'metadata' not in message:
            message['metadata'] = {}
            
        # Добавляем system_prompt в metadata
        if 'system_prompt' in message:
            # Если system_prompt уже есть в корне запроса, перемещаем его в metadata
            message['metadata']['system_prompt'] = message.pop('system_prompt')
            logger.debug("[REQUEST] Пользовательский системный промпт перемещен в metadata")
        else:
            # Добавляем стандартный системный промпт в metadata
            message['metadata']['system_prompt'] = system_prompt
            logger.debug("[REQUEST] Добавлен стандартный системный промпт в metadata")
            
        logger.debug(f"[REQUEST] Подготовка к отправке запроса в CrewAI API")
        
        try:
            # Увеличиваем таймаут для первого запроса, так как сервер может обрабатывать его дольше
            first_request_timeout = max(30, (timeout or self.timeout) * 2)
            logger.debug(f"[REQUEST] Установлен таймаут {first_request_timeout} секунд для запроса")
            
            url = f"{self.base_url}/api/process"
            logger.debug(f"[REQUEST] Отправка POST запроса на {url} с заголовком Content-Type: application/json; charset=utf-8")
            
            response = requests.post(
                url,
                json=message,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=first_request_timeout
            )
            
            logger.debug(f"[REQUEST] Получен ответ от сервера: HTTP {response.status_code}")
            response.raise_for_status()
            
            # Обработка ответа
            result: Dict[str, Any] = response.json()
            logger.debug(f'Полный ответ Gemini: {result}')
            logger.debug(f"[REQUEST] Успешно парсим JSON ответ: {result}")
            
            # Если ответ содержит только текст, оборачиваем его в словарь
            if isinstance(result, str):
                logger.debug("[REQUEST] Получен текстовый ответ, преобразуем в словарь")
                result = {"response": result}
            
            # Проверяем, вернул ли сервер task_id для асинхронной обработки
            if 'task_id' in result and 'status' in result:
                logger.info(f"[TASK-START] [ASYNC] Получен task_id для асинхронной обработки: {result['task_id']}")
                logger.debug(f"[TASK-START] Начальный статус задачи: {result['status']}")
                return result
                
            # Если это синхронный ответ, добавляем анализ эмоций
            if 'metadata' in message and 'emotion_analysis' in message['metadata']:
                logger.debug("[REQUEST] Добавляем анализ эмоций в синхронный ответ")
                result['emotion_analysis'] = message['metadata']['emotion_analysis']
                
                # Добавляем рекомендации по ответу на основе эмоций
                recommendations = message['metadata']['emotion_analysis'].get('recommendations', [])
                if recommendations and 'metadata' not in result:
                    result['metadata'] = {}
                if recommendations:
                    logger.debug(f"[REQUEST] Добавлены рекомендации по ответу: {recommendations}")
                    result['metadata']['recommended_responses'] = recommendations
            
            # Добавляем обработку терминального вывода
            if isinstance(result, dict) and 'terminal_output' in result:
                term_out = result['terminal_output']
                formatted_output = f"Команда '{term_out['command']}' выполнена в терминале.\nВывод: {term_out['output']}\nОшибки: {term_out['error'] if term_out['error'] else 'Нет'}"
                result['response'] = formatted_output
                result['metadata'] = result.get('metadata', {})
                result['metadata']['terminal_output'] = term_out
                logger.info(f"[TERMINAL] Обработан терминальный вывод для команды: {term_out['command']}")
            
            # Убедимся, что ответ содержит хотя бы пустую строку, а не None
            if 'response' not in result or result['response'] is None:
                logger.debug("[REQUEST] Ответ не содержит 'response', добавляем пустую строку")
                result['response'] = ""
            else:
                logger.debug(f"[REQUEST] Получен ответ: {result['response'][:50]}..." if len(result['response']) > 50 else result['response'])
                
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[REQUEST-ERROR] Ошибка при отправке запроса в CrewAI: {str(e)}")
            return {
                "response": f"Ошибка при отправке запроса: {str(e)}",
                "error": "request_error",
                "processed_with_crewai": False
            }
            
    def check_task_status(self, task_id):
        """
        Проверяет статус асинхронной задачи
        
        Args:
            task_id: ID задачи для проверки
            
        Returns:
            dict: Состояние задачи или сообщение об ошибке
        """
        logger.debug(f"[TASK-CHECK] Проверка статуса задачи: {task_id}")
        
        if not self.is_available():
            logger.error(f"[TASK-CHECK] Сервер CrewAI недоступен при проверке задачи {task_id}")
            return {"error": "Сервер CrewAI недоступен", "status": "error"}
            
        try:
            url = f"{self.base_url}/api/task/{task_id}"
            logger.debug(f"[TASK-CHECK] Отправка GET запроса на: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"[TASK-CHECK] Получен ответ для задачи {task_id}: {result}")
                
                # Подробное логирование состояния задачи
                if result.get("done"):
                    # Извлекаем информацию о модели из ответа
                    task_result = result.get('result', {})
                    model_info = task_result.get('model_info', {})
                    
                    if model_info:
                        model_display = f"{model_info.get('display_name', 'Unknown')} ({model_info.get('provider', 'unknown')}/{model_info.get('model_id', 'unknown')})"
                        logger.info(f"[TASK-COMPLETE] ✅ Задача {task_id} завершена. Ответ от модели: {model_display}")
                        logger.info(f"[RESPONSE-FROM-MODEL] 🤖 Модель: {model_display} | Ответ: {task_result.get('response', '')[:100]}...")
                    else:
                        logger.info(f"[TASK-COMPLETE] Задача {task_id} завершена. Результат: {task_result.get('response', '')[:100]}...")
                else:
                    logger.info(f"[TASK-PROGRESS] Задача {task_id} в процессе. Статус: {result.get('status', 'неизвестно')}")
                
                return result
            else:
                logger.error(f"[TASK-ERROR] Ошибка при проверке статуса задачи {task_id}: HTTP {response.status_code} - {response.text}")
                return {"error": f"Ошибка сервера: {response.status_code}", "status": "error"}
                
        except requests.RequestException as e:
            logger.error(f"[TASK-ERROR] Ошибка соединения при проверке задачи {task_id}: {str(e)}")
            return {"error": f"Ошибка соединения: {str(e)}", "status": "error"}
            
    def get_task_status(self, task_id):
        """
        Алиас для check_task_status для обратной совместимости
        
        Args:
            task_id: ID задачи для проверки
            
        Returns:
            dict: Состояние задачи или сообщение об ошибке
        """
        logger.debug(f"[TASK-CHECK] Вызов get_task_status (алиас) для задачи: {task_id}")
        return self.check_task_status(task_id)
            
    def index_documentation(self):
        """Запускает индексацию документации CrewAI"""
        if not self.is_available():
            return False
            
        try:
            response = requests.post(
                f"{self.base_url}/api/index_docs",
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                print(f"❌ Ошибка API: {response.status_code} - {response.text}")
                return False
        except requests.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            return {"error_message": str(e), "processed_with_crewai": False}

    def get_terminal_unsafe(self) -> Optional[bool]:
        """Возвращает текущее значение флага небезопасного терминала из CrewAI API.

        Пробует основной путь без префикса /api, затем с /api как запасной.
        """
        logger.debug("[UNSAFE] Запрос текущего состояния terminal_unsafe")
        if not self.is_available():
            logger.error("[UNSAFE] Сервер CrewAI недоступен")
            return None

        endpoints = [
            f"{self.base_url}/settings/terminal_unsafe",
            f"{self.base_url}/api/settings/terminal_unsafe",
        ]
        for url in endpoints:
            try:
                resp = requests.get(url, timeout=10)
                logger.debug(f"[UNSAFE] GET {url} -> {resp.status_code}")
                if resp.status_code == 200:
                    data = resp.json()
                    # поддерживаем оба варианта ответа
                    if isinstance(data, dict):
                        if "terminal_unsafe" in data:
                            return bool(data["terminal_unsafe"])
                        if "value" in data:
                            return bool(data["value"])
                    # если вернули просто true/false
                    if isinstance(data, bool):
                        return data
                else:
                    logger.warning(f"[UNSAFE] Ошибка ответа: {resp.status_code} {resp.text}")
            except requests.RequestException as e:
                logger.error(f"[UNSAFE] Ошибка запроса GET {url}: {e}")
        return None

    def set_terminal_unsafe(self, value: bool) -> bool:
        """Устанавливает флаг небезопасного терминала через CrewAI API.

        Возвращает True при успехе, False иначе. Пробует /settings и /api/settings пути.
        """
        logger.info(f"[UNSAFE] Установка terminal_unsafe={value}")
        if not self.is_available():
            logger.error("[UNSAFE] Сервер CrewAI недоступен")
            return False

        payload = {"terminal_unsafe": bool(value)}
        headers = {"Content-Type": "application/json; charset=utf-8"}
        endpoints = [
            f"{self.base_url}/settings/terminal_unsafe",
            f"{self.base_url}/api/settings/terminal_unsafe",
        ]
        for url in endpoints:
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=10)
                logger.debug(f"[UNSAFE] POST {url} -> {resp.status_code}")
                if resp.status_code in (200, 204):
                    return True
                # некоторые реализации возвращают JSON с success
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        if isinstance(data, dict) and data.get("success", False):
                            return True
                    except Exception:
                        pass
                logger.warning(f"[UNSAFE] Ошибка ответа POST: {resp.status_code} {resp.text}")
            except requests.RequestException as e:
                logger.error(f"[UNSAFE] Ошибка запроса POST {url}: {e}")
        return False

    def _get_dynamic_tool_instructions(self, message_text: str) -> dict:
        """
        Анализирует сообщение пользователя и определяет, какие инструменты могут понадобиться.
        Возвращает словарь с детальными инструкциями для релевантных инструментов.
        
        Args:
            message_text: Текст сообщения пользователя
            
        Returns:
            dict: Словарь {tool_name: detailed_instructions} для релевантных инструментов
        """
        if not message_text:
            return {}
        
        # Проверяем доступность менеджера инструкций
        if not TOOLS_INSTRUCTION_MANAGER_AVAILABLE:
            logger.warning("[DYNAMIC-TOOLS] ❌ tools_instruction_manager недоступен, возвращаем пустые инструкции")
            return {}
        
        try:
            # Получаем экземпляр менеджера инструкций
            manager = get_tools_instruction_manager()
            if not manager:
                logger.error("[DYNAMIC-TOOLS] ❌ Не удалось получить экземпляр tools_instruction_manager")
                return {}
            
            # Получаем список доступных инструментов
            tools_summary = manager.get_tools_summary()
            
            # Предварительная обработка сообщения для определения потенциальных инструментов
            message_lower = message_text.lower()
            result = {}
            
            # Простая эвристика для определения необходимых инструментов
            # Проверяем ключевые слова в сообщении
            tool_keywords = {
                "filesystem_tools": ["файл", "директор", "папк", "zip", "архив", "поиск файл", "json", "csv"],
                "local_mcp_tools": ["сайт", "скрап", "парс", "api", "запрос", "post", "get", "http"],
                "browser_tools": ["браузер", "открой сайт", "перейди", "нажми", "скриншот", "selenium"],
                "web_search": ["найди", "поиск", "погугли", "поищи", "google", "yandex", "найти информацию"],
                "page_analyzer": ["проанализируй", "анализ сайта", "seo", "оцени сайт", "скорость сайта"]
            }
            
            # Выявляем инструменты по ключевым словам
            for tool_name, keywords in tool_keywords.items():
                if any(kw in message_lower for kw in keywords):
                    detailed_instructions = manager.get_tool_detailed_instructions(tool_name)
                    if detailed_instructions:
                        result[tool_name] = detailed_instructions
                        logger.info(f"[DYNAMIC-TOOLS] ✅ Добавлены инструкции для инструмента: {tool_name}")
            
            # Если ни одного инструмента не определено, возвращаем базовый набор для основных задач
            if not result:
                # Базовый набор инструментов для типичных задач
                default_tools = ["filesystem_tools", "web_search"]
                for tool_name in default_tools:
                    detailed_instructions = manager.get_tool_detailed_instructions(tool_name)
                    if detailed_instructions:
                        result[tool_name] = detailed_instructions
                        logger.info(f"[DYNAMIC-TOOLS] ✅ Добавлены базовые инструкции: {tool_name}")
            
            logger.debug(f"[DYNAMIC-TOOLS] Сформированы инструкции для {len(result)} инструментов")
            return result
            
        except Exception as e:
            logger.error(f"[DYNAMIC-TOOLS] ❌ Ошибка при генерации инструкций: {e}")
            return {}

    def _handle_browser_command(self, message):
        """
        Обрабатывает команды браузера, начинающиеся с /browser или /браузер
        
{{ ... }}
            message: Полный текст сообщения с командой
            
        Returns:
            dict: Ответ с командой для браузера
        """
        # Удаляем префикс команды
        command = message.split(' ', 1)[1] if ' ' in message else ""
        
        # Простая проверка на URL
        url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+)', command)
        
        # Если в команде есть URL, используем его, иначе ищем через поиск
        if url_match:
            url = url_match.group(0)
            return {
                "impl": "browser-use",
                "command": "go_to_url",
                "args": {"url": url},
                "response": f"Открываю: {url}"
            }
        elif command.strip():
            # Если это не URL, но есть текст команды - ищем через поиск
            return {
                "impl": "browser-use",
                "command": "search",
                "args": {"query": command},
                "response": f"Ищу в интернете: {command}"
            }
        else:
            # Если команда пустая после префикса
            return {
                "response": "Пожалуйста, укажите URL или поисковый запрос после /browser",
                "error": "invalid_browser_command"
            }

    def nlp_parse_command(self, message, lang_hint=None):
        """
        Пример базового NLP-парсинга команды с помощью spaCy.
        Возвращает список сущностей и ключевых слов.
        lang_hint: 'ru' или 'en' — если явно известно, иначе autodetect.
        """
        if nlp_ru is None or nlp_en is None:
            logger.warning("spaCy не инициализирован — NLP-парсинг недоступен")
            return None
        # Определяем язык (очень просто)
        lang = lang_hint
        if not lang:
            if any(ord(c) > 127 for c in message):
                lang = 'ru'
            else:
                lang = 'en'
        nlp = nlp_ru if lang == 'ru' else nlp_en
        doc = nlp(message)
        # Извлекаем сущности и ключевые слова
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        logger.info(f"[NLP] entities: {entities}, tokens: {tokens}")
        return {"entities": entities, "tokens": tokens, "lang": lang}

# Глобальный экземпляр клиента
crewai_client = CrewAIClient()
