"""
Core memory management functionality for GopiAI.

This package provides memory management functionality without UI dependencies,
making it suitable for testing and non-UI applications.
"""

from .manager import MemoryManager, get_memory_manager

__all__ = ['MemoryManager', 'get_memory_manager']
