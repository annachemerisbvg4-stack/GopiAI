"""
🧠 Простой менеджер памяти для GopiAI на основе txtai
Адаптировано из similarity.py - никакого оверинжиниринга!
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np


# Проверяем доступность txtai
try:
    from txtai.embeddings import Embeddings
    TXTAI_AVAILABLE = True
except ImportError:
    TXTAI_AVAILABLE = False
    print(" txtai не установлен. Установите: pip install txtai sentence-transformers")

# Проверяем доступность FAISS
try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print(" FAISS не установлен. Для лучшей производительности: pip install faiss-cpu")


class SimpleMemoryManager:
    """Простой менеджер памяти, полностью основанный на txtai для персистентности."""

    def __init__(self, data_dir: str = "conversations"):
        """Инициализация"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.chats_file = self.data_dir / "chats.json"
        self.chats = []
        self.sessions = {}

        disable_embeddings = os.getenv('GOPI_DISABLE_EMBEDDINGS', 'false').lower() == 'true'
        self.embeddings = None

        if TXTAI_AVAILABLE and not disable_embeddings:
            try:
                print(" Инициализация txtai embeddings...")
                embeddings_path = self.data_dir.joinpath("vectors").as_posix()
                self.embeddings = Embeddings({
                    "path": embeddings_path,
                    "model": "sentence-transformers/nli-mpnet-base-v2",
                    "content": True,
                    "objects": True,
                    "backend": "faiss" if FAISS_AVAILABLE else "annoy",
                })
                print(f" txtai инициализирован. Векторов в базе: {self.embeddings.count()}")
            except Exception as e:
                print(f" Ошибка инициализации txtai: {e}")
        else:
            if disable_embeddings:
                print(" Векторизация отключена через GOPI_DISABLE_EMBEDDINGS")
            else:
                print(" txtai недоступен - работаем без поиска")

        self._load_data()

        if self.embeddings:
            self._migrate_old_chats_to_txtai()

        self.session_id = "default_session"

    def _load_data(self):
        """Загрузка данных из JSON"""
        try:
            if self.chats_file.exists():
                with open(self.chats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.chats = data.get('chats', [])
                    self.sessions = data.get('sessions', {})
                    print(f" Загружено {len(self.chats)} сообщений и {len(self.sessions)} сессий")
            else:
                print(" Файл чатов не найден, начинаем с чистого листа")
        except (json.JSONDecodeError, IOError) as e:
            print(f" Ошибка загрузки чатов: {e}")
            self.chats = []
            self.sessions = {}

    def _save_data(self):
        """Сохранение данных в JSON"""
        try:
            with open(self.chats_file, 'w', encoding='utf-8') as f:
                json.dump({'chats': self.chats, 'sessions': self.sessions}, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f" Ошибка сохранения чатов: {e}")

    def _migrate_old_chats_to_txtai(self):
        """Мигрирует старые чаты из chats.json в индекс txtai, если их там еще нет."""
        if not self.chats or not self.embeddings:
            return

        print(" Проверка необходимости миграции старых сообщений в txtai...")
        try:
            # Получаем все ID из существующего индекса
            if self.embeddings.count() > 0:
                existing_ids = {str(row["id"]) for row in self.embeddings.search("select id from txtai", limit=self.embeddings.count() + 1)}
            else:
                existing_ids = set()
            
            new_data_to_index = []
            for chat in self.chats:
                if self._should_index_message(chat.get('content', ''), chat.get('role', '')):
                    if chat['id'] not in existing_ids:
                        new_data_to_index.append((chat['id'], chat, None)) # Индексируем весь объект сообщения

            if new_data_to_index:
                print(f" Найдены {len(new_data_to_index)} новых сообщений для индексации. Индексируем...")
                self.embeddings.index(new_data_to_index)
                self.embeddings.save() # Принудительно сохраняем после массовой индексации
                print(" Миграция завершена.")
            else:
                print(" Все сообщения уже в индексе.")
        except Exception as e:
            print(f" Ошибка миграции: {e}")

    def create_session(self, title: str = "Новый чат") -> str:
        """Создание новой сессии"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'id': session_id,
            'title': title,
            'created_at': datetime.now().isoformat(),
            'message_count': 0
        }
        self._save_data()
        return session_id

    def _should_index_message(self, content: str, role: str) -> bool:
        """Определяет, нужно ли индексировать сообщение"""
        if not content or len(content.strip()) < 10 or role in ['system', 'assistant']:
            return False
        return True

    def add_message(self, session_id: str, content: str, role: str = "user") -> str:
        """Добавление сообщения в историю и в индекс txtai."""
        message_id = str(uuid.uuid4())
        should_index = self._should_index_message(content, role)

        message = {
            'id': message_id,
            'session_id': session_id,
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'should_index': should_index
        }
        self.chats.append(message)

        if session_id in self.sessions:
            self.sessions[session_id]['message_count'] += 1

        if should_index and self.embeddings:
            try:
                # Индексируем (id, object, tags). txtai обработает эмбеддинг и сохранение.
                self.embeddings.index([(message_id, message, None)])
                self.embeddings.save()
                print(f" Сообщение '{content[:30]}...' добавлено в векторную базу.")
            except Exception as e:
                print(f" Ошибка при добавлении в векторную базу txtai: {e}")

        self._save_data()
        return message_id

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Поиск в памяти с использованием txtai."""
        if not self.embeddings or self.embeddings.count() == 0:
            print(" Поиск недоступен - векторная база пуста или не готова.")
            return []

        try:
            # Важно: для similar() нужно экранировать одинарные кавычки в запросе
            safe_query = query.replace("'", "''")
            # Ищем и возвращаем весь объект
            results = self.embeddings.search(f"select object, score from txtai where similar('{safe_query}') limit {limit}")
            
            # Добавляем score к объекту и возвращаем
            formatted_results = []
            for res in results:
                message_object = res['object']
                message_object['score'] = res['score']
                formatted_results.append(message_object)
            
            print(f" Найдено {len(formatted_results)} результатов в txtai для: '{query[:30]}...' ")
            return formatted_results
        except Exception as e:
            print(f" Ошибка поиска в txtai: {e}")
            return []

    def get_session_messages(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Получение сообщений сессии"""
        messages = [chat for chat in self.chats if chat['session_id'] == session_id]
        return messages[-limit:] if limit else messages
    
    def get_all_sessions(self) -> List[Dict]:
        """Получение всех сессий"""
        return list(self.sessions.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Статистика"""
        vector_count = 0
        if self.embeddings:
            try:
                vector_count = self.embeddings.count()
            except Exception as e:
                print(f"Не удалось получить кол-во векторов: {e}")

        return {
            'total_messages': len(self.chats),
            'total_sessions': len(self.sessions),
            'txtai_available': self.embeddings is not None,
            'vector_messages': vector_count,
            'faiss_available': FAISS_AVAILABLE,
            'data_dir': str(self.data_dir)
        }
    
    # Методы совместимости с существующим API GopiAI
    
    def enrich_message(self, message: str) -> str:
        """
        Обогащает сообщение пользователя контекстом из памяти.
        
        Добавляет:
        1. Недавние сообщения из текущей сессии (контекст разговора)
        2. Релевантные воспоминания из памяти по запросу
        
        Args:
            message: Исходное сообщение пользователя
            
        Returns:
            Обогащенное сообщение с контекстом
        """
        try:
            # Получаем недавние сообщения текущей сессии (до 5)
            recent_messages = self._format_recent_messages(self.session_id, 5)
            
            # Поиск релевантных воспоминаний по запросу (до 3 результатов)
            memory_results = self.search(message, limit=3)
            memory_context = self._format_memory_results(memory_results)
            
            # Собираем все вместе
            parts = []
            
            # Добавляем оригинальное сообщение
            parts.append(message)
            
            # Добавляем контекстную информацию только если она есть
            context_parts = []
            
            if recent_messages:
                context_parts.append(f"Контекст разговора:\n{recent_messages}")
            
            if memory_context:
                context_parts.append(f"Релевантная информация из памяти:\n{memory_context}")
            
            # Добавляем контекст только если он есть
            if context_parts:
                parts.append("\n\n--- Дополнительный контекст ---\n" + "\n\n".join(context_parts))
                
                # Добавляем мягкую инструкцию, как использовать контекст
                parts.append("Используй приведенный выше контекст при необходимости, но не упоминай его напрямую в ответе.")
            
            # Формируем итоговое обогащенное сообщение
            enriched_message = "\n\n".join(parts)
            
            # Логгируем результат (для отладки)
            enrichment_stats = {
                "original_length": len(message),
                "enriched_length": len(enriched_message),
                "memory_results": len(memory_results) if memory_results else 0,
                "has_recent_context": bool(recent_messages)
            }
            print(f"🧠 Message enriched: {enrichment_stats}")
            
            return enriched_message
            
        except Exception as e:
            # В случае любой ошибки возвращаем исходное сообщение
            print(f"❌ Error enriching message: {e}")
            return message

    def _format_recent_messages(self, session_id: str, limit: int = 5) -> str:
        """
        Форматирует последние сообщения из указанной сессии.
        
        Args:
            session_id: ID сессии
            limit: Максимальное количество сообщений
            
        Returns:
            Отформатированный текст сообщений
        """
        messages = self.get_session_messages(session_id, limit=limit)
        if not messages:
            return ""
        
        formatted = []
        for msg in messages:
            role_emoji = "👤" if msg['role'] == 'user' else "🤖"
            formatted.append(f"{role_emoji} {msg['content']}")
        
        return "\n\n".join(formatted)

    def _format_memory_results(self, results: List[Dict]) -> str:
        """
        Форматирует результаты поиска в памяти.
        
        Args:
            results: Список результатов поиска
            
        Returns:
            Отформатированный текст результатов
        """
        if not results:
            return ""
        
        formatted = []
        for result in results:
            content = result.get('content', '')
            formatted.append(content)
        
        return "\n\n---\n\n".join(formatted)

    def start_new_session(self, title: str = "Новый чат") -> str:
        """Начать новую сессию (для совместимости с js_bridge)"""
        self.session_id = self.create_session(title)
        return self.session_id

    def get_memory_stats(self) -> Dict[str, Any]:
        """Получить статистику памяти (алиас для get_stats)"""
        stats = self.get_stats()
        # Добавляем дополнительные поля для совместимости
        stats.update({
            'current_session': self.session_id,
            'memory_available': True,
            'recent_messages': len(self.get_session_messages(self.session_id, limit=10))
        })
        return stats

    def save_chat_exchange(self, user_msg_or_session: str, ai_response_or_user: str, ai_response: Optional[str] = None) -> bool:
        """
        Сохранение обмена сообщениями (с поддержкой двух сигнатур для совместимости)
        
        Если 3 параметра: save_chat_exchange(session_id, user_msg, ai_response) - новый API
        Если 2 параметра: save_chat_exchange(user_msg, ai_response) - старый API для js_bridge
        """
        try:
            if ai_response is None:
                # Старая сигнатура: save_chat_exchange(user_msg, ai_response)
                user_message = user_msg_or_session
                ai_message = ai_response_or_user
                session_id = self.session_id  # Используем текущую сессию
            else:
                # Новая сигнатура: save_chat_exchange(session_id, user_msg, ai_response)  
                session_id = user_msg_or_session
                user_message = ai_response_or_user
                ai_message = ai_response
            
            self.add_message(session_id, "user", user_message)
            self.add_message(session_id, "assistant", ai_message)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения обмена: {e}")
            return False


# Глобальный экземпляр
_memory_manager = None

def get_memory_manager() -> SimpleMemoryManager:
    """Получить менеджер памяти (синглтон)"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = SimpleMemoryManager()
    return _memory_manager


# Для совместимости
class TxtAIMemoryManager(SimpleMemoryManager):
    """Алиас для совместимости с существующим кодом"""
    pass


""" if __name__ == "__main__":
    # Быстрый тест
    print("🧪 Тестируем Simple Memory Manager...")
    
    manager = SimpleMemoryManager()
    
    # Создаем сессию
    session_id = manager.create_session("Тест txtai")
    
    # Добавляем сообщения
    manager.add_message(session_id, "user", "Привет! Как дела с txtai интеграцией?")
    manager.add_message(session_id, "assistant", "Отлично! txtai работает прекрасно для семантического поиска в GopiAI")
    manager.add_message(session_id, "user", "Расскажи про архитектуру системы памяти")
    
    # Тестируем поиск
    results = manager.search_memory("txtai поиск")
    print(f"✅ Найдено результатов: {len(results)}")
    
    # Статистика
    stats = manager.get_stats()
    print(f"📊 Статистика: {stats}")
    
print("🎉 Всё работает!") """