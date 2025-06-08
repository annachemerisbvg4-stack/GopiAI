"""
Интерфейс для взаимодействия ИИ-агента с браузером.
Обеспечивает эффективную работу ИИ с веб-страницами.
"""

import asyncio
import datetime
from gopiai.core.logging import get_logger
logger = get_logger().logger
from typing import Dict, Optional, Any

from gopiai.app.ui.browser_integrator import get_browser_integrator

logger = get_logger().logger

class BrowserAIInterface:
    """
    Интерфейс для взаимодействия ИИ-агента с браузером.
    """
    
    def __init__(self):
        """Инициализирует интерфейс."""
        try:
            self.browser_integrator = get_browser_integrator()
        except Exception as e:
            logger.warning(f"Не удалось получить browser_integrator: {str(e)}")
            self.browser_integrator = None
        self._last_content = {}
        self._last_analysis = {}
        logger.info("BrowserAIInterface initialized")
    
    async def analyze_page(self, goal: Optional[str] = None) -> Dict[str, Any]:
        """
        Анализирует текущую страницу с помощью улучшенного браузера.
        
        Args:
            goal: Цель анализа
            
        Returns:
            Dict: Результаты анализа
        """
        logger.info(f"Analyzing page with goal: {goal}")
        
        # Создаем будущий объект для получения результатов
        future = asyncio.Future()
        
        # Определяем обработчик сигнала
        def handle_analysis(url, results):
            if not future.done():
                # Сохраняем результаты
                self._last_analysis = {
                    "url": url,
                    "results": results,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                future.set_result(self._last_analysis)
        
        # Подключаем обработчик к сигналу
        self.browser_integrator.browser_analysis_ready.connect(handle_analysis)
        
        # Запускаем анализ
        self.browser_integrator.analyze_current_page(goal)
        
        try:
            # Ожидаем результаты с таймаутом
            result = await asyncio.wait_for(future, timeout=10.0)
            return result
        except asyncio.TimeoutError:
            logger.warning("Timeout waiting for page analysis")
            return {
                "error": "Timeout waiting for page analysis",
                "timestamp": datetime.datetime.now().isoformat()
            }
        finally:
            # Отключаем обработчик
            self.browser_integrator.browser_analysis_ready.disconnect(handle_analysis)
    
    async def extract_content(self, goal: Optional[str] = None) -> Dict[str, Any]:
        """
        Извлекает содержимое текущей страницы.
        
        Args:
            goal: Цель извлечения
            
        Returns:
            Dict: Извлеченное содержимое
        """
        logger.info(f"Extracting content with goal: {goal}")
        
        # Создаем будущий объект для получения результатов
        future = asyncio.Future()
        
        # Определяем обработчик сигнала
        def handle_content(url, title, content_data):
            if not future.done():
                # Сохраняем результаты
                self._last_content = {
                    "url": url,
                    "title": title,
                    "content": content_data,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                future.set_result(self._last_content)
        
        # Подключаем обработчик к сигналу
        self.browser_integrator.browser_content_ready.connect(handle_content)
        
        # Запускаем извлечение содержимого
        self.browser_integrator.extract_content(goal)
        
        try:
            # Ожидаем результаты с таймаутом
            result = await asyncio.wait_for(future, timeout=10.0)
            return result
        except asyncio.TimeoutError:
            logger.warning("Timeout waiting for content extraction")
            return {
                "error": "Timeout waiting for content extraction",
                "timestamp": datetime.datetime.now().isoformat()
            }
        finally:
            # Отключаем обработчик
            self.browser_integrator.browser_content_ready.disconnect(handle_content)
    
    async def predict_actions(self, goal: Optional[str] = None) -> Dict[str, Any]:
        """
        Предсказывает следующие действия пользователя.
        
        Args:
            goal: Цель пользователя
            
        Returns:
            Dict: Предсказанные действия
        """
        logger.info(f"Predicting actions with goal: {goal}")
        
        # Создаем будущий объект для получения результатов
        future = asyncio.Future()
        
        # Определяем обработчик сигнала
        def handle_analysis(url, results):
            if not future.done() and "predictions" in results:
                future.set_result({
                    "url": url,
                    "predictions": results["predictions"],
                    "timestamp": datetime.datetime.now().isoformat()
                })
        
        # Подключаем обработчик к сигналу
        self.browser_integrator.browser_analysis_ready.connect(handle_analysis)
        
        # Запускаем предсказание действий
        self.browser_integrator.predict_actions(goal)
        
        try:
            # Ожидаем результаты с таймаутом
            result = await asyncio.wait_for(future, timeout=10.0)
            return result
        except asyncio.TimeoutError:
            logger.warning("Timeout waiting for action prediction")
            return {
                "error": "Timeout waiting for action prediction",
                "timestamp": datetime.datetime.now().isoformat()
            }
        finally:
            # Отключаем обработчик
            self.browser_integrator.browser_analysis_ready.disconnect(handle_analysis)
    
    def get_last_content(self) -> Dict[str, Any]:
        """
        Возвращает последнее извлеченное содержимое.
        
        Returns:
            Dict: Последнее извлеченное содержимое
        """
        return self._last_content
    
    def get_last_analysis(self) -> Dict[str, Any]:
        """
        Возвращает результаты последнего анализа.
        
        Returns:
            Dict: Результаты последнего анализа
        """
        return self._last_analysis
    
    def clear_cache(self) -> None:
        """Очищает кэш браузера."""
        self.browser_integrator.clear_cache()
        self._last_content = {}
        self._last_analysis = {}
        logger.info("Browser cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику браузера.
        
        Returns:
            Dict: Статистика браузера
        """
        return self.browser_integrator.get_stats()


# Создаем глобальный экземпляр интерфейса
browser_ai = BrowserAIInterface()

def get_browser_ai() -> BrowserAIInterface:
    """
    Возвращает глобальный экземпляр интерфейса ИИ-агента.
    
    Returns:
        BrowserAIInterface: Экземпляр интерфейса
    """
    return browser_ai
