#!/usr/bin/env python3
"""
Unit tests for GopiAI Core Schema

Tests data models, validation schemas, and data structures.
"""

import pytest
import json
from datetime import datetime, timezone
from typing import Dict, Any, List

from gopiai.core.schema import (
    MessageRole,
    AIProvider,
    ServiceStatus,
    LogLevel,
    Message,
    Conversation,
    ModelInfo,
    APIResponse,
    UsageStats,
    ServiceConfig,
    ToolConfig,
    UITheme,
    MemoryEntry,
    SearchResult,
    ValidationSchema,
    ConfigSchema,
    serialize_dataclass,
    deserialize_message,
    deserialize_conversation,
    create_api_response,
    create_default_service_config
)


class TestEnums:
    """Test enumeration classes."""
    
    @pytest.mark.unit
    def test_message_role_enum(self):
        """Test MessageRole enumeration."""
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.SYSTEM.value == "system"
        assert MessageRole.TOOL.value == "tool"
        
        # Test enum creation from string
        assert MessageRole("user") == MessageRole.USER
        assert MessageRole("assistant") == MessageRole.ASSISTANT
    
    @pytest.mark.unit
    def test_ai_provider_enum(self):
        """Test AIProvider enumeration."""
        assert AIProvider.OPENAI.value == "openai"
        assert AIProvider.ANTHROPIC.value == "anthropic"
        assert AIProvider.GOOGLE.value == "google"
        assert AIProvider.OPENROUTER.value == "openrouter"
        assert AIProvider.LOCAL.value == "local"
    
    @pytest.mark.unit
    def test_service_status_enum(self):
        """Test ServiceStatus enumeration."""
        assert ServiceStatus.RUNNING.value == "running"
        assert ServiceStatus.STOPPED.value == "stopped"
        assert ServiceStatus.ERROR.value == "error"
        assert ServiceStatus.STARTING.value == "starting"
        assert ServiceStatus.STOPPING.value == "stopping"
    
    @pytest.mark.unit
    def test_log_level_enum(self):
        """Test LogLevel enumeration."""
        assert LogLevel.DEBUG.value == "debug"
        assert LogLevel.INFO.value == "info"
        assert LogLevel.WARNING.value == "warning"
        assert LogLevel.ERROR.value == "error"
        assert LogLevel.CRITICAL.value == "critical"


class TestMessage:
    """Test Message dataclass."""
    
    @pytest.mark.unit
    def test_message_creation(self):
        """Test basic message creation."""
        message = Message(
            role=MessageRole.USER,
            content="Hello, AI!"
        )
        
        assert message.role == MessageRole.USER
        assert message.content == "Hello, AI!"
        assert isinstance(message.timestamp, datetime)
        assert message.metadata == {}
    
    @pytest.mark.unit
    def test_message_with_metadata(self):
        """Test message creation with metadata."""
        metadata = {"model": "gpt-4", "tokens": 10}
        message = Message(
            role=MessageRole.ASSISTANT,
            content="Hello, human!",
            metadata=metadata
        )
        
        assert message.metadata == metadata
    
    @pytest.mark.unit
    def test_message_to_dict(self):
        """Test message serialization to dictionary."""
        message = Message(
            role=MessageRole.USER,
            content="Test message"
        )
        
        data = message.to_dict()
        
        assert data["role"] == "user"
        assert data["content"] == "Test message"
        assert "timestamp" in data
        assert data["metadata"] == {}
    
    @pytest.mark.unit
    def test_message_from_dict(self):
        """Test message deserialization from dictionary."""
        data = {
            "role": "assistant",
            "content": "Test response",
            "timestamp": "2025-01-01T00:00:00",
            "metadata": {"model": "gpt-4"}
        }
        
        message = Message.from_dict(data)
        
        assert message.role == MessageRole.ASSISTANT
        assert message.content == "Test response"
        assert message.metadata == {"model": "gpt-4"}
    
    @pytest.mark.unit
    def test_message_validation(self):
        """Test message validation."""
        # Valid message
        valid_message = Message(MessageRole.USER, "Valid content")
        assert valid_message.validate() is True
        
        # Invalid message - empty content
        invalid_message = Message(MessageRole.USER, "")
        assert invalid_message.validate() is False
        
        # Invalid message - whitespace only content
        whitespace_message = Message(MessageRole.USER, "   ")
        assert whitespace_message.validate() is False


