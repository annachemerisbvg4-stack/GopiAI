#!/usr/bin/env python3
"""
Unit tests for GopiAI Core Exceptions

Tests the custom exception hierarchy and error handling functionality.
"""

import pytest
from typing import Dict, Any

from gopiai.core.exceptions import (
    GopiAIError,
    ConfigurationError,
    AIProviderError,
    APIKeyError,
    RateLimitError,
    ModelNotFoundError,
    MemoryError,
    IndexNotFoundError,
    SearchError,
    UIError,
    WidgetError,
    ThemeError,
    ServiceError,
    ServiceUnavailableError,
    ServiceTimeoutError,
    ValidationError,
    SchemaError,
    ToolError,
    ToolNotFoundError,
    ToolExecutionError,
    SecurityError,
    AuthenticationError,
    AuthorizationError,
    FileSystemError,
    FileNotFoundError,
    FilePermissionError,
    NetworkError,
    ConnectionError,
    TimeoutError,
    EXCEPTION_MAP,
    get_exception_class,
    create_exception
)


class TestGopiAIError:
    """Test base GopiAIError exception."""
    
    @pytest.mark.unit
    def test_basic_error_creation(self):
        """Test basic error creation with message only."""
        error = GopiAIError("Test error message")
        
        assert str(error) == "GOPIAI_ERROR: Test error message"
        assert error.message == "Test error message"
        assert error.error_code == "GOPIAI_ERROR"
        assert error.context == {}
    
    @pytest.mark.unit
    def test_error_with_code_and_context(self):
        """Test error creation with custom code and context."""
        context = {"user_id": "123", "action": "test"}
        error = GopiAIError("Test error", "CUSTOM_ERROR", context)
        
        assert error.error_code == "CUSTOM_ERROR"
        assert error.context == context
        assert "Context: {'user_id': '123', 'action': 'test'}" in str(error)
    
    @pytest.mark.unit
    def test_error_inheritance(self):
        """Test that GopiAIError inherits from Exception."""
        error = GopiAIError("Test error")
        assert isinstance(error, Exception)
        assert isinstance(error, GopiAIError)


class TestConfigurationError:
    """Test ConfigurationError exception."""
    
    @pytest.mark.unit
    def test_configuration_error_creation(self):
        """Test ConfigurationError creation."""
        error = ConfigurationError("Invalid config", "api.timeout")
        
        assert error.error_code == "CONFIG_ERROR"
        assert error.config_key == "api.timeout"
        assert isinstance(error, GopiAIError)
    
    @pytest.mark.unit
    def test_configuration_error_without_key(self):
        """Test ConfigurationError without config key."""
        error = ConfigurationError("General config error")
        
        assert error.config_key is None
        assert error.error_code == "CONFIG_ERROR"


class TestAIProviderErrors:
    """Test AI provider related exceptions."""
    
    @pytest.mark.unit
    def test_ai_provider_error(self):
        """Test basic AIProviderError."""
        error = AIProviderError("Provider failed", "openai", "gpt-4")
        
        assert error.error_code == "AI_PROVIDER_ERROR"
        assert error.provider == "openai"
        assert error.model == "gpt-4"
        assert isinstance(error, GopiAIError)
    
    @pytest.mark.unit
    def test_api_key_error(self):
        """Test APIKeyError."""
        error = APIKeyError("Invalid API key", "openai")
        
        assert error.error_code == "API_KEY_ERROR"
        assert error.provider == "openai"
        assert error.model is None
        assert isinstance(error, AIProviderError)
    
    @pytest.mark.unit
    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError("Rate limit exceeded", "openai", retry_after=60)
        
        assert error.error_code == "RATE_LIMIT_ERROR"
        assert error.provider == "openai"
        assert error.retry_after == 60
        assert isinstance(error, AIProviderError)
    
    @pytest.mark.unit
    def test_model_not_found_error(self):
        """Test ModelNotFoundError."""
        error = ModelNotFoundError("Model not available", "openai", "gpt-5")
        
        assert error.error_code == "MODEL_NOT_FOUND_ERROR"
        assert error.provider == "openai"
        assert error.model == "gpt-5"
        assert isinstance(error, AIProviderError)


