"""
Конфигурация RAG Memory системы для GopiAI
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class RAGConfig:
    """Конфигурация для RAG Memory системы"""
    
    # Пути
    base_dir: Path = Path(__file__).parent
    chroma_db_path: str = str(base_dir / "chroma_db")
    conversations_path: str = str(base_dir / "conversations")
    
    # ChromaDB настройки
    collection_name: str = "gopiai_conversations"
    chunk_size: int = 1000
    chunk_overlap: int = 200    # Поиск и ретривер
    top_k_results: int = 5
    similarity_threshold: float = 0.0  # Убираем threshold совсем
    
    # OpenAI настройки (если нужно)
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    embedding_model: str = "text-embedding-3-small"
    
    # Логирование
    log_level: str = "INFO"
    log_file: str = str(base_dir / "rag_memory.log")
    
    # Автосохранение
    auto_save_enabled: bool = True
    save_interval_minutes: int = 30
    
    def __post_init__(self):
        """Создать необходимые директории"""
        os.makedirs(self.chroma_db_path, exist_ok=True)
        os.makedirs(self.conversations_path, exist_ok=True)

# Глобальный экземпляр конфигурации
config = RAGConfig()
