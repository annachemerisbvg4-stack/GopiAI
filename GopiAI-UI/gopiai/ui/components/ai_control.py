"""
AI Control System for GopiAI UI

This module provides functionality for AI-assisted control of the application,
including screen capture, command execution, and AI integration.
"""

import os
import base64
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum, auto

from PySide6.QtCore import QObject, QTimer, Signal, QPoint, QSize, QRect, QBuffer, QIODevice, Qt
from PySide6.QtGui import QPixmap, QGuiApplication, QScreen, QPainter, QColor, QPen, QFont, QImage
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QMessageBox

from ..llm import get_llm_client  # Import from local ui llm module

class CommandType(Enum):
    CLICK = "click"
    INPUT = "input"
    NAVIGATE = "navigate"
    SCROLL = "scroll"
    WAIT = "wait"

@dataclass
class AICommand:
    """Data class representing a command from the AI."""
    type: CommandType
    x: Optional[int] = None
    y: Optional[int] = None
    selector: Optional[str] = None
    text: Optional[str] = None
    target: Optional[str] = None
    duration: float = 0.5  # seconds

class AIControlSystem(QObject):
    """
    System for AI-assisted control of the application.
    Handles screen capture, command execution, and AI integration.
    """
    # Signals
    command_started = Signal(AICommand)
    command_completed = Signal(AICommand, bool)  # Command, success
    status_updated = Signal(str)  # Status messages
    screenshot_captured = Signal(QPixmap)  # Emitted when a new screenshot is taken

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.current_screenshot: Optional[QPixmap] = None
        self.overlay_widget: Optional[QWidget] = None
        self.overlay_label: Optional[QLabel] = None
        self.is_running = False
        self.current_task = ""
        self.command_history: List[AICommand] = []
        
        # Initialize LLM client
        self.llm_client = get_llm_client()
        
        # Set up the overlay for visual feedback
        self._setup_overlay()

    def _setup_overlay(self) -> None:
        """Set up the overlay widget for visual feedback."""
        if not QApplication.instance():
            return
            
        # Create a transparent overlay window
        self.overlay_widget = QWidget()
        self.overlay_widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.overlay_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.overlay_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout = QVBoxLayout()
        
        # Status label
        self.overlay_label = QLabel("AI Control: Ready")
        self.overlay_label.setStyleSheet(
            """
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            """
        )
        layout.addWidget(self.overlay_label)
        self.overlay_widget.setLayout(layout)
        
        # Hide by default
        self.overlay_widget.hide()

    def capture_screen(self, widget: Optional[QWidget] = None) -> Optional[QPixmap]:
        """
        Capture the screen or a specific widget.
        
        Args:
            widget: Optional widget to capture. If None, captures the entire screen.
            
        Returns:
            QPixmap containing the screenshot, or None if failed.
        """
        try:
            if widget:
                # Capture specific widget
                screenshot = widget.grab()
            else:
                # Capture primary screen
                screen = QGuiApplication.primaryScreen()
                screenshot = screen.grabWindow(0)
                
            self.current_screenshot = screenshot
            self.screenshot_captured.emit(screenshot)
            return screenshot
            
        except Exception as e:
            self.status_updated.emit(f"Error capturing screen: {str(e)}")
            return None

    def capture_screen_to_base64(self, widget: Optional[QWidget] = None) -> Optional[str]:
        """
        Capture the screen or widget and return as base64 string.
        
        Args:
            widget: Optional widget to capture.
            
        Returns:
            Base64 encoded string of the screenshot, or None if failed.
        """
        screenshot = self.capture_screen(widget)
        if not screenshot:
            return None
            
        # Convert to base64
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        screenshot.save(buffer, "PNG")
        return f"data:image/png;base64,{base64.b64encode(buffer.data()).decode('utf-8')}"

    async def get_ai_commands(self, screenshot: QPixmap, task: str) -> List[AICommand]:
        """
        Get commands from the AI based on the current screen and task.
        
        Args:
            screenshot: The screenshot to analyze.
            task: The task description.
            
        Returns:
            List of AICommand objects.
        """
        self.status_updated.emit("Analyzing screen with AI...")
        
        try:
            # Convert screenshot to base64 for the API
            screenshot_data = self.capture_screen_to_base64()
            if not screenshot_data:
                raise ValueError("Failed to capture screenshot")
            
            # Prepare the prompt
            prompt = f"""
            Task: {task}
            
            Analyze the current application state and provide a list of commands to complete the task.
            Available commands:
            - click(x, y): Click at screen coordinates (x, y)
            - input(selector, text): Enter text into an input field
            - navigate(target): Navigate to a specific part of the app
            - wait(seconds): Wait for a specified duration
            """
            
            # Call the LLM API (implementation depends on your LLM client)
            response = await self.llm_client.generate(
                prompt=prompt,
                context={"screenshot": screenshot_data},
                max_tokens=500
            )
            
            # Parse the response into commands
            commands = self._parse_ai_response(response)
            return commands
            
        except Exception as e:
            self.status_updated.emit(f"Error getting AI commands: {str(e)}")
            return []

    def _parse_ai_response(self, response: str) -> List[AICommand]:
        """
        Parse the AI response into a list of commands.
        
        Args:
            response: Raw response from the AI.
            
        Returns:
            List of parsed AICommand objects.
        """
        # This is a simplified implementation. In a real app, you'd want to parse
        # the AI's response more carefully and handle errors.
        commands = []
        try:
            # Parse the response as JSON
            data = json.loads(response)
            for cmd in data.get("commands", []):
                try:
                    cmd_type = CommandType(cmd["type"].lower())
                    if cmd_type == CommandType.CLICK:
                        commands.append(AICommand(
                            type=cmd_type,
                            x=cmd["x"],
                            y=cmd["y"]
                        ))
                    elif cmd_type == CommandType.INPUT:
                        commands.append(AICommand(
                            type=cmd_type,
                            selector=cmd["selector"],
                            text=cmd["text"]
                        ))
                    elif cmd_type == CommandType.NAVIGATE:
                        commands.append(AICommand(
                            type=cmd_type,
                            target=cmd["target"]
                        ))
                    elif cmd_type == CommandType.WAIT:
                        commands.append(AICommand(
                            type=cmd_type,
                            duration=float(cmd.get("duration", 1.0))
                        ))
                except (KeyError, ValueError) as e:
                    self.status_updated.emit(f"Error parsing command: {e}")
                    continue
        except json.JSONDecodeError:
            self.status_updated.emit("Failed to parse AI response")
            
        return commands

    async def execute_command(self, command: AICommand) -> bool:
        """
        Execute a single AI command.
        
        Args:
            command: The command to execute.
            
        Returns:
            bool: True if the command executed successfully, False otherwise.
        """
        self.command_started.emit(command)
        success = False
        
        try:
            if command.type == CommandType.CLICK:
                success = self._execute_click(command.x, command.y)
            elif command.type == CommandType.INPUT:
                success = self._execute_input(command.selector, command.text)
            elif command.type == CommandType.NAVIGATE:
                success = self._execute_navigate(command.target)
            elif command.type == CommandType.WAIT:
                success = self._execute_wait(command.duration)
            else:
                self.status_updated.emit(f"Unknown command type: {command.type}")
                
        except Exception as e:
            self.status_updated.emit(f"Error executing command: {str(e)}")
            success = False
            
        self.command_completed.emit(command, success)
        return success

    def _execute_click(self, x: int, y: int) -> bool:
        """Simulate a mouse click at the specified coordinates."""
        self.status_updated.emit(f"Clicking at ({x}, {y})")
        
        # In a real implementation, you would use platform-specific code to simulate a click
        # This is a simplified version that just shows visual feedback
        self._show_click_feedback(x, y)
        return True

    def _execute_input(self, selector: str, text: str) -> bool:
        """Enter text into an input field."""
        self.status_updated.emit(f"Entering text into {selector}")
        
        # In a real implementation, you would find the input element and set its value
        # This is a simplified version
        return True

    def _execute_navigate(self, target: str) -> bool:
        """Navigate to a specific part of the app."""
        self.status_updated.emit(f"Navigating to {target}")
        
        # In a real implementation, you would handle navigation based on the target
        return True

    def _execute_wait(self, duration: float) -> bool:
        """Wait for a specified duration."""
        self.status_updated.emit(f"Waiting for {duration} seconds...")
        time.sleep(duration)
        return True

    def _show_click_feedback(self, x: int, y: int) -> None:
        """Show visual feedback for a click."""
        if not self.overlay_widget or not self.overlay_label:
            return
            
        # Position the overlay near the click
        self.overlay_widget.move(x + 20, y + 20)
        self.overlay_label.setText("Click")
        self.overlay_widget.show()
        
        # Hide after a short delay
        QTimer.singleShot(1000, self.overlay_widget.hide)

    async def run_ai_control_loop(self, task: str, max_steps: int = 10) -> None:
        """
        Run the main AI control loop.
        
        Args:
            task: The task description.
            max_steps: Maximum number of steps to run.
        """
        if self.is_running:
            self.status_updated.emit("AI control is already running")
            return
            
        self.is_running = True
        self.current_task = task
        self.status_updated.emit(f"Starting AI control for task: {task}")
        
        try:
            for step in range(max_steps):
                self.status_updated.emit(f"Step {step + 1}/{max_steps}")
                
                # 1. Capture the current screen
                screenshot = self.capture_screen()
                if not screenshot:
                    self.status_updated.emit("Failed to capture screen")
                    break
                
                # 2. Get commands from AI
                commands = await self.get_ai_commands(screenshot, self.current_task)
                if not commands:
                    self.status_updated.emit("No commands received from AI")
                    break
                
                # 3. Execute each command
                for cmd in commands:
                    success = await self.execute_command(cmd)
                    self.command_history.append(cmd)
                    if not success:
                        self.status_updated.emit(f"Command failed: {cmd}")
                        break
                
                # 4. Check if task is complete
                # In a real implementation, you might have a way to check task completion
                
        except Exception as e:
            self.status_updated.emit(f"Error in AI control loop: {str(e)}")
            
        finally:
            self.is_running = False
            self.status_updated.emit("AI control loop finished")
            
    def stop_ai_control(self) -> None:
        """Stop the AI control loop."""
        self.is_running = False
        self.status_updated.emit("AI control stopped by user")
