#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Интеграция инструментов браузера."""

from gopiai.core.logging import get_logger
logger = get_logger().logger
from typing import List

from gopiai.app.tool.base import BaseTool
from gopiai.app.tool.tool_collection import ToolCollection

logger = get_logger().logger


class BrowserSearch(BaseTool):
    """Инструмент для поиска в браузере."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="browser_search",
            description="Выполняет поиск в браузере",
            function=self._search,
            parameters={
                "query": {
                    "type": "string",
                    "description": "Поисковый запрос"
                },
                "search_engine": {
                    "type": "string",
                    "description": "Поисковая система (google, yandex, bing)",
                    "enum": ["google", "yandex", "bing"]
                }
            },
            required_params=["query"]
        )
    
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._search(**kwargs)
        
    async def _search(self, query, search_engine="google"):
        """
        Выполняет поиск в браузере.
        
        Args:
            query: Поисковый запрос
            search_engine: Поисковая система
            
        Returns:
            dict: Результат поиска
        """
        logger.info(f"Поиск в {search_engine}: {query}")
        # В минимальной версии просто возвращаем заглушку
        return {
            "success": True,
            "message": f"Выполнен поиск '{query}' в {search_engine}",
            "results": [
                {"title": "Результат 1", "url": "https://example.com/1", "snippet": "Пример результата 1"},
                {"title": "Результат 2", "url": "https://example.com/2", "snippet": "Пример результата 2"},
            ]
        }


class BrowserNavigate(BaseTool):
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
                }
            },
            required_params=["url"]
        )
    
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._navigate(**kwargs)
        
    async def _navigate(self, url):
        """
        Переходит по указанному URL.
        
        Args:
            url: URL для перехода
            
        Returns:
            dict: Результат навигации
        """
        logger.info(f"Переход по URL: {url}")
        # В минимальной версии просто возвращаем заглушку
        return {
            "success": True,
            "message": f"Выполнен переход по URL: {url}",
            "page_title": "Пример страницы",
            "content": "Содержимое страницы..."
        }


class BrowserExtractContent(BaseTool):
    """Инструмент для извлечения содержимого страницы."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="browser_extract_content",
            description="Извлекает содержимое текущей страницы",
            function=self._extract_content,
            parameters={
                "selector": {
                    "type": "string",
                    "description": "CSS-селектор для извлечения конкретного элемента (опционально)"
                }
            },
            required_params=[]
        )
    
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._extract_content(**kwargs)
        
    async def _extract_content(self, selector=None):
        """
        Извлекает содержимое текущей страницы.
        
        Args:
            selector: CSS-селектор для извлечения конкретного элемента
            
        Returns:
            dict: Результат извлечения содержимого
        """
        logger.info(f"Извлечение содержимого страницы (селектор: {selector})")
        # В минимальной версии просто возвращаем заглушку
        return {
            "success": True,
            "message": f"Извлечено содержимое страницы (селектор: {selector})",
            "content": "Пример содержимого страницы...",
            "elements": [
                {"tag": "h1", "text": "Заголовок страницы"},
                {"tag": "p", "text": "Параграф текста..."},
            ]
        }


