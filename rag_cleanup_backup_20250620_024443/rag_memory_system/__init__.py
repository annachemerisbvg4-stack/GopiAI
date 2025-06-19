"""
GopiAI Memory System - TxtAI Integration
Система памяти на основе txtai для семантического поиска
"""

from .txtai_memory_manager import TxtAIMemoryManager
from .models import ConversationSession, Message, MessageRole
from .config import MemoryConfig

__all__ = [
    "TxtAIMemoryManager",
    "ConversationSession", 
    "Message",
    "MessageRole",
    "MemoryConfig"
]

# Основной менеджер памяти (txtai)
memory_manager = None

def get_memory_manager() -> TxtAIMemoryManager:
    """Получить экземпляр менеджера памяти"""
    global memory_manager
    if memory_manager is None:
        memory_manager = TxtAIMemoryManager()
    return memory_manager