class TestConversation:
    """Test Conversation dataclass."""
    
    @pytest.mark.unit
    def test_conversation_creation(self):
        """Test basic conversation creation."""
        conversation = Conversation(
            id="conv-123",
            title="Test Conversation"
        )
        
        assert conversation.id == "conv-123"
        assert conversation.title == "Test Conversation"
        assert conversation.messages == []
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)
    
    @pytest.mark.unit
    def test_conversation_add_message(self):
        """Test adding messages to conversation."""
        conversation = Conversation("conv-123", "Test")
        message = Message(MessageRole.USER, "Hello")
        
        original_updated_at = conversation.updated_at
        # Add a small delay to ensure timestamp difference
        import time
        time.sleep(0.001)
        conversation.add_message(message)
        
        assert len(conversation.messages) == 1
        assert conversation.messages[0] == message
        assert conversation.updated_at >= original_updated_at
    
    @pytest.mark.unit
    def test_conversation_get_messages_by_role(self):
        """Test getting messages by role."""
        conversation = Conversation("conv-123", "Test")
        
        user_msg = Message(MessageRole.USER, "User message")
        assistant_msg = Message(MessageRole.ASSISTANT, "Assistant message")
        system_msg = Message(MessageRole.SYSTEM, "System message")
        
        conversation.add_message(user_msg)
        conversation.add_message(assistant_msg)
        conversation.add_message(system_msg)
        
        user_messages = conversation.get_messages_by_role(MessageRole.USER)
        assert len(user_messages) == 1
        assert user_messages[0] == user_msg
        
        assistant_messages = conversation.get_messages_by_role(MessageRole.ASSISTANT)
        assert len(assistant_messages) == 1
        assert assistant_messages[0] == assistant_msg
    
    @pytest.mark.unit
    def test_conversation_serialization(self):
        """Test conversation serialization and deserialization."""
        conversation = Conversation("conv-123", "Test Conversation")
        message = Message(MessageRole.USER, "Test message")
        conversation.add_message(message)
        
        # Serialize to dict
        data = conversation.to_dict()
        assert data["id"] == "conv-123"
        assert data["title"] == "Test Conversation"
        assert len(data["messages"]) == 1
        
        # Deserialize from dict
        restored_conversation = Conversation.from_dict(data)
        assert restored_conversation.id == conversation.id
        assert restored_conversation.title == conversation.title
        assert len(restored_conversation.messages) == 1
        assert restored_conversation.messages[0].content == "Test message"


class TestModelInfo:
    """Test ModelInfo dataclass."""
    
    @pytest.mark.unit
    def test_model_info_creation(self):
        """Test ModelInfo creation."""
        model_info = ModelInfo(
            name="gpt-4",
            provider=AIProvider.OPENAI,
            max_tokens=8192,
            supports_functions=True,
            supports_vision=False,
            cost_per_token=0.00003
        )
        
        assert model_info.name == "gpt-4"
        assert model_info.provider == AIProvider.OPENAI
        assert model_info.max_tokens == 8192
        assert model_info.supports_functions is True
        assert model_info.supports_vision is False
        assert model_info.cost_per_token == 0.00003
    
    @pytest.mark.unit
    def test_model_info_validation(self):
        """Test ModelInfo validation."""
        # Valid model info
        valid_model = ModelInfo("gpt-4", AIProvider.OPENAI, 8192)
        assert valid_model.validate() is True
        
        # Invalid model info - empty name
        invalid_model = ModelInfo("", AIProvider.OPENAI, 8192)
        assert invalid_model.validate() is False
        
        # Invalid model info - zero max_tokens
        invalid_model = ModelInfo("gpt-4", AIProvider.OPENAI, 0)
        assert invalid_model.validate() is False