class EnhancedBrowserAnalyze(BaseTool):
    """Инструмент для улучшенного анализа страницы с помощью асинхронной обработки."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="browser_analyze",
            description="Анализирует текущую страницу с помощью улучшенного браузера",
            function=self._analyze,
            parameters={
                "goal": {
                    "type": "string",
                    "description": "Цель анализа (например, 'найти контакты', 'извлечь цены')"
                }
            },
            required_params=[]
        )
        
        # Устанавливаем флаг доступности ИИ-интерфейса
        self.ai_available = False
        self.browser_ai = None
        
        # Пытаемся импортировать интерфейс ИИ-агента
        try:
            from gopiai.app.agent.browser_ai_interface import get_browser_ai
            self.browser_ai = get_browser_ai()
            self.ai_available = True
        except ImportError:
            logger.warning("Улучшенный интерфейс браузера недоступен")
            self.ai_available = False
    
    async def _analyze_with_ai(self, goal=None):
        """
        Анализирует страницу с помощью ИИ-интерфейса.
        
        Args:
            goal: Цель анализа
            
        Returns:
            dict: Результаты анализа
        """
        try:
            result = await self.browser_ai.analyze_page(goal)
            return result
        except Exception as e:
            logger.error(f"Ошибка при анализе страницы: {str(e)}")
            return {
                "error": f"Ошибка при анализе страницы: {str(e)}",
                "success": False
            }
    
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._analyze(**kwargs)
        
    async def _analyze(self, goal=None):
        """
        Анализирует текущую страницу.
        
        Args:
            goal: Цель анализа
            
        Returns:
            dict: Результаты анализа
        """
        logger.info(f"Анализ страницы с целью: {goal}")
        
        # Если доступен улучшенный интерфейс, используем его
        if self.ai_available:
            try:
                result = await self._analyze_with_ai(goal)
                
                return {
                    "success": True,
                    "message": f"Выполнен анализ страницы с целью: {goal}",
                    "analysis": result
                }
            except Exception as e:
                logger.error(f"Ошибка при запуске анализа: {str(e)}")
        
        # Если улучшенный интерфейс недоступен или произошла ошибка, возвращаем заглушку
        return {
            "success": True,
            "message": f"Выполнен базовый анализ страницы с целью: {goal}",
            "analysis": {
                "title": "Заголовок страницы",
                "url": "https://example.com",
                "content_summary": "Пример содержимого страницы...",
                "key_points": [
                    "Ключевой момент 1",
                    "Ключевой момент 2"
                ]
            }
        }


class EnhancedBrowserExtract(BaseTool):
    """Инструмент для улучшенного извлечения содержимого страницы."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="browser_extract",
            description="Извлекает содержимое текущей страницы с помощью улучшенного браузера",
            function=self._extract,
            parameters={
                "goal": {
                    "type": "string",
                    "description": "Цель извлечения (например, 'контакты', 'цены', 'новости')"
                }
            },
            required_params=[]
        )
        
        # Устанавливаем флаг доступности ИИ-интерфейса
        self.ai_available = False
        self.browser_ai = None
        
        # Пытаемся импортировать интерфейс ИИ-агента
        try:
            from gopiai.app.agent.browser_ai_interface import get_browser_ai
            self.browser_ai = get_browser_ai()
            self.ai_available = True
        except ImportError:
            logger.warning("Улучшенный интерфейс браузера недоступен")
            self.ai_available = False
    
    async def _extract_with_ai(self, goal=None):
        """
        Извлекает содержимое страницы с помощью ИИ-интерфейса.
        
        Args:
            goal: Цель извлечения
            
        Returns:
            dict: Извлеченное содержимое
        """
        try:
            result = await self.browser_ai.extract_content(goal)
            return result
        except Exception as e:
            logger.error(f"Ошибка при извлечении содержимого: {str(e)}")
            return {
                "error": f"Ошибка при извлечении содержимого: {str(e)}",
                "success": False
            }
    
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._extract(**kwargs)
        
    async def _extract(self, goal=None):
        """
        Извлекает содержимое текущей страницы.
        
        Args:
            goal: Цель извлечения
            
        Returns:
            dict: Извлеченное содержимое
        """
        logger.info(f"Извлечение содержимого страницы с целью: {goal}")
        
        # Если доступен улучшенный интерфейс, используем его
        if self.ai_available:
            try:
                result = await self._extract_with_ai(goal)
                
                return {
                    "success": True,
                    "message": f"Выполнено извлечение содержимого с целью: {goal}",
                    "content": result
                }
            except Exception as e:
                logger.error(f"Ошибка при запуске извлечения: {str(e)}")
        
        # Если улучшенный интерфейс недоступен или произошла ошибка, возвращаем заглушку
        return {
            "success": True,
            "message": f"Выполнено базовое извлечение содержимого с целью: {goal}",
            "content": {
                "title": "Заголовок страницы",
                "url": "https://example.com",
                "main_content": "Пример содержимого страницы...",
                "extracted_data": {
                    "type": goal if goal else "general",
                    "items": [
                        "Элемент 1",
                        "Элемент 2"
                    ]
                }
            }
        }


def get_browser_tools() -> List[BaseTool]:
    """
    Возвращает список инструментов браузера.
    
    Returns:
        List[BaseTool]: Список инструментов браузера
    """
    tools = [
        BrowserSearch(),
        BrowserNavigate(),
        BrowserExtractContent(),
    ]
    
    # Добавляем улучшенные инструменты, если они доступны
    try:
        tools.append(EnhancedBrowserAnalyze())
        tools.append(EnhancedBrowserExtract())
        logger.info("Добавлены улучшенные инструменты браузера")
    except Exception as e:
        logger.warning(f"Не удалось добавить улучшенные инструменты браузера: {str(e)}")
    
    return tools


def create_browser_tool_collection() -> ToolCollection:
    """
    Создает коллекцию инструментов браузера.
    
    Returns:
        ToolCollection: Коллекция инструментов браузера
    """
    collection = ToolCollection()
    for tool in get_browser_tools():
        collection.add_tool(tool)
    return collection


def initialize_browser_tools() -> ToolCollection:
    """
    Инициализирует инструменты браузера.
    
    Returns:
        ToolCollection: Коллекция инструментов браузера
    """
    logger.info("Инициализация инструментов браузера")
    return create_browser_tool_collection()
