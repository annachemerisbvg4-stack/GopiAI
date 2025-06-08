#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Базовый класс для всех агентов в GopiAI.
"""

from gopiai.core.logging import get_logger
logger = get_logger().logger
from abc import ABC, abstractmethod

logger = get_logger().logger


class BaseAgent(ABC):
    """
    Базовый абстрактный класс для всех агентов.
    Определяет общий интерфейс и базовую функциональность.
    """

    def __init__(self, name="BaseAgent"):
        """
        Инициализирует базового агента.

        Args:
            name (str): Имя агента
        """
        self.name = name
        self.is_running = False
        logger.info(f"Инициализирован агент: {self.name}")

    @abstractmethod
    def process(self, input_text):
        """
        Обрабатывает входной текст и возвращает результат.
        
        Args:
            input_text (str): Входной текст для обработки
            
        Returns:
            str: Результат обработки
        """
        pass

    def start(self):
        """Запускает агента."""
        self.is_running = True
        logger.info(f"Агент {self.name} запущен")

    def stop(self):
        """Останавливает агента."""
        self.is_running = False
        logger.info(f"Агент {self.name} остановлен")

    def status(self):
        """Возвращает текущий статус агента."""
        return {
            "name": self.name,
            "is_running": self.is_running,
        }

    def __str__(self):
        return f"{self.name} (running: {self.is_running})"
