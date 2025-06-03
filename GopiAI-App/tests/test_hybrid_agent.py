#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестирование гибридного браузерного агента.

Простой скрипт для тестирования гибридного браузерного агента.
"""

import asyncio
from gopiai.core.logging import get_logger
logger = get_logger().logger
import sys
import os
import json
from typing import Dict, List, Any, Optional

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = get_logger().logger

# Импортируем адаптер из предыдущего теста
from test_hybrid_adapter import HybridBrowserAdapter

# Создаем простой класс специализированного агента
class SpecializedAgent:
    """Простой специализированный агент для тестирования."""
    
    def __init__(self, name="specialized"):
        """Инициализирует агента."""
        self.name = name
        self.context = {}
        self.actions = []
        self.system_prompt = "Вы специализированный агент."
        logger.info(f"Создан агент {self.name}")
        
    async def set_context(self, context):
        """Устанавливает контекст для агента."""
        self.context = context
        logger.info(f"Установлен контекст для агента {self.name}")
        
    async def process(self, query):
        """Обрабатывает запрос."""
        self.actions.append(f"Processing query: {query[:50]}...")
        logger.info(f"Обработка запроса: {query}")
        return f"Результат обработки запроса: {query}"
        
    def get_current_state(self):
        """Возвращает текущее состояние агента."""
        return {
            "name": self.name,
            "actions": self.actions,
            "context": self.context
        }

# Создаем класс гибридного браузерного агента
class HybridBrowserAgent(SpecializedAgent):
    """Гибридный браузерный агент для тестирования."""
    
    def __init__(self, preferred_tool="auto"):
        """Инициализирует гибридного браузерного агента."""
        super().__init__(name="hybrid_browser")
        self.browser_adapter = HybridBrowserAdapter(preferred_tool=preferred_tool)
        self._update_system_prompt_with_browser_info()
        logger.info(f"Создан гибридный браузерный агент")
        
    def _update_system_prompt_with_browser_info(self):
        """Обновляет системный промпт с информацией о браузере."""
        browser_info = (
            "Вы специализированный браузерный агент. "
            "Вы можете управлять браузером и анализировать веб-страницы."
        )
        
        if self.system_prompt:
            self.system_prompt = f"{self.system_prompt}\n\n{browser_info}"
        else:
            self.system_prompt = browser_info
            
    async def get_browser_state(self):
        """Получает текущее состояние браузера."""
        # Имитация получения состояния браузера
        return {
            "current_url": "https://www.example.com",
            "page_title": "Example Domain"
        }
        
    async def process(self, query):
        """Обрабатывает запрос с использованием браузера."""
        # Инициализируем адаптер, если он еще не инициализирован
        if not self.browser_adapter.initialized:
            await self.browser_adapter.initialize()
            
        # Добавляем действие в историю
        self.actions.append(f"Processing browser query: {query[:50]}...")
        
        # Анализируем запрос для определения необходимых действий
        actions = await self._analyze_query(query)
        
        # Выполняем действия
        results = []
        for action in actions:
            action_type = action.get("type")
            
            # Выполняем действие
            if action_type == "navigate":
                result = await self.browser_adapter.navigate(action.get("url"))
            elif action_type == "extract":
                result = await self.browser_adapter.extract_content(action.get("selector"))
            else:
                result = {
                    "success": False,
                    "message": f"Неизвестное действие: {action_type}",
                    "data": action
                }
                
            results.append(result)
            
        # Формируем ответ
        response = self._format_response(results)
        
        return response
        
    async def _analyze_query(self, query):
        """Анализирует запрос и определяет необходимые действия."""
        # Простой анализ запроса
        actions = []
        
        if "перейти" in query.lower() or "открыть" in query.lower():
            # Извлекаем URL из запроса
            url = "https://www.example.com"
            actions.append({
                "type": "navigate",
                "url": url
            })
            
        if "извлечь" in query.lower() or "получить" in query.lower():
            # Извлекаем содержимое
            actions.append({
                "type": "extract",
                "selector": None
            })
            
        # Если не удалось определить действия, используем запрос как есть
        if not actions:
            actions.append({
                "type": "extract",
                "selector": None
            })
            
        return actions
        
    def _format_response(self, results):
        """Форматирует результаты выполнения действий в ответ."""
        response_parts = []
        
        for result in results:
            if result.get("success"):
                response_parts.append(result.get("message"))
                
                # Добавляем данные результата, если они есть
                data = result.get("data")
                if data:
                    if "content" in data:
                        response_parts.append(f"Содержимое: {data['content']}")
            else:
                response_parts.append(f"Ошибка: {result.get('message')}")
                
        return "\n".join(response_parts)
        
    async def cleanup(self):
        """Очищает ресурсы агента."""
        if self.browser_adapter:
            await self.browser_adapter.close()
            
        logger.info(f"Ресурсы агента {self.name} очищены")

async def main():
    """Основная функция."""
    logger.info("Запуск тестирования гибридного браузерного агента")
    
    # Создаем гибридного браузерного агента
    agent = HybridBrowserAgent(preferred_tool="auto")
    
    # Устанавливаем контекст
    await agent.set_context({
        "task": "Тестирование браузерного агента",
        "relevant_files": {
            "test_hybrid_agent.py": {
                "summary": "Тестирование гибридного браузерного агента"
            }
        }
    })
    
    # Выполняем запрос
    result = await agent.process("Перейти на сайт example.com и извлечь содержимое страницы")
    logger.info(f"Результат запроса: {result}")
    
    # Получаем состояние агента
    state = agent.get_current_state()
    logger.info(f"Состояние агента: {state}")
    
    # Очищаем ресурсы агента
    await agent.cleanup()
    
    logger.info("Тестирование завершено")

if __name__ == "__main__":
    asyncio.run(main())
