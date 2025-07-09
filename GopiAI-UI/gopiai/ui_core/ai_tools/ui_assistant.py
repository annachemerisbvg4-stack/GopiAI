"""
UI Assistant Tool for AI (Core Functionality)

This module provides core tools for the AI to interact with the UI on behalf of the user.
It integrates with the AI Control System to perform actions like clicking, typing,
navigating, and more.

Note: This is a non-UI version of the assistant. The UI components have been moved to ChatWidget.
"""

import asyncio
import json
import os
import time
from typing import Dict, List, Optional, Any, Union, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum, auto

from PySide6.QtCore import QObject, Signal, Slot, Qt, QPoint, QSize, QRect
from PySide6.QtGui import QPixmap

# Import types to avoid circular imports
from .types import CommandType, AICommand

# Lazy import to avoid circular dependencies
if TYPE_CHECKING:
    from gopiai.ui.components.ai_control import AIControlSystem

class UIAssistantTool(QObject):
    """
    UI Assistant Tool that allows the AI to interact with the UI.
    
    This tool provides methods for the AI to perform actions in the UI
    and get information about the current state of the application.
    """
    
    # Signals for communication with the main UI
    action_started = Signal(str)  # Message about the action being performed
    action_completed = Signal(str, bool)  # Action description, success status
    visual_feedback = Signal(str, dict)  # Type of feedback, data
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        # Lazy import to avoid circular dependencies
        from gopiai.ui.components.ai_control import AIControlSystem
        
        self.ai_control = AIControlSystem()
        self._setup_connections()
        self.current_context = {}
        
        # Visual feedback elements (moved to ChatWidget)
        self.main_window = None
        
    def _setup_connections(self):
        """Set up signal connections."""
        self.ai_control.command_started.connect(self._on_command_started)
        self.ai_control.command_completed.connect(self._on_command_completed)
        self.ai_control.status_updated.connect(self._on_status_updated)
        self.ai_control.screenshot_captured.connect(self._on_screenshot_captured)
    
    def _setup_visual_feedback(self):
        """Set up visual feedback elements."""
        # UI elements have been moved to ChatWidget
        pass
    
    def set_main_window(self, window):
        """Set the main window reference for positioning the overlay."""
        self.main_window = window
    
    def show_status_message(self, message: str, duration: int = 3000):
        """Show a status message to the user."""
        # Emit signal that will be handled by ChatWidget
        self.visual_feedback.emit("status_message", {"message": message, "duration": duration})
    
    def highlight_element(self, rect: QRect, duration: int = 1000):
        """Request to highlight an element on the screen."""
        # Emit signal that will be handled by ChatWidget
        self.visual_feedback.emit("highlight_element", {
            "x": rect.x(),
            "y": rect.y(),
            "width": rect.width(),
            "height": rect.height(),
            "duration": duration
        })
    
    # Signal handlers
    def _on_command_started(self, command: AICommand):
        """Handle command started event."""
        action_desc = self._get_action_description(command)
        self.action_started.emit(f"Выполняю: {action_desc}")
        self.show_status_message(f"Выполняю: {action_desc}")
        self.update_status(f"Выполняю: {action_desc}")
        
        # Show visual feedback for the command
        if command.type == CommandType.CLICK and command.x and command.y:
            self.highlight_element(QRect(command.x - 10, command.y - 10, 20, 20), 1.0)
    
    def _on_command_completed(self, command: AICommand, success: bool):
        """Handle command completed event."""
        action_desc = self._get_action_description(command)
        status = "успешно" if success else "с ошибкой"
        self.action_completed.emit(f"Действие завершено {status}: {action_desc}", success)
        self.update_status(f"Готово: {action_desc}", 2.0)
    
    def _on_status_updated(self, status: str):
        """Handle status updates from the AI control system."""
        self.update_status(status)
    
    def _on_screenshot_captured(self, screenshot: QPixmap):
        """Handle screenshot captured event."""
        # Emit the screenshot for any UI components that need it
        self.visual_feedback.emit("screenshot", {"image": screenshot})
    
    def _get_action_description(self, command: AICommand) -> str:
        """Get a human-readable description of a command."""
        if command.type == CommandType.CLICK:
            return f"Клик в точке ({command.x}, {command.y})"
        elif command.type == CommandType.INPUT:
            return f"Ввод текста в поле"
        elif command.type == CommandType.NAVIGATE:
            return f"Переход к {command.target}"
        elif command.type == CommandType.WAIT:
            return f"Ожидание {command.duration} сек."
        return f"Неизвестное действие: {command.type}"
    
    # Public API for the AI to use
    
    async def help_with_ui(self, user_request: str) -> str:
        """
        Help the user with a UI-related task.
        
        Args:
            user_request: The user's request for help with the UI.
            
        Returns:
            A message describing what actions were taken.
        """
        try:
            # Show visual feedback
            self.show_visual_feedback(True)
            self.update_status(f"Помогаю с: {user_request}")
            
            # Capture the current screen
            screenshot = self.ai_control.capture_screen()
            if not screenshot:
                return "Не удалось сделать скриншот экрана."
            
            # Analyze the screen and get commands from the AI
            commands = await self.ai_control.get_ai_commands(screenshot, user_request)
            if not commands:
                return "Не удалось определить, как помочь с этим запросом."
            
            # Execute the commands
            results = []
            for cmd in commands:
                success = await self.ai_control.execute_command(cmd)
                results.append((cmd, success))
                
                # Small delay between commands
                await asyncio.sleep(0.5)
            
            # Generate a summary of actions taken
            success_count = sum(1 for _, success in results if success)
            return f"Выполнено {success_count} из {len(results)} действий для выполнения запроса."
            
        except Exception as e:
            return f"Произошла ошибка при выполнении запроса: {str(e)}"
        finally:
            # Hide visual feedback after a delay
            QTimer.singleShot(2000, lambda: self.show_visual_feedback(False))
    
    async def click_at(self, x: int, y: int) -> bool:
        """Click at the specified coordinates."""
        return await self.ai_control.execute_command(AICommand(
            type=CommandType.CLICK,
            x=x,
            y=y
        ))
    
    async def type_text(self, selector: str, text: str) -> bool:
        """Type text into the specified input field."""
        return await self.ai_control.execute_command(AICommand(
            type=CommandType.INPUT,
            selector=selector,
            text=text
        ))
    
    async def navigate_to(self, target: str) -> bool:
        """Navigate to the specified target."""
        return await self.ai_control.execute_command(AICommand(
            type=CommandType.NAVIGATE,
            target=target
        ))
    
    def get_ui_state(self) -> Dict[str, Any]:
        """
        Get the current state of the UI.
        
        Returns:
            A dictionary containing information about the current UI state.
        """
        # Capture the current screen
        screenshot = self.ai_control.capture_screen()
        screenshot_data = None
        
        if screenshot:
            # Convert to base64 for JSON serialization
            import base64
            from io import BytesIO
            
            buffer = BytesIO()
            screenshot.save(buffer, "PNG")
            screenshot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Get information about the active window/widget
        active_window = QApplication.activeWindow()
        active_widget = QApplication.focusWidget()
        
        return {
            "screenshot": screenshot_data,
            "active_window": active_window.objectName() if active_window else None,
            "active_widget": active_widget.objectName() if active_widget else None,
            "mouse_position": QCursor.pos().toTuple(),
            "timestamp": time.time()
        }

# Singleton instance
_ui_assistant_instance = None

def get_ui_assistant() -> UIAssistantTool:
    """Get the global UI Assistant instance."""
    global _ui_assistant_instance
    if _ui_assistant_instance is None:
        _ui_assistant_instance = UIAssistantTool()
    return _ui_assistant_instance