class TestAPIResponse:
    """Test APIResponse dataclass."""
    
    @pytest.mark.unit
    def test_api_response_success(self):
        """Test successful API response."""
        response = APIResponse(
            success=True,
            data={"result": "success", "value": 42}
        )
        
        assert response.success is True
        assert response.data == {"result": "success", "value": 42}
        assert response.error is None
        assert response.error_code is None
        assert isinstance(response.timestamp, datetime)
    
    @pytest.mark.unit
    def test_api_response_error(self):
        """Test error API response."""
        response = APIResponse(
            success=False,
            error="Something went wrong",
            error_code="INTERNAL_ERROR"
        )
        
        assert response.success is False
        assert response.error == "Something went wrong"
        assert response.error_code == "INTERNAL_ERROR"
        assert response.data is None
    
    @pytest.mark.unit
    def test_api_response_serialization(self):
        """Test API response serialization."""
        response = APIResponse(True, {"test": "data"})
        data = response.to_dict()
        
        assert data["success"] is True
        assert data["data"] == {"test": "data"}
        assert "timestamp" in data


class TestUsageStats:
    """Test UsageStats dataclass."""
    
    @pytest.mark.unit
    def test_usage_stats_creation(self):
        """Test UsageStats creation."""
        stats = UsageStats(
            provider=AIProvider.OPENAI,
            model="gpt-4"
        )
        
        assert stats.provider == AIProvider.OPENAI
        assert stats.model == "gpt-4"
        assert stats.requests_made == 0
        assert stats.tokens_used == 0
        assert stats.cost_incurred == 0.0
        assert stats.errors_count == 0
        assert stats.last_request is None
    
    @pytest.mark.unit
    def test_usage_stats_update(self):
        """Test updating usage statistics."""
        stats = UsageStats(AIProvider.OPENAI, "gpt-4")
        
        # Update with successful request
        stats.update_usage(tokens=100, cost=0.003, error=False)
        
        assert stats.requests_made == 1
        assert stats.tokens_used == 100
        assert abs(stats.cost_incurred - 0.003) < 0.0001  # Use approximate comparison for floats
        assert stats.errors_count == 0
        assert stats.last_request is not None
        
        # Update with error
        stats.update_usage(tokens=50, cost=0.0015, error=True)
        
        assert stats.requests_made == 2
        assert stats.tokens_used == 150
        assert abs(stats.cost_incurred - 0.0045) < 0.0001  # Use approximate comparison for floats
        assert stats.errors_count == 1


class TestServiceConfig:
    """Test ServiceConfig dataclass."""
    
    @pytest.mark.unit
    def test_service_config_creation(self):
        """Test ServiceConfig creation."""
        config = ServiceConfig(
            name="crewai-server",
            host="localhost",
            port=5051,
            timeout=30
        )
        
        assert config.name == "crewai-server"
        assert config.host == "localhost"
        assert config.port == 5051
        assert config.timeout == 30
        assert config.enabled is True
    
    @pytest.mark.unit
    def test_service_config_urls(self):
        """Test ServiceConfig URL generation."""
        config = ServiceConfig("test-service", "example.com", 8080)
        
        assert config.get_url() == "http://example.com:8080"
        assert config.get_health_check_url() == "http://example.com:8080/health"
        
        # Test with custom health check path
        config.health_check_path = "/status"
        assert config.get_health_check_url() == "http://example.com:8080/status"


class TestToolConfig:
    """Test ToolConfig dataclass."""
    
    @pytest.mark.unit
    def test_tool_config_creation(self):
        """Test ToolConfig creation."""
        config = ToolConfig(
            name="browser_tool",
            description="Web browsing capabilities",
            enabled=True,
            parameters={"required": ["url"], "optional": ["timeout"]},
            permissions=["web_access", "file_read"]
        )
        
        assert config.name == "browser_tool"
        assert config.description == "Web browsing capabilities"
        assert config.enabled is True
        assert "url" in config.parameters["required"]
        assert "web_access" in config.permissions
    
    @pytest.mark.unit
    def test_tool_config_parameter_validation(self):
        """Test ToolConfig parameter validation."""
        config = ToolConfig(
            name="test_tool",
            description="Test tool",
            parameters={"required": ["param1", "param2"]}
        )
        
        # Valid parameters
        valid_params = {"param1": "value1", "param2": "value2", "param3": "optional"}
        assert config.validate_parameters(valid_params) is True
        
        # Missing required parameter
        invalid_params = {"param1": "value1"}
        assert config.validate_parameters(invalid_params) is False


