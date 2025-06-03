#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Интерфейсы для GopiAI.
Определяет абстрактные классы и интерфейсы для компонентов приложения.
"""

from gopiai.core.logging import get_logger
logger = get_logger().logger
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = get_logger().logger


class ITool(ABC):
    """Интерфейс для инструментов агента."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Возвращает имя инструмента."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Возвращает описание инструмента."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Выполняет инструмент с указанными параметрами."""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """Возвращает параметры инструмента."""
        pass


class IAgent(ABC):
    """Интерфейс для агентов."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Возвращает имя агента."""
        pass
    
    @abstractmethod
    def process(self, input_text: str) -> str:
        """Обрабатывает входной текст и возвращает результат."""
        pass
    
    @abstractmethod
    def start(self) -> None:
        """Запускает агента."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Останавливает агента."""
        pass
    
    @property
    @abstractmethod
    def is_running(self) -> bool:
        """Возвращает статус агента."""
        pass


class ToolResult:
    """Результат выполнения инструмента."""
    
    def __init__(self, message: Optional[str], data: Optional[Dict[str, Any]] = None, tool_name: Optional[str] = None, content: Optional[str] = None, success: bool = True):
        """
        Инициализирует результат выполнения инструмента.
        
        Args:
            message: Текстовое сообщение с результатом
            data: Дополнительные данные результата
            tool_name: Имя инструмента (для обратной совместимости)
            content: Содержание сообщения (для обратной совместимости)
            success: Успешно ли выполнение инструмента
        """
        self.success = success
        # Используем либо message, либо content
        self.message = message or content or ""
        self.data = data or {}
        # Для обратной совместимости
        self.tool_name = tool_name


class IUI(ABC):
    """Интерфейс для компонентов пользовательского интерфейса."""
    
    @abstractmethod
    def update(self) -> None:
        """Обновляет компонент."""
        pass
    
    @abstractmethod
    def show(self) -> None:
        """Показывает компонент."""
        pass
    
    @abstractmethod
    def hide(self) -> None:
        """Скрывает компонент."""
        pass
