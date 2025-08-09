"""
Core Interfaces for GopiAI System

Defines abstract base classes and interfaces for all GopiAI components.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass


class AIProviderInterface(ABC):
    """Abstract interface for AI service providers."""
    
    @abstractmethod
    def get_response(self, messages: List[Dict[str, str]], model: str = None) -> str:
        """Get response from AI provider."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate API key for the provider."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name."""
        pass


class MemoryInterface(ABC):
    """Abstract interface for memory/RAG systems."""
    
    @abstractmethod
    def store_conversation(self, conversation_id: str, messages: List[Dict[str, str]]) -> bool:
        """Store conversation in memory."""
        pass
    
    @abstractmethod
    def search_memory(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memory for relevant information."""
        pass
    
    @abstractmethod
    def get_conversation_context(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get conversation context from memory."""
        pass
    
    @abstractmethod
    def clear_memory(self) -> bool:
        """Clear all memory data."""
        pass


class UIComponentInterface(ABC):
    """Abstract interface for UI components."""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the UI component."""
        pass
    
    @abstractmethod
    def update_display(self, data: Any) -> None:
        """Update component display with new data."""
        pass
    
    @abstractmethod
    def handle_user_input(self, input_data: Any) -> Any:
        """Handle user input and return result."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup component resources."""
        pass


class ConfigurationInterface(ABC):
    """Abstract interface for configuration management."""
    
    @abstractmethod
    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from file."""
        pass
    
    @abstractmethod
    def save_config(self, config: Dict[str, Any], config_path: str = None) -> bool:
        """Save configuration to file."""
        pass
    
    @abstractmethod
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        pass
    
    @abstractmethod
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a specific setting value."""
        pass


class ToolInterface(ABC):
    """Abstract interface for CrewAI tools."""
    
    @abstractmethod
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate tool parameters."""
        pass
    
    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Get tool name."""
        pass
    
    @property
    @abstractmethod
    def tool_description(self) -> str:
        """Get tool description."""
        pass


class LoggerInterface(ABC):
    """Abstract interface for logging systems."""
    
    @abstractmethod
    def log_info(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log info message."""
        pass
    
    @abstractmethod
    def log_warning(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log warning message."""
        pass
    
    @abstractmethod
    def log_error(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log error message."""
        pass
    
    @abstractmethod
    def log_debug(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log debug message."""
        pass


class StateManagerInterface(ABC):
    """Abstract interface for state management."""
    
    @abstractmethod
    def get_state(self, key: str) -> Any:
        """Get state value by key."""
        pass
    
    @abstractmethod
    def set_state(self, key: str, value: Any) -> bool:
        """Set state value by key."""
        pass
    
    @abstractmethod
    def clear_state(self, key: str = None) -> bool:
        """Clear state (specific key or all)."""
        pass
    
    @abstractmethod
    def get_all_state(self) -> Dict[str, Any]:
        """Get all state data."""
        pass


class ValidationInterface(ABC):
    """Abstract interface for data validation."""
    
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate data."""
        pass
    
    @abstractmethod
    def get_validation_errors(self, data: Any) -> List[str]:
        """Get validation errors for data."""
        pass
    
    @abstractmethod
    def sanitize(self, data: Any) -> Any:
        """Sanitize data."""
        pass


@dataclass
class ServiceInfo:
    """Information about a service."""
    name: str
    version: str
    status: str
    health_check_url: Optional[str] = None
    dependencies: List[str] = None


class ServiceInterface(ABC):
    """Abstract interface for services."""
    
    @abstractmethod
    def start(self) -> bool:
        """Start the service."""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Stop the service."""
        pass
    
    @abstractmethod
    def restart(self) -> bool:
        """Restart the service."""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check service health."""
        pass
    
    @abstractmethod
    def get_service_info(self) -> ServiceInfo:
        """Get service information."""
        pass