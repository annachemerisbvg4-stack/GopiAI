#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Схемы данных для GopiAI.
Определяет структуры данных, используемые в приложении.
"""

from gopiai.core.logging import get_logger
logger = get_logger().logger
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Literal

logger = get_logger().logger

# Типы выбора инструментов
TOOL_CHOICE_TYPE = Literal["auto", "required", "none"]


class AgentState(Enum):
    """Состояния агента."""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    ERROR = "error"
    DONE = "done"


@dataclass
class Message:
    """Сообщение в чате."""
    content: str
    role: str = "user"  # user, assistant, system
    timestamp: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Memory:
    """Класс для хранения памяти агента."""
    messages: List[Message] = field(default_factory=list)
    content: str = ""
    timestamp: float = 0.0
    source: str = "user"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """Разговор в чате."""
    messages: List[Message] = field(default_factory=list)
    id: Optional[str] = None
    title: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tool:
    """Инструмент, который может использовать агент."""
    name: str
    description: str
    function: Any
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCall:
    """Вызов инструмента агентом."""
    tool_name: str
    parameters: Dict[str, Any]
    result: Any = None
    error: Optional[str] = None
    timestamp: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolChoice:
    """Выбор инструмента для агента."""
    type: TOOL_CHOICE_TYPE = "auto"
    tool: Optional[str] = None
    tools: List[str] = field(default_factory=list)
    
    # Константы для удобства
    AUTO: TOOL_CHOICE_TYPE = "auto"
    REQUIRED: TOOL_CHOICE_TYPE = "required"
    NONE: TOOL_CHOICE_TYPE = "none"
