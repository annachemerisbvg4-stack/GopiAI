#!/usr/bin/env python3
"""
Заглушка для LLM из crewai
Используется для совместимости с кодом, который импортирует LLM из crewai
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class LLM:
    """
    Заглушка для LLM из crewai
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.7, **kwargs):
        """
        Инициализирует заглушку LLM
        
        Args:
            model: Название модели
            temperature: Температура генерации
            **kwargs: Дополнительные параметры
        """
        self.model = model
        self.temperature = temperature
        self.kwargs = kwargs
        logger.warning("WARNING: Using LLM stub instead of crewai.LLM")
    
    def complete(self, prompt: str, **kwargs) -> str:
        """
        Заглушка для метода complete
        
        Args:
            prompt: Промпт для генерации
            **kwargs: Дополнительные параметры
            
        Returns:
            str: Заглушка ответа
        """
        logger.warning("WARNING: Using LLM stub - no actual completion will be generated")
        return "[LLM STUB] This is a stub response. The crewai module is not available."
    
    def generate(self, prompts: List[str], **kwargs) -> List[str]:
        """
        Заглушка для метода generate
        
        Args:
            prompts: Список промптов для генерации
            **kwargs: Дополнительные параметры
            
        Returns:
            List[str]: Список заглушек ответов
        """
        logger.warning("WARNING: Using LLM stub - no actual generation will be performed")
        return ["[LLM STUB] This is a stub response. The crewai module is not available." for _ in prompts]
