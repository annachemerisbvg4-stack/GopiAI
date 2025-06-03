"""
Модуль для интеллектуального предсказания действий пользователя в браузере.
Оптимизирует взаимодействие ИИ с веб-страницами за счет предварительной загрузки и анализа.
"""

import asyncio
from gopiai.core.logging import get_logger
logger = get_logger().logger
from typing import Dict, List, Optional, Any

from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView

from gopiai.widgets.processors.browser_processor import AsyncPagePreProcessor

logger = get_logger().logger

class ActionPredictor:
    """
    Предсказывает следующие действия пользователя для предварительной загрузки веб-страниц.
    """
    
    def __init__(self, browser_widget, preprocessor: AsyncPagePreProcessor):
        """
        Инициализирует предсказатель действий.
        
        Args:
            browser_widget: Виджет браузера для взаимодействия
            preprocessor: Экземпляр AsyncPagePreProcessor для обработки страниц
        """
        self.browser_widget = browser_widget
        self.preprocessor = preprocessor
        self.history = []  # История посещенных URL
        self.preloaded_pages = set()  # Множество предварительно загруженных URL
        self.max_history = 50  # Максимальный размер истории
        self.max_preloaded = 5  # Максимальное количество предварительно загруженных страниц
        
        logger.info("ActionPredictor initialized")
    
    async def predict_next_actions(self, current_url: str, user_goal: Optional[str] = None) -> Dict[str, Any]:
        """
        Предсказывает следующие действия и предварительно загружает страницы.
        
        Args:
            current_url: Текущий URL
            user_goal: Цель пользователя (если известна)
            
        Returns:
            Dict: Результаты предсказания
        """
        logger.info(f"Predicting next actions for {current_url} with goal: {user_goal}")
        
        # Обновляем историю
        self._update_history(current_url)
        
        # Получаем страницу из кэша или обрабатываем её
        page_data = await self.preprocessor.get_page_data(current_url)
        
        if not page_data:
            # Если страницы нет в кэше, запускаем обработку и используем базовую логику
            await self.preprocessor.preprocess_page(current_url, self.browser_widget)
            prediction_results = await self._basic_prediction(current_url, user_goal)
        else:
            # Если страница есть в кэше, используем интеллектуальное предсказание
            prediction_results = await self._intelligent_prediction(current_url, page_data, user_goal)
        
        # Запускаем предварительную загрузку вероятных URL
        for url in prediction_results["likely_urls"]:
            asyncio.create_task(self._preload_page(url))
        
        return prediction_results
    
    async def _basic_prediction(self, current_url: str, user_goal: Optional[str] = None) -> Dict[str, Any]:
        """
        Базовое предсказание на основе URL и истории.
        
        Args:
            current_url: Текущий URL
            user_goal: Цель пользователя
            
        Returns:
            Dict: Результаты предсказания
        """
        likely_urls = []
        
        # 1. Проверяем похожие URL из истории
        for url in self.history:
            if url != current_url and self._are_urls_related(url, current_url):
                if url not in likely_urls:
                    likely_urls.append(url)
        
        # 2. Добавляем стандартные переходы на основе URL
        standard_transitions = self._get_standard_transitions(current_url)
        for url in standard_transitions:
            if url not in likely_urls:
                likely_urls.append(url)
        
        # Ограничиваем количество URL
        likely_urls = likely_urls[:self.max_preloaded]
        
        return {
            "likely_urls": likely_urls,
            "prediction_type": "basic",
            "confidence": 0.5,
            "suggested_actions": self._generate_suggested_actions(current_url, likely_urls, user_goal)
        }
    
    async def _intelligent_prediction(self, current_url: str, page_data: Dict[str, Any], user_goal: Optional[str] = None) -> Dict[str, Any]:
        """
        Интеллектуальное предсказание на основе данных страницы.
        
        Args:
            current_url: Текущий URL
            page_data: Данные о странице
            user_goal: Цель пользователя
            
        Returns:
            Dict: Результаты предсказания
        """
        likely_urls = []
        confidence = 0.7  # Базовый уровень уверенности
        
        # Извлекаем ссылки из данных страницы
        links = page_data.get("links", [])
        
        # Если есть цель пользователя, фильтруем ссылки по релевантности
        if user_goal:
            filtered_links = self._filter_links_by_goal(links, user_goal)
            
            # Если после фильтрации остались ссылки, используем их
            if filtered_links:
                links = filtered_links
                confidence = 0.9  # Повышаем уверенность
        
        # Извлекаем URL из ссылок
        for link in links:
            url = link.get("url", "")
            
            # Проверяем, что URL валидный и не является якорем
            if url and not url.startswith("#") and url not in likely_urls:
                # Нормализуем URL (превращаем относительные URL в абсолютные)
                normalized_url = self._normalize_url(url, current_url)
                if normalized_url and normalized_url not in likely_urls:
                    likely_urls.append(normalized_url)
        
        # Добавляем URL из истории, которые связаны с текущим
        for url in self.history:
            if url != current_url and self._are_urls_related(url, current_url):
                if url not in likely_urls:
                    likely_urls.append(url)
        
        # Ограничиваем количество URL
        likely_urls = likely_urls[:self.max_preloaded]
        
        return {
            "likely_urls": likely_urls,
            "prediction_type": "intelligent",
            "confidence": confidence,
            "suggested_actions": self._generate_suggested_actions(current_url, likely_urls, user_goal)
        }
    
    def _filter_links_by_goal(self, links: List[Dict[str, str]], goal: str) -> List[Dict[str, str]]:
        """
        Фильтрует ссылки по релевантности цели пользователя.
        
        Args:
            links: Список ссылок
            goal: Цель пользователя
            
        Returns:
            List: Отфильтрованные ссылки
        """
        filtered_links = []
        goal_keywords = goal.lower().split()
        
        for link in links:
            text = link.get("text", "").lower()
            title = link.get("title", "").lower()
            url = link.get("url", "").lower()
            
            # Проверяем, содержит ли текст, заголовок или URL ключевые слова из цели
            for keyword in goal_keywords:
                if len(keyword) > 3 and (keyword in text or keyword in title or keyword in url):
                    filtered_links.append(link)
                    break
        
        return filtered_links if filtered_links else links
    
    def _update_history(self, url: str) -> None:
        """
        Обновляет историю посещенных URL.
        
        Args:
            url: Посещенный URL
        """
        # Добавляем URL в историю, если его там нет
        if url not in self.history:
            self.history.append(url)
            
        # Ограничиваем размер истории
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def _are_urls_related(self, url1: str, url2: str) -> bool:
        """
        Проверяет, связаны ли два URL.
        
        Args:
            url1: Первый URL
            url2: Второй URL
            
        Returns:
            bool: True, если URL связаны
        """
        try:
            # Нормализуем URL
            url1 = url1.lower()
            url2 = url2.lower()
            
            # Проверяем, имеют ли URL одинаковый домен
            from urllib.parse import urlparse
            
            domain1 = urlparse(url1).netloc
            domain2 = urlparse(url2).netloc
            
            if not domain1 or not domain2:
                return False
                
            return domain1 == domain2
            
        except Exception as e:
            logger.error(f"Error checking URL relation: {str(e)}")
            return False
    
    def _get_standard_transitions(self, url: str) -> List[str]:
        """
        Возвращает стандартные переходы для URL.
        
        Args:
            url: URL
            
        Returns:
            List: Список вероятных переходов
        """
        try:
            from urllib.parse import urlparse, urljoin
            
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            path = parsed_url.path
            
            standard_transitions = []
            
            # Добавляем главную страницу домена
            if path and path != "/" and domain:
                standard_transitions.append(f"{parsed_url.scheme}://{domain}/")
            
            # Добавляем страницу уровнем выше
            if "/" in path and path.count("/") > 1:
                parent_path = path.rsplit("/", 1)[0]
                if parent_path:
                    standard_transitions.append(
                        f"{parsed_url.scheme}://{domain}{parent_path}/"
                    )
            
            # Добавляем стандартные страницы
            standard_pages = ["about", "contact", "products", "services", "faq", "help"]
            for page in standard_pages:
                standard_transitions.append(
                    f"{parsed_url.scheme}://{domain}/{page}"
                )
            
            return standard_transitions
            
        except Exception as e:
            logger.error(f"Error getting standard transitions: {str(e)}")
            return []
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        """
        Нормализует URL, превращая относительные URL в абсолютные.
        
        Args:
            url: URL для нормализации
            base_url: Базовый URL
            
        Returns:
            str: Нормализованный URL
        """
        try:
            from urllib.parse import urljoin
            
            # Если URL уже абсолютный, возвращаем его
            if url.startswith(("http://", "https://")):
                return url
                
            # Иначе преобразуем относительный URL в абсолютный
            return urljoin(base_url, url)
            
        except Exception as e:
            logger.error(f"Error normalizing URL: {str(e)}")
            return url
    
    async def _preload_page(self, url: str) -> None:
        """
        Предварительно загружает страницу и запускает её анализ.
        
        Args:
            url: URL для предварительной загрузки
        """
        try:
            # Проверяем, не была ли страница уже предварительно загружена
            if url in self.preloaded_pages:
                logger.debug(f"Page {url} already preloaded")
                return
                
            # Добавляем URL в множество предварительно загруженных страниц
            self.preloaded_pages.add(url)
            
            # Ограничиваем количество предварительно загруженных страниц
            if len(self.preloaded_pages) > self.max_preloaded:
                # Удаляем самую старую предварительно загруженную страницу
                self.preloaded_pages.pop()
            
            logger.info(f"Preloading page: {url}")
            
            # Запускаем предварительную обработку страницы
            await self.preprocessor.preprocess_page(url, self.browser_widget)
            
            logger.info(f"Page {url} preloaded successfully")
            
        except Exception as e:
            logger.error(f"Error preloading page {url}: {str(e)}")
    
    def _generate_suggested_actions(self, current_url: str, likely_urls: List[str], user_goal: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Генерирует список рекомендуемых действий.
        
        Args:
            current_url: Текущий URL
            likely_urls: Вероятные URL для перехода
            user_goal: Цель пользователя
            
        Returns:
            List: Список рекомендуемых действий
        """
        actions = []
        
        # Действия для навигации по вероятным URL
        for i, url in enumerate(likely_urls[:3]):  # Рекомендуем только первые 3 URL
            # Создаем человекочитаемое описание URL
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            
            # Получаем последнюю часть пути
            path = parsed_url.path
            path_parts = path.strip("/").split("/")
            page_name = path_parts[-1] if path_parts else "homepage"
            
            # Заменяем дефисы и подчеркивания на пробелы
            page_name = page_name.replace("-", " ").replace("_", " ")
            
            # Если имя страницы пустое, используем домен
            if not page_name:
                page_name = parsed_url.netloc
            
            actions.append({
                "type": "navigate",
                "url": url,
                "description": f"Перейти на страницу '{page_name}'",
                "reason": f"Релевантная страница для цели{f' {user_goal}' if user_goal else ''}"
            })
        
        # Действие для анализа текущей страницы
        actions.append({
            "type": "analyze",
            "url": current_url,
            "description": "Проанализировать текущую страницу",
            "reason": "Извлечь полезную информацию с текущей страницы"
        })
        
        # Действие для поиска на странице
        if user_goal:
            actions.append({
                "type": "search",
                "url": current_url,
                "description": f"Поиск по странице: {user_goal}",
                "reason": "Найти релевантную информацию на текущей странице"
            })
        
        return actions
    
    def clear_preloaded(self) -> None:
        """Очищает список предварительно загруженных страниц."""
        self.preloaded_pages.clear()
    
    def get_prediction_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику предсказаний.
        
        Returns:
            Dict: Статистика предсказаний
        """
        return {
            "history_size": len(self.history),
            "preloaded_pages": len(self.preloaded_pages),
            "max_history": self.max_history,
            "max_preloaded": self.max_preloaded
        }
