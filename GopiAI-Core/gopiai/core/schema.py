"""
Core Schema Definitions for GopiAI System

Defines data models, validation schemas, and data structures used across all GopiAI components.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime
from enum import Enum
import json
import re


class MessageRole(Enum):
    """Enumeration for message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class AIProvider(Enum):
    """Enumeration for AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OPENROUTER = "openrouter"
    LOCAL = "local"


class ServiceStatus(Enum):
    """Enumeration for service status."""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"


class LogLevel(Enum):
    """Enumeration for log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Message:
    """Represents a chat message."""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            metadata=data.get("metadata", {})
        )
    
    def validate(self) -> bool:
        """Validate message data."""
        if not isinstance(self.content, str) or not self.content.strip():
            return False
        if not isinstance(self.role, MessageRole):
            return False
        return True


@dataclass
class Conversation:
    """Represents a conversation with messages."""
    id: str
    title: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: Message) -> None:
        """Add message to conversation."""
        if message.validate():
            self.messages.append(message)
            self.updated_at = datetime.now()
    
    def get_messages_by_role(self, role: MessageRole) -> List[Message]:
        """Get messages by role."""
        return [msg for msg in self.messages if msg.role == role]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create conversation from dictionary."""
        messages = [Message.from_dict(msg_data) for msg_data in data.get("messages", [])]
        return cls(
            id=data["id"],
            title=data["title"],
            messages=messages,
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
            metadata=data.get("metadata", {})
        )


@dataclass
class ModelInfo:
    """Information about an AI model."""
    name: str
    provider: AIProvider
    max_tokens: int
    supports_functions: bool = False
    supports_vision: bool = False
    cost_per_token: float = 0.0
    rate_limits: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate model info."""
        if not self.name or not isinstance(self.name, str):
            return False
        if not isinstance(self.provider, AIProvider):
            return False
        if self.max_tokens <= 0:
            return False
        return True


@dataclass
class APIResponse:
    """Represents an API response."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "error_code": self.error_code,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class UsageStats:
    """Usage statistics for AI services."""
    provider: AIProvider
    model: str
    requests_made: int = 0
    tokens_used: int = 0
    cost_incurred: float = 0.0
    errors_count: int = 0
    last_request: Optional[datetime] = None
    
    def update_usage(self, tokens: int, cost: float = 0.0, error: bool = False) -> None:
        """Update usage statistics."""
        self.requests_made += 1
        self.tokens_used += tokens
        self.cost_incurred += cost
        if error:
            self.errors_count += 1
        self.last_request = datetime.now()


@dataclass
class ServiceConfig:
    """Configuration for a service."""
    name: str
    host: str = "localhost"
    port: int = 5000
    timeout: int = 30
    max_retries: int = 3
    health_check_path: str = "/health"
    enabled: bool = True
    environment: str = "development"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_url(self) -> str:
        """Get service URL."""
        return f"http://{self.host}:{self.port}"
    
    def get_health_check_url(self) -> str:
        """Get health check URL."""
        return f"{self.get_url()}{self.health_check_path}"


@dataclass
class ToolConfig:
    """Configuration for a tool."""
    name: str
    description: str
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate tool parameters."""
        # Basic validation - can be extended
        for required_param in self.parameters.get("required", []):
            if required_param not in params:
                return False
        return True


@dataclass
class UITheme:
    """UI theme configuration."""
    name: str
    colors: Dict[str, str] = field(default_factory=dict)
    fonts: Dict[str, str] = field(default_factory=dict)
    sizes: Dict[str, int] = field(default_factory=dict)
    styles: Dict[str, str] = field(default_factory=dict)
    
    def get_color(self, color_name: str, default: str = "#000000") -> str:
        """Get color value."""
        return self.colors.get(color_name, default)
    
    def get_font(self, font_name: str, default: str = "Arial") -> str:
        """Get font value."""
        return self.fonts.get(font_name, default)


@dataclass
class MemoryEntry:
    """Entry in the memory system."""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    relevance_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory entry to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "relevance_score": self.relevance_score
        }


@dataclass
class SearchResult:
    """Result from memory search."""
    entry: MemoryEntry
    score: float
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert search result to dictionary."""
        return {
            "entry": self.entry.to_dict(),
            "score": self.score,
            "context": self.context
        }


class ValidationSchema:
    """Base class for validation schemas."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format."""
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format."""
        if not api_key or not isinstance(api_key, str):
            return False
        # Basic validation - at least 10 characters, alphanumeric
        return len(api_key) >= 10 and api_key.replace('-', '').replace('_', '').isalnum()
    
    @staticmethod
    def validate_model_name(model_name: str) -> bool:
        """Validate model name format."""
        if not model_name or not isinstance(model_name, str):
            return False
        # Allow alphanumeric, hyphens, underscores, dots, and slashes
        pattern = r'^[a-zA-Z0-9\-_./]+$'
        return bool(re.match(pattern, model_name))
    
    @staticmethod
    def validate_conversation_id(conv_id: str) -> bool:
        """Validate conversation ID format."""
        if not conv_id or not isinstance(conv_id, str):
            return False
        # UUID-like format or alphanumeric with hyphens
        pattern = r'^[a-zA-Z0-9\-_]+$'
        return bool(re.match(pattern, conv_id)) and len(conv_id) >= 8


class ConfigSchema:
    """Schema for configuration validation."""
    
    REQUIRED_FIELDS = {
        "api": ["base_url", "timeout"],
        "ui": ["theme", "font_size"],
        "memory": ["max_entries", "embedding_model"]
    }
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        for section, required_fields in cls.REQUIRED_FIELDS.items():
            if section not in config:
                errors.append(f"Missing required section: {section}")
                continue
            
            section_config = config[section]
            for field in required_fields:
                if field not in section_config:
                    errors.append(f"Missing required field: {section}.{field}")
        
        # Validate specific field types
        if "api" in config:
            api_config = config["api"]
            if "base_url" in api_config and not ValidationSchema.validate_url(api_config["base_url"]):
                errors.append("Invalid API base URL format")
            if "timeout" in api_config and not isinstance(api_config["timeout"], int):
                errors.append("API timeout must be an integer")
        
        return errors


# Utility functions for schema operations
def serialize_dataclass(obj: Any) -> Dict[str, Any]:
    """Serialize dataclass to dictionary."""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif hasattr(obj, '__dict__'):
        result = {}
        for key, value in obj.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, list):
                result[key] = [serialize_dataclass(item) for item in value]
            elif hasattr(value, '__dict__'):
                result[key] = serialize_dataclass(value)
            else:
                result[key] = value
        return result
    else:
        return obj


def deserialize_message(data: Dict[str, Any]) -> Message:
    """Deserialize message from dictionary."""
    return Message.from_dict(data)


def deserialize_conversation(data: Dict[str, Any]) -> Conversation:
    """Deserialize conversation from dictionary."""
    return Conversation.from_dict(data)


def create_api_response(success: bool, data: Any = None, error: str = None, error_code: str = None) -> APIResponse:
    """Create API response object."""
    return APIResponse(
        success=success,
        data=data,
        error=error,
        error_code=error_code
    )


def create_default_service_config(name: str, port: int) -> ServiceConfig:
    """Create default service configuration."""
    return ServiceConfig(
        name=name,
        port=port,
        timeout=30,
        max_retries=3,
        health_check_path="/health",
        enabled=True
    )