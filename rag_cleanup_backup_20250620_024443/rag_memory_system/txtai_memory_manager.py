"""
Простой TxtAI Memory Manager на основе официальных примеров
Без изобретения велосипедов - берем готовые паттерны от разработчиков txtai
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

try:
    from txtai.embeddings import Embeddings
    TXTAI_AVAILABLE = True
except ImportError:
    TXTAI_AVAILABLE = False
    print("⚠️ txtai не установлен. Установите: pip install txtai sentence-transformers")

from .models import ConversationSession, ConversationMessage, MessageRole

logger = logging.getLogger(__name__)

class SimpleTxtAIManager:
    """
    Простой менеджер памяти на txtai
    На основе официальных примеров txtai - без лишних усложнений
    """
    
    def __init__(self, data_dir: str = "conversations"):
        """
        Инициализация менеджера
        
        Args:
            data_dir: Директория для хранения данных
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Файлы для хранения
        self.conversations_file = self.data_dir / "conversations.json"
        self.index_path = self.data_dir / "txtai_index"
        
        # Данные в памяти
        self.conversations: Dict[str, ConversationSession] = {}
        self.embeddings = None
        
        # Загружаем данные
        self._load_conversations()
        
        # Инициализируем txtai если доступно
        if TXTAI_AVAILABLE:
            self._init_txtai()
        else:
            logger.warning("txtai недоступен - работаем без семантического поиска")
    
    def _load_conversations(self):
        """Загрузка сохраненных разговоров"""
        if self.conversations_file.exists():
            try:
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Восстанавливаем объекты из JSON
                for conv_data in data:
                    session = ConversationSession(**conv_data)
                    self.conversations[session.session_id] = session
                    
                logger.info(f"Загружено {len(self.conversations)} разговоров")
            except Exception as e:
                logger.error(f"Ошибка загрузки разговоров: {e}")
    
    def _save_conversations(self):
        """Сохранение разговоров в JSON"""
        try:
            # Конвертируем в JSON-совместимый формат
            data = []
            for session in self.conversations.values():
                data.append(session.dict())
            
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
    
    def _init_txtai(self):
        """Инициализация txtai - по примеру из официальной документации"""
        try:
            # Простая конфигурация как в примерах txtai
            self.embeddings = Embeddings({
                "path": "sentence-transformers/all-MiniLM-L6-v2",
                "content": True
            })
            
            # Если есть существующий индекс - загружаем
            if self.index_path.exists():
                self.embeddings.load(str(self.index_path))
                logger.info("Загружен существующий txtai индекс")
            else:
                # Строим новый индекс из существующих данных
                self._rebuild_index()
                
        except Exception as e:
            logger.error(f"Ошибка инициализации txtai: {e}")
            self.embeddings = None
    
    def _rebuild_index(self):
        """Пересборка индекса из всех сообщений"""
        if not self.embeddings:
            return
            
        try:
            # Собираем все сообщения для индексирования
            documents = []
            
            for session in self.conversations.values():
                for message in session.messages:
                    # Формат документа для txtai: (id, text, metadata)
                    doc_id = f"{session.session_id}_{message.id}"
                    doc_text = message.content
                    doc_metadata = {
                        "session_id": session.session_id,
                        "session_title": session.title,
                        "message_id": message.id,
                        "role": message.role.value,
                        "timestamp": message.timestamp.isoformat()
                    }
                    
                    documents.append((doc_id, doc_text, doc_metadata))
            
            if documents:
                # Строим индекс - как в примерах txtai
                self.embeddings.index(documents)
                
                # Сохраняем
                self.index_path.mkdir(exist_ok=True)
                self.embeddings.save(str(self.index_path))
                
                logger.info(f"Построен txtai индекс для {len(documents)} сообщений")
            
        except Exception as e:
            logger.error(f"Ошибка построения индекса: {e}")
    
    def create_session(self, title: str, project_context: str = "GopiAI", 
                      tags: List[str] = None) -> ConversationSession:
        """Создание новой сессии"""
        import uuid
        
        session = ConversationSession(
            session_id=str(uuid.uuid4()),
            title=title,
            project_context=project_context,
            tags=tags or []
        )
        
        self.conversations[session.session_id] = session
        self._save_conversations()
        
        logger.info(f"Создана сессия: {title}")
        return session
    
    def add_message(self, session_id: str, role: str, content: str, 
                   metadata: Dict = None) -> ConversationMessage:
        """Добавление сообщения в сессию"""
        if session_id not in self.conversations:
            raise ValueError(f"Сессия {session_id} не найдена")
        
        import uuid
        
        message = ConversationMessage(
            id=str(uuid.uuid4()),
            role=MessageRole(role),
            content=content,
            metadata=metadata or {}
        )
        
        # Добавляем в сессию
        session = self.conversations[session_id]
        session.messages.append(message)
        session.updated_at = datetime.now()
        
        # Добавляем в txtai индекс
        if self.embeddings:
            try:
                doc_id = f"{session_id}_{message.id}"
                doc_text = content
                doc_metadata = {
                    "session_id": session_id,
                    "session_title": session.title,
                    "message_id": message.id,
                    "role": role,
                    "timestamp": message.timestamp.isoformat()
                }
                
                # Обновляем индекс
                self.embeddings.upsert([(doc_id, doc_text, doc_metadata)])
                self.embeddings.save(str(self.index_path))
                
            except Exception as e:
                logger.error(f"Ошибка обновления индекса: {e}")
        
        self._save_conversations()
        
        logger.debug(f"Добавлено сообщение в сессию {session_id}")
        return message
    
    def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Семантический поиск по разговорам
        Простая реализация как в примерах txtai
        """
        if not self.embeddings:
            logger.warning("txtai недоступен - возвращаем пустые результаты")
            return []
        
        try:
            # Простой поиск как в примерах txtai
            results = self.embeddings.search(query, limit)
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result.get("text", ""),
                    "score": result.get("score", 0.0),
                    "metadata": result.get("metadata", {}),
                    "session_id": result.get("metadata", {}).get("session_id", ""),
                    "session_title": result.get("metadata", {}).get("session_title", "")
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            return []
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Получение сессии по ID"""
        return self.conversations.get(session_id)
    
    def get_all_sessions(self) -> List[ConversationSession]:
        """Получение всех сессий"""
        sessions = list(self.conversations.values())
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions
    
    def get_stats(self) -> Dict[str, Any]:
        """Статистика системы"""
        total_messages = sum(len(s.messages) for s in self.conversations.values())
        
        return {
            "total_sessions": len(self.conversations),
            "total_messages": total_messages,
            "txtai_available": self.embeddings is not None,
            "data_directory": str(self.data_dir)
        }
    
    # Методы совместимости с существующим API
    
    def enrich_message(self, message: str) -> str:
        """Обогащение сообщения контекстом"""
        try:
            results = self.search_conversations(message, limit=3)
            if results:
                context = "\n".join([r["content"][:200] for r in results[:2]])
                return f"{message}\n\nКонтекст:\n{context}"
            return message
        except:
            return message
    
    def save_chat_exchange(self, session_id: str, user_msg: str, ai_response: str):
        """Сохранение обмена сообщениями"""
        try:
            self.add_message(session_id, "user", user_msg)
            self.add_message(session_id, "assistant", ai_response)
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения обмена: {e}")
            return False


# Функция для легкого создания менеджера
def create_txtai_manager(data_dir: str = "rag_memory_system/conversations") -> SimpleTxtAIManager:
    """Создание менеджера памяти txtai"""
    return SimpleTxtAIManager(data_dir)


# Для совместимости с существующим кодом
def get_memory_manager() -> SimpleTxtAIManager:
    """Получить экземпляр менеджера памяти"""
    global _manager
    if '_manager' not in globals():
        _manager = create_txtai_manager()
    return _manager