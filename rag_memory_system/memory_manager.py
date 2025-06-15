"""
Основной класс RAG Memory Manager для управления разговорами и поиском
"""
import json
import uuid
import logging
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.embeddings.base import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

from models import ConversationSession, ConversationMessage, MessageRole, SearchResult, MemoryStats
from config import config

JSON_GLOB_PATTERN = "*.json"

class SimpleEmbeddings(Embeddings):
    """Простые эмбеддинги без зависимости от OpenAI"""
    
    def __init__(self):
        # Используем HuggingFace эмбеддинги (бесплатные)
        self.hf_embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.hf_embeddings.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        return self.hf_embeddings.embed_query(text)

class SafePathManager:
    """Безопасное управление путями файловой системы"""
    
    ALLOWED_EXTENSIONS = {'.json', '.txt', '.md'}
    SAFE_FILENAME_PATTERN = re.compile(r'^[\w\-\.]+$')
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir).resolve()
        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_filename(self, filename: str) -> bool:
        """Проверка имени файла по белому списку"""
        return bool(self.SAFE_FILENAME_PATTERN.match(filename))
    
    def get_safe_path(self, filename: str) -> Path:
        """Получить безопасный путь к файлу"""
        if not self.validate_filename(filename):
            raise ValueError(f"Invalid filename: {filename}")
            
        # Проверяем расширение
        suffix = Path(filename).suffix.lower()
        if suffix not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file extension: {suffix}")
        
        # Создаем путь относительно базовой директории
        safe_path = (self.base_dir / filename).resolve()
        
        # Проверяем, что путь находится внутри базовой директории
        try:
            safe_path.relative_to(self.base_dir)
        except ValueError:
            raise ValueError("Path is outside of allowed directory")
            
        return safe_path