class TestUITheme:
    """Test UITheme dataclass."""
    
    @pytest.mark.unit
    def test_ui_theme_creation(self):
        """Test UITheme creation."""
        theme = UITheme(
            name="dark_theme",
            colors={"background": "#2b2b2b", "text": "#ffffff"},
            fonts={"main": "Arial", "mono": "Courier New"},
            sizes={"font_size": 12, "padding": 8}
        )
        
        assert theme.name == "dark_theme"
        assert theme.colors["background"] == "#2b2b2b"
        assert theme.fonts["main"] == "Arial"
        assert theme.sizes["font_size"] == 12
    
    @pytest.mark.unit
    def test_ui_theme_getters(self):
        """Test UITheme getter methods."""
        theme = UITheme(
            name="test_theme",
            colors={"primary": "#007acc"},
            fonts={"header": "Helvetica"}
        )
        
        # Test existing values
        assert theme.get_color("primary") == "#007acc"
        assert theme.get_font("header") == "Helvetica"
        
        # Test default values
        assert theme.get_color("nonexistent", "#000000") == "#000000"
        assert theme.get_font("nonexistent", "Arial") == "Arial"
        
        # Test built-in defaults
        assert theme.get_color("nonexistent") == "#000000"
        assert theme.get_font("nonexistent") == "Arial"


class TestMemoryEntry:
    """Test MemoryEntry dataclass."""
    
    @pytest.mark.unit
    def test_memory_entry_creation(self):
        """Test MemoryEntry creation."""
        entry = MemoryEntry(
            id="mem-123",
            content="This is a test memory entry",
            embedding=[0.1, 0.2, 0.3],
            metadata={"source": "conversation", "user_id": "user123"}
        )
        
        assert entry.id == "mem-123"
        assert entry.content == "This is a test memory entry"
        assert entry.embedding == [0.1, 0.2, 0.3]
        assert entry.metadata["source"] == "conversation"
        assert isinstance(entry.created_at, datetime)
        assert entry.relevance_score == 0.0
    
    @pytest.mark.unit
    def test_memory_entry_serialization(self):
        """Test MemoryEntry serialization."""
        entry = MemoryEntry("mem-123", "Test content")
        data = entry.to_dict()
        
        assert data["id"] == "mem-123"
        assert data["content"] == "Test content"
        assert "created_at" in data
        assert data["relevance_score"] == 0.0


class TestSearchResult:
    """Test SearchResult dataclass."""
    
    @pytest.mark.unit
    def test_search_result_creation(self):
        """Test SearchResult creation."""
        entry = MemoryEntry("mem-123", "Test content")
        result = SearchResult(
            entry=entry,
            score=0.85,
            context={"query": "test", "method": "semantic"}
        )
        
        assert result.entry == entry
        assert result.score == 0.85
        assert result.context["query"] == "test"
    
    @pytest.mark.unit
    def test_search_result_serialization(self):
        """Test SearchResult serialization."""
        entry = MemoryEntry("mem-123", "Test content")
        result = SearchResult(entry, 0.85)
        
        data = result.to_dict()
        assert "entry" in data
        assert data["score"] == 0.85
        assert data["entry"]["id"] == "mem-123"


