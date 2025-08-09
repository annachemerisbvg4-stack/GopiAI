#!/usr/bin/env python3
"""
Unit tests for GopiAI Core Interfaces

Tests the abstract base classes and interface definitions.
"""

import pytest
from abc import ABC
from typing import Dict, List, Any
from unittest.mock import Mock, MagicMock

from gopiai.core.interfaces import (
    AIProviderInterface,
    MemoryInterface,
    UIComponentInterface,
    ConfigurationInterface,
    ToolInterface,
    LoggerInterface,
    StateManagerInterface,
    ValidationInterface,
    ServiceInterface,
    ServiceInfo
)


class TestAIProviderInterface:
    """Test AIProviderInterface abstract base class."""
    
    def test_interface_is_abstract(self):
        """Test that AIProviderInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AIProviderInterface()
    
    def test_concrete_implementation(self):
        """Test that concrete implementation works correctly."""
        class ConcreteProvider(AIProviderInterface):
            def get_response(self, messages: List[Dict[str, str]], model: str = None) -> str:
                return "Test response"
            
            def get_available_models(self) -> List[str]:
                return ["test-model-1", "test-model-2"]
            
            def validate_api_key(self) -> bool:
                return True
            
            @property
            def provider_name(self) -> str:
                return "test-provider"
        
        provider = ConcreteProvider()
        assert provider.get_response([{"role": "user", "content": "test"}]) == "Test response"
        assert provider.get_available_models() == ["test-model-1", "test-model-2"]
        assert provider.validate_api_key() is True
        assert provider.provider_name == "test-provider"
    
    def test_incomplete_implementation_fails(self):
        """Test that incomplete implementation cannot be instantiated."""
        class IncompleteProvider(AIProviderInterface):
            def get_response(self, messages: List[Dict[str, str]], model: str = None) -> str:
                return "Test response"
            # Missing other required methods
        
        with pytest.raises(TypeError):
            IncompleteProvider()
    
    @pytest.mark.unit
    def test_method_signatures(self):
        """Test that interface methods have correct signatures."""
        # Create a mock implementation to test method signatures
        mock_provider = Mock(spec=AIProviderInterface)
        
        # Test get_response signature
        mock_provider.get_response([{"role": "user", "content": "test"}], "gpt-4")
        mock_provider.get_response.assert_called_once_with([{"role": "user", "content": "test"}], "gpt-4")
        
        # Test get_available_models signature
        mock_provider.get_available_models()
        mock_provider.get_available_models.assert_called_once()
        
        # Test validate_api_key signature
        mock_provider.validate_api_key()
        mock_provider.validate_api_key.assert_called_once()


class TestMemoryInterface:
    """Test MemoryInterface abstract base class."""
    
    def test_interface_is_abstract(self):
        """Test that MemoryInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            MemoryInterface()
    
    def test_concrete_implementation(self):
        """Test that concrete implementation works correctly."""
        class ConcreteMemory(MemoryInterface):
            def __init__(self):
                self.conversations = {}
                self.memory_data = []
            
            def store_conversation(self, conversation_id: str, messages: List[Dict[str, str]]) -> bool:
                self.conversations[conversation_id] = messages
                return True
            
            def search_memory(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
                return [{"id": "1", "content": "test memory", "score": 0.9}]
            
            def get_conversation_context(self, conversation_id: str) -> List[Dict[str, str]]:
                return self.conversations.get(conversation_id, [])
            
            def clear_memory(self) -> bool:
                self.conversations.clear()
                self.memory_data.clear()
                return True
        
        memory = ConcreteMemory()
        
        # Test store_conversation
        messages = [{"role": "user", "content": "Hello"}]
        assert memory.store_conversation("test-conv", messages) is True
        
        # Test get_conversation_context
        context = memory.get_conversation_context("test-conv")
        assert context == messages
        
        # Test search_memory
        results = memory.search_memory("test query")
        assert len(results) == 1
        assert results[0]["content"] == "test memory"
        
        # Test clear_memory
        assert memory.clear_memory() is True
        assert memory.get_conversation_context("test-conv") == []
    
    @pytest.mark.unit
    def test_search_memory_with_limit(self):
        """Test search_memory respects limit parameter."""
        class TestMemory(MemoryInterface):
            def store_conversation(self, conversation_id: str, messages: List[Dict[str, str]]) -> bool:
                return True
            
            def search_memory(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
                # Return more results than limit to test limiting
                all_results = [{"id": str(i), "content": f"result {i}"} for i in range(20)]
                return all_results[:limit]
            
            def get_conversation_context(self, conversation_id: str) -> List[Dict[str, str]]:
                return []
            
            def clear_memory(self) -> bool:
                return True
        
        memory = TestMemory()
        results = memory.search_memory("test", limit=5)
        assert len(results) == 5


class TestUIComponentInterface:
    """Test UIComponentInterface abstract base class."""
    
    def test_interface_is_abstract(self):
        """Test that UIComponentInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            UIComponentInterface()
    
    def test_concrete_implementation(self):
        """Test that concrete implementation works correctly."""
        class ConcreteUIComponent(UIComponentInterface):
            def __init__(self):
                self.initialized = False
                self.data = None
            
            def initialize(self) -> bool:
                self.initialized = True
                return True
            
            def update_display(self, data: Any) -> None:
                self.data = data
            
            def handle_user_input(self, input_data: Any) -> Any:
                return f"Processed: {input_data}"
            
            def cleanup(self) -> None:
                self.initialized = False
                self.data = None
        
        component = ConcreteUIComponent()
        
        # Test initialize
        assert component.initialize() is True
        assert component.initialized is True
        
        # Test update_display
        test_data = {"message": "Hello"}
        component.update_display(test_data)
        assert component.data == test_data
        
        # Test handle_user_input
        result = component.handle_user_input("test input")
        assert result == "Processed: test input"
        
        # Test cleanup
        component.cleanup()
        assert component.initialized is False
        assert component.data is None


class TestConfigurationInterface:
    """Test ConfigurationInterface abstract base class."""
    
    def test_interface_is_abstract(self):
        """Test that ConfigurationInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ConfigurationInterface()
    
    def test_concrete_implementation(self):
        """Test that concrete implementation works correctly."""
        class ConcreteConfig(ConfigurationInterface):
            def __init__(self):
                self.config_data = {}
            
            def load_config(self, config_path: str = None) -> Dict[str, Any]:
                # Mock loading from file
                return {"api_key": "test-key", "timeout": 30}
            
            def save_config(self, config: Dict[str, Any], config_path: str = None) -> bool:
                self.config_data = config
                return True
            
            def get_setting(self, key: str, default: Any = None) -> Any:
                return self.config_data.get(key, default)
            
            def set_setting(self, key: str, value: Any) -> bool:
                self.config_data[key] = value
                return True
        
        config = ConcreteConfig()
        
        # Test load_config
        loaded = config.load_config()
        assert "api_key" in loaded
        assert loaded["timeout"] == 30
        
        # Test set_setting and get_setting
        assert config.set_setting("test_key", "test_value") is True
        assert config.get_setting("test_key") == "test_value"
        assert config.get_setting("nonexistent", "default") == "default"
        
        # Test save_config
        test_config = {"new_key": "new_value"}
        assert config.save_config(test_config) is True
        assert config.config_data == test_config


class TestToolInterface:
    """Test ToolInterface abstract base class."""
    
    def test_interface_is_abstract(self):
        """Test that ToolInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ToolInterface()
    
    def test_concrete_implementation(self):
        """Test that concrete implementation works correctly."""
        class ConcreteTool(ToolInterface):
            def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
                return {"status": "success", "result": parameters.get("input", "")}
            
            def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
                return "input" in parameters
            
            @property
            def tool_name(self) -> str:
                return "test-tool"
            
            @property
            def tool_description(self) -> str:
                return "A test tool for unit testing"
        
        tool = ConcreteTool()
        
        # Test properties
        assert tool.tool_name == "test-tool"
        assert tool.tool_description == "A test tool for unit testing"
        
        # Test validate_parameters
        assert tool.validate_parameters({"input": "test"}) is True
        assert tool.validate_parameters({}) is False
        
        # Test execute
        result = tool.execute({"input": "test data"})
        assert result["status"] == "success"
        assert result["result"] == "test data"


class TestServiceInterface:
    """Test ServiceInterface abstract base class."""
    
    def test_interface_is_abstract(self):
        """Test that ServiceInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ServiceInterface()
    
    def test_concrete_implementation(self):
        """Test that concrete implementation works correctly."""
        class ConcreteService(ServiceInterface):
            def __init__(self):
                self.running = False
                self.healthy = True
            
            def start(self) -> bool:
                self.running = True
                return True
            
            def stop(self) -> bool:
                self.running = False
                return True
            
            def restart(self) -> bool:
                self.stop()
                return self.start()
            
            def health_check(self) -> bool:
                return self.healthy and self.running
            
            def get_service_info(self) -> ServiceInfo:
                return ServiceInfo(
                    name="test-service",
                    version="1.0.0",
                    status="running" if self.running else "stopped"
                )
        
        service = ConcreteService()
        
        # Test start
        assert service.start() is True
        assert service.running is True
        
        # Test health_check
        assert service.health_check() is True
        
        # Test get_service_info
        info = service.get_service_info()
        assert info.name == "test-service"
        assert info.version == "1.0.0"
        assert info.status == "running"
        
        # Test stop
        assert service.stop() is True
        assert service.running is False
        
        # Test restart
        assert service.restart() is True
        assert service.running is True


class TestServiceInfo:
    """Test ServiceInfo dataclass."""
    
    @pytest.mark.unit
    def test_service_info_creation(self):
        """Test ServiceInfo dataclass creation."""
        info = ServiceInfo(
            name="test-service",
            version="1.0.0",
            status="running"
        )
        
        assert info.name == "test-service"
        assert info.version == "1.0.0"
        assert info.status == "running"
        assert info.health_check_url is None
        assert info.dependencies is None
    
    @pytest.mark.unit
    def test_service_info_with_optional_fields(self):
        """Test ServiceInfo with optional fields."""
        info = ServiceInfo(
            name="test-service",
            version="1.0.0",
            status="running",
            health_check_url="/health",
            dependencies=["database", "cache"]
        )
        
        assert info.health_check_url == "/health"
        assert info.dependencies == ["database", "cache"]


class TestInterfaceInheritance:
    """Test interface inheritance and ABC behavior."""
    
    @pytest.mark.unit
    def test_all_interfaces_inherit_from_abc(self):
        """Test that all interfaces inherit from ABC."""
        interfaces = [
            AIProviderInterface,
            MemoryInterface,
            UIComponentInterface,
            ConfigurationInterface,
            ToolInterface,
            LoggerInterface,
            StateManagerInterface,
            ValidationInterface,
            ServiceInterface
        ]
        
        for interface in interfaces:
            assert issubclass(interface, ABC)
    
    @pytest.mark.unit
    def test_interface_method_requirements(self):
        """Test that interfaces define required abstract methods."""
        # Test AIProviderInterface
        assert hasattr(AIProviderInterface, 'get_response')
        assert hasattr(AIProviderInterface, 'get_available_models')
        assert hasattr(AIProviderInterface, 'validate_api_key')
        assert hasattr(AIProviderInterface, 'provider_name')
        
        # Test MemoryInterface
        assert hasattr(MemoryInterface, 'store_conversation')
        assert hasattr(MemoryInterface, 'search_memory')
        assert hasattr(MemoryInterface, 'get_conversation_context')
        assert hasattr(MemoryInterface, 'clear_memory')
        
        # Test UIComponentInterface
        assert hasattr(UIComponentInterface, 'initialize')
        assert hasattr(UIComponentInterface, 'update_display')
        assert hasattr(UIComponentInterface, 'handle_user_input')
        assert hasattr(UIComponentInterface, 'cleanup')


@pytest.mark.xfail_known_issue
class TestKnownInterfaceIssues:
    """Test known issues with interfaces marked as expected failures."""
    
    def test_interface_multiple_inheritance_issue(self):
        """Test known issue with multiple interface inheritance."""
        # This test documents a known limitation with multiple interface inheritance
        # that may need to be addressed in future versions
        
        class MultipleInheritanceTest(AIProviderInterface, MemoryInterface):
            # This should theoretically work but may have issues in practice
            pass
        
        # This will fail because we can't implement all required methods easily
        with pytest.raises(TypeError):
            MultipleInheritanceTest()
    
    def test_interface_property_override_issue(self):
        """Test known issue with property overrides in interfaces."""
        # This documents a potential issue with property definitions in interfaces
        
        class PropertyOverrideTest(AIProviderInterface):
            def get_response(self, messages, model=None):
                return "test"
            
            def get_available_models(self):
                return ["test"]
            
            def validate_api_key(self):
                return True
            
            # This property override might not work as expected in all Python versions
            @property
            def provider_name(self):
                # Simulate a complex property that might fail
                raise NotImplementedError("Complex property logic not implemented")
        
        provider = PropertyOverrideTest()
        
        # This should fail due to the NotImplementedError
        with pytest.raises(NotImplementedError):
            _ = provider.provider_name


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])