class RAGMemoryManager:
    """Главный класс для управления RAG памятью разговоров"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Инициализация компонентов
        self.embeddings = SimpleEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Инициализация ChromaDB
        self.setup_chroma_db()
        
        # Кэш активных сессий
        self.active_sessions: Dict[str, ConversationSession] = {}
        
        # Инициализация SafePathManager
        self.path_manager = SafePathManager(Path(config.conversations_path))
        
        self.logger.info("RAG Memory Manager инициализирован")
    
    def setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def setup_chroma_db(self):
        """Настройка ChromaDB для векторного поиска"""
        try:
            # Инициализация ChromaDB клиента
            self.chroma_client = chromadb.PersistentClient(path=config.chroma_db_path)
            
            # Получение или создание коллекции
            try:
                self.collection = self.chroma_client.get_collection(config.collection_name)
                self.logger.info(f"Найдена существующая коллекция: {config.collection_name}")
            except chromadb.ApiError:
                self.collection = self.chroma_client.create_collection(config.collection_name)
                self.logger.info(f"Создана новая коллекция: {config.collection_name}")
            
            # Инициализация LangChain Chroma
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name=config.collection_name,
                embedding_function=self.embeddings,
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки ChromaDB: {e}")
            raise
    
    def create_session(self, title: str, project_context: Optional[str] = None, 
                      tags: Optional[List[str]] = None) -> ConversationSession:
        """Создать новую сессию разговора"""
        session_id = str(uuid.uuid4())
        session = ConversationSession(
            session_id=session_id,
            title=title,
            project_context=project_context,
            tags=tags or [],
            summary=""  # Добавляем пустую строку как начальное значение для summary
        )
        
        self.active_sessions[session_id] = session
        self.logger.info("Создана новая сессия (ID скрыт)")
        return session
    
    def add_message(self, session_id: str, role: MessageRole, content: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> ConversationMessage:
        """Добавить сообщение в сессию"""
        if session_id not in self.active_sessions:
            # Попытаемся загрузить сессию из файла
            session = self.load_session(session_id)
            if not session:
                raise ValueError("Сессия не найдена")
            self.active_sessions[session_id] = session
        
        session = self.active_sessions[session_id]
        message = session.add_message(role, content, metadata or {})
        
        # Автосохранение если включено
        if config.auto_save_enabled:
            self.save_session(session)
        
        self.logger.info("Добавлено сообщение в сессию (ID скрыт)")
        return message
    
    def _get_session_filename(self, session_id: str) -> str:
        """Генерация имени файла сессии на основе хэшированного session_id"""
        hashed_id = hashlib.sha256(session_id.encode()).hexdigest()[:16]
        return f"{hashed_id}.json"
    
    def save_session(self, session: ConversationSession):
        """Сохранить сессию в файл и индексировать в векторной БД"""
        try:
            file_name = self._get_session_filename(session.session_id)
            session_file = self.path_manager.get_safe_path(file_name)
            
            # Сохранение в JSON файл
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.model_dump(), f, ensure_ascii=False, indent=2, default=str)
            
            # Индексирование в векторной БД
            self.index_session(session)
            
            self.logger.info("Сессия сохранена")
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения сессии: {e}")
            raise

    def load_session(self, session_id: str) -> Optional[ConversationSession]:
        """Загрузить сессию из файла"""
        try:
            file_name = self._get_session_filename(session_id)
            session_file = self.path_manager.get_safe_path(file_name)
            
            if not session_file.exists():
                return None
            
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session = ConversationSession(**data)
            self.logger.info("Сессия загружена")
            return session
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки сессии: {e}")
            return None
    
    def index_session(self, session: ConversationSession):
        """Индексировать сессию в векторной БД"""
        try:
            # Получаем текст для индексации
            context_text = session.get_context_string()
            
            # Разбиваем на чанки
            chunks = self.text_splitter.split_text(context_text)
            
            # Подготавливаем метаданные
            metadata = {
                "session_id": session.session_id,
                "title": session.title,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "tags": ",".join(session.tags),
                "project_context": session.project_context or "",
                "message_count": len(session.messages)
            }
            
            # Добавляем чанки в векторную БД
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_id"] = f"{session.session_id}_chunk_{i}"
                
                self.vector_store.add_texts(
                    texts=[chunk],
                    metadatas=[chunk_metadata],
                    ids=[chunk_metadata["chunk_id"]]
                )
            
            self.logger.info(f"Сессия проиндексирована ({len(chunks)} чанков)")
            
        except Exception as e:
            self.logger.error(f"Ошибка индексации сессии: {e}")
    
    def search_conversations(self, query: str, limit: Optional[int] = None) -> List[SearchResult]:
        """Поиск релевантных разговоров"""
        try:
            limit = limit or config.top_k_results
            
            # Поиск в векторной БД
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=limit
            )
            
            search_results = []
            for doc, score in results:
                # Преобразуем score в релевантность (чем меньше distance, тем выше релевантность)
                relevance = max(0, 1 - score)
                
                if relevance >= config.similarity_threshold:
                    result = SearchResult(
                        session_id=doc.metadata["session_id"],
                        title=doc.metadata["title"],
                        relevance_score=relevance,
                        matched_content=doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                        context_preview=doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        timestamp=datetime.fromisoformat(doc.metadata["created_at"]),
                        tags=doc.metadata["tags"].split(",") if doc.metadata["tags"] else []
                    )
                    search_results.append(result)
            
            # Сортируем по релевантности
            search_results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            self.logger.info(f"Найдено {len(search_results)} релевантных разговоров")
            return search_results
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска: {e}")
            return []
    
    def get_conversation_history(self, session_id: str) -> Optional[ConversationSession]:
        """Получить историю конкретного разговора"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        return self.load_session(session_id)
    
    def get_memory_stats(self) -> MemoryStats:
        """Получить статистику памяти"""
        try:
            # Используем безопасный путь для поиска файлов
            json_files = list(self.path_manager.base_dir.glob(JSON_GLOB_PATTERN))
            total_sessions = len(json_files)
            total_messages, oldest_date, newest_date, all_tags = self._analyze_json_files(json_files)
            most_active_tags = self._compute_most_active_tags(all_tags)
            storage_size = self._compute_storage_size([Path(config.conversations_path), Path(config.chroma_db_path)])
            total_documents = self.collection.count()

            return MemoryStats(
                total_sessions=total_sessions,
                total_messages=total_messages,
                total_documents=total_documents,
                oldest_session=oldest_date,
                newest_session=newest_date,
                most_active_tags=most_active_tags,
                storage_size_mb=storage_size / (1024 * 1024)
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return MemoryStats(
                total_sessions=0, 
                total_messages=0, 
                total_documents=0,
                oldest_session=None,
                newest_session=None,
                most_active_tags=[],
                storage_size_mb=0.0
            )
    
    def cleanup_old_sessions(self, days_old: int = 30):
        """Очистка старых сессий (архивирование)"""
        archive_dir = self.path_manager.base_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        cutoff_date = datetime.now() - timedelta(days=days_old)

        for session_file in self.path_manager.base_dir.glob(JSON_GLOB_PATTERN):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                session_date = datetime.fromisoformat(data["created_at"])
                if session_date < cutoff_date:
                    archived_file = archive_dir / session_file.name
                    session_file.replace(archived_file)
                    self.logger.info("Сессия архивирована.")
            except Exception as e:
                self.logger.warning(f"Ошибка архивирования (файл скрыт): {e}")
    
    def _collect_sessions_data(self):
        sessions_data = []
        for session_file in self.path_manager.base_dir.glob(JSON_GLOB_PATTERN):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                sessions_data.append(data)
            except Exception as e:
                self.logger.warning(f"Файл {session_file} пропущен: {e}")
        return sessions_data

    def _export_to_json(self, sessions_data, output_file):
        with open(output_file, 'w', encoding='utf-8') as out:
            json.dump(sessions_data, out, ensure_ascii=False, indent=2)

    def _export_to_csv(self, sessions_data, output_file):
        import csv
        if sessions_data:
            field_names = list(sessions_data[0].keys())
            with open(output_file, 'w', newline='', encoding='utf-8') as out:
                writer = csv.DictWriter(out, fieldnames=field_names)
                writer.writeheader()
                for row in sessions_data:
                    writer.writerow(row)

    def _export_to_markdown(self, sessions_data, output_file):
        with open(output_file, 'w', encoding='utf-8') as out:
            for session in sessions_data:
                out.write(f"# {session.get('title','Без названия')}\n\n")
                out.write(f"**ID:** {session.get('session_id','')}\n\n")
                out.write("## Сообщения:\n")
                for msg in session.get('messages', []):
                    out.write(f"- **{msg.get('role')}**: {msg.get('content')}\n")
                out.write("\n---\n\n")

    def export_conversations(self, output_file: str, format: str = "json"):
        """Экспорт разговоров в различные форматы"""
        sessions_data = self._collect_sessions_data()
        fmt = format.lower()
        if fmt == "json":
            self._export_to_json(sessions_data, output_file)
        elif fmt == "csv":
            self._export_to_csv(sessions_data, output_file)
        elif fmt in ["md", "markdown"]:
            self._export_to_markdown(sessions_data, output_file)
        else:
            self.logger.warning(f"Неизвестный формат: {format}")
    
    def _analyze_json_files(self, json_files: List[Path]):
        total_messages = 0
        oldest_date = None
        newest_date = None
        all_tags = []
        for session_file in json_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                total_messages += len(data.get("messages", []))
                created_at = datetime.fromisoformat(data["created_at"])
                
                if oldest_date is None or created_at < oldest_date:
                    oldest_date = created_at
                if newest_date is None or created_at > newest_date:
                    newest_date = created_at
                
                all_tags.extend(data.get("tags", []))
                
            except Exception:
                self.logger.warning(f"Ошибка чтения файла {session_file}")
        
        return total_messages, oldest_date, newest_date, all_tags

    def _compute_most_active_tags(self, all_tags: List[str]) -> List[str]:
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return sorted(tag_counts.keys(), key=lambda x: tag_counts[x], reverse=True)[:10]

    def _compute_storage_size(self, paths: List[Path]) -> int:
        storage_size = 0
        for path in paths:
            if path.exists():
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        storage_size += file_path.stat().st_size
        return storage_size
