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
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum, auto

# Import performance optimization utilities
from ...utils.performance import async_execute, AsyncTask, cached

from PySide6.QtCore import QObject, Signal, Slot, Qt, QPoint, QSize, QRect, QTimer
from PySide6.QtGui import QPixmap, QGuiApplication, QCursor
from PySide6.QtWidgets import QApplication

# Import security module
from .security import (
    SecurityManager, SecurityContext, OperationType,
    ValidationError, PermissionDeniedError,
    security_manager
)

# Import types to avoid circular imports
from .types import CommandType, AICommand

# Import the session logger
from .session_logger import get_session_logger

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
        
        # Initialize the session logger
        self.logger = get_session_logger()
        self.logger.log_action("Initializing UIAssistantTool")
        
        try:
            # Initialize security context
            self._security_context = SecurityContext(
                user_id="default",
                permissions={
                    "execute_ui_commands",
                    "access_ui_elements",
                    "capture_screen"
                },
                is_privileged=False
            )
            
            # Initialize security manager
            self.security_manager = security_manager
            
            # Initialize AI control system
            self.ai_control = AIControlSystem()
            self._setup_connections()
            self.current_context = {}
            
            # Visual feedback elements (moved to ChatWidget)
            self.main_window = None
            
            # Get screen geometry for coordinate validation
            self.screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
            
            # Cache for expensive operations
            self._ui_state_cache = None
            self._last_ui_state_time = 0
            self._ui_state_cache_ttl = 5.0  # seconds
            
            self.logger.log_action("UIAssistantTool initialized successfully")
        except Exception as e:
            self.logger.log_error(f"Failed to initialize UIAssistantTool: {str(e)}", exc_info=sys.exc_info())
            raise
        
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
        status_msg = f"Выполняю: {action_desc}"
        
        # Log the command
        self.logger.log_action("Command started", {
            "command": command.type.name if hasattr(command.type, 'name') else str(command.type),
            "description": action_desc,
            "x": getattr(command, 'x', None),
            "y": getattr(command, 'y', None)
        })
        
        # Update UI
        self.action_started.emit(status_msg)
        self.show_status_message(status_msg)
        self.update_status(status_msg)
        
        # Show visual feedback for the command
        if command.type == CommandType.CLICK and command.x and command.y:
            self.highlight_element(QRect(command.x - 10, command.y - 10, 20, 20), 1.0)
    
    def _on_command_completed(self, command: AICommand, success: bool):
        """Handle command completed event."""
        action_desc = self._get_action_description(command)
        status = "успешно" if success else "с ошибкой"
        status_msg = f"Действие завершено {status}: {action_desc}"
        
        # Log command completion
        self.logger.log_action("Command completed" if success else "Command failed", {
            "command": command.type.name if hasattr(command.type, 'name') else str(command.type),
            "description": action_desc,
            "success": success
        })
        
        # Update UI
        self.action_completed.emit(status_msg, success)
        self.update_status(f"Готово: {action_desc}", 2.0)
    
    def _on_status_updated(self, status: str):
        """Handle status updates from the AI control system."""
        self.logger.log_action("Status updated", {"status": status})
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
    
    @async_execute
    def _process_ui_help_request(self, user_request: str) -> str:
        """
        Process the UI help request (run in a separate thread).
        
        Args:
            user_request: The user's request for help with the UI.
        
        Returns:
            A message describing what actions were taken.
        """
        try:
            # Simulate processing time
            time.sleep(1)
            
            # In a real implementation, this would use AI to determine actions
            return "Я помогу вам с этим интерфейсом. Что именно вызывает у вас затруднения?"
            
        except Exception as e:
            error_msg = f"Failed to process UI help request: {str(e)}"
            self.logger.log_error(error_msg, exc_info=sys.exc_info())
            return "Извините, произошла ошибка при обработке вашего запроса."

    async def help_with_ui(self, user_request: str) -> str:
        """
        Help the user with a UI-related task.
        
        Args:
            user_request: The user's request for help with the UI.
        
        Returns:
            A message describing what actions were taken.
        """
        try:
            # Log the request
            self.logger.log_action("UI help requested", {"request": user_request})
            
            # Process the request asynchronously
            return await self._process_ui_help_request(user_request)
            
        except Exception as e:
            error_msg = f"Failed to process UI help request: {str(e)}"
            self.logger.log_error(error_msg, exc_info=sys.exc_info())
            return "Извините, произошла ошибка при обработке вашего запроса."

    async def click_at(self, x: int, y: int) -> bool:
        """
        Click at the specified screen coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            bool: True if the click was successful, False otherwise
        
        Raises:
            ValidationError: If coordinates are invalid
            PermissionDeniedError: If operation is not allowed
        """
        self.logger.log_action("Click command", {"x": x, "y": y})
        
        try:
            # Validate coordinates
            is_valid, error_msg = self.security_manager.validate_click_coordinates(
                x, y, self.screen_geometry
            )
            if not is_valid:
                raise ValidationError(f"Invalid click coordinates: {error_msg}")
            
            # Check permissions
            allowed, reason = self.security_manager.check_permission(
                self._security_context, OperationType.CLICK
            )
            if not allowed:
                raise PermissionDeniedError(reason or "Click operation not permitted")
            
            # Execute the command
            result = await self.ai_control.execute_command(AICommand(
                type=CommandType.CLICK,
                x=x,
                y=y
            ))
            
            self.logger.log_action("Click command executed", {
                "x": x, 
                "y": y, 
                "success": result
            })
            
            return result
            
        except (ValidationError, PermissionDeniedError):
            # Re-raise security-related exceptions
            raise
            
        except Exception as e:
            self.logger.log_error(
                f"Error in click_at({x}, {y}): {str(e)}", 
                exc_info=sys.exc_info()
            )
            raise
    
    async def type_text(self, selector: str, text: str, max_length: int = 1000) -> bool:
        """
        Type text into the specified input field.
        
        Args:
            selector: CSS selector for the input field
            text: Text to type
            max_length: Maximum allowed text length (default: 1000)
        
        Returns:
            bool: True if the text was typed successfully, False otherwise
        
        Raises:
            ValidationError: If input validation fails
            PermissionDeniedError: If operation is not allowed
        """
        self.logger.log_action("Type text command", {
            "selector": selector, 
            "text_length": len(text)
        })
        
        try:
            # Validate input
            is_valid, error_msg = self.security_manager.validate_text_input(
                text, max_length
            )
            if not is_valid:
                raise ValidationError(f"Invalid text input: {error_msg}")
                
            # Validate selector
            if not selector or not isinstance(selector, str) or len(selector) > 1000:
                raise ValidationError("Invalid selector")
            
            # Check permissions
            allowed, reason = self.security_manager.check_permission(
                self._security_context, OperationType.TYPE_TEXT
            )
            if not allowed:
                raise PermissionDeniedError(reason or "Type text operation not permitted")
            
            # Execute the command
            result = await self.ai_control.execute_command(AICommand(
                type=CommandType.INPUT,
                selector=selector,
                text=text
            ))
            
            self.logger.log_action("Type text command executed", {
                "selector": selector, 
                "text_length": len(text),
                "success": result
            })
            
            return result
            
        except (ValidationError, PermissionDeniedError):
            # Re-raise security-related exceptions
            raise
            
        except Exception as e:
            self.logger.log_error(
                f"Error in type_text({selector}, ...): {str(e)}", 
                exc_info=sys.exc_info()
            )
            raise
    
    async def navigate_to(self, target: str) -> bool:
        """
        Navigate to the specified target (URL or application screen).
        
        Args:
            target: URL or screen identifier to navigate to
        
        Returns:
            bool: True if navigation was successful, False otherwise
        
        Raises:
            ValidationError: If target is invalid
            PermissionDeniedError: If navigation is not allowed
        """
        self.logger.log_action("Navigate command", {"target": target})
        
        try:
            # Validate target
            if not target or not isinstance(target, str) or len(target) > 2000:
                raise ValidationError("Invalid navigation target")
                
            # Check if this is a URL
            if target.startswith(('http://', 'https://', 'file://')):
                from urllib.parse import urlparse
                parsed = urlparse(target)
                
                # Validate domain for http/https URLs
                if target.startswith(('http://', 'https://')):
                    domain = parsed.netloc.split(':')[0]  # Remove port if present
                    if domain not in self.security_manager.SAFE_DOMAINS:
                        raise PermissionDeniedError(
                            f"Navigation to domain '{domain}' is not allowed"
                        )
                
                # Additional validation for file URLs
                elif target.startswith('file://'):
                    file_path = parsed.path
                    # On Windows, remove leading slash from path
                    if os.name == 'nt' and len(file_path) > 2 and file_path[0] == '/':
                        file_path = file_path[1:]
                    
                    is_valid, error_msg = self.security_manager.validate_file_path(
                        file_path, 'read'
                    )
                    if not is_valid:
                        raise ValidationError(f"Invalid file path: {error_msg}")
            
            # Check permissions
            allowed, reason = self.security_manager.check_permission(
                self._security_context, OperationType.NAVIGATE
            )
            if not allowed:
                raise PermissionDeniedError(reason or "Navigation not permitted")
            
            # Execute the command
            result = await self.ai_control.execute_command(AICommand(
                type=CommandType.NAVIGATE,
                target=target
            ))
            
            self.logger.log_action("Navigate command executed", {
                "target": target, 
                "success": result
            })
            
            return result
            
        except (ValidationError, PermissionDeniedError):
            # Re-raise security-related exceptions
            raise
            
        except Exception as e:
            self.logger.log_error(
                f"Error in navigate_to({target}): {str(e)}", 
                exc_info=sys.exc_info()
            )
            raise
    
    @cached(ttl=1)  # Cache for 1 second to prevent rapid consecutive calls
    def get_ui_state(self) -> Dict[str, Any]:
        """
        Get the current state of the UI with caching.
        
        Returns:
            A dictionary containing information about the current UI state.
        
        Raises:
            PermissionDeniedError: If the operation is not allowed
        """
        try:
            # Check permissions
            if not self.security_manager.check_permission(
                self._security_context, "access_ui_elements"
            ):
                raise PermissionDeniedError("Access to UI elements is not allowed")
            
            # Get UI state from the AI control system
            state = self.ai_control.get_ui_state()
            
            # Add additional context
            state.update({
                "timestamp": time.time(),
                "screen_size": {
                    "width": self.screen_geometry.width(),
                    "height": self.screen_geometry.height()
                },
                "cursor_position": {
                    "x": QCursor.pos().x(),
                    "y": QCursor.pos().y()
                }
            })
            
            return state
            
        except Exception as e:
            self.logger.log_error(f"Failed to get UI state: {str(e)}", exc_info=sys.exc_info())
            raise

