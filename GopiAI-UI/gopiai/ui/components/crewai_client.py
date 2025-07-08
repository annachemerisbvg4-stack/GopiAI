import urllib.parse

"""
🔌 CrewAI API Client
Клиент для интеграции с CrewAI через REST API
"""

import requests
import requests.exceptions
import threading
import time
import json
import os
import sys
from pathlib import Path

# Add the parent directory to path to import emotional_classifier
sys.path.append(str(Path(__file__).parent.parent.parent.parent / 'GopiAI-CrewAI' / 'tools' / 'gopiai_integration'))
try:
    from emotional_classifier import EmotionalClassifier, EmotionalState
    EMOTIONAL_CLASSIFIER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Не удалось загрузить эмоциональный классификатор: {e}")
    EMOTIONAL_CLASSIFIER_AVAILABLE = False


# DEBUG LOGGING PATCH - Added for hang diagnosis
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
print("🔧 DEBUG logging enabled for crewai_client.py")


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

    def __init__(self, base_url="http://127.0.0.1:5050"):
        self.base_url = base_url
        self.timeout = 30  # Таймаут для API запросов (в секундах)
        self._server_available = None  # Кеш статуса сервера
        self._last_check = 0  # Время последней проверки
        
        # Инициализация эмоционального классификатора
        self.emotional_classifier = None
        if EMOTIONAL_CLASSIFIER_AVAILABLE:
            try:
                from emotional_classifier import EmotionalClassifier
                # Инициализируем с None, так как мы будем использовать моковый роутер
                self.emotional_classifier = EmotionalClassifier(ai_router=None)
                print("✅ Эмоциональный классификатор успешно инициализирован")
            except Exception as e:
                print(f"⚠️ Ошибка при инициализации эмоционального классификатора: {e}")

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
        # Используем кеш, если проверка была недавно
        current_time = time.time()
        if not force_check and self._server_available is not None and (current_time - self._last_check) < 30:
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
            
    def process_request(self, message, force_crewai=False, timeout=None):
        """
        Обрабатывает запрос через CrewAI API с учетом эмоционального состояния
        
        Args:
            message: Сообщение пользователя (может быть строкой или JSON с контекстом)
            force_crewai: Принудительно отправить запрос в CrewAI (игнорируя команды браузера)
            timeout: Таймаут запроса в секундах
            
        Returns:
            dict: Ответ от API с полями 'response', 'command' (опционально) и 'emotion_analysis' (при наличии)
        """
        if not self.is_available():
            return {"response": "Ошибка: Сервер CrewAI недоступен", "error": "CrewAI server not available"}
            
        # Обработка JSON-строки, если она пришла
        if isinstance(message, str):
            try:
                message_data = json.loads(message)
                if 'message' in message_data:
                    message = message_data
            except json.JSONDecodeError:
                message = {"message": message}
        
        # Если message не словарь, делаем его словарем
        if not isinstance(message, dict):
            message = {"message": str(message)}
            
        # Извлекаем текст сообщения для анализа эмоций
        message_text = message.get('message', '')
        
        # Анализируем эмоциональное состояние, если это не команда
        emotion_analysis = None
        if not any(message_text.startswith(prefix) for prefix in ('/', '!', '#')):
            emotion_analysis = self.analyze_emotion(message_text)
            
            # Добавляем информацию об эмоциях в метаданные запроса
            if emotion_analysis:
                if 'metadata' not in message:
                    message['metadata'] = {}
                message['metadata']['emotion_analysis'] = emotion_analysis
            
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
            
            if emotion in ['depressed', 'sad', 'anxious']:
                system_prompt += " Пользователь выглядит расстроенным, прояви сочувствие и поддержку."
            elif emotion in ['angry', 'frustrated']:
                system_prompt += " Пользователь раздражен, сохраняй спокойствие и будь особенно вежливым."
            elif emotion == 'happy':
                system_prompt += " Пользователь в хорошем настроении, можно быть немного более неформальным."
                
        if 'system_prompt' not in message:
            message['system_prompt'] = system_prompt
            
        logger.debug(f"Отправка запроса в CrewAI: {message}")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/process",
                json=message,
                timeout=timeout or self.timeout
            )
            response.raise_for_status()
            
            # Обработка ответа
            result = response.json()
            
            # Если ответ содержит только текст, оборачиваем его в словарь
            if isinstance(result, str):
                result = {"response": result}
            
            # Добавляем анализ эмоций в результат, если он есть
            if 'metadata' in message and 'emotion_analysis' in message['metadata']:
                result['emotion_analysis'] = message['metadata']['emotion_analysis']
                
                # Добавляем рекомендации по ответу на основе эмоций
                recommendations = message['metadata']['emotion_analysis'].get('recommendations', [])
                if recommendations and 'metadata' not in result:
                    result['metadata'] = {}
                if recommendations:
                    result['metadata']['recommended_responses'] = recommendations
            
            # Убедимся, что ответ содержит хотя бы пустую строку, а не None
            if 'response' not in result or result['response'] is None:
                result['response'] = ""
                
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при отправке запроса в CrewAI: {str(e)}")
            return {
                "response": f"Ошибка при отправке запроса: {str(e)}",
                "error": "request_error",
                "processed_with_crewai": False
            }
            
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

    def _handle_browser_command(self, message):
        """
        Обрабатывает команды браузера, начинающиеся с /browser или /браузер
        
        Args:
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