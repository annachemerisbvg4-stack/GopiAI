#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль с инструментами для агентов.
"""

from gopiai.core.logging import get_logger
logger = get_logger().logger
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable

logger = get_logger().logger


@dataclass
class Tool:
    """Инструмент для агента."""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_params: List[str] = field(default_factory=list)
    is_async: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolCollection:
    """Коллекция инструментов для агента."""
    
    def __init__(self):
        """Инициализирует коллекцию инструментов."""
        self.tools: Dict[str, Tool] = {}
    
    def add_tool(self, tool: Tool):
        """Добавляет инструмент в коллекцию."""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Возвращает инструмент по имени."""
        return self.tools.get(name)
    
    def get_all_tools(self) -> List[Tool]:
        """Возвращает все инструменты."""
        return list(self.tools.values())
    
    def get_tool_names(self) -> List[str]:
        """Возвращает имена всех инструментов."""
        return list(self.tools.keys())
    
    def remove_tool(self, name: str):
        """Удаляет инструмент из коллекции."""
        if name in self.tools:
            del self.tools[name]


# Стандартные инструменты
class CreateChatCompletion(Tool):
    """Инструмент для создания ответа в чате."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="create_chat_completion",
            description="Создает ответ в чате на основе истории сообщений",
            function=self._create_chat_completion,
            parameters={
                "messages": {
                    "type": "array",
                    "description": "История сообщений",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "enum": ["user", "assistant", "system"]
                            },
                            "content": {
                                "type": "string"
                            }
                        },
                        "required": ["role", "content"]
                    }
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Максимальное количество токенов в ответе"
                },
                "temperature": {
                    "type": "number",
                    "description": "Температура генерации (0.0-1.0)"
                }
            },
            required_params=["messages"]
        )
    
    def _create_chat_completion(self, messages, max_tokens=1000, temperature=0.7):
        """Создает ответ в чате."""
        from gopiai.app.llm import llm
        return llm.chat(messages, max_tokens, temperature)


class Terminate(Tool):
    """Инструмент для завершения работы агента."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="terminate",
            description="Завершает работу агента и возвращает результат",
            function=self._terminate,
            parameters={
                "message": {
                    "type": "string",
                    "description": "Сообщение для пользователя"
                }
            },
            required_params=["message"]
        )
    
    def _terminate(self, message):
        """Завершает работу агента."""
        return {"terminated": True, "message": message}
