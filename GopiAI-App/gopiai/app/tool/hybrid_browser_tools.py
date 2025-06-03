#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Инструменты для работы с гибридным браузерным агентом.

Предоставляет набор инструментов для взаимодействия с браузером
через гибридного браузерного агента.
"""

from typing import List

from gopiai.app.agent.orchestrator import get_orchestrator
from gopiai.core.logging import get_logger
logger = get_logger().logger
from gopiai.app.tool.base import BaseTool, ToolResult


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
        
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._navigate(**kwargs)
    
    async def _navigate(self, url, preferred_tool="auto"):
        """
        Переходит по указанному URL.
        
        Args:
            url: URL для перехода
            preferred_tool: Предпочтительный инструмент
            
        Returns:
            ToolResult: Результат навигации
        """
        try:
            # Получаем оркестратор
            orchestrator = get_orchestrator()
            
            # Создаем или получаем браузерного агента
            agent_id = "browser_navigator"
            agent = orchestrator.specialized_agents.get(agent_id)
            
            if not agent:
                agent = await orchestrator.create_hybrid_browser_agent(
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


class BrowserClickTool(BaseTool):
    """Инструмент для клика по элементу в браузере."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="browser_click",
            description="Кликает по элементу с указанным селектором",
            function=self._click,
            parameters={
                "selector": {
                    "type": "string",
                    "description": "CSS-селектор элемента"
                },
                "preferred_tool": {
                    "type": "string",
                    "description": "Предпочтительный инструмент (mcp, browser_use или auto)",
                    "enum": ["mcp", "browser_use", "auto"]
                }
            },
            required_params=["selector"]
        )
        
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._click(**kwargs)
    
    async def _click(self, selector, preferred_tool="auto"):
        """
        Кликает по элементу с указанным селектором.
        
        Args:
            selector: CSS-селектор элемента
            preferred_tool: Предпочтительный инструмент
            
        Returns:
            ToolResult: Результат клика
        """
        try:
            # Получаем оркестратор
            orchestrator = get_orchestrator()
            
            # Создаем или получаем браузерного агента
            agent_id = "browser_clicker"
            agent = orchestrator.specialized_agents.get(agent_id)
            
            if not agent:
                agent = await orchestrator.create_hybrid_browser_agent(
                    agent_id=agent_id,
                    task_description=f"Клик по элементам на странице",
                    preferred_tool=preferred_tool
                )
                
            # Выполняем клик
            result = await agent.process(f"Кликнуть по элементу с селектором: {selector}")
            
            return ToolResult(
                success=True,
                message=f"Успешно выполнен клик по элементу: {selector}",
                data={"result": result}
            )
        except Exception as e:
            logger.error(f"Ошибка при клике по элементу: {str(e)}")
            return ToolResult(
                success=False,
                message=f"Ошибка при клике по элементу: {str(e)}",
                data={"error": str(e)}
            )