class TestMemoryErrors:
    """Test memory system related exceptions."""
    
    @pytest.mark.unit
    def test_memory_error(self):
        """Test basic MemoryError."""
        error = MemoryError("Memory operation failed", "search")
        
        assert error.error_code == "MEMORY_ERROR"
        assert error.operation == "search"
        assert isinstance(error, GopiAIError)
    
    @pytest.mark.unit
    def test_index_not_found_error(self):
        """Test IndexNotFoundError."""
        error = IndexNotFoundError("Index not found", "/path/to/index")
        
        assert error.error_code == "INDEX_NOT_FOUND_ERROR"
        assert error.index_path == "/path/to/index"
        assert error.operation == "index_lookup"
        assert isinstance(error, MemoryError)
    
    @pytest.mark.unit
    def test_search_error(self):
        """Test SearchError."""
        error = SearchError("Search failed", "test query")
        
        assert error.error_code == "SEARCH_ERROR"
        assert error.query == "test query"
        assert error.operation == "search"
        assert isinstance(error, MemoryError)


class TestUIErrors:
    """Test UI related exceptions."""
    
    @pytest.mark.unit
    def test_ui_error(self):
        """Test basic UIError."""
        error = UIError("UI operation failed", "chat_widget")
        
        assert error.error_code == "UI_ERROR"
        assert error.component == "chat_widget"
        assert isinstance(error, GopiAIError)
    
    @pytest.mark.unit
    def test_widget_error(self):
        """Test WidgetError."""
        error = WidgetError("Widget initialization failed", "MessageWidget")
        
        assert error.error_code == "WIDGET_ERROR"
        assert error.widget_name == "MessageWidget"
        assert isinstance(error, UIError)
    
    @pytest.mark.unit
    def test_theme_error(self):
        """Test ThemeError."""
        error = ThemeError("Theme loading failed", "dark_theme")
        
        assert error.error_code == "THEME_ERROR"
        assert error.theme_name == "dark_theme"
        assert isinstance(error, UIError)


class TestServiceErrors:
    """Test service related exceptions."""
    
    @pytest.mark.unit
    def test_service_error(self):
        """Test basic ServiceError."""
        error = ServiceError("Service operation failed", "crewai_server")
        
        assert error.error_code == "SERVICE_ERROR"
        assert error.service_name == "crewai_server"
        assert isinstance(error, GopiAIError)
    
    @pytest.mark.unit
    def test_service_unavailable_error(self):
        """Test ServiceUnavailableError."""
        error = ServiceUnavailableError("Service not available", "memory_service")
        
        assert error.error_code == "SERVICE_UNAVAILABLE_ERROR"
        assert error.service_name == "memory_service"
        assert isinstance(error, ServiceError)
    
    @pytest.mark.unit
    def test_service_timeout_error(self):
        """Test ServiceTimeoutError."""
        error = ServiceTimeoutError("Service timeout", "api_server", timeout=30)
        
        assert error.error_code == "SERVICE_TIMEOUT_ERROR"
        assert error.service_name == "api_server"
        assert error.timeout == 30
        assert isinstance(error, ServiceError)


class TestValidationErrors:
    """Test validation related exceptions."""
    
    @pytest.mark.unit
    def test_validation_error(self):
        """Test basic ValidationError."""
        error = ValidationError("Validation failed", "email", "invalid@")
        
        assert error.error_code == "VALIDATION_ERROR"
        assert error.field == "email"
        assert error.value == "invalid@"
        assert isinstance(error, GopiAIError)
    
    @pytest.mark.unit
    def test_schema_error(self):
        """Test SchemaError."""
        error = SchemaError("Schema validation failed", "MessageSchema")
        
        assert error.error_code == "SCHEMA_ERROR"
        assert error.schema_name == "MessageSchema"
        assert isinstance(error, ValidationError)


class TestToolErrors:
    """Test tool related exceptions."""
    
    @pytest.mark.unit
    def test_tool_error(self):
        """Test basic ToolError."""
        error = ToolError("Tool operation failed", "browser_tool")
        
        assert error.error_code == "TOOL_ERROR"
        assert error.tool_name == "browser_tool"
        assert isinstance(error, GopiAIError)
    
    @pytest.mark.unit
    def test_tool_not_found_error(self):
        """Test ToolNotFoundError."""
        error = ToolNotFoundError("Tool not found", "missing_tool")
        
        assert error.error_code == "TOOL_NOT_FOUND_ERROR"
        assert error.tool_name == "missing_tool"
        assert isinstance(error, ToolError)
    
    @pytest.mark.unit
    def test_tool_execution_error(self):
        """Test ToolExecutionError."""
        params = {"url": "https://example.com"}
        error = ToolExecutionError("Tool execution failed", "web_scraper", params)
        
        assert error.error_code == "TOOL_EXECUTION_ERROR"
        assert error.tool_name == "web_scraper"
        assert error.parameters == params
        assert isinstance(error, ToolError)


