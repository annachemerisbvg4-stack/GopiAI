"""
GopiAI Memory System - Simple TxtAI Integration
Простая система памяти на основе txtai
"""

from .simple_memory_manager import SimpleMemoryManager, get_memory_manager
from .models import ConversationSession, MessageRole

# Алиас для совместимости
TxtAIMemoryManager = SimpleMemoryManager

__all__ = [
    "SimpleMemoryManager",
    "TxtAIMemoryManager", 
    "get_memory_manager",
    "ConversationSession",
    "MessageRole"
]
