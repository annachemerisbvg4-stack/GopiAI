"""
GopiAI Core Module

This package contains core functionality for the GopiAI application,
including AI tools, memory management, and other essential components.
"""

# Import the required functions directly
from .ai_tools import get_ui_assistant_tool
from .ai_tools.ui_assistant import UIAssistantTool

# Create aliases for backward compatibility
get_ui_assistant = get_ui_assistant_tool

__all__ = ['get_ui_assistant', 'get_ui_assistant_tool', 'UIAssistantTool']
