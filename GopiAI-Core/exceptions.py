#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Исключения для GopiAI.
Определяет пользовательские исключения, используемые в приложении.
"""

from gopiai.core.logging import get_logger
logger = get_logger().logger

logger = get_logger().logger


class GopiAIException(Exception):
    """Базовое исключение для всех исключений GopiAI."""
    pass


class TokenLimitExceeded(GopiAIException):
    """Исключение, возникающее при превышении лимита токенов."""
    pass


class AgentError(GopiAIException):
    """Исключение, возникающее при ошибке агента."""
    pass


class ToolError(GopiAIException):
    """Исключение, возникающее при ошибке инструмента."""
    pass


class ConfigError(GopiAIException):
    """Исключение, возникающее при ошибке конфигурации."""
    pass


class APIError(GopiAIException):
    """Исключение, возникающее при ошибке API."""
    pass


class AuthenticationError(GopiAIException):
    """Исключение, возникающее при ошибке аутентификации."""
    pass
