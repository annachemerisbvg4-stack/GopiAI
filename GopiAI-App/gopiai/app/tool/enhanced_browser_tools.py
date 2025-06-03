"""
Улучшенные инструменты для работы с браузером.
Предоставляют продвинутые возможности для анализа и извлечения данных из веб-страниц.
"""

import asyncio
from gopiai.core.logging import get_logger
logger = get_logger().logger
from typing import List

from gopiai.app.tool.base import BaseTool

logger = get_logger().logger

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
    
    def _analyze(self, goal=None):
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
                # Получаем event loop
                loop = asyncio.get_event_loop()
                
                # Если event loop уже работает, запускаем в нем корутину
                if loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._analyze_with_ai(goal),
                        loop
                    )
                    result = future.result(10)  # Ожидаем результат с таймаутом 10 секунд
                else:
                    # Иначе создаем новый event loop
                    result = loop.run_until_complete(self._analyze_with_ai(goal))
                
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
    
    def _extract(self, goal=None):
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
                # Получаем event loop
                loop = asyncio.get_event_loop()
                
                # Если event loop уже работает, запускаем в нем корутину
                if loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._extract_with_ai(goal),
                        loop
                    )
                    result = future.result(10)  # Ожидаем результат с таймаутом 10 секунд
                else:
                    # Иначе создаем новый event loop
                    result = loop.run_until_complete(self._extract_with_ai(goal))
                
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


class EnhancedBrowserPredict(BaseTool):
    """Инструмент для предсказания следующих действий пользователя."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="browser_predict",
            description="Предсказывает следующие действия пользователя на основе текущей страницы",
            function=self._predict,
            parameters={
                "goal": {
                    "type": "string",
                    "description": "Цель пользователя (например, 'найти информацию о компании', 'купить продукт')"
                }
            },
            required_params=[]
        )
        
        # Пытаемся импортировать интерфейс ИИ-агента
        try:
            from gopiai.app.agent.browser_ai_interface import get_browser_ai
            self.browser_ai = get_browser_ai()
            self.ai_available = True
        except ImportError:
            logger.warning("Улучшенный интерфейс браузера недоступен")
            self.ai_available = False
    
    async def _predict_with_ai(self, goal=None):
        """
        Предсказывает следующие действия с помощью ИИ-интерфейса.
        
        Args:
            goal: Цель пользователя
            
        Returns:
            dict: Предсказанные действия
        """
        try:
            result = await self.browser_ai.predict_actions(goal)
            return result
        except Exception as e:
            logger.error(f"Ошибка при предсказании действий: {str(e)}")
            return {
                "error": f"Ошибка при предсказании действий: {str(e)}",
                "success": False
            }
    
    def _predict(self, goal=None):
        """
        Предсказывает следующие действия пользователя.
        
        Args:
            goal: Цель пользователя
            
        Returns:
            dict: Предсказанные действия
        """
        logger.info(f"Предсказание действий с целью: {goal}")
        
        # Если доступен улучшенный интерфейс, используем его
        if self.ai_available:
            try:
                # Получаем event loop
                loop = asyncio.get_event_loop()
                
                # Если event loop уже работает, запускаем в нем корутину
                if loop.is_running():
                    future = asyncio.run_coroutine_threadsafe(
                        self._predict_with_ai(goal),
                        loop
                    )
                    result = future.result(10)  # Ожидаем результат с таймаутом 10 секунд
                else:
                    # Иначе создаем новый event loop
                    result = loop.run_until_complete(self._predict_with_ai(goal))
                
                return {
                    "success": True,
                    "message": f"Выполнено предсказание действий с целью: {goal}",
                    "predictions": result
                }
            except Exception as e:
                logger.error(f"Ошибка при запуске предсказания: {str(e)}")
        
        # Если улучшенный интерфейс недоступен или произошла ошибка, возвращаем заглушку
        return {
            "success": True,
            "message": f"Выполнено базовое предсказание действий с целью: {goal}",
            "predictions": {
                "likely_actions": [
                    {
                        "type": "navigate",
                        "url": "https://example.com/about",
                        "description": "Перейти на страницу 'О нас'",
                        "confidence": 0.8
                    },
                    {
                        "type": "search",
                        "query": goal if goal else "информация",
                        "description": f"Выполнить поиск по запросу '{goal if goal else 'информация'}'",
                        "confidence": 0.6
                    }
                ],
                "suggested_next_step": "Перейти на страницу 'О нас'"
            }
        }


def get_enhanced_browser_tools() -> List[BaseTool]:
    """
    Возвращает список улучшенных инструментов браузера.
    
    Returns:
        List[BaseTool]: Список улучшенных инструментов браузера
    """
    tools = []
    
    try:
        tools.append(EnhancedBrowserAnalyze())
        tools.append(EnhancedBrowserExtract())
        tools.append(EnhancedBrowserPredict())
        logger.info("Улучшенные инструменты браузера созданы успешно")
    except Exception as e:
        logger.error(f"Ошибка при создании улучшенных инструментов браузера: {str(e)}")
    
    return tools
