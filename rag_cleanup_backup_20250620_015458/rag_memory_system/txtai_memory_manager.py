"""
🧠 TxtAI Memory Manager для GopiAI
Современная система памяти на основе txtai для семантического поиска
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging

try:
    from txtai import Embeddings
    from txtai.pipeline import Segmentation
except ImportError:
    raise ImportError(
        "❌ txtai не установлен. Установите: pip install txtai>=7.0.0 sentence-transformers>=2.2.0"
    )

from .models import ConversationSession, Message, MessageRole
from .config import MemoryConfig

logger = logging.getLogger(__name__)

class TxtAIMemoryManager:
    """
    Менеджер памяти на основе txtai для GopiAI
    
    Особенности:
    - 🚀 Embedded режим (без отдельного сервера)
    - 🧠 Семантический поиск через txtai
    - 💾 Сохранение в JSON + txtai индекс
    - 🔍 Автоматическое векторизирование текста
    - 🔄 Совместимость с существующими интерфейсами
    """
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        """Инициализация менеджера памяти"""
        self.config = config or MemoryConfig()
        self.data_dir = Path(self.config.data_directory)
        self.data_dir.mkdir(exist_ok=True)
        
        # Файлы для хранения данных
        self.sessions_file = self.data_dir / "sessions.json"
        self.messages_file = self.data_dir / "messages.json"
        self.index_dir = self.data_dir / "txtai_index"
        
        # Хранилища в памяти
        self.sessions: Dict[str, ConversationSession] = {}
        self.messages: Dict[str, Message] = {}
        
        # TxtAI компоненты
        self.embeddings: Optional[Embeddings] = None
        self.segmentation = None
        
        # Загружаем данные и инициализируем txtai
        self._load_data()
        self._initialize_txtai()
        
        logger.info("✅ TxtAI Memory Manager инициализирован")
    
    def _initialize_txtai(self):
        """Инициализация txtai для семантического поиска"""
        try:
            # Настройки для txtai
            config = {
                "path": "sentence-transformers/all-MiniLM-L6-v2",  # Легкая модель
                "content": True,  # Включаем хранение контента
                "objects": True,  # Поддержка объектов
            }
            
            # Создаем embeddings
            self.embeddings = Embeddings(config)
            
            # Сегментация для разбивки длинных текстов
            self.segmentation = Segmentation(sentences=True)
            
            # Загружаем существующий индекс или создаем новый
            if self.index_dir.exists():
                try:
                    self.embeddings.load(str(self.index_dir))
                    logger.info("📂 Загружен существующий txtai индекс")
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось загрузить индекс: {e}")
                    self._rebuild_index()
            else:
                self._rebuild_index()
                
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации txtai: {e}")
            raise
    
    def _rebuild_index(self):
        """Пересборка txtai индекса из существующих сообщений"""
        if not self.embeddings:
            return
        
        logger.info("🔄 Пересборка txtai индекса...")
        
        try:
            # Подготавливаем документы для индексирования
            documents = []
            for message in self.messages.values():
                # Создаем текст документа
                doc_text = f"{message.content}"
                
                # Метаданные
                metadata = {
                    "message_id": message.message_id,
                    "session_id": message.session_id,
                    "role": message.role.value,
                    "timestamp": message.timestamp.isoformat(),
                }
                
                documents.append((message.message_id, doc_text, metadata))
            
            # Строим индекс
            if documents:
                self.embeddings.index(documents)
                
                # Сохраняем индекс
                self.index_dir.mkdir(exist_ok=True)
                self.embeddings.save(str(self.index_dir))
                
                logger.info(f"✅ Индекс создан для {len(documents)} сообщений")
            else:
                logger.info("📝 Нет сообщений для индексирования")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания индекса: {e}")
    
    def _load_data(self):
        """Загрузка данных из JSON файлов"""
        # Загружаем сессии
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    sessions_data = json.load(f)
                    for session_data in sessions_data:
                        session = ConversationSession.from_dict(session_data)
                        self.sessions[session.session_id] = session
                logger.info(f"📂 Загружено {len(self.sessions)} сессий")
            except Exception as e:
                logger.error(f"❌ Ошибка загрузки сессий: {e}")
        
        # Загружаем сообщения
        if self.messages_file.exists():
            try:
                with open(self.messages_file, "r", encoding="utf-8") as f:
                    messages_data = json.load(f)
                    for message_data in messages_data:
                        message = Message.from_dict(message_data)
                        self.messages[message.message_id] = message
                logger.info(f"📂 Загружено {len(self.messages)} сообщений")
            except Exception as e:
                logger.error(f"❌ Ошибка загрузки сообщений: {e}")
    
    def _save_data(self):
        """Сохранение данных в JSON файлы"""
        try:
            # Сохраняем сессии
            sessions_data = [session.to_dict() for session in self.sessions.values()]
            with open(self.sessions_file, "w", encoding="utf-8") as f:
                json.dump(sessions_data, f, ensure_ascii=False, indent=2)
            
            # Сохраняем сообщения
            messages_data = [message.to_dict() for message in self.messages.values()]
            with open(self.messages_file, "w", encoding="utf-8") as f:
                json.dump(messages_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения данных: {e}")
    
    def create_session(
        self, 
        title: str, 
        project_context: str = "GopiAI",
        tags: Optional[List[str]] = None
    ) -> ConversationSession:
        """Создание новой сессии чата"""
        session = ConversationSession(
            session_id=str(uuid.uuid4()),
            title=title,
            project_context=project_context,
            tags=tags or [],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.sessions[session.session_id] = session
        self._save_data()
        
        logger.info(f"✅ Создана сессия: {session.session_id} - {title}")
        return session
    
    def add_message(
        self,
        session_id: str,
        role: Union[MessageRole, str],
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Добавление сообщения в сессию"""
        if session_id not in self.sessions:
            raise ValueError(f"Сессия {session_id} не найдена")
        
        # Конвертируем строку в MessageRole если нужно
        if isinstance(role, str):
            role = MessageRole(role.lower())
        
        message = Message(
            message_id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {}
        )
        
        self.messages[message.message_id] = message
        
        # Обновляем время сессии
        self.sessions[session_id].updated_at = message.timestamp
        
        # Добавляем в txtai индекс
        self._add_to_index(message)
        
        self._save_data()
        
        logger.debug(f"📝 Добавлено сообщение: {message.message_id}")
        return message
    
    def _add_to_index(self, message: Message):
        """Добавление сообщения в txtai индекс"""
        if not self.embeddings:
            return
        
        try:
            # Подготавливаем документ
            doc_text = message.content
            metadata = {
                "message_id": message.message_id,
                "session_id": message.session_id,
                "role": message.role.value,
                "timestamp": message.timestamp.isoformat(),
            }
            
            # Добавляем в индекс
            document = (message.message_id, doc_text, metadata)
            self.embeddings.upsert([document])
            
            # Сохраняем обновленный индекс
            if self.index_dir.exists():
                self.embeddings.save(str(self.index_dir))
                
        except Exception as e:
            logger.error(f"❌ Ошибка добавления в индекс: {e}")
    
    def search_conversations(
        self, 
        query: str, 
        limit: int = 10,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Семантический поиск по сообщениям
        
        Args:
            query: Поисковый запрос
            limit: Максимум результатов
            session_id: Поиск только в определенной сессии
            
        Returns:
            Список результатов с релевантностью
        """
        if not self.embeddings:
            logger.warning("⚠️ txtai не инициализирован, возвращаем пустой результат")
            return []
        
        try:
            # Выполняем семантический поиск
            results = self.embeddings.search(query, limit * 2)  # Берем больше для фильтрации
            
            formatted_results = []
            for result in results:
                if len(formatted_results) >= limit:
                    break
                
                # Получаем метаданные
                message_id = result.get("id")
                if not message_id or message_id not in self.messages:
                    continue
                
                message = self.messages[message_id]
                
                # Фильтрация по сессии
                if session_id and message.session_id != session_id:
                    continue
                
                # Получаем информацию о сессии
                session = self.sessions.get(message.session_id)
                
                formatted_result = {
                    "message_id": message.message_id,
                    "session_id": message.session_id,
                    "session_title": session.title if session else "Unknown",
                    "role": message.role.value,
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat(),
                    "score": result.get("score", 0.0),
                    "metadata": message.metadata
                }
                
                formatted_results.append(formatted_result)
            
            logger.info(f"🔍 Поиск '{query}': найдено {len(formatted_results)} результатов")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")
            return []
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Получение сессии по ID"""
        return self.sessions.get(session_id)
    
    def get_session_messages(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[Message]:
        """Получение сообщений сессии"""
        session_messages = [
            msg for msg in self.messages.values() 
            if msg.session_id == session_id
        ]
        
        # Сортируем по времени
        session_messages.sort(key=lambda m: m.timestamp)
        
        if limit:
            session_messages = session_messages[-limit:]
        
        return session_messages
    
    def get_all_sessions(self) -> List[ConversationSession]:
        """Получение всех сессий"""
        sessions = list(self.sessions.values())
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Удаление сессии и всех её сообщений"""
        if session_id not in self.sessions:
            return False
        
        # Удаляем сообщения сессии
        message_ids_to_delete = [
            msg_id for msg_id, msg in self.messages.items()
            if msg.session_id == session_id
        ]
        
        for msg_id in message_ids_to_delete:
            del self.messages[msg_id]
        
        # Удаляем сессию
        del self.sessions[session_id]
        
        # Пересобираем индекс
        self._rebuild_index()
        self._save_data()
        
        logger.info(f"🗑️ Удалена сессия {session_id} и {len(message_ids_to_delete)} сообщений")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики системы памяти"""
        return {
            "total_sessions": len(self.sessions),
            "total_messages": len(self.messages),
            "txtai_enabled": self.embeddings is not None,
            "data_directory": str(self.data_dir),
            "index_directory": str(self.index_dir) if self.index_dir.exists() else None,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    # Методы для совместимости с существующим API
    
    def enrich_message(self, message_content: str, context: str = "") -> str:
        """
        Обогащение сообщения контекстом из памяти
        Совместимость с существующим API
        """
        try:
            # Ищем релевантные сообщения
            search_query = f"{message_content} {context}".strip()
            results = self.search_conversations(search_query, limit=3)
            
            if not results:
                return message_content
            
            # Добавляем контекст
            context_parts = []
            for result in results:
                context_parts.append(f"Контекст: {result['content'][:200]}...")
            
            enriched = f"{message_content}\n\nРелевантный контекст:\n" + "\n".join(context_parts)
            return enriched
            
        except Exception as e:
            logger.error(f"❌ Ошибка обогащения сообщения: {e}")
            return message_content
    
    def save_chat_exchange(
        self, 
        session_id: str,
        user_message: str,
        ai_response: str,
        metadata: Optional[Dict] = None
    ) -> tuple[Message, Message]:
        """
        Сохранение обмена сообщениями (пользователь + ИИ)
        Совместимость с существующим API
        """
        # Сохраняем сообщение пользователя
        user_msg = self.add_message(
            session_id=session_id,
            role=MessageRole.USER,
            content=user_message,
            metadata=metadata
        )
        
        # Сохраняем ответ ИИ
        ai_msg = self.add_message(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=ai_response,
            metadata=metadata
        )
        
        return user_msg, ai_msg
    
    def __del__(self):
        """Деструктор - сохраняем данные при закрытии"""
        try:
            self._save_data()
        except:
            pass