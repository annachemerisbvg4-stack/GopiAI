"""
🔌 CrewAI API Client (ИСПРАВЛЕННАЯ ВЕРСИЯ)
Клиент для интеграции с CrewAI через REST API
"""

import requests
import threading
import time
import json
import os

class CrewAIClient:
    """
    Клиент для взаимодействия с CrewAI API сервером
    
    Позволяет UI приложению использовать функциональность CrewAI,
    запущенного в отдельном окружении через REST API.
    """
    
    def __init__(self, base_url="http://127.0.0.1:5050"):
        self.base_url = base_url
        self.timeout = 5  # Таймаут для API запросов (в секундах)
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
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка API: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            return None
    
    def process_request(self, message, force_crewai=False):
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
            # Всегда используем force_crewai=False, чтобы система сама определяла
            # необходимость использования CrewAI на основе анализа сложности запроса
            response = requests.post(
                f"{self.base_url}/api/process",
                json={
                    "message": message,
                    "force_crewai": False  # Игнорируем входной параметр force_crewai
                },
                timeout=60  # Увеличенный таймаут, т.к. обработка может быть долгой
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
                "response": f"Ошибка связи с CrewAI API: {str(e)}",
                "error": "connection_error"
            }
            
    def index_documentation(self):
        """Запускает индексацию документации CrewAI"""
        if not self.is_available():
            return False
            
        try:
            response = requests.post(f"{self.base_url}/api/index_docs", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                print(f"❌ Ошибка API: {response.status_code} - {response.text}")
                return False
        except requests.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            return False