class TestValidationSchema:
    """Test ValidationSchema utility class."""
    
    @pytest.mark.unit
    def test_email_validation(self):
        """Test email validation."""
        # Valid emails
        assert ValidationSchema.validate_email("test@example.com") is True
        assert ValidationSchema.validate_email("user.name+tag@domain.co.uk") is True
        
        # Invalid emails
        assert ValidationSchema.validate_email("invalid-email") is False
        assert ValidationSchema.validate_email("@domain.com") is False
        assert ValidationSchema.validate_email("user@") is False
    
    @pytest.mark.unit
    def test_url_validation(self):
        """Test URL validation."""
        # Valid URLs
        assert ValidationSchema.validate_url("https://example.com") is True
        assert ValidationSchema.validate_url("http://localhost:8080/path") is True
        
        # Invalid URLs
        assert ValidationSchema.validate_url("not-a-url") is False
        assert ValidationSchema.validate_url("ftp://example.com") is False
    
    @pytest.mark.unit
    def test_api_key_validation(self):
        """Test API key validation."""
        # Valid API keys
        assert ValidationSchema.validate_api_key("sk-1234567890abcdef") is True
        assert ValidationSchema.validate_api_key("api_key_123456789012345") is True
        
        # Invalid API keys
        assert ValidationSchema.validate_api_key("short") is False
        assert ValidationSchema.validate_api_key("") is False
        assert ValidationSchema.validate_api_key(None) is False
    
    @pytest.mark.unit
    def test_model_name_validation(self):
        """Test model name validation."""
        # Valid model names
        assert ValidationSchema.validate_model_name("gpt-4") is True
        assert ValidationSchema.validate_model_name("claude-3-sonnet") is True
        assert ValidationSchema.validate_model_name("openai/gpt-3.5-turbo") is True
        
        # Invalid model names
        assert ValidationSchema.validate_model_name("") is False
        assert ValidationSchema.validate_model_name(None) is False
        assert ValidationSchema.validate_model_name("model with spaces") is False
    
    @pytest.mark.unit
    def test_conversation_id_validation(self):
        """Test conversation ID validation."""
        # Valid conversation IDs
        assert ValidationSchema.validate_conversation_id("conv-123456") is True
        assert ValidationSchema.validate_conversation_id("12345678") is True
        assert ValidationSchema.validate_conversation_id("uuid-like-id-123") is True
        
        # Invalid conversation IDs
        assert ValidationSchema.validate_conversation_id("short") is False
        assert ValidationSchema.validate_conversation_id("") is False
        assert ValidationSchema.validate_conversation_id(None) is False