class BrowserTypeTool(BaseTool):
    """Инструмент для ввода текста в элемент в браузере."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="browser_type",
            description="Вводит текст в элемент с указанным селектором",
            function=self._type,
            parameters={
                "selector": {
                    "type": "string",
                    "description": "CSS-селектор элемента"
                },
                "text": {
                    "type": "string",
                    "description": "Текст для ввода"
                },
                "preferred_tool": {
                    "type": "string",
                    "description": "Предпочтительный инструмент (mcp, browser_use или auto)",
                    "enum": ["mcp", "browser_use", "auto"]
                }
            },
            required_params=["selector", "text"]
        )
        
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._type(**kwargs)
    
    async def _type(self, selector, text, preferred_tool="auto"):
        """
        Вводит текст в элемент с указанным селектором.
        
        Args:
            selector: CSS-селектор элемента
            text: Текст для ввода
            preferred_tool: Предпочтительный инструмент
            
        Returns:
            ToolResult: Результат ввода текста
        """
        try:
            # Получаем оркестратор
            orchestrator = get_orchestrator()
            
            # Создаем или получаем браузерного агента
            agent_id = "browser_typer"
            agent = orchestrator.specialized_agents.get(agent_id)
            
            if not agent:
                agent = await orchestrator.create_hybrid_browser_agent(
                    agent_id=agent_id,
                    task_description=f"Ввод текста в элементы на странице",
                    preferred_tool=preferred_tool
                )
                
            # Выполняем ввод текста
            result = await agent.process(f"Ввести текст '{text}' в элемент с селектором: {selector}")
            
            return ToolResult(
                success=True,
                message=f"Успешно введен текст в элемент: {selector}",
                data={"result": result}
            )
        except Exception as e:
            logger.error(f"Ошибка при вводе текста: {str(e)}")
            return ToolResult(
                success=False,
                message=f"Ошибка при вводе текста: {str(e)}",
                data={"error": str(e)}
            )


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
        
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._extract(**kwargs)
    
    async def _extract(self, selector=None, preferred_tool="auto"):
        """
        Извлекает содержимое страницы или элемента.
        
        Args:
            selector: CSS-селектор элемента (опционально)
            preferred_tool: Предпочтительный инструмент
            
        Returns:
            ToolResult: Результат извлечения содержимого
        """
        try:
            # Получаем оркестратор
            orchestrator = get_orchestrator()
            
            # Создаем или получаем браузерного агента
            agent_id = "browser_extractor"
            agent = orchestrator.specialized_agents.get(agent_id)
            
            if not agent:
                agent = await orchestrator.create_hybrid_browser_agent(
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


class BrowserJavaScriptTool(BaseTool):
    """Инструмент для выполнения JavaScript-кода в браузере."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="browser_javascript",
            description="Выполняет JavaScript-код в браузере",
            function=self._execute_javascript,
            parameters={
                "code": {
                    "type": "string",
                    "description": "JavaScript-код для выполнения"
                },
                "preferred_tool": {
                    "type": "string",
                    "description": "Предпочтительный инструмент (mcp, browser_use или auto)",
                    "enum": ["mcp", "browser_use", "auto"]
                }
            },
            required_params=["code"]
        )
        
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._execute_javascript(**kwargs)
    
    async def _execute_javascript(self, code, preferred_tool="auto"):
        """
        Выполняет JavaScript-код в браузере.
        
        Args:
            code: JavaScript-код для выполнения
            preferred_tool: Предпочтительный инструмент
            
        Returns:
            ToolResult: Результат выполнения JavaScript-кода
        """
        try:
            # Получаем оркестратор
            orchestrator = get_orchestrator()
            
            # Создаем или получаем браузерного агента
            agent_id = "browser_javascript"
            agent = orchestrator.specialized_agents.get(agent_id)
            
            if not agent:
                agent = await orchestrator.create_hybrid_browser_agent(
                    agent_id=agent_id,
                    task_description=f"Выполнение JavaScript-кода в браузере",
                    preferred_tool=preferred_tool
                )
                
            # Выполняем JavaScript-код
            result = await agent.process(f"Выполнить JavaScript-код: {code}")
            
            return ToolResult(
                success=True,
                message=f"Успешно выполнен JavaScript-код",
                data={"result": result}
            )
        except Exception as e:
            logger.error(f"Ошибка при выполнении JavaScript-кода: {str(e)}")
            return ToolResult(
                success=False,
                message=f"Ошибка при выполнении JavaScript-кода: {str(e)}",
                data={"error": str(e)}
            )