class TestSecurityErrors:
    """Test security related exceptions."""
    
    @pytest.mark.unit
    def test_security_error(self):
        """Test basic SecurityError."""
        error = SecurityError("Security violation", "unauthorized_access")
        
        assert error.error_code == "SECURITY_ERROR"
        assert error.violation_type == "unauthorized_access"
        assert isinstance(error, GopiAIError)
    
    @pytest.mark.unit
    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Authentication failed")
        
        assert error.error_code == "AUTHENTICATION_ERROR"
        assert error.violation_type == "authentication"
        assert isinstance(error, SecurityError)
    
    @pytest.mark.unit
    def test_authorization_error(self):
        """Test AuthorizationError."""
        error = AuthorizationError("Access denied", "admin_panel")
        
        assert error.error_code == "AUTHORIZATION_ERROR"
        assert error.resource == "admin_panel"
        assert error.violation_type == "authorization"
        assert isinstance(error, SecurityError)


class TestFileSystemErrors:
    """Test file system related exceptions."""
    
    @pytest.mark.unit
    def test_filesystem_error(self):
        """Test basic FileSystemError."""
        error = FileSystemError("File operation failed", "/path/to/file", "write")
        
        assert error.error_code == "FILESYSTEM_ERROR"
        assert error.file_path == "/path/to/file"
        assert error.operation == "write"
        assert isinstance(error, GopiAIError)
    
    @pytest.mark.unit
    def test_file_not_found_error(self):
        """Test FileNotFoundError."""
        error = FileNotFoundError("File not found", "/missing/file.txt")
        
        assert error.error_code == "FILE_NOT_FOUND_ERROR"
        assert error.file_path == "/missing/file.txt"
        assert error.operation == "read"
        assert isinstance(error, FileSystemError)
    
    @pytest.mark.unit
    def test_file_permission_error(self):
        """Test FilePermissionError."""
        error = FilePermissionError("Permission denied", "/protected/file", "write")
        
        assert error.error_code == "FILE_PERMISSION_ERROR"
        assert error.file_path == "/protected/file"
        assert error.operation == "write"
        assert isinstance(error, FileSystemError)


class TestNetworkErrors:
    """Test network related exceptions."""
    
    @pytest.mark.unit
    def test_network_error(self):
        """Test basic NetworkError."""
        error = NetworkError("Network operation failed", "https://api.example.com", 500)
        
        assert error.error_code == "NETWORK_ERROR"
        assert error.url == "https://api.example.com"
        assert error.status_code == 500
        assert isinstance(error, GopiAIError)
    
    @pytest.mark.unit
    def test_connection_error(self):
        """Test ConnectionError."""
        error = ConnectionError("Connection failed", "https://api.example.com")
        
        assert error.error_code == "CONNECTION_ERROR"
        assert error.url == "https://api.example.com"
        assert error.status_code is None
        assert isinstance(error, NetworkError)
    
    @pytest.mark.unit
    def test_timeout_error(self):
        """Test TimeoutError."""
        error = TimeoutError("Request timeout", "https://api.example.com", timeout=30)
        
        assert error.error_code == "TIMEOUT_ERROR"
        assert error.url == "https://api.example.com"
        assert error.timeout == 30
        assert isinstance(error, NetworkError)


