"""
Dialogs - Modal and dialog window components

This module contains dialog windows and popup interfaces including:
- Chat and search dialogs
- Agent communication dialogs  
- Utility dialogs (emoji picker)
- Reasoning and coding agent interfaces
"""

from .chat_search_dialog import ChatSearchDialog
# Временно отключены для исправления импортов
# from .coding_agent_dialog import CodingAgentDialog
# from .emoji_dialog import EmojiDialog
# from .reasoning_agent_dialog import ReasoningAgentDialog

__all__ = [
    'ChatSearchDialog',
    # 'CodingAgentDialog', 
    # 'EmojiDialog',
    # 'ReasoningAgentDialog'
]