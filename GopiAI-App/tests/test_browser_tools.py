#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестирование инструментов для работы с браузером.

Простой скрипт для тестирования инструментов для работы с браузером.
"""

import asyncio
from gopiai.core.logging import get_logger
logger = get_logger().logger
import sys
import os
from typing import Dict, List, Any, Optional

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = get_logger().logger

# Импортируем адаптер из предыдущего теста
from test_hybrid_adapter import HybridBrowserAdapter

# Создаем простой класс результата инструмента
class ToolResult:
    """Результат выполнения инструмента."""
    
    def __init__(self, success=True, message="", data=None):
        """Инициализирует результат."""
        self.success = success
        self.message = message
        self.data = data or {}
        
    def __str__(self):
        """Возвращает строковое представление результата."""
        return f"ToolResult(success={self.success}, message={self.message}, data={self.data})"

# Создаем простой класс базового инструмента
class BaseTool:
    """Базовый класс инструмента."""
    
    def __init__(self, name, description, function, parameters=None, required_params=None):
        """Инициализирует инструмент."""
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters or {}
        self.required_params = required_params or []
        
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        # Проверяем наличие обязательных параметров
        for param in self.required_params:
            if param not in kwargs:
                return ToolResult(
                    success=False,
                    message=f"Отсутствует обязательный параметр: {param}",
                    data={"missing_param": param}
                )
                
        # Выполняем функцию инструмента
        try:
            return await self.function(**kwargs)
        except Exception as e:
            logger.error(f"Ошибка при выполнении инструмента {self.name}: {str(e)}")
            return ToolResult(
                success=False,
                message=f"Ошибка при выполнении инструмента: {str(e)}",
                data={"error": str(e)}
            )

# Создаем класс оркестратора
class Orchestrator:
    """Простой оркестратор для тестирования."""
    
    def __init__(self):
        """Инициализирует оркестратор."""
        self.specialized_agents = {}
        
    async def create_hybrid_browser_agent(self, agent_id, task_description, preferred_tool="auto"):
        """Создает гибридного браузерного агента."""
        # Импортируем агента из предыдущего теста
        from test_hybrid_agent import HybridBrowserAgent
        
        # Создаем агента
        agent = HybridBrowserAgent(preferred_tool=preferred_tool)
        
        # Устанавливаем контекст
        await agent.set_context({
            "task": task_description,
            "relevant_files": {}
        })
        
        # Сохраняем агента
        self.specialized_agents[agent_id] = agent
        
        return agent

# Создаем инструмент для навигации в браузере
class BrowserNavigateTool(BaseTool):
    """Инструмент для навигации в браузере."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="browser_navigate",
            description="Переходит по указанному URL",
            function=self._navigate,
            parameters={
                "url": {
                    "type": "string",
                    "description": "URL для перехода"
                },
                "preferred_tool": {
                    "type": "string",
                    "description": "Предпочтительный инструмент (mcp, browser_use или auto)",
                    "enum": ["mcp", "browser_use", "auto"]
                }
            },
            required_params=["url"]
        )
        
        # Создаем оркестратор
        self.orchestrator = Orchestrator()
    
    async def _navigate(self, url, preferred_tool="auto"):
        """Переходит по указанному URL."""
        try:
            # Создаем или получаем браузерного агента
            agent_id = "browser_navigator"
            agent = self.orchestrator.specialized_agents.get(agent_id)
            
            if not agent:
                agent = await self.orchestrator.create_hybrid_browser_agent(
                    agent_id=agent_id,
                    task_description=f"Навигация по URL: {url}",
                    preferred_tool=preferred_tool
                )
                
            # Выполняем навигацию
            result = await agent.process(f"Перейти по URL: {url}")
            
            return ToolResult(
                success=True,
                message=f"Успешно выполнена навигация по URL: {url}",
                data={"result": result}
            )
        except Exception as e:
            logger.error(f"Ошибка при навигации по URL: {str(e)}")
            return ToolResult(
                success=False,
                message=f"Ошибка при навигации по URL: {str(e)}",
                data={"error": str(e)}
            )

# Создаем инструмент для извлечения содержимого
class BrowserExtractTool(BaseTool):
    """Инструмент для извлечения содержимого страницы или элемента."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="browser_extract",
            description="Извлекает содержимое страницы или элемента",
            function=self._extract,
            parameters={
                "selector": {
                    "type": "string",
                    "description": "CSS-селектор элемента (опционально)"
                },
                "preferred_tool": {
                    "type": "string",
                    "description": "Предпочтительный инструмент (mcp, browser_use или auto)",
                    "enum": ["mcp", "browser_use", "auto"]
                }
            },
            required_params=[]
        )
        
        # Создаем оркестратор
        self.orchestrator = Orchestrator()
    
    async def _extract(self, selector=None, preferred_tool="auto"):
        """Извлекает содержимое страницы или элемента."""
        try:
            # Создаем или получаем браузерного агента
            agent_id = "browser_extractor"
            agent = self.orchestrator.specialized_agents.get(agent_id)
            
            if not agent:
                agent = await self.orchestrator.create_hybrid_browser_agent(
                    agent_id=agent_id,
                    task_description=f"Извлечение содержимого страницы или элементов",
                    preferred_tool=preferred_tool
                )
                
            # Выполняем извлечение содержимого
            if selector:
                result = await agent.process(f"Извлечь содержимое элемента с селектором: {selector}")
            else:
                result = await agent.process("Извлечь содержимое текущей страницы")
            
            return ToolResult(
                success=True,
                message=f"Успешно извлечено содержимое" + (f" элемента: {selector}" if selector else " страницы"),
                data={"result": result}
            )
        except Exception as e:
            logger.error(f"Ошибка при извлечении содержимого: {str(e)}")
            return ToolResult(
                success=False,
                message=f"Ошибка при извлечении содержимого: {str(e)}",
                data={"error": str(e)}
            )

# Функция для получения инструментов
def get_browser_tools():
    """Возвращает список инструментов для работы с браузером."""
    return [
        BrowserNavigateTool(),
        BrowserExtractTool()
    ]

async def main():
    """Основная функция."""
    logger.info("Запуск тестирования инструментов для работы с браузером")
    
    # Получаем инструменты
    tools = get_browser_tools()
    
    # Тестируем инструмент навигации
    navigate_tool = tools[0]
    result = await navigate_tool.execute(url="https://www.example.com")
    logger.info(f"Результат навигации: {result}")
    
    # Тестируем инструмент извлечения содержимого
    extract_tool = tools[1]
    result = await extract_tool.execute()
    logger.info(f"Результат извлечения содержимого: {result}")
    
    logger.info("Тестирование завершено")

if __name__ == "__main__":
    asyncio.run(main())