class TestExceptionUtilities:
    """Test exception utility functions."""
    
    @pytest.mark.unit
    def test_exception_map_completeness(self):
        """Test that EXCEPTION_MAP contains all expected exception types."""
        expected_keys = [
            "config", "ai_provider", "api_key", "rate_limit", "model_not_found",
            "memory", "index_not_found", "search", "ui", "widget", "theme",
            "service", "service_unavailable", "service_timeout", "validation",
            "schema", "tool", "tool_not_found", "tool_execution", "security",
            "authentication", "authorization", "filesystem", "file_not_found",
            "file_permission", "network", "connection", "timeout"
        ]
        
        for key in expected_keys:
            assert key in EXCEPTION_MAP
            assert issubclass(EXCEPTION_MAP[key], GopiAIError)
    
    @pytest.mark.unit
    def test_get_exception_class(self):
        """Test get_exception_class function."""
        # Test known exception types
        assert get_exception_class("config") == ConfigurationError
        assert get_exception_class("ai_provider") == AIProviderError
        assert get_exception_class("memory") == MemoryError
        
        # Test unknown exception type returns base class
        assert get_exception_class("unknown_type") == GopiAIError
    
    @pytest.mark.unit
    def test_create_exception(self):
        """Test create_exception function."""
        # Test creating known exception type
        error = create_exception("config", "Test config error", config_key="test.key")
        assert isinstance(error, ConfigurationError)
        assert error.message == "Test config error"
        assert error.config_key == "test.key"
        
        # Test creating unknown exception type
        error = create_exception("unknown", "Test unknown error")
        assert isinstance(error, GopiAIError)
        assert error.message == "Test unknown error"
    
    @pytest.mark.unit
    def test_create_exception_with_kwargs(self):
        """Test create_exception with various keyword arguments."""
        # Test AIProviderError with provider and model
        error = create_exception("ai_provider", "Provider error", provider="openai", model="gpt-4")
        assert isinstance(error, AIProviderError)
        assert error.provider == "openai"
        assert error.model == "gpt-4"
        
        # Test ServiceTimeoutError with timeout
        error = create_exception("service_timeout", "Timeout error", service_name="api", timeout=30)
        assert isinstance(error, ServiceTimeoutError)
        assert error.service_name == "api"
        assert error.timeout == 30


class TestExceptionContextHandling:
    """Test exception context handling."""
    
    @pytest.mark.unit
    def test_exception_with_context(self):
        """Test exception creation with context dictionary."""
        context = {
            "user_id": "user123",
            "request_id": "req456",
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
        error = GopiAIError("Test error with context", context=context)
        assert error.context == context
        assert "user_id" in str(error)
        assert "req456" in str(error)
    
    @pytest.mark.unit
    def test_exception_context_inheritance(self):
        """Test that context is properly inherited in derived exceptions."""
        context = {"operation": "test", "data": {"key": "value"}}
        
        error = AIProviderError("Provider error", "openai", "gpt-4", context)
        assert error.context == context
        assert error.provider == "openai"
        assert error.model == "gpt-4"


@pytest.mark.xfail_known_issue
class TestKnownExceptionIssues:
    """Test known issues with exceptions marked as expected failures."""
    
    def test_exception_serialization_issue(self):
        """Test known issue with exception serialization."""
        # This test documents a known issue with serializing complex exceptions
        # that contain non-serializable context data
        
        import pickle
        
        # Create exception with complex context that might not serialize well
        class NonSerializableClass:
            def __init__(self):
                self.func = lambda x: x
        
        complex_context = {
            "obj": NonSerializableClass(),  # Non-serializable object
            "data": {"nested": {"deep": "value"}}
        }
        
        error = GopiAIError("Test error", context=complex_context)
        
        # This should fail due to the non-serializable object in context
        with pytest.raises((pickle.PicklingError, TypeError, AttributeError)):
            pickle.dumps(error)
    
    def test_exception_chaining_issue(self):
        """Test known issue with exception chaining."""
        # This documents a potential issue with exception chaining
        # in complex error scenarios
        
        try:
            # Simulate nested error scenario
            try:
                raise ValueError("Original error")
            except ValueError as e:
                # This chaining might not work as expected in all cases
                raise AIProviderError("Provider error") from e
        except AIProviderError as provider_error:
            # The original exception might not be properly preserved
            # This is a known limitation that may need addressing
            assert provider_error.__cause__ is not None
            assert isinstance(provider_error.__cause__, ValueError)
    
    def test_unicode_handling_issue(self):
        """Test known issue with Unicode handling in error messages."""
        # This test documents potential issues with Unicode characters
        # in error messages and context
        
        unicode_message = "Error with Unicode: 🚨 测试 العربية"
        unicode_context = {"user": "用户", "error": "خطأ"}
        
        error = GopiAIError(unicode_message, context=unicode_context)
        
        # String representation might have issues with Unicode
        error_str = str(error)
        assert unicode_message in error_str
        
        # This might fail on some systems with encoding issues
        # but should generally work in modern Python environments


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])