"""
Типы данных для интеграции с MCP.
Эмулирует классы из официального модуля mcp.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class JSONRPCRequest:
    """Представляет запрос JSON-RPC."""
    id: str
    method: str
    params: Dict[str, Any]


@dataclass
class JSONRPCResponse:
    """Представляет ответ JSON-RPC."""
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


@dataclass
class JSONRPCNotification:
    """Представляет уведомление JSON-RPC."""
    method: str
    params: Dict[str, Any]
