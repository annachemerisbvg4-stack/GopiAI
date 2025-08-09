# GopiAI-Core

Core interfaces, exceptions, and schema definitions for the GopiAI system.

## Overview

GopiAI-Core provides the foundational components used across all GopiAI modules:

- **Interfaces**: Abstract base classes defining contracts for AI providers, memory systems, UI components, and services
- **Exceptions**: Custom exception hierarchy for comprehensive error handling
- **Schema**: Data models and validation schemas for consistent data structures
- **Utils**: Common utility functions used throughout the system

## Installation

```bash
pip install -e .
```

## Development

Install development dependencies:

```bash
pip install -e .[dev]
```

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=gopiai --cov-report=html
```

## Usage

```python
from gopiai.core import interfaces, exceptions, schema

# Use interfaces for implementing providers
class MyAIProvider(interfaces.AIProviderInterface):
    def get_response(self, messages, model=None):
        # Implementation here
        pass

# Use exceptions for error handling
try:
    # Some operation
    pass
except exceptions.AIProviderError as e:
    print(f"AI Provider error: {e}")

# Use schema for data validation
message = schema.Message(
    role=schema.MessageRole.USER,
    content="Hello, AI!"
)
```

## Components

### Interfaces

- `AIProviderInterface`: Contract for AI service providers
- `MemoryInterface`: Contract for memory/RAG systems  
- `UIComponentInterface`: Contract for UI components
- `ConfigurationInterface`: Contract for configuration management
- `ToolInterface`: Contract for CrewAI tools
- `ServiceInterface`: Contract for services

### Exceptions

- `GopiAIError`: Base exception for all GopiAI errors
- `AIProviderError`: AI provider related errors
- `MemoryError`: Memory system related errors
- `UIError`: UI component related errors
- `ServiceError`: Service related errors
- `ValidationError`: Data validation errors

### Schema

- `Message`: Chat message data model
- `Conversation`: Conversation with messages
- `ModelInfo`: AI model information
- `APIResponse`: Standard API response format
- `ServiceConfig`: Service configuration
- `ValidationSchema`: Data validation utilities

### Utils

- ID generation utilities
- File system operations
- JSON handling
- Timestamp utilities
- Dictionary operations
- Environment variable handling
- Logging setup

## Testing

The module includes comprehensive unit tests covering:

- Interface definitions and contracts
- Exception hierarchy and error handling
- Schema validation and data models
- Utility function behavior
- Known issues marked as expected failures

Run specific test categories:

```bash
# Unit tests only
pytest -m unit

# Known issues (expected failures)
pytest -m xfail_known_issue

# Slow tests
pytest -m slow
```