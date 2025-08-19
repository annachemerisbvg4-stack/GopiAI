"""
Memory management package for GopiAI

This package provides memory management functionality, including:
- Short-term chat history
- Long-term semantic memory
- Emotion analysis
- Session management
"""

from .manager import MemoryManager, get_memory_manager

# Export public API
__all__ = ['MemoryManager', 'get_memory_manager']
