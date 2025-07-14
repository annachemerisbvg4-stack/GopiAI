# --- START OF FILE rag_system.py (САМОВОССТАНАВЛИВАЮЩАЯСЯ ВЕРСИЯ) ---

import os
import json
import logging
import uuid
import datetime
from pathlib import Path
from typing import List, Dict, Optional

# --- Настройка логирования ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Загрузка конфигурации ---
from rag_config import MEMORY_BASE_DIR, CHATS_FILE_PATH, VECTOR_INDEX_PATH, EMBEDDING_MODEL

# --- Проверка зависимостей ---
try:
    from txtai.embeddings import Embeddings
    TXT_AI_AVAILABLE = True
except ImportError:
    logger.warning("[WARNING] txtai is not installed. Semantic memory will be disabled. Run: pip install txtai[faiss]")
    Embeddings = None
    TXT_AI_AVAILABLE = False

class RAGSystem:
    """
    Unified self-healing RAG system for GopiAI.
    At startup, it checks for all necessary files and folders and creates them if needed.
    """
    _instance: Optional['RAGSystem'] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RAGSystem, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        logger.info("--- Инициализация экземпляра RAGSystem (Singleton) ---")
        self.embeddings: Optional[Embeddings] = None
        
        # ### ИЗМЕНЕНО: ГАРАНТИРУЕМ НАЛИЧИЕ ВСЕХ ФАЙЛОВ ###
        self._ensure_memory_structure()
        
        if TXT_AI_AVAILABLE:
            self._initialize_embeddings()
        
        self._initialized = True

    def _ensure_memory_structure(self):
        """Checks and creates necessary folders and files for memory to work."""
        try:
            logger.info("Checking memory structure in directory: {}".format(MEMORY_BASE_DIR))
            
            # 1. Create base directory /memory
            MEMORY_BASE_DIR.mkdir(parents=True, exist_ok=True)
            
            # 2. Create directory for vectors /memory/vectors
            VECTOR_INDEX_PATH.mkdir(parents=True, exist_ok=True)
            
            # 3. Check and create chats.json if it doesn't exist
            if not CHATS_FILE_PATH.exists():
                logger.warning("File {} not found. Creating a new empty file.".format(CHATS_FILE_PATH))
                with open(CHATS_FILE_PATH, 'w', encoding='utf-8') as f:
                    json.dump([], f) # Create file with an empty list
            
            logger.info("[OK] Memory folder and file structure is in order.")
            
        except Exception as e:
            logger.error("Failed to create memory structure: {}".format(e), exc_info=True)
            raise # If we can't create folders, it's pointless to continue

    def _safe_count(self) -> int:
        """Safely returns the number of vectors, even if the backend is not initialized"""
        try:
            return self.embeddings.count() if self.embeddings else 0
        except Exception:
            return 0

    def _initialize_embeddings(self):
        """Initializes or loads the embeddings database."""
        try:
            logger.info("Initializing embeddings. Model: {}".format(EMBEDDING_MODEL))
            
            config = {"path": EMBEDDING_MODEL, "content": True}
            self.embeddings = Embeddings(config)
            
            # Attempt to load existing index
            if (VECTOR_INDEX_PATH / "config.json").exists():
                logger.info("Found existing index. Attempting to load from {}...".format(VECTOR_INDEX_PATH))
                try:
                    self.embeddings.load(str(VECTOR_INDEX_PATH))
                    logger.info("Index loaded successfully. Records in memory: {}".format(self.embeddings.count()))
                except Exception as load_err:
                    # Index is damaged or incomplete (often missing embeddings file)
                    logger.warning("Failed to load existing index: {}. Will reindex from scratch.".format(load_err))
                    # Clear the directory with the damaged index
                    for item in VECTOR_INDEX_PATH.glob("*"):
                        try:
                            item.unlink(missing_ok=True)
                        except IsADirectoryError:
                            # In case FAISS creates subfolders – remove recursively
                            # На случай, если FAISS создаст подпапки – удаляем рекурсивно
                            import shutil
                            shutil.rmtree(item, ignore_errors=True)
                    
                    # Переинициализируем embeddings с нуля и создаём новый пустой индекс
                    self.embeddings = Embeddings(config)
                    # Продолжаем – далее выполнится переиндексация при пустой базе
                
            # Если база пуста (после загрузки или изначально), индексируем данные
            if self._safe_count() == 0:
                logger.info("Vector database is empty. Starting chat history indexing...")
                self.reindex_all_chats()

        except Exception as e:
            logger.error(f"❌ Критическая ошибка при инициализации txtai: {e}", exc_info=True)
            self.embeddings = None

    def reindex_all_chats(self):
        """Полностью переиндексирует все сообщения из chats.json."""
        if not self.embeddings:
            logger.warning("Переиндексация невозможна: embeddings не инициализированы.")
            return
        
        try:
            with open(CHATS_FILE_PATH, 'r', encoding='utf-8') as f:
                all_messages = json.load(f)
            
            logger.info(f"Загружено сообщений из chats.json: {len(all_messages)}")
            
            if not all_messages:
                logger.info("Chat history file is empty, nothing to index.")
                # Создаем пустой индекс, чтобы система работала корректно
                self.embeddings.index([("dummy_id", {"content": "dummy_text"}, None)])
                self.embeddings.delete(["dummy_id"])
                self.embeddings.save(str(VECTOR_INDEX_PATH))
                return

            # Отладочный вывод: проверяем содержимое первого сообщения
            if len(all_messages) > 0:
                first_msg = all_messages[0]
                logger.info(f"Пример сообщения: {first_msg}")
            
            # Подсчитываем, сколько сообщений проходят каждый этап фильтрации
            dict_count = sum(1 for msg in all_messages if isinstance(msg, dict))
            content_count = sum(1 for msg in all_messages if isinstance(msg, dict) and "content" in msg)
            non_empty_count = sum(1 for msg in all_messages if isinstance(msg, dict) and msg.get("content") and msg["content"].strip())
            non_placeholder_count = sum(1 for msg in all_messages if isinstance(msg, dict) and msg.get("content") 
                                     and msg["content"].strip() and "⏳" not in msg["content"])
            
            logger.info(f"Статистика фильтрации: всего={len(all_messages)}, dict={dict_count}, "
                      f"с полем content={content_count}, непустые={non_empty_count}, без заглушек={non_placeholder_count}")

            # Добавляем более строгую фильтрацию служебных сообщений
            # Исправленная фильтрация и подготовка данных для индексации
            valid_messages = []
            for i, msg in enumerate(all_messages):
                # Проверка структуры и содержания сообщения
                if not isinstance(msg, dict):
                    continue
                if not msg.get("content") or not msg["content"].strip():
                    continue
                if "⏳ Обрабатываю запрос" in msg["content"]:
                    continue
                if "Произошла ошибка" in msg["content"]:
                    continue
                
                # Если прошли все проверки, добавляем сообщение
                msg_id = msg.get("id", f"msg_{i}_{uuid.uuid4()}")
                valid_messages.append((msg_id, msg["content"], None))
            
            # Показываем примеры сообщений, которые мы пытаемся индексировать
            if valid_messages:
                logger.info(f"Пример сообщения для индексации: {valid_messages[0]}")
                
            if valid_messages:
                logger.info(f"Начинаю индексацию {len(valid_messages)} сообщений...")
                
                # Добавляем каждое сообщение по одному для диагностики
                try:
                    # Сначала пробуем простой тестовый документ
                    test_doc = [("test_msg", "This is a test message", None)]
                    self.embeddings.index(test_doc)
                    logger.info(f"Test document indexed. Count: {self.embeddings.count()}")
                    
                    # Теперь индексируем все сообщения
                    self.embeddings.index(valid_messages)
                    self.embeddings.save(str(VECTOR_INDEX_PATH))
                    logger.info(f"✅ Индексация завершена. База сохранена. Записей: {self.embeddings.count()}")
                except Exception as e:
                    logger.error(f"Ошибка при индексации: {e}", exc_info=True)
                    
                    # Пробуем индексировать по одному
                    logger.info("Пробуем индексировать по одному сообщению...")
                    for idx, (doc_id, content, _) in enumerate(valid_messages[:5]):  # Первые 5 сообщений для теста
                        try:
                            self.embeddings.index([(doc_id, content, None)])
                            logger.info(f"  - Сообщение {idx} добавлено. Записей: {self.embeddings.count()}")
                        except Exception as e2:
                            logger.error(f"  - Ошибка при индексации сообщения {idx}: {e2}")
                    
                    self.embeddings.save(str(VECTOR_INDEX_PATH))
                    logger.info(f"Записей после попытки индексировать по одному: {self.embeddings.count()}")

            else:
                logger.warning("В файле истории не найдено валидных сообщений для индексации.")
                # Создаем пустой индекс, чтобы система работала корректно
                self.embeddings.index([("dummy_id", {"content": "dummy_text"}, None)])
                self.embeddings.delete(["dummy_id"])
                self.embeddings.save(str(VECTOR_INDEX_PATH))
                logger.info("Создан пустой индекс для корректной работы системы.")

        except Exception as e:
            logger.error(f"❌ Ошибка при переиндексации чатов: {e}", exc_info=True)

    # ... (методы search и get_context_for_prompt остаются без изменений) ...
    def search(self, query: str, limit: int = 3) -> List[Dict]:
        if not self.embeddings or self.embeddings.count() == 0:
            logger.warning("Поиск невозможен: векторная база пуста.")
            return []
        try:
            results = self.embeddings.search(query, limit)
            logger.info(f"Найдено {len(results)} результатов для запроса: '{query[:40]}...'")
            return results
        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}", exc_info=True)
            return []

    def get_context_for_prompt(self, query: str, limit: int = 3) -> str:
        search_results = self.search(query, limit)
        if not search_results:
            return "No relevant context found in memory."
        context_parts = ["CONTEXT FROM MEMORY:"]
        for res in search_results:
            try:
                # В txtai 6.x+ объект хранится в поле 'object'
                content_obj = res.get('object') if 'object' in res else json.loads(res['text'].replace("'", "\""))
                role = content_obj.get('role', 'unknown')
                content = content_obj.get('content', '')
                context_parts.append(f"- Previous message from {role}: {content}")
            except Exception:
                context_parts.append(f"- {res.get('text', '')}")
        return "\n".join(context_parts)

# --- Singleton Instance ---
_rag_system_instance: Optional[RAGSystem] = None

def get_rag_system() -> RAGSystem:
    """Фабричная функция для получения единственного экземпляра RAGSystem."""
    global _rag_system_instance
    if _rag_system_instance is None:
        logger.info("Создание первого и единственного экземпляра RAGSystem.")
        _rag_system_instance = RAGSystem()
    return _rag_system_instance
    
# --- END OF FILE rag_system.py ---