# Singleton instance
_ui_assistant_instance = None

@cached(ttl=300)  # Cache the instance for 5 minutes
def get_ui_assistant(user_id: str = "default", is_privileged: bool = False) -> 'UIAssistantTool':
    """
    Get the global UI Assistant instance with the specified security context.
    
    Args:
        user_id: ID of the current user (for access control)
        is_privileged: Whether the user has privileged access
    
    Returns:
        UIAssistantTool: The UI Assistant instance
    """
    global _ui_assistant_instance
    
    # Create a cache key based on user_id and privilege level
    cache_key = (user_id, is_privileged)
    
    # Return cached instance if available
    if _ui_assistant_instance is not None and _ui_assistant_instance._security_context.user_id == user_id:
        return _ui_assistant_instance
    
    # Create new instance if needed
    if _ui_assistant_instance is None:
        _ui_assistant_instance = UIAssistantTool()
    
    # Update security context
    _ui_assistant_instance._security_context.user_id = user_id
    _ui_assistant_instance._security_context.is_privileged = is_privileged
    
    # Update permissions based on privilege level
    if is_privileged:
        _ui_assistant_instance._security_context.permissions.update({
            "execute_ui_commands",
            "access_ui_elements",
            "capture_screen",
            "admin_operations"
        })
    
    return _ui_assistant_instance
