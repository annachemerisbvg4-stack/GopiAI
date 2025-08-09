"""
Core Exceptions for GopiAI System

Defines custom exception classes for error handling across all GopiAI components.
"""


class GopiAIError(Exception):
    """Base exception for all GopiAI errors."""
    
    def __init__(self, message: str, error_code: str = None, context: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "GOPIAI_ERROR"
        self.context = context or {}
    
    def __str__(self):
        if self.context:
            return f"{self.error_code}: {self.message} (Context: {self.context})"
        return f"{self.error_code}: {self.message}"


class ConfigurationError(GopiAIError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: str = None, context: dict = None):
        super().__init__(message, "CONFIG_ERROR", context)
        self.config_key = config_key


class AIProviderError(GopiAIError):
    """Raised when AI provider operations fail."""
    
    def __init__(self, message: str, provider: str = None, model: str = None, context: dict = None):
        super().__init__(message, "AI_PROVIDER_ERROR", context)
        self.provider = provider
        self.model = model


class APIKeyError(AIProviderError):
    """Raised when API key is invalid or missing."""
    
    def __init__(self, message: str, provider: str = None, context: dict = None):
        super().__init__(message, provider, None, context)
        self.error_code = "API_KEY_ERROR"


class RateLimitError(AIProviderError):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str, provider: str = None, retry_after: int = None, context: dict = None):
        super().__init__(message, provider, None, context)
        self.error_code = "RATE_LIMIT_ERROR"
        self.retry_after = retry_after


class ModelNotFoundError(AIProviderError):
    """Raised when requested model is not available."""
    
    def __init__(self, message: str, provider: str = None, model: str = None, context: dict = None):
        super().__init__(message, provider, model, context)
        self.error_code = "MODEL_NOT_FOUND_ERROR"


class MemoryError(GopiAIError):
    """Raised when memory/RAG operations fail."""
    
    def __init__(self, message: str, operation: str = None, context: dict = None):
        super().__init__(message, "MEMORY_ERROR", context)
        self.operation = operation


class IndexNotFoundError(MemoryError):
    """Raised when memory index is not found."""
    
    def __init__(self, message: str, index_path: str = None, context: dict = None):
        super().__init__(message, "index_lookup", context)
        self.error_code = "INDEX_NOT_FOUND_ERROR"
        self.index_path = index_path


class SearchError(MemoryError):
    """Raised when memory search operations fail."""
    
    def __init__(self, message: str, query: str = None, context: dict = None):
        super().__init__(message, "search", context)
        self.error_code = "SEARCH_ERROR"
        self.query = query


class UIError(GopiAIError):
    """Raised when UI operations fail."""
    
    def __init__(self, message: str, component: str = None, context: dict = None):
        super().__init__(message, "UI_ERROR", context)
        self.component = component


class WidgetError(UIError):
    """Raised when widget operations fail."""
    
    def __init__(self, message: str, widget_name: str = None, context: dict = None):
        super().__init__(message, widget_name, context)
        self.error_code = "WIDGET_ERROR"
        self.widget_name = widget_name


class ThemeError(UIError):
    """Raised when theme operations fail."""
    
    def __init__(self, message: str, theme_name: str = None, context: dict = None):
        super().__init__(message, "theme", context)
        self.error_code = "THEME_ERROR"
        self.theme_name = theme_name


class ServiceError(GopiAIError):
    """Raised when service operations fail."""
    
    def __init__(self, message: str, service_name: str = None, context: dict = None):
        super().__init__(message, "SERVICE_ERROR", context)
        self.service_name = service_name


class ServiceUnavailableError(ServiceError):
    """Raised when a required service is unavailable."""
    
    def __init__(self, message: str, service_name: str = None, context: dict = None):
        super().__init__(message, service_name, context)
        self.error_code = "SERVICE_UNAVAILABLE_ERROR"


class ServiceTimeoutError(ServiceError):
    """Raised when service operations timeout."""
    
    def __init__(self, message: str, service_name: str = None, timeout: int = None, context: dict = None):
        super().__init__(message, service_name, context)
        self.error_code = "SERVICE_TIMEOUT_ERROR"
        self.timeout = timeout


class ValidationError(GopiAIError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: str = None, value: str = None, context: dict = None):
        super().__init__(message, "VALIDATION_ERROR", context)
        self.field = field
        self.value = value


class SchemaError(ValidationError):
    """Raised when schema validation fails."""
    
    def __init__(self, message: str, schema_name: str = None, context: dict = None):
        super().__init__(message, None, None, context)
        self.error_code = "SCHEMA_ERROR"
        self.schema_name = schema_name


