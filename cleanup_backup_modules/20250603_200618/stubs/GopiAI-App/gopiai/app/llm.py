#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль для работы с языковыми моделями (LLM).
Предоставляет унифицированный интерфейс для различных LLM.
"""

from gopiai.core.logging import get_logger
logger = get_logger().logger

logger = get_logger().logger


class LLM:
    """
    Класс для работы с языковыми моделями.
    В минимальной версии предоставляет заглушки для основных методов.
    """

    _instance = None

    @classmethod
    def instance(cls):
        """Возвращает синглтон-экземпляр класса LLM."""
        if cls._instance is None:
            cls._instance = LLM()
        return cls._instance

    def __init__(self):
        """Инициализирует экземпляр LLM."""
        self.model_name = "stub-model"
        self.is_initialized = False
        logger.info(f"Инициализирован LLM: {self.model_name}")

    def initialize(self):
        """Инициализирует модель."""
        self.is_initialized = True
        logger.info(f"Модель {self.model_name} инициализирована")
        return True

    def generate(self, prompt, max_tokens=1000, temperature=0.7):
        """
        Генерирует текст на основе промпта.
        
        Args:
            prompt (str): Текст промпта
            max_tokens (int): Максимальное количество токенов в ответе
            temperature (float): Температура генерации (0.0-1.0)
            
        Returns:
            str: Сгенерированный текст
        """
        logger.info(f"Запрос к LLM: {prompt[:50]}...")
        # В минимальной версии просто возвращаем заглушку
        return f"[Заглушка LLM] Ответ на запрос: {prompt[:20]}..."

    def chat(self, messages, max_tokens=1000, temperature=0.7):
        """
        Генерирует ответ на основе истории сообщений.
        
        Args:
            messages (list): Список сообщений в формате [{"role": "user", "content": "..."}, ...]
            max_tokens (int): Максимальное количество токенов в ответе
            temperature (float): Температура генерации (0.0-1.0)
            
        Returns:
            str: Сгенерированный ответ
        """
        logger.info(f"Запрос к LLM (чат): {len(messages)} сообщений")
        # В минимальной версии просто возвращаем заглушку
        last_message = messages[-1]["content"] if messages else ""
        return f"[Заглушка LLM] Ответ на сообщение: {last_message[:20]}..."

    def embed(self, text):
        """
        Создает эмбеддинг для текста.
        
        Args:
            text (str): Текст для эмбеддинга
            
        Returns:
            list: Вектор эмбеддинга
        """
        logger.info(f"Запрос эмбеддинга для текста: {text[:50]}...")
        # В минимальной версии возвращаем случайный вектор
        import random
        return [random.random() for _ in range(10)]


# Создаем глобальный экземпляр для удобства использования
llm = LLM.instance()
