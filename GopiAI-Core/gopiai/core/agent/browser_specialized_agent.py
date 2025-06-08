#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль специализированного браузерного агента.

Предоставляет реализацию агента, который объединяет возможности
специализированного агента (ограниченный контекст, руководство от оркестратора)
и браузерного агента (управление браузером, анализ веб-страниц).
"""

import json
from typing import Dict, Optional, Union

from gopiai.app.agent.hybrid_browser_agent import HybridBrowserAgent
from gopiai.app.agent.specialized_agent import SpecializedAgent
from gopiai.core.logging import get_logger
logger = get_logger().logger
from gopiai.app.tool.browser_tools_integration import get_browser_tools
from gopiai.app.tool.hybrid_browser_tools import get_hybrid_browser_tools
from gopiai.app.utils.browser_adapters import get_browser_adapter, HybridBrowserAdapter, BrowserAdapter


class BrowserSpecializedAgent(SpecializedAgent):
    """
    Специализированный агент для работы с браузером.
    
    Объединяет возможности специализированного агента (ограниченный контекст,
    руководство от оркестратора) и браузерного агента (управление браузером,
    анализ веб-страниц). Использует гибридный браузерный адаптер для
    поддержки различных браузерных инструментов (BrowserMCP, Browser-use).
    """
    
    name: str = "browser_specialized"
    description: str = "Специализированный агент для работы с браузером"
    
    # Браузерный агент для делегирования операций
    _browser_agent: Optional[HybridBrowserAgent] = None
    
    # Браузерный адаптер для прямого доступа к браузеру
    _browser_adapter: Optional[Union[BrowserAdapter, HybridBrowserAdapter]] = None
    
    # Предпочтительный инструмент
    preferred_tool: str = "auto"
    
    # Встроенный браузер (если есть)
    browser = None
    
    def __init__(self, preferred_tool="auto", browser=None, **data):
        """
        Инициализирует специализированного браузерного агента.
        
        Args:
            preferred_tool: Предпочтительный инструмент ("mcp", "browser_use" или "auto")
            browser: Экземпляр встроенного браузера (опционально)
            **data: Дополнительные параметры для инициализации
        """
        # Сохраняем параметры
        self.preferred_tool = preferred_tool
        self.browser = browser
        
        super().__init__(**data)
        
        # Создаем браузерный адаптер
        try:
            self._browser_adapter = get_browser_adapter(
                preferred_tool=self.preferred_tool,
                browser=self.browser
            )
        except Exception as e:
            logger.warning(f"Не удалось создать браузерный адаптер: {str(e)}")
            self._browser_adapter = None
        
        # Создаем внутренний браузерный агент
        try:
            self._browser_agent = HybridBrowserAgent(
                preferred_tool=self.preferred_tool,
                browser=self.browser
            )
        except Exception as e:
            logger.warning(f"Не удалось создать гибридный браузерный агент: {str(e)}")
            self._browser_agent = None
        
        # Добавляем инструменты браузера
        browser_tools = get_browser_tools()
        for tool in browser_tools:
            self.add_tool(tool)
            
        # Добавляем гибридные инструменты браузера
        hybrid_tools = get_hybrid_browser_tools()
        for tool in hybrid_tools:
            self.add_tool(tool)
        
        # Добавляем информацию о браузере в системный промпт
        self._update_system_prompt_with_browser_info()
        
        adapter_name = self._browser_adapter.name if self._browser_adapter else "неизвестный адаптер"
        tools_count = len(self.tools.tools) if hasattr(self, 'tools') else 0
        logger.info(f"Инициализирован {self.name} с {tools_count} инструментами и адаптером {adapter_name}")
    
    def _update_system_prompt_with_browser_info(self):
        """Обновляет системный промпт с информацией о браузере."""
        browser_info = (
            "Вы специализированный браузерный агент. "
            "Вы можете управлять браузером и анализировать веб-страницы. "
            "Используйте инструменты браузера для выполнения задач, связанных с веб-страницами.\n\n"
            f"Вы используете гибридный браузерный адаптер с предпочтительным инструментом: {self.preferred_tool}. "
            "Этот адаптер может автоматически переключаться между BrowserMCP и Browser-use "
            "в зависимости от доступности и требований задачи."
        )
        
        if hasattr(self, 'system_prompt') and self.system_prompt:
            self.system_prompt = f"{self.system_prompt}\n\n{browser_info}"
        elif hasattr(self, 'system_prompt'):
            self.system_prompt = browser_info
    
    async def set_context(self, context):
        """
        Устанавливает контекст для агента с учетом браузерной специфики.
        
        Args:
            context: Контекст для агента
        """
        await super().set_context(context)
        
        # Добавляем информацию о браузере в контекст
        browser_state = await self.get_browser_state()
        if browser_state:
            self.context["browser_state"] = browser_state
            
            # Обновляем системный промпт с информацией о текущем состоянии браузера
            if self.system_prompt:
                browser_state_info = f"Текущее состояние браузера: {json.dumps(browser_state, ensure_ascii=False)}"
                
                # Проверяем, есть ли уже информация о состоянии браузера в промпте
                if "Текущее состояние браузера:" not in self.system_prompt:
                    self.system_prompt = f"{self.system_prompt}\n\n{browser_state_info}"
    
    async def get_browser_state(self) -> Optional[Dict]:
        """
        Получает текущее состояние браузера.
        
        Returns:
            Dict: Состояние браузера или None, если информация недоступна
        """
        try:
            # Инициализируем адаптер, если он еще не инициализирован
            if self._browser_adapter and not self._browser_adapter.initialized:
                try:
                    await self._browser_adapter.initialize()
                except Exception as e:
                    logger.warning(f"Не удалось инициализировать браузерный адаптер: {str(e)}")
                
            # Получаем состояние от браузерного агента
            if self._browser_agent:
                try:
                    agent_state = await self._browser_agent.get_browser_state()
                    if agent_state:
                        return agent_state
                except Exception as e:
                    logger.warning(f"Не удалось получить состояние от браузерного агента: {str(e)}")
                    
            # Если не удалось получить состояние от агента, пробуем напрямую через адаптер
            if self._browser_adapter and self._browser_adapter.initialized:
                try:
                    # Получаем текущий URL
                    url_result = await self._browser_adapter.get_current_url()
                    
                    # Получаем заголовок страницы
                    title_result = await self._browser_adapter.get_page_title()
                    
                    # Формируем состояние браузера
                    state = {
                        "current_url": url_result.get("data", {}).get("url", "unknown"),
                        "page_title": title_result.get("data", {}).get("title", "unknown"),
                        "adapter": self._browser_adapter.name if self._browser_adapter else "unknown",
                        "preferred_tool": self.preferred_tool
                    }
                    
                    return state
                except Exception as e:
                    logger.warning(f"Не удалось получить состояние через адаптер: {str(e)}")
            
            # Если не удалось получить состояние, возвращаем заглушку
            return {
                "current_url": "about:blank",
                "page_title": "No page loaded",
                "adapter": "none",
                "preferred_tool": self.preferred_tool,
                "status": "browser_not_available"
            }
        except Exception as e:
            logger.error(f"Ошибка при получении состояния браузера: {str(e)}")
            return {
                "error": str(e),
                "status": "error"
            }
        
    async def update_browser_state(self):
        """Обновляет сохраненное состояние браузера."""
        try:
            # Получаем новое состояние через браузерный агент
            if self._browser_agent:
                await self._browser_agent.get_browser_state()
                
            # Инициализируем адаптер, если он еще не инициализирован
            if self._browser_adapter and not self._browser_adapter.initialized:
                await self._browser_adapter.initialize()
        except Exception as e:
            logger.error(f"Ошибка при обновлении состояния браузера: {str(e)}")
    
    async def process(self, query):
        """
        Обрабатывает запрос с учетом браузерного контекста.
        
        Args:
            query: Запрос для обработки
            
        Returns:
            str: Результат обработки запроса
        """
        try:
            # Инициализируем адаптер, если он еще не инициализирован
            if self._browser_adapter and not self._browser_adapter.initialized:
                await self._browser_adapter.initialize()
                
            # Обновляем состояние браузера перед обработкой
            await self.update_browser_state()
            
            # Добавляем информацию о браузере в контекст
            browser_state = await self.get_browser_state()
            
            # Анализируем запрос для определения, связан ли он с браузером
            is_browser_query = self._is_browser_query(query)
            
            if browser_state:
                browser_context = f"BROWSER STATE: {json.dumps(browser_state, ensure_ascii=False)}"
                
                # Если контекст ограничен или запрос связан с браузером, добавляем информацию о браузере к запросу
                if self.is_limited_context or is_browser_query:
                    # Создаем краткое описание контекста с информацией о браузере
                    context_summary = self._create_context_summary()
                    
                    # Добавляем описание контекста и состояние браузера к запросу
                    enhanced_query = f"CONTEXT: {context_summary}\n\nBROWSER STATE: {json.dumps(browser_state, ensure_ascii=False)}\n\nQUERY: {query}"
                    
                    # Сохраняем действие
                    self.actions.append(f"Processing browser query: {query[:50]}...")
                    
                    # Вызываем стандартную обработку с расширенным запросом
                    return await super().process(enhanced_query)
            
            # Если запрос связан с браузером, но нет состояния браузера, пробуем делегировать его браузерному агенту
            if is_browser_query and self._browser_agent:
                logger.info(f"Делегирование запроса браузерному агенту: {query[:50]}...")
                self.actions.append(f"Delegating to browser agent: {query[:50]}...")
                return await self._browser_agent.process(query)
            
            # Если нет состояния браузера или контекст не ограничен и запрос не связан с браузером, используем стандартную обработку
            return await super().process(query)
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {str(e)}")
            return f"Произошла ошибка при обработке запроса: {str(e)}"
            
    def _is_browser_query(self, query):
        """
        Определяет, связан ли запрос с браузером.
        
        Args:
            query: Запрос для анализа
            
        Returns:
            bool: True, если запрос связан с браузером
        """
        # Ключевые слова, связанные с браузером
        browser_keywords = [
            "браузер", "browser", "сайт", "site", "страница", "page",
            "url", "ссылка", "link", "перейти", "navigate", "открыть", "open",
            "кликнуть", "click", "нажать", "press", "ввести", "type",
            "извлечь", "extract", "скриншот", "screenshot", "скачать", "download"
        ]
        
        # Проверяем наличие ключевых слов в запросе
        query_lower = query.lower()
        for keyword in browser_keywords:
            if keyword in query_lower:
                return True
                
        # Проверяем наличие URL в запросе
        import re
        url_match = re.search(r'https?://[^\s]+', query)
        if url_match:
            return True
            
        return False
    
    async def _handle_tool_call(self, tool_name, tool_args):
        """
        Обрабатывает вызов инструмента.
        
        Args:
            tool_name: Имя инструмента
            tool_args: Аргументы инструмента
            
        Returns:
            Any: Результат вызова инструмента
        """
        try:
            # Сохраняем действие с информацией о браузерном инструменте
            if tool_name.startswith("browser_") or tool_name.startswith("hybrid_browser_"):
                self.actions.append(f"Using browser tool: {tool_name}")
                
                # Если инструмент гибридный, убеждаемся, что адаптер инициализирован
                if tool_name.startswith("hybrid_browser_") and self._browser_adapter and not self._browser_adapter.initialized:
                    await self._browser_adapter.initialize()
            else:
                self.actions.append(f"Using tool: {tool_name}")
            
            # Вызываем стандартную обработку
            result = await super()._handle_tool_call(tool_name, tool_args)
            
            # Обновляем состояние браузера после использования браузерного инструмента
            if tool_name.startswith("browser_") or tool_name.startswith("hybrid_browser_"):
                await self.update_browser_state()
                
            return result
        except Exception as e:
            logger.error(f"Ошибка при вызове инструмента {tool_name}: {str(e)}")
            return f"Ошибка при вызове инструмента {tool_name}: {str(e)}"
    
    def get_current_state(self):
        """
        Возвращает текущее состояние агента.
        
        Returns:
            dict: Текущее состояние агента
        """
        # Получаем базовое состояние от специализированного агента
        state = super().get_current_state()
        
        # Добавляем информацию о браузере
        if self._browser_agent:
            browser_agent_state = self._browser_agent.get_current_state()
            if "browser_state" in browser_agent_state:
                state["browser_state"] = browser_agent_state["browser_state"]
                
        # Добавляем информацию о браузерном адаптере
        if self._browser_adapter:
            state["browser_adapter"] = {
                "name": self._browser_adapter.name,
                "initialized": self._browser_adapter.initialized,
                "preferred_tool": self.preferred_tool
            }
        
        return state
        
    async def cleanup(self):
        """
        Очищает ресурсы агента.
        
        Закрывает браузер и освобождает ресурсы.
        """
        try:
            # Очищаем ресурсы браузерного агента
            if self._browser_agent and hasattr(self._browser_agent, "cleanup"):
                await self._browser_agent.cleanup()
                
            # Закрываем браузерный адаптер
            if self._browser_adapter and self._browser_adapter.initialized:
                await self._browser_adapter.close()
                
            logger.info(f"Ресурсы агента {self.name} очищены")
        except Exception as e:
            logger.error(f"Ошибка при очистке ресурсов агента {self.name}: {str(e)}")
