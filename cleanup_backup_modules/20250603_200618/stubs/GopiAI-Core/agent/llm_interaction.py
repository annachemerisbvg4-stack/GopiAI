#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль для взаимодействия с LLM в агентах.
"""

from gopiai.core.logging import get_logger
logger = get_logger().logger
from typing import List, Dict, Any, Optional

from gopiai.app.llm import llm
from gopiai.app.schema import Message

logger = get_logger().logger


def llm_agentic_action(
    messages: List[Dict[str, str]],
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> Dict[str, Any]:
    """
    Выполняет агентное действие с помощью LLM.
    
    Args:
        messages: Список сообщений
        tools: Список инструментов
        tool_choice: Выбор инструмента
        temperature: Температура генерации
        max_tokens: Максимальное количество токенов
        
    Returns:
        Dict[str, Any]: Результат выполнения действия
    """
    logger.debug(f"LLM агентное действие: {len(messages)} сообщений, {len(tools) if tools else 0} инструментов")
    
    # В минимальной версии просто возвращаем заглушку
    last_message = messages[-1]["content"] if messages else ""
    
    # Если есть инструменты, имитируем выбор инструмента
    if tools and len(tools) > 0:
        tool = tools[0]
        return {
            "content": f"[Заглушка LLM] Я выбираю инструмент {tool['name']}",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "arguments": "{}"
                    }
                }
            ]
        }
    
    # Иначе просто возвращаем текстовый ответ
    return {
        "content": f"[Заглушка LLM] Ответ на сообщение: {last_message[:20]}..."
    }


def llm_chat_completion(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> str:
    """
    Выполняет генерацию текста в чате.
    
    Args:
        messages: Список сообщений
        temperature: Температура генерации
        max_tokens: Максимальное количество токенов
        
    Returns:
        str: Сгенерированный текст
    """
    logger.debug(f"LLM генерация текста: {len(messages)} сообщений")
    
    # В минимальной версии просто возвращаем заглушку
    last_message = messages[-1]["content"] if messages else ""
    return f"[Заглушка LLM] Ответ на сообщение: {last_message[:20]}..."
