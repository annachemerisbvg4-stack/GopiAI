"""
AI Assistant Widget for GopiAI

This module provides a widget that integrates the AI Assistant into the main application.
"""

from typing import Any, Dict, Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gopiai.ui.components.ai_assistant_integration import AIAssistantIntegration
from gopiai.ui.components.ai_tools import get_ui_assistant

class AIAssistantWidget(QWidget):
    """
    Widget that provides an interface for the AI Assistant.
    """
    
    # Signal emitted when the assistant sends a message
    message_received = Signal(str, str)  # role, message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ai_assistant = AIAssistantIntegration()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title
        title = QLabel("AI Assistant")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                border-bottom: 1px solid #ddd;
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(title)
        
        # Splitter for chat and controls
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(1)
        layout.addWidget(splitter)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setPlaceholderText("Здесь будет отображаться диалог с ассистентом...")
        splitter.addWidget(self.chat_area)
        
        # Controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setContentsMargins(8, 8, 8, 8)
        
        # Input field
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Введите ваш запрос...")
        self.input_field.setMaximumHeight(80)
        controls_layout.addWidget(self.input_field)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self._on_send_clicked)
        
        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self._on_clear_clicked)
        
        buttons_layout.addWidget(self.send_button)
        buttons_layout.addWidget(self.clear_button)
        controls_layout.addLayout(buttons_layout)
        
        splitter.addWidget(controls_widget)
        
        # Set initial sizes
        splitter.setSizes([400, 100])
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # Connect AI Assistant signals
        self.ai_assistant.assistant_message.connect(self._on_assistant_message)
        self.ai_assistant.action_started.connect(self._on_action_started)
        self.ai_assistant.action_completed.connect(self._on_action_completed)
        
        # Connect UI signals
        self.send_button.clicked.connect(self._on_send_clicked)
        self.clear_button.clicked.connect(self._on_clear_clicked)
        
        # Enable Enter key to send message
        self.input_field.keyPressEvent = self._on_input_key_press
    
    def set_main_window(self, window):
        """Set the main window reference."""
        self.ai_assistant.set_main_window(window)
    
    def _on_send_clicked(self):
        """Handle send button click."""
        message = self.input_field.toPlainText().strip()
        if not message:
            return
            
        # Add user message to chat
        self._add_message("user", message)
        self.input_field.clear()
        
        # Process the message
        self.ai_assistant.start_assistant_task("help_with_ui", message)
    
    def _on_clear_clicked(self):
        """Handle clear button click."""
        self.chat_area.clear()
    
    def _on_input_key_press(self, event):
        """Handle key press events in the input field."""
        # Send message on Ctrl+Enter or Cmd+Enter
        if (event.key() == Qt.Key_Return and 
            (event.modifiers() & Qt.ControlModifier or 
             event.modifiers() & Qt.MetaModifier)):
            self._on_send_clicked()
        else:
            # Call the original keyPressEvent
            QTextEdit.keyPressEvent(self.input_field, event)
    
    def _add_message(self, role: str, message: str):
        """Add a message to the chat area."""
        if role == "user":
            prefix = "<b>Вы:</b> "
            style = "color: #2b7de9;"
        else:
            prefix = "<b>Ассистент:</b> "
            style = "color: #333;"
        
        self.chat_area.append(f"<div style='margin: 5px 0; {style}'>{prefix}{message}</div>")
        
        # Scroll to bottom
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )
    
    # Slot implementations
    @Slot(str)
    def _on_assistant_message(self, message: str):
        """Handle a message from the assistant."""
        self._add_message("assistant", message)
    
    @Slot(str)
    def _on_action_started(self, action: str):
        """Handle an action starting."""
        self._add_message("system", f"🔹 {action}...")
    
    @Slot(str, bool)
    def _on_action_completed(self, message: str, success: bool):
        """Handle an action completing."""
        status = "успешно" if success else "с ошибкой"
        self._add_message("system", f"✅ {message} ({status})")
