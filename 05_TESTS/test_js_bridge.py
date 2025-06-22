import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from PySide6.QtCore import QObject
from gopiai.webview.js_bridge import JavaScriptBridge

class TestExecuteBrowserAction:
    """Test cases for JavaScriptBridge.execute_browser_action method."""
    
    @pytest.fixture
    def bridge(self):
        """Create a JavaScriptBridge instance for testing."""
        return JavaScriptBridge()
    
    @pytest.fixture
    def mock_parent(self):
        """Create a mock parent with execute_browser_automation method."""
        parent = Mock()
        parent.execute_browser_automation = Mock(return_value={"status": "success"})
        return parent
    
    def test_execute_browser_action_basic_functionality(self, bridge):
        """Test basic functionality with valid action and params."""
        action = "navigate"
        params = '{"url": "https://example.com"}'
        
        result = bridge.execute_browser_action(action, params)
        result_dict = json.loads(result)
        
        assert result_dict["action"] == action
        assert result_dict["status"] == "pending"
        assert "timestamp" in result_dict
        assert "Browser action 'navigate' received" in result_dict["message"]
    
    def test_execute_browser_action_empty_params(self, bridge):
        """Test with empty params string."""
        action = "screenshot"
        params = ""
        
        result = bridge.execute_browser_action(action, params)
        result_dict = json.loads(result)
        
        assert result_dict["action"] == action
        assert result_dict["status"] == "pending"
        assert "timestamp" in result_dict
    
    def test_execute_browser_action_none_params(self, bridge):
        """Test with None params."""
        action = "click"
        params = None
        
        result = bridge.execute_browser_action(action, params)
        result_dict = json.loads(result)
        
        assert result_dict["action"] == action
        assert result_dict["status"] == "pending"
    
    def test_execute_browser_action_with_parent_automation(self, bridge, mock_parent):
        """Test when parent has execute_browser_automation method."""
        bridge.setParent(mock_parent)
        action = "type"
        params = '{"text": "hello world"}'
        
        result = bridge.execute_browser_action(action, params)
        result_dict = json.loads(result)
        
        # Verify parent method was called
        mock_parent.execute_browser_automation.assert_called_once_with(
            action, {"text": "hello world"}
        )
        
        # Verify result contains parent's response
        assert result_dict["status"] == "success"
        assert result_dict["action"] == action
    
    def test_execute_browser_action_parent_returns_none(self, bridge):
        """Test when parent returns None from execute_browser_automation."""
        mock_parent = Mock()
        mock_parent.execute_browser_automation = Mock(return_value=None)
        bridge.setParent(mock_parent)
        
        action = "scroll"
        params = '{"direction": "down"}'
        
        result = bridge.execute_browser_action(action, params)
        result_dict = json.loads(result)
        
        # Should still have default result since parent returned None
        assert result_dict["status"] == "pending"
        assert result_dict["action"] == action
    
    def test_execute_browser_action_no_parent_automation(self, bridge):
        """Test when parent doesn't have execute_browser_automation method."""
        mock_parent = Mock()
        # Don't add execute_browser_automation method
        bridge.setParent(mock_parent)
        
        action = "get_text"
        params = '{"selector": ".title"}'
        
        result = bridge.execute_browser_action(action, params)
        result_dict = json.loads(result)
        
        # Should return default result
        assert result_dict["status"] == "pending"
        assert result_dict["action"] == action
    
    def test_execute_browser_action_invalid_json_params(self, bridge):
        """Test with invalid JSON params."""
        action = "navigate"
        params = '{"url": invalid json'
        
        with patch.object(bridge, 'error_occurred') as mock_error:
            result = bridge.execute_browser_action(action, params)
            result_dict = json.loads(result)
            
            assert result_dict["action"] == action
            assert result_dict["status"] == "error"
            assert "error" in result_dict
            assert "timestamp" in result_dict
            mock_error.emit.assert_called_once()
    
    def test_execute_browser_action_parent_method_raises_exception(self, bridge):
        """Test when parent's execute_browser_automation raises an exception."""
        mock_parent = Mock()
        mock_parent.execute_browser_automation = Mock(side_effect=Exception("Parent error"))
        bridge.setParent(mock_parent)
        
        action = "click"
        params = '{"selector": "#button"}'
        
        with patch.object(bridge, 'error_occurred') as mock_error:
            result = bridge.execute_browser_action(action, params)
            result_dict = json.loads(result)
            
            assert result_dict["action"] == action
            assert result_dict["status"] == "error"
            assert "Parent error" in result_dict["error"]
            mock_error.emit.assert_called_once()
    
    @patch('gopiai.webview.js_bridge.datetime')
    def test_execute_browser_action_timestamp_format(self, mock_datetime, bridge):
        """Test that timestamp is properly formatted."""
        mock_now = Mock()
        mock_now.isoformat.return_value = "2023-12-01T10:30:00"
        mock_datetime.now.return_value = mock_now
        
        action = "get_source"
        params = '{}'
        
        result = bridge.execute_browser_action(action, params)
        result_dict = json.loads(result)
        
        assert result_dict["timestamp"] == "2023-12-01T10:30:00"
        mock_datetime.now.assert_called_once()
    
    def test_execute_browser_action_complex_params(self, bridge):
        """Test with complex JSON parameters."""
        action = "wait"
        params = json.dumps({
            "selector": ".dynamic-content",
            "timeout": 5000,
            "conditions": ["visible", "enabled"],
            "retry": True
        })
        
        result = bridge.execute_browser_action(action, params)
        result_dict = json.loads(result)
        
        assert result_dict["action"] == action
        assert result_dict["status"] == "pending"
    
    def test_execute_browser_action_special_characters(self, bridge):
        """Test with special characters in params."""
        action = "type"
        params = json.dumps({
            "text": "Тест с кириллицей и спецсимволами: !@#$%^&*()",
            "selector": "#input"
        })
        
        result = bridge.execute_browser_action(action, params)
        result_dict = json.loads(result)
        
        assert result_dict["action"] == action
        assert result_dict["status"] == "pending"
        # Verify JSON is properly encoded
        assert isinstance(result, str)
    
    def test_execute_browser_action_return_format(self, bridge):
        """Test that return value is always a valid JSON string."""
        action = "screenshot"
        params = '{"format": "png"}'
        
        result = bridge.execute_browser_action(action, params)
        
        # Should be a string
        assert isinstance(result, str)
        
        # Should be valid JSON
        result_dict = json.loads(result)
        assert isinstance(result_dict, dict)
        
        # Should have required fields
        assert "action" in result_dict
        assert "status" in result_dict
        assert "timestamp" in result_dict