class TestConfigSchema:
    """Test ConfigSchema validation class."""
    
    @pytest.mark.unit
    def test_valid_config_validation(self):
        """Test validation of valid configuration."""
        valid_config = {
            "api": {
                "base_url": "http://localhost:5051",
                "timeout": 30
            },
            "ui": {
                "theme": "dark",
                "font_size": 12
            },
            "memory": {
                "max_entries": 1000,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        }
        
        errors = ConfigSchema.validate_config(valid_config)
        assert len(errors) == 0
    
    @pytest.mark.unit
    def test_missing_section_validation(self):
        """Test validation with missing sections."""
        invalid_config = {
            "api": {
                "base_url": "http://localhost:5051",
                "timeout": 30
            }
            # Missing ui and memory sections
        }
        
        errors = ConfigSchema.validate_config(invalid_config)
        assert len(errors) == 2
        assert "Missing required section: ui" in errors
        assert "Missing required section: memory" in errors
    
    @pytest.mark.unit
    def test_missing_field_validation(self):
        """Test validation with missing fields."""
        invalid_config = {
            "api": {
                "base_url": "http://localhost:5051"
                # Missing timeout
            },
            "ui": {
                "theme": "dark"
                # Missing font_size
            },
            "memory": {
                "max_entries": 1000,
                "embedding_model": "test-model"
            }
        }
        
        errors = ConfigSchema.validate_config(invalid_config)
        assert len(errors) == 2
        assert "Missing required field: api.timeout" in errors
        assert "Missing required field: ui.font_size" in errors
    
    @pytest.mark.unit
    def test_invalid_field_type_validation(self):
        """Test validation with invalid field types."""
        invalid_config = {
            "api": {
                "base_url": "not-a-valid-url",
                "timeout": "not-an-integer"
            },
            "ui": {
                "theme": "dark",
                "font_size": 12
            },
            "memory": {
                "max_entries": 1000,
                "embedding_model": "test-model"
            }
        }
        
        errors = ConfigSchema.validate_config(invalid_config)
        assert len(errors) == 2
        assert "Invalid API base URL format" in errors
        assert "API timeout must be an integer" in errors


class TestUtilityFunctions:
    """Test utility functions."""
    
    @pytest.mark.unit
    def test_serialize_dataclass(self):
        """Test dataclass serialization."""
        message = Message(MessageRole.USER, "Test message")
        serialized = serialize_dataclass(message)
        
        assert isinstance(serialized, dict)
        assert serialized["role"] == "user"
        assert serialized["content"] == "Test message"
        assert "timestamp" in serialized
    
    @pytest.mark.unit
    def test_deserialize_message(self):
        """Test message deserialization."""
        data = {
            "role": "assistant",
            "content": "Test response",
            "timestamp": "2025-01-01T00:00:00",
            "metadata": {}
        }
        
        message = deserialize_message(data)
        assert isinstance(message, Message)
        assert message.role == MessageRole.ASSISTANT
        assert message.content == "Test response"
    
    @pytest.mark.unit
    def test_deserialize_conversation(self):
        """Test conversation deserialization."""
        data = {
            "id": "conv-123",
            "title": "Test Conversation",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello",
                    "timestamp": "2025-01-01T00:00:00",
                    "metadata": {}
                }
            ],
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
            "metadata": {}
        }
        
        conversation = deserialize_conversation(data)
        assert isinstance(conversation, Conversation)
        assert conversation.id == "conv-123"
        assert len(conversation.messages) == 1
        assert conversation.messages[0].content == "Hello"
    
    @pytest.mark.unit
    def test_create_api_response(self):
        """Test API response creation utility."""
        # Success response
        success_response = create_api_response(True, {"result": "success"})
        assert success_response.success is True
        assert success_response.data == {"result": "success"}
        assert success_response.error is None
        
        # Error response
        error_response = create_api_response(False, error="Something failed", error_code="ERROR_CODE")
        assert error_response.success is False
        assert error_response.error == "Something failed"
        assert error_response.error_code == "ERROR_CODE"
    
    @pytest.mark.unit
    def test_create_default_service_config(self):
        """Test default service config creation."""
        config = create_default_service_config("test-service", 8080)
        
        assert config.name == "test-service"
        assert config.port == 8080
        assert config.host == "localhost"
        assert config.timeout == 30
        assert config.enabled is True


@pytest.mark.xfail_known_issue
class TestKnownSchemaIssues:
    """Test known issues with schema marked as expected failures."""
    
    def test_datetime_timezone_issue(self):
        """Test known issue with datetime timezone handling."""
        # This test documents a known issue with timezone-aware datetime objects
        # in serialization/deserialization
        
        # Create message with timezone-aware datetime
        tz_aware_time = datetime.now(timezone.utc)
        message = Message(MessageRole.USER, "Test message", timestamp=tz_aware_time)
        
        # Serialize and deserialize
        data = message.to_dict()
        restored_message = Message.from_dict(data)
        
        # This might fail due to timezone information loss
        # The restored timestamp might not have timezone info
        assert restored_message.timestamp.tzinfo is not None
    
    def test_large_embedding_serialization_issue(self):
        """Test known issue with large embedding serialization."""
        # This documents a potential issue with very large embeddings
        # that might cause memory or performance problems
        
        # Create memory entry with very large embedding
        large_embedding = [0.1] * 10000  # Very large embedding vector
        entry = MemoryEntry("mem-123", "Test content", embedding=large_embedding)
        
        # Serialization might be slow or fail for very large embeddings
        data = entry.to_dict()
        
        # This assertion might fail due to performance issues
        # but should generally work for reasonable embedding sizes
        assert len(data["embedding"]) == 10000
    
    def test_circular_reference_issue(self):
        """Test known issue with circular references in metadata."""
        # This documents a potential issue with circular references
        # in metadata that could cause infinite recursion
        
        metadata = {"self_ref": None}
        metadata["self_ref"] = metadata  # Create circular reference
        
        # Create message with circular reference
        message = Message(MessageRole.USER, "Test", metadata=metadata)
        
        # This should fail due to circular reference during serialization
        with pytest.raises((ValueError, RecursionError, TypeError)):
            json.dumps(serialize_dataclass(message))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])