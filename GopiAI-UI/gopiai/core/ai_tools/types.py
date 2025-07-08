"""
Shared types and interfaces for AI Tools.

This module contains shared types and interfaces used across the AI tools
package to avoid circular imports.
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum, auto

class CommandType(Enum):
    """Types of commands that can be executed by the AI."""
    CLICK = auto()
    TYPE = auto()
    NAVIGATE = auto()
    EXECUTE = auto()
    QUERY = auto()

@dataclass
class AICommand:
    """A command to be executed by the AI."""
    type: CommandType
    target: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    text: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
