"""
AutoGen Extension Package for GopiAI

Мультиагентная система на основе AutoGen с поддержкой Cerebras и OpenAI
"""

from .autogen_extension import add_autogen_dock, init_autogen_extension

__version__ = "1.0.0"
__all__ = ['add_autogen_dock', 'init_autogen_extension']