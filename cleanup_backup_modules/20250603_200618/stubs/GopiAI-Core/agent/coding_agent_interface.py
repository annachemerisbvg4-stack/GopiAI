#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Интерфейс для взаимодействия с агентом для программирования.
"""

from gopiai.core.logging import get_logger
logger = get_logger().logger
from typing import Dict, List

from PySide6.QtCore import QObject, Signal, Slot, Qt
from gopiai.app.agent.coding_agent import CodingAgent
from gopiai.app.schema import Message

logger = get_logger().logger


class CodingAgentInterface(QObject):
    """
    Интерфейс для взаимодействия с агентом для программирования.
    """
    
    # Сигналы
    message_received = Signal(str)
    thinking_started = Signal()
    thinking_finished = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, parent=None):
        """
        Инициализирует интерфейс.
        
        Args:
            parent: Родительский объект
        """
        super().__init__(parent)
        self.agent = CodingAgent()
        self.conversation: List[Dict[str, str]] = []
        logger.info("Инициализирован интерфейс агента для программирования")
    
    @Slot(str)
    def send_message(self, message: str):
        """
        Отправляет сообщение агенту.
        
        Args:
            message: Текст сообщения
        """
        logger.info(f"Отправка сообщения агенту для программирования: {message[:50]}...")
        
        # Добавляем сообщение пользователя в историю
        self.conversation.append({"role": "user", "content": message})
        
        # Сигнализируем о начале обработки
        self.thinking_started.emit()
        
        try:
            # В минимальной версии просто возвращаем заглушку
            response = f"[Заглушка агента для программирования] Ответ на сообщение: {message[:20]}..."
            
            # Добавляем ответ агента в историю
            self.conversation.append({"role": "assistant", "content": response})
            
            # Отправляем ответ
            self.message_received.emit(response)
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения агентом для программирования: {e}")
            self.error_occurred.emit(str(e))
        finally:
            # Сигнализируем о завершении обработки
            self.thinking_finished.emit()
    
    @Slot()
    def clear_conversation(self):
        """Очищает историю разговора."""
        self.conversation = []
        logger.info("История разговора с агентом для программирования очищена")
    
    @Slot(str)
    def execute_code(self, code: str):
        """
        Выполняет код.
        
        Args:
            code: Код для выполнения
        """
        logger.info(f"Выполнение кода: {code[:50]}...")
        
        # В минимальной версии просто возвращаем заглушку
        result = f"[Заглушка выполнения кода] Результат выполнения: {code[:20]}..."
        self.message_received.emit(result)
