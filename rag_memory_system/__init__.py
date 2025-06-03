"""
Инициализация пакета RAG Memory системы
"""
from .memory_manager import RAGMemoryManager
from .models import ConversationSession, ConversationMessage, MessageRole, SearchResult, MemoryStats
from .config import config
from .client import RAGMemoryClient

__version__ = "1.0.0"
__all__ = [
    "RAGMemoryManager",
    "ConversationSession", 
    "ConversationMessage",
    "MessageRole",
    "SearchResult",
    "MemoryStats",
    "config",
    "RAGMemoryClient"
]
