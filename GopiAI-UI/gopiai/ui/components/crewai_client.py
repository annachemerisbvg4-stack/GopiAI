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


# DEBUG LOGGING PATCH - Added for hang diagnosis
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
print("🔧 DEBUG logging enabled for crewai_client.py")


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
    
    def analyze_request(self, message):
        """Анализирует запрос пользователя"""
        if not self.is_available():
            return {
                "complexity": 3,
                "crew_type": "general",
                "requires_crewai": False
            }
            
        try:
            response = requests.post(
                f"{self.base_url}/api/analyze",
                json={"message": message},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка API: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            return {"error_message": str(e), "processed_with_crewai": False}
    
    def process_request(self, message, force_crewai=False, timeout=None):
        """
        Обрабатывает запрос через CrewAI API
        
        ИСПРАВЛЕНИЕ: Теперь возвращает структурированный объект,
        а не только строку ответа
        """
        if not self.is_available():
            return {
                "response": f"CrewAI API сервер недоступен. Запустите его с помощью 'run_crewai_api_server.bat'.\n\nВаш запрос: {message}",
                "error": "server_unavailable",
                "processed_with_crewai": False
            }
            
        try:
            # Расширенный список браузерных команд с популярными сайтами
            browser_commands = [
                # Основные команды навигации
                "открой сайт", "открой страницу", "перейди на сайт", "зайди на сайт",
                "загрузи сайт", "иди на сайт", "переходи на", "открыть сайт",
                
                # Популярные сайты (без .com для гибкости)
                "открой github", "открой гитхаб", "открой google", "открой гугл",
                "открой youtube", "открой ютуб", "открой stackoverflow",
                "открой вконтакте", "открой вк", "открой telegram", "открой телеграм",
                
                # Конкретные домены
                "github.com", "google.com", "youtube.com", "stackoverflow.com",
                "vk.com", "telegram.org", "habr.com", "yandex.ru",
                
                # Поисковые команды
                "найди в google", "поиск в google", "google поиск",
                "найди в гугле", "поищи в google", "погугли"
            ]
            
            message_lower = message.lower()
            
            # Ищем ТОЛЬКО очень явные команды
            is_browser_command = False
            for cmd in browser_commands:
                if cmd in message_lower:
                    is_browser_command = True
                    break
            
            # Проверяем URL только если есть протокол или www
            import re
            url_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
            if re.search(url_pattern, message):
                is_browser_command = True
            
            if is_browser_command:
                # Возвращаем специальный объект для обработки как команды браузера
                return {
                    "impl": "browser-use",  # Указывает, что браузерная команда
                    "command": message,
                    "processed_with_crewai": False
                }
            
            # Всегда используем force_crewai=False, чтобы система сама определяла
            # необходимость использования CrewAI на основе анализа сложности запроса
            
            # ИСПРАВЛЕНИЕ: Используем timeout параметр если передан, иначе дефолтный
            request_timeout = timeout if timeout is not None else 60
            
            response = requests.post(
                f"{self.base_url}/api/process",
                json={
                    "message": message,
                    "force_crewai": False  # Игнорируем входной параметр force_crewai
                },
                timeout=120  # Увеличенный таймаут для длительных операций CrewAI
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # ИСПРАВЛЕНИЕ: Возвращаем полный объект вместо только data["response"]
                if "response" in data:
                    return {
                        "response": data["response"],
                        "processed_with_crewai": data.get("processed_with_crewai", False)
                    }
                elif "error_message" in data:
                    return {
                        "response": data["error_message"],
                        "error": data.get("error", "unknown_error"),
                        "processed_with_crewai": data.get("processed_with_crewai", False)
                    }
                else:
                    return {
                        "response": "Неизвестный формат ответа от сервера",
                        "error": "invalid_response_format"
                    }
            else:
                print(f"❌ Ошибка API: {response.status_code} - {response.text}")
                return {
                    "response": f"Произошла ошибка при обработке запроса (код {response.status_code})",
                    "error": f"http_error_{response.status_code}"
                }
        except requests.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            return {
                "error_message": f"Ошибка связи с CrewAI API: {str(e)}",
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

# Глобальный экземпляр клиента
crewai_client = CrewAIClient()