class ToolError(GopiAIError):
    """Raised when tool operations fail."""
    
    def __init__(self, message: str, tool_name: str = None, context: dict = None):
        super().__init__(message, "TOOL_ERROR", context)
        self.tool_name = tool_name


class ToolNotFoundError(ToolError):
    """Raised when requested tool is not found."""
    
    def __init__(self, message: str, tool_name: str = None, context: dict = None):
        super().__init__(message, tool_name, context)
        self.error_code = "TOOL_NOT_FOUND_ERROR"


class ToolExecutionError(ToolError):
    """Raised when tool execution fails."""
    
    def __init__(self, message: str, tool_name: str = None, parameters: dict = None, context: dict = None):
        super().__init__(message, tool_name, context)
        self.error_code = "TOOL_EXECUTION_ERROR"
        self.parameters = parameters


class SecurityError(GopiAIError):
    """Raised when security violations occur."""
    
    def __init__(self, message: str, violation_type: str = None, context: dict = None):
        super().__init__(message, "SECURITY_ERROR", context)
        self.violation_type = violation_type


class AuthenticationError(SecurityError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str, context: dict = None):
        super().__init__(message, "authentication", context)
        self.error_code = "AUTHENTICATION_ERROR"


class AuthorizationError(SecurityError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str, resource: str = None, context: dict = None):
        super().__init__(message, "authorization", context)
        self.error_code = "AUTHORIZATION_ERROR"
        self.resource = resource


class FileSystemError(GopiAIError):
    """Raised when file system operations fail."""
    
    def __init__(self, message: str, file_path: str = None, operation: str = None, context: dict = None):
        super().__init__(message, "FILESYSTEM_ERROR", context)
        self.file_path = file_path
        self.operation = operation


class FileNotFoundError(FileSystemError):
    """Raised when a required file is not found."""
    
    def __init__(self, message: str, file_path: str = None, context: dict = None):
        super().__init__(message, file_path, "read", context)
        self.error_code = "FILE_NOT_FOUND_ERROR"


class FilePermissionError(FileSystemError):
    """Raised when file permission is denied."""
    
    def __init__(self, message: str, file_path: str = None, operation: str = None, context: dict = None):
        super().__init__(message, file_path, operation, context)
        self.error_code = "FILE_PERMISSION_ERROR"


class NetworkError(GopiAIError):
    """Raised when network operations fail."""
    
    def __init__(self, message: str, url: str = None, status_code: int = None, context: dict = None):
        super().__init__(message, "NETWORK_ERROR", context)
        self.url = url
        self.status_code = status_code


class ConnectionError(NetworkError):
    """Raised when network connection fails."""
    
    def __init__(self, message: str, url: str = None, context: dict = None):
        super().__init__(message, url, None, context)
        self.error_code = "CONNECTION_ERROR"


class TimeoutError(NetworkError):
    """Raised when network operations timeout."""
    
    def __init__(self, message: str, url: str = None, timeout: int = None, context: dict = None):
        super().__init__(message, url, None, context)
        self.error_code = "TIMEOUT_ERROR"
        self.timeout = timeout


# Exception mapping for common error scenarios
EXCEPTION_MAP = {
    "config": ConfigurationError,
    "ai_provider": AIProviderError,
    "api_key": APIKeyError,
    "rate_limit": RateLimitError,
    "model_not_found": ModelNotFoundError,
    "memory": MemoryError,
    "index_not_found": IndexNotFoundError,
    "search": SearchError,
    "ui": UIError,
    "widget": WidgetError,
    "theme": ThemeError,
    "service": ServiceError,
    "service_unavailable": ServiceUnavailableError,
    "service_timeout": ServiceTimeoutError,
    "validation": ValidationError,
    "schema": SchemaError,
    "tool": ToolError,
    "tool_not_found": ToolNotFoundError,
    "tool_execution": ToolExecutionError,
    "security": SecurityError,
    "authentication": AuthenticationError,
    "authorization": AuthorizationError,
    "filesystem": FileSystemError,
    "file_not_found": FileNotFoundError,
    "file_permission": FilePermissionError,
    "network": NetworkError,
    "connection": ConnectionError,
    "timeout": TimeoutError,
}


def get_exception_class(error_type: str) -> type:
    """Get exception class by error type string."""
    return EXCEPTION_MAP.get(error_type, GopiAIError)


def create_exception(error_type: str, message: str, **kwargs) -> GopiAIError:
    """Create exception instance by error type."""
    exception_class = get_exception_class(error_type)
    return exception_class(message, **kwargs)