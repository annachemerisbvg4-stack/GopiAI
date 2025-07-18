"""
Core memory management functionality for GopiAI.

This package provides memory configuration without UI dependencies,
making it suitable for testing and non-UI applications.
"""

from .memory_config import MEMORY_BASE_DIR, CHATS_FILE_PATH, VECTOR_INDEX_PATH, CREWAI_ROOT

__all__ = ['MEMORY_BASE_DIR', 'CHATS_FILE_PATH', 'VECTOR_INDEX_PATH', 'CREWAI_ROOT']