class BrowserScreenshotTool(BaseTool):
    """Инструмент для создания скриншота страницы или элемента."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="browser_screenshot",
            description="Создает скриншот страницы или элемента",
            function=self._screenshot,
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
        
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._screenshot(**kwargs)
    
    async def _screenshot(self, selector=None, preferred_tool="auto"):
        """
        Создает скриншот страницы или элемента.
        
        Args:
            selector: CSS-селектор элемента (опционально)
            preferred_tool: Предпочтительный инструмент
            
        Returns:
            ToolResult: Результат создания скриншота
        """
        try:
            # Получаем оркестратор
            orchestrator = get_orchestrator()
            
            # Создаем или получаем браузерного агента
            agent_id = "browser_screenshot"
            agent = orchestrator.specialized_agents.get(agent_id)
            
            if not agent:
                agent = await orchestrator.create_hybrid_browser_agent(
                    agent_id=agent_id,
                    task_description=f"Создание скриншотов страницы или элементов",
                    preferred_tool=preferred_tool
                )
                
            # Выполняем создание скриншота
            if selector:
                result = await agent.process(f"Сделать скриншот элемента с селектором: {selector}")
            else:
                result = await agent.process("Сделать скриншот текущей страницы")
            
            return ToolResult(
                success=True,
                message=f"Успешно создан скриншот" + (f" элемента: {selector}" if selector else " страницы"),
                data={"result": result}
            )
        except Exception as e:
            logger.error(f"Ошибка при создании скриншота: {str(e)}")
            return ToolResult(
                success=False,
                message=f"Ошибка при создании скриншота: {str(e)}",
                data={"error": str(e)}
            )


class BrowserExternalAITool(BaseTool):
    """Инструмент для взаимодействия с внешними ИИ-сервисами через браузер."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="browser_external_ai",
            description="Взаимодействует с внешними ИИ-сервисами через браузер",
            function=self._use_external_ai,
            parameters={
                "service": {
                    "type": "string",
                    "description": "Название сервиса (chatgpt, claude, midjourney, leonardo, etc.)"
                },
                "prompt": {
                    "type": "string",
                    "description": "Промпт для ИИ-сервиса"
                },
                "preferred_tool": {
                    "type": "string",
                    "description": "Предпочтительный инструмент (mcp, browser_use или auto)",
                    "enum": ["mcp", "browser_use", "auto"]
                }
            },
            required_params=["service", "prompt"]
        )
        
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._use_external_ai(**kwargs)
    
    async def _use_external_ai(self, service, prompt, preferred_tool="auto"):
        """
        Взаимодействует с внешними ИИ-сервисами через браузер.
        
        Args:
            service: Название сервиса
            prompt: Промпт для ИИ-сервиса
            preferred_tool: Предпочтительный инструмент
            
        Returns:
            ToolResult: Результат взаимодействия с ИИ-сервисом
        """
        try:
            # Получаем оркестратор
            orchestrator = get_orchestrator()
            
            # Создаем или получаем браузерного агента
            agent_id = f"browser_external_ai_{service}"
            agent = orchestrator.specialized_agents.get(agent_id)
            
            if not agent:
                agent = await orchestrator.create_hybrid_browser_agent(
                    agent_id=agent_id,
                    task_description=f"Взаимодействие с внешним ИИ-сервисом {service}",
                    preferred_tool=preferred_tool
                )
                
            # Формируем задачу для агента
            task = f"Использовать сервис {service} с промптом: '{prompt}'. Перейти на сайт сервиса, ввести промпт, получить результат и вернуть его."
            
            # Выполняем задачу
            result = await agent.process(task)
            
            return ToolResult(
                success=True,
                message=f"Успешно получен результат от сервиса {service}",
                data={"result": result, "service": service, "prompt": prompt}
            )
        except Exception as e:
            logger.error(f"Ошибка при взаимодействии с сервисом {service}: {str(e)}")
            return ToolResult(
                success=False,
                message=f"Ошибка при взаимодействии с сервисом {service}: {str(e)}",
                data={"error": str(e), "service": service, "prompt": prompt}
            )


def get_hybrid_browser_tools() -> List[BaseTool]:
    """
    Возвращает список инструментов для работы с гибридным браузерным агентом.
    
    Returns:
        List[BaseTool]: Список инструментов
    """
    return [
        BrowserNavigateTool(),
        BrowserClickTool(),
        BrowserTypeTool(),
        BrowserExtractTool(),
        BrowserJavaScriptTool(),
        BrowserScreenshotTool(),
        BrowserExternalAITool()
    ]
