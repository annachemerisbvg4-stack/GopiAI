"""
Test cases for UI Assistant security features.
"""

import os
import sys
import unittest
import asyncio
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gopiai.ui_core.ai_tools.ui_assistant import UIAssistantTool, get_ui_assistant
from gopiai.ui_core.ai_tools.security import (
    ValidationError, 
    PermissionDeniedError,
    OperationType,
    SecurityContext
)

class TestUIAssistantSecurity(unittest.TestCase):
    """Test cases for UI Assistant security features."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a test instance of UIAssistantTool
        self.assistant = UIAssistantTool()
        
        # Mock the AI control system
        self.assistant.ai_control = MagicMock()
        self.assistant.ai_control.execute_command = MagicMock(return_value=True)
        self.assistant.ai_control.capture_screen = MagicMock(return_value=MagicMock())
        
        # Set up a test security context
        self.assistant._security_context = SecurityContext(
            user_id="test_user",
            permissions={"execute_ui_commands", "access_ui_elements"},
            is_privileged=False
        )
        
        # Set up screen geometry
        self.assistant.screen_geometry = MagicMock()
        self.assistant.screen_geometry.contains.return_value = True
        
        # Patch the logger to avoid actual file I/O during tests
        self.logger_patcher = patch('gopiai.ui_core.ai_tools.ui_assistant.get_session_logger')
        self.mock_logger = self.logger_patcher.start()
        self.mock_logger.return_value = MagicMock()
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger_patcher.stop()
    
    # Test click_at method
    async def test_click_at_valid_coordinates(self):
        """Test clicking with valid coordinates."""
        result = await self.assistant.click_at(100, 200)
        self.assertTrue(result)
        self.assistant.ai_control.execute_command.assert_called_once()
    
    async def test_click_at_invalid_coordinates(self):
        """Test clicking with invalid coordinates."""
        self.assistant.screen_geometry.contains.return_value = False
        
        with self.assertRaises(ValidationError):
            await self.assistant.click_at(-100, 9999)
        
        self.assistant.ai_control.execute_command.assert_not_called()
    
    async def test_click_at_no_permission(self):
        """Test clicking without permission."""
        self.assistant._security_context.permissions = set()  # Remove all permissions
        
        with self.assertRaises(PermissionDeniedError):
            await self.assistant.click_at(100, 200)
        
        self.assistant.ai_control.execute_command.assert_not_called()
    
    # Test type_text method
    async def test_type_text_valid_input(self):
        """Test typing with valid input."""
        result = await self.assistant.type_text("#username", "testuser")
        self.assertTrue(result)
        self.assistant.ai_control.execute_command.assert_called_once()
    
    async def test_type_text_invalid_selector(self):
        """Test typing with invalid selector."""
        with self.assertRaises(ValidationError):
            await self.assistant.type_text("", "test")
        
        with self.assertRaises(ValidationError):
            await self.assistant.type_text("a" * 1001, "test")
        
        self.assistant.ai_control.execute_command.assert_not_called()
    
    async def test_type_text_dangerous_input(self):
        """Test typing with potentially dangerous input."""
        dangerous_input = "test; rm -rf /"
        
        # This should be allowed by default unless explicitly restricted by the security manager
        # The actual command execution is handled by the mocked AI control system
        result = await self.assistant.type_text("#input", dangerous_input)
        self.assertTrue(result)
        self.assistant.ai_control.execute_command.assert_called_once()
    
    # Test navigate_to method
    async def test_navigate_to_valid_url(self):
        """Test navigating to a valid URL."""
        result = await self.assistant.navigate_to("http://localhost:8000")
        self.assertTrue(result)
        self.assistant.ai_control.execute_command.assert_called_once()
    
    async def test_navigate_to_restricted_domain(self):
        """Test navigating to a restricted domain."""
        with self.assertRaises(PermissionDeniedError):
            await self.assistant.navigate_to("http://malicious-site.com")
        
        self.assistant.ai_control.execute_command.assert_not_called()
    
    async def test_navigate_to_file_url(self):
        """Test navigating to a file URL."""
        # This should be allowed for files in safe directories
        test_file = os.path.abspath("test.txt")
        result = await self.assistant.navigate_to(f"file://{test_file}")
        self.assertTrue(result)
        self.assistant.ai_control.execute_command.assert_called_once()
    
    # Test get_ui_state method
    def test_get_ui_state_with_permission(self):
        """Test getting UI state with permission."""
        result = self.assistant.get_ui_state()
        self.assertIsInstance(result, dict)
        self.assistant.ai_control.capture_screen.assert_called_once()
    
    def test_get_ui_state_without_permission(self):
        """Test getting UI state without permission."""
        self.assistant._security_context.permissions = set()  # Remove all permissions
        
        with self.assertRaises(PermissionDeniedError):
            self.assistant.get_ui_state()
        
        self.assistant.ai_control.capture_screen.assert_not_called()
    
    # Test security context
    def test_security_context_privileged(self):
        """Test privileged security context."""
        privileged_context = SecurityContext(
            user_id="admin",
            permissions=set(),
            is_privileged=True
        )
        
        # Privileged users should be able to perform any operation
        self.assertTrue(privileged_context.is_privileged)
    
    def test_security_context_permissions(self):
        """Test security context permissions."""
        context = SecurityContext(
            user_id="test_user",
            permissions={"access_ui_elements"},
            is_privileged=False
        )
        
        self.assertTrue("access_ui_elements" in context.permissions)
        self.assertFalse("execute_system_commands" in context.permissions)

# Run the tests
if __name__ == "__main__":
    unittest.main()
