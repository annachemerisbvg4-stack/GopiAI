"""
Dialogs - Modal and dialog window components

This module contains dialog windows and popup interfaces including:
- Chat and search dialogs
- Agent communication dialogs  
- Utility dialogs (emoji picker)
- Reasoning and coding agent interfaces
"""

# Импортируем только существующие файлы
from .emoji_dialog import EmojiDialog
from .reasoning_agent_dialog import ReasoningAgentDialog

__all__ = [
    'EmojiDialog',
    'ReasoningAgentDialog'
]