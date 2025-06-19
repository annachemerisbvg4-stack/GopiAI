"""
TxtAI Memory System for GopiAI
Simplified RAG replacement using txtai
"""
from .txtai_memory_manager import TxtAIMemoryManager
from .models import ConversationSession, ConversationMessage, MessageRole, SearchResult

__all__ = ['TxtAIMemoryManager', 'ConversationSession', 'ConversationMessage', 'MessageRole', 'SearchResult']
