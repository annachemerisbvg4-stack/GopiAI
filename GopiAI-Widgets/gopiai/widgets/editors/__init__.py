"""
Editors - Code editing and syntax highlighting components

This module contains editor components including:
- Advanced code editors with syntax highlighting
- Language-specific syntax highlighters
- Code formatting and analysis tools
"""

# Импортируем только существующие файлы
from .syntax_highlighter import PythonHighlighter

__all__ = [
    'PythonHighlighter'
]