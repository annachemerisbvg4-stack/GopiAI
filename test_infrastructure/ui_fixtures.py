#!/usr/bin/env python3
"""
UI-specific Test Fixtures

Provides specialized fixtures for testing GopiAI-UI components with pytest-qt.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from typing import Dict, Any, List
import sys
import os


@pytest.fixture
def qtbot():
    """Provide qtbot for UI testing."""
    try:
        from pytestqt.qtbot import QtBot
        from PySide6.QtWidgets import QApplication
        
        # Ensure QApplication exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        bot = QtBot(app)
        return bot
    except ImportError:
        # If pytest-qt is not available, provide a mock
        mock_bot = MagicMock()
        mock_bot.addWidget = MagicMock()
        mock_bot.mouseClick = MagicMock()
        mock_bot.keyClick = MagicMock()
        mock_bot.keyClicks = MagicMock()
        mock_bot.wait = MagicMock()
        return mock_bot


@pytest.fixture
def mock_main_window():
    """Mock main application window."""
    try:
        from PySide6.QtWidgets import QMainWindow
        mock_window = MagicMock(spec=QMainWindow)
    except ImportError:
        mock_window = MagicMock()
    
    # Configure window properties
    mock_window.isVisible.return_value = True
    mock_window.size.return_value = MagicMock()
    mock_window.size().width.return_value = 1200
    mock_window.size().height.return_value = 800
    
    # Mock window operations
    mock_window.show.return_value = None
    mock_window.hide.return_value = None
    mock_window.close.return_value = True
    mock_window.setWindowTitle.return_value = None
    
    return mock_window


@pytest.fixture
def mock_chat_widget():
    """Mock chat widget for testing."""
    # Don't use spec to avoid attribute restrictions
    mock_widget = MagicMock()
    
    # Mock chat functionality
    mock_widget.send_message.return_value = True
    mock_widget.get_message_text.return_value = "Test message"
    mock_widget.set_message_text.return_value = None
    mock_widget.clear_chat.return_value = None
    mock_widget.add_message.return_value = None
    
    # Mock message history
    mock_widget.get_messages.return_value = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    
    return mock_widget


@pytest.fixture
def mock_model_selector():
    """Mock model selector widget."""
    # Don't use spec to avoid attribute restrictions
    mock_selector = MagicMock()
    
    # Mock model selection
    mock_selector.currentText.return_value = "gpt-4"
    mock_selector.currentData.return_value = {"provider": "openai", "model": "gpt-4"}
    mock_selector.setCurrentText.return_value = None
    mock_selector.addItem.return_value = None
    mock_selector.clear.return_value = None
    
    # Mock available models
    mock_selector.count.return_value = 3
    mock_selector.itemText.side_effect = lambda i: ["gpt-4", "claude-3-sonnet", "gemini-pro"][i]
    
    return mock_selector


@pytest.fixture
def mock_settings_dialog():
    """Mock settings dialog."""
    # Don't use spec to avoid attribute restrictions
    mock_dialog = MagicMock()
    
    # Mock dialog operations
    mock_dialog.exec.return_value = 1  # QDialog.Accepted
    mock_dialog.show.return_value = None
    mock_dialog.hide.return_value = None
    mock_dialog.close.return_value = True
    
    # Mock settings
    mock_dialog.get_settings.return_value = {
        "theme": "dark",
        "font_size": 12,
        "auto_save": True
    }
    mock_dialog.set_settings.return_value = None
    
    return mock_dialog


@pytest.fixture
def mock_conversation_list():
    """Mock conversation list widget."""
    # Don't use spec to avoid attribute restrictions
    mock_list = MagicMock()
    
    # Mock conversation list
    mock_conversations = [
        {"id": "conv1", "title": "Test Chat 1", "timestamp": "2025-01-01T00:00:00Z"},
        {"id": "conv2", "title": "Test Chat 2", "timestamp": "2025-01-01T01:00:00Z"}
    ]
    
    mock_list.count.return_value = len(mock_conversations)
    mock_list.currentRow.return_value = 0
    mock_list.currentItem.return_value = MagicMock()
    mock_list.currentItem().data.return_value = mock_conversations[0]
    
    # Mock list operations
    mock_list.addItem.return_value = None
    mock_list.removeItemWidget.return_value = None
    mock_list.clear.return_value = None
    mock_list.setCurrentRow.return_value = None
    
    return mock_list


@pytest.fixture
def mock_theme_manager():
    """Mock theme manager for UI testing."""
    mock_manager = MagicMock()
    
    # Available themes
    mock_themes = ["light", "dark", "auto"]
    
    mock_manager.get_available_themes.return_value = mock_themes
    mock_manager.get_current_theme.return_value = "dark"
    mock_manager.set_theme.return_value = True
    mock_manager.apply_theme.return_value = None
    
    # Mock theme properties
    mock_manager.get_theme_colors.return_value = {
        "background": "#2b2b2b",
        "foreground": "#ffffff",
        "accent": "#0078d4"
    }
    
    return mock_manager


@pytest.fixture
def mock_notification_system():
    """Mock notification system."""
    mock_system = MagicMock()
    
    # Mock notification methods
    mock_system.show_info.return_value = None
    mock_system.show_warning.return_value = None
    mock_system.show_error.return_value = None
    mock_system.show_success.return_value = None
    
    # Mock notification queue
    mock_system.get_pending_notifications.return_value = []
    mock_system.clear_notifications.return_value = None
    
    return mock_system


@pytest.fixture
def mock_file_dialog():
    """Mock file dialog for testing."""
    # Don't use spec to avoid attribute restrictions
    mock_dialog = MagicMock()
    
    # Mock file dialog operations
    mock_dialog.getOpenFileName.return_value = ("/path/to/test/file.txt", "Text Files (*.txt)")
    mock_dialog.getSaveFileName.return_value = ("/path/to/save/file.txt", "Text Files (*.txt)")
    mock_dialog.getExistingDirectory.return_value = "/path/to/directory"
    
    return mock_dialog


@pytest.fixture
def mock_message_box():
    """Mock message box for testing."""
    # Don't use spec to avoid attribute restrictions
    mock_box = MagicMock()
    
    # Mock message box operations
    mock_box.information.return_value = None
    mock_box.warning.return_value = None
    mock_box.critical.return_value = None
    mock_box.question.return_value = 16384  # QMessageBox.Yes
    
    return mock_box


@pytest.fixture
def mock_progress_dialog():
    """Mock progress dialog for testing."""
    # Don't use spec to avoid attribute restrictions
    mock_dialog = MagicMock()
    
    # Mock progress operations
    mock_dialog.setValue.return_value = None
    mock_dialog.setMaximum.return_value = None
    mock_dialog.setMinimum.return_value = None
    mock_dialog.setLabelText.return_value = None
    mock_dialog.wasCanceled.return_value = False
    mock_dialog.show.return_value = None
    mock_dialog.hide.return_value = None
    
    return mock_dialog


@pytest.fixture
def mock_system_tray():
    """Mock system tray for testing."""
    # Don't use spec to avoid attribute restrictions
    mock_tray = MagicMock()
    
    # Mock system tray operations
    mock_tray.isVisible.return_value = True
    mock_tray.show.return_value = None
    mock_tray.hide.return_value = None
    mock_tray.showMessage.return_value = None
    mock_tray.setToolTip.return_value = None
    
    return mock_tray


@pytest.fixture
def mock_keyboard_shortcuts():
    """Mock keyboard shortcuts for testing."""
    # Don't use spec to avoid attribute restrictions
    mock_shortcuts = MagicMock()
    
    # Mock shortcut operations
    mock_shortcuts.register_shortcut.return_value = True
    mock_shortcuts.unregister_shortcut.return_value = True
    mock_shortcuts.get_shortcuts.return_value = {
        "Ctrl+N": "new_conversation",
        "Ctrl+S": "save_conversation",
        "Ctrl+Q": "quit_application"
    }
    
    return mock_shortcuts


@pytest.fixture
def ui_test_data():
    """Provide test data for UI testing."""
    return {
        "sample_messages": [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"},
            {"role": "user", "content": "Can you help me with Python?"},
            {"role": "assistant", "content": "Of course! What would you like to know?"}
        ],
        "sample_conversations": [
            {
                "id": "conv1",
                "title": "Python Help",
                "created_at": "2025-01-01T00:00:00Z",
                "message_count": 4
            },
            {
                "id": "conv2", 
                "title": "General Chat",
                "created_at": "2025-01-01T01:00:00Z",
                "message_count": 2
            }
        ],
        "sample_settings": {
            "theme": "dark",
            "font_family": "Consolas",
            "font_size": 12,
            "auto_save": True,
            "show_timestamps": True,
            "enable_notifications": True
        }
    }


@pytest.fixture
def mock_drag_drop():
    """Mock drag and drop operations."""
    mock_dd = MagicMock()
    
    # Mock drag and drop events
    mock_dd.dragEnterEvent.return_value = None
    mock_dd.dragMoveEvent.return_value = None
    mock_dd.dropEvent.return_value = None
    mock_dd.mimeData.return_value = MagicMock()
    mock_dd.mimeData().hasUrls.return_value = True
    mock_dd.mimeData().urls.return_value = [MagicMock()]
    
    return mock_dd