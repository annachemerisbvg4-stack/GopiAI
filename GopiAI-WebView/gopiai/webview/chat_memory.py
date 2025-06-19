"""
Система памяти для веб-чата GopiAI с RAG поддержкой
Минимальная интеграция с существующей RAG системой
"""
import json
import uuid
import asyncio
import requests
from datetime import datetime
from collections import deque
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import logging

# Настройка логирования
logger = logging.getLogger(__name__)


class ChatMemoryManager:
    """
    Управляет краткосрочной и долгосрочной памятью чата
    Интегрируется с существующей RAG системой через REST API
    """

    def __init__(self, 
                 rag_api_url: str = "http://127.0.0.1:8080",
                 max_context_messages: int = 15,
                 similarity_threshold: float = 0.7):
        """
        Инициализация менеджера памяти
        
        Args:
            rag_api_url: URL RAG API сервера
            max_context_messages: Максимум сообщений в краткосрочной памяти
            similarity_threshold: Порог релевантности для поиска
        """
        self.rag_api_url = rag_api_url.rstrip('/')
        self.max_context_messages = max_context_messages
        self.similarity_threshold = similarity_threshold
        
        # Краткосрочная память - текущий чат
        self.current_session = deque(maxlen=max_context_messages)
        self.session_id = str(uuid.uuid4())
        
        # Проверяем доступность RAG API
        self.rag_available = self._check_rag_availability()
        
        if self.rag_available:
            # Создаем сессию в RAG системе
            self._create_rag_session()
    
    def _check_rag_availability(self) -> bool:
        """Проверка доступности RAG API"""
        try:
            response = requests.get(f"{self.rag_api_url}/health", timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"RAG API недоступен: {e}")
            return False
    
    def _create_rag_session(self) -> bool:
        """Создание новой сессии в RAG системе"""
        if not self.rag_available:
            return False
            
        try:
            response = requests.post(f"{self.rag_api_url}/sessions", 
                                   json={
                                       "title": f"GopiAI Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                                       "project_context": "GopiAI-WebView",
                                       "tags": ["webview", "chat", "interactive"]
                                   },
                                   timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id", self.session_id)
                logger.info(f"RAG сессия создана: {self.session_id}")
                return True
        except Exception as e:
            logger.error(f"Ошибка создания RAG сессии: {e}")
            
        return False
    
    def enrich_message(self, user_message: str) -> str:
        """
        Обогащает сообщение пользователя контекстом из памяти
        Основной метод для интеграции с JavaScript
        
        Args:
            user_message: Исходное сообщение пользователя
            
        Returns:
            Обогащенное сообщение с контекстом
        """
        context_parts = []
        
        # 1. Краткосрочная память (последние сообщения)
        recent_context = self._format_recent_context()
        if recent_context:
            context_parts.append(f"Недавний контекст разговора:\n{recent_context}")
        
        # 2. Долгосрочная память (похожие обсуждения из RAG)
        if self.rag_available:
            relevant_history = self._search_rag_memory(user_message)
            if relevant_history:
                context_parts.append(f"Релевантная информация из истории:\n{relevant_history}")
        
        # Формируем финальное сообщение
        if context_parts:
            enriched_message = f"""Контекст из памяти:
{chr(10).join(context_parts)}

Новый вопрос пользователя: {user_message}"""
        else:
            enriched_message = user_message
        
        return enriched_message
    
    def save_chat_exchange(self, user_message: str, ai_response: str) -> bool:
        """
        Сохраняет обмен сообщениями в память
        Вызывается после получения ответа ИИ
        
        Args:
            user_message: Сообщение пользователя
            ai_response: Ответ ИИ
            
        Returns:
            True если сохранение успешно
        """
        timestamp = datetime.now().isoformat()
        
        # Добавляем в краткосрочную память
        self.current_session.append({
            "timestamp": timestamp,
            "user": user_message,
            "assistant": ai_response
        })
        
        # Сохраняем в долгосрочную память через RAG API
        if self.rag_available:
            return self._save_to_rag_memory(user_message, ai_response, timestamp)
        
        return True
    
    def _format_recent_context(self) -> str:
        """Форматирует последние сообщения для контекста"""
        if not self.current_session:
            return ""
        
        formatted_messages = []
        # Берем последние 3 обмена сообщениями
        for msg in list(self.current_session)[-3:]:
            formatted_messages.append(f"Пользователь: {msg['user']}")
            # Обрезаем длинные ответы ИИ
            ai_response = msg['assistant'][:200] + "..." if len(msg['assistant']) > 200 else msg['assistant']
            formatted_messages.append(f"Ассистент: {ai_response}")
        
        return "\n".join(formatted_messages)
    
    def _search_rag_memory(self, query: str, max_results: int = 3) -> str:
        """Поиск релевантных сообщений в RAG памяти"""
        if not self.rag_available:
            return ""
        
        try:
            response = requests.get(f"{self.rag_api_url}/search", 
                                  params={"q": query, "limit": max_results}, 
                                  timeout=5)
            if response.status_code == 200:
                results = response.json().get("results", [])
                relevant_docs = []
                for result in results:
                    if result.get("relevance_score", 0) >= self.similarity_threshold:
                        content = result.get("content", "")[:300]
                        if content:
                            relevant_docs.append(content)
                return "\n---\n".join(relevant_docs) if relevant_docs else ""
        except Exception as e:
            logger.error(f"Ошибка поиска в RAG памяти: {e}")
        return ""

    def search_conversations(self, query: str) -> str:
        """Временный метод для совместимости"""
        return self._search_rag_memory(query)
    
    def _save_to_rag_memory(self, user_message: str, ai_response: str, timestamp: str) -> bool:
        """Сохранение сообщений в RAG память"""
        if not self.rag_available:
            return False
            
        try:
            # Сначала сохраняем сообщение пользователя
            user_response = requests.post(f"{self.rag_api_url}/sessions/{self.session_id}/messages",
                                        json={
                                            "content": user_message,
                                            "role": "user",
                                            "metadata": {"timestamp": timestamp}
                                        },
                                        timeout=5)
            
            # Затем ответ ИИ
            ai_response_req = requests.post(f"{self.rag_api_url}/sessions/{self.session_id}/messages",
                                          json={
                                              "content": ai_response,
                                              "role": "assistant", 
                                              "metadata": {"timestamp": timestamp}
                                          },
                                          timeout=5)
            
            return user_response.status_code == 200 and ai_response_req.status_code == 200
            
        except Exception as e:
            logger.error(f"Ошибка сохранения в RAG память: {e}")
            return False
    
    def start_new_session(self):
        """Начинает новую сессию чата"""
        self.current_session.clear()
        self.session_id = str(uuid.uuid4())
        
        if self.rag_available:
            self._create_rag_session()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Возвращает краткую сводку текущей сессии"""
        return {
            "session_id": self.session_id,
            "messages_count": len(self.current_session),
            "started_at": list(self.current_session)[0]["timestamp"] if self.current_session else None,
            "rag_available": self.rag_available
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Получение статистики памяти"""
        stats = {
            "short_term_messages": len(self.current_session),
            "session_id": self.session_id,
            "rag_available": self.rag_available
        }
        
        if self.rag_available:
            try:
                response = requests.get(f"{self.rag_api_url}/stats", timeout=5)
                if response.status_code == 200:
                    rag_stats = response.json()
                    stats.update(rag_stats)
            except Exception as e:
                logger.error(f"Ошибка получения статистики RAG: {e}")
        
        return stats


# Фабрика для создания менеджера памяти
def create_memory_manager(rag_api_url: str = "http://127.0.0.1:8080") -> ChatMemoryManager:
    """
    Создает и возвращает экземпляр ChatMemoryManager
    
    Args:
        rag_api_url: URL RAG API сервера
    
    Returns:
        ChatMemoryManager: Готовый к использованию менеджер памяти
    """
    return ChatMemoryManager(rag_api_url=rag_api_url)