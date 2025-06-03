"""
Модуль для асинхронной обработки и оптимизации браузерного контента.
Повышает скорость и эффективность взаимодействия ИИ с веб-страницами.
"""

import asyncio
import datetime
from gopiai.core.logging import get_logger
logger = get_logger().logger
from typing import Dict, List, Optional, Any

from PySide6.QtCore import QUrl, Signal, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView

logger = get_logger().logger

class AsyncPagePreProcessor:
    """
    Асинхронно обрабатывает страницы в фоновом режиме для повышения 
    скорости взаимодействия ИИ с браузером.
    """
    
    def __init__(self, max_cache_size=50):
        """
        Инициализирует обработчик страниц.
        
        Args:
            max_cache_size: Максимальный размер кэша обработанных страниц
        """
        self.page_cache = {}  # Кэш обработанных страниц
        self.processing_tasks = {}  # Задачи обработки
        self.max_cache_size = max_cache_size
        self.lock = asyncio.Lock()
        logger.info(f"AsyncPagePreProcessor initialized with max_cache_size={max_cache_size}")
        
    async def preprocess_page(self, url: str, browser_view: QWebEngineView) -> None:
        """
        Запускает предварительную обработку страницы.
        
        Args:
            url: URL страницы для обработки
            browser_view: Экземпляр браузера для взаимодействия со страницей
        """
        async with self.lock:
            # Проверяем, не обрабатывается ли уже страница
            if url in self.page_cache:
                # Если в кэше, обновляем timestamp
                self.page_cache[url]["timestamp"] = datetime.datetime.now()
                logger.debug(f"Page {url} already in cache, updated timestamp")
                return
                
            if url in self.processing_tasks:
                logger.debug(f"Page {url} is already being processed")
                return
                
            # Запускаем задачу обработки
            logger.info(f"Starting preprocessing for {url}")
            self.processing_tasks[url] = asyncio.create_task(
                self._process_page(url, browser_view)
            )
               
    async def _process_page(self, url: str, browser_view: QWebEngineView) -> None:
        """
        Обрабатывает страницу и сохраняет результаты.
        
        Args:
            url: URL страницы
            browser_view: Экземпляр браузера
        """
        try:
            logger.info(f"Processing page: {url}")
            
            # Получаем содержимое страницы
            page_content = await self._extract_page_content(browser_view)
            
            if not page_content:
                logger.warning(f"Failed to extract content from {url}")
                return
                
            # Запускаем параллельные задачи анализа
            content_task = asyncio.create_task(self._analyze_content(page_content))
            links_task = asyncio.create_task(self._extract_links(page_content))
            structure_task = asyncio.create_task(self._analyze_structure(page_content))
            
            # Ожидаем завершения всех задач
            content_analysis = await content_task
            links = await links_task
            structure = await structure_task
            
            # Сохраняем результаты в кэш
            async with self.lock:
                self.page_cache[url] = {
                    "content_analysis": content_analysis,
                    "links": links,
                    "structure": structure,
                    "raw_content": page_content[:50000],  # Сохраняем часть контента
                    "timestamp": datetime.datetime.now()
                }
                
                # Ограничиваем размер кэша
                await self._trim_cache()
                
            logger.info(f"Page {url} processed and cached successfully")
            
        except Exception as e:
            logger.error(f"Error processing page {url}: {str(e)}")
        finally:
            # Удаляем задачу из списка активных
            async with self.lock:
                if url in self.processing_tasks:
                    del self.processing_tasks[url]
    
    async def _extract_page_content(self, browser_view: QWebEngineView) -> str:
        """
        Извлекает содержимое страницы из браузера.
        
        Args:
            browser_view: Экземпляр браузера
            
        Returns:
            str: HTML-содержимое страницы
        """
        try:
            # Создаем future для получения HTML
            future = asyncio.Future()
            
            def callback(html):
                if not future.done():
                    future.set_result(html)
            
            # Запрашиваем HTML страницы
            browser_view.page().toHtml(callback)
            
            # Ожидаем результат с таймаутом
            try:
                html = await asyncio.wait_for(future, timeout=5.0)
                return html
            except asyncio.TimeoutError:
                logger.error("Timeout extracting page content")
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting page content: {str(e)}")
            return ""
    
    async def _analyze_content(self, html_content: str) -> Dict[str, Any]:
        """
        Анализирует содержимое страницы и извлекает ключевую информацию.
        
        Args:
            html_content: HTML-содержимое страницы
            
        Returns:
            Dict: Результаты анализа
        """
        try:
            # Используем BeautifulSoup для анализа HTML
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Извлекаем заголовок
            title = soup.title.string if soup.title else "No title"
            
            # Извлекаем метаданные
            meta_tags = {}
            for meta in soup.find_all('meta'):
                if meta.get('name'):
                    meta_tags[meta.get('name')] = meta.get('content')
                elif meta.get('property'):
                    meta_tags[meta.get('property')] = meta.get('content')
            
            # Извлекаем основной текст
            main_content = ""
            content_elements = soup.select('main, article, .content, #content')
            if content_elements:
                main_content = content_elements[0].get_text(strip=True)
            else:
                # Если не нашли основные контейнеры, берем текст из body
                main_content = soup.body.get_text(strip=True) if soup.body else ""
            
            # Извлекаем заголовки для структуры
            headings = []
            for i in range(1, 7):
                for heading in soup.find_all(f'h{i}'):
                    headings.append({
                        'level': i,
                        'text': heading.get_text(strip=True)
                    })
            
            return {
                'title': title,
                'meta': meta_tags,
                'main_content': main_content[:5000],  # Ограничиваем размер
                'headings': headings
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            return {
                'title': "Error analyzing content",
                'error': str(e)
            }
    
    async def _extract_links(self, html_content: str) -> List[Dict[str, str]]:
        """
        Извлекает ссылки из страницы.
        
        Args:
            html_content: HTML-содержимое страницы
            
        Returns:
            List: Список словарей с информацией о ссылках
        """
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            
            for a in soup.find_all('a', href=True):
                link_text = a.get_text(strip=True)
                link_href = a['href']
                
                # Фильтруем пустые и якорные ссылки
                if link_href and not link_href.startswith('#'):
                    links.append({
                        'text': link_text if link_text else "No text",
                        'url': link_href,
                        'title': a.get('title', "")
                    })
            
            return links
            
        except Exception as e:
            logger.error(f"Error extracting links: {str(e)}")
            return []
    
    async def _analyze_structure(self, html_content: str) -> Dict[str, Any]:
        """
        Анализирует структуру страницы.
        
        Args:
            html_content: HTML-содержимое страницы
            
        Returns:
            Dict: Информация о структуре страницы
        """
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Анализируем навигацию
            navigation = []
            nav_elements = soup.select('nav, .navigation, .menu, .nav')
            for nav in nav_elements:
                nav_items = []
                for a in nav.find_all('a', href=True):
                    nav_items.append({
                        'text': a.get_text(strip=True),
                        'url': a['href']
                    })
                if nav_items:
                    navigation.append(nav_items)
            
            # Анализируем формы
            forms = []
            for form in soup.find_all('form'):
                form_info = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get'),
                    'inputs': []
                }
                
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    input_info = {
                        'type': input_tag.name,
                        'name': input_tag.get('name', ''),
                        'id': input_tag.get('id', '')
                    }
                    
                    if input_tag.name == 'input':
                        input_info['input_type'] = input_tag.get('type', 'text')
                    
                    form_info['inputs'].append(input_info)
                
                forms.append(form_info)
            
            # Анализируем разделы страницы
            sections = []
            for section in soup.select('section, div.section, .container'):
                section_id = section.get('id', '')
                section_class = section.get('class', [])
                heading = section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                
                sections.append({
                    'id': section_id,
                    'class': ' '.join(section_class) if isinstance(section_class, list) else section_class,
                    'heading': heading.get_text(strip=True) if heading else 'No heading'
                })
            
            return {
                'navigation': navigation,
                'forms': forms,
                'sections': sections
            }
            
        except Exception as e:
            logger.error(f"Error analyzing structure: {str(e)}")
            return {
                'error': str(e)
            }
    
    async def _trim_cache(self) -> None:
        """
        Ограничивает размер кэша, удаляя самые старые записи.
        """
        if len(self.page_cache) <= self.max_cache_size:
            return
            
        # Сортируем по времени последнего доступа
        sorted_cache = sorted(
            self.page_cache.items(),
            key=lambda x: x[1]["timestamp"]
        )
        
        # Удаляем старые записи
        to_remove = len(self.page_cache) - self.max_cache_size
        for i in range(to_remove):
            url, _ = sorted_cache[i]
            del self.page_cache[url]
            logger.debug(f"Removed {url} from cache (cache trimming)")
    
    async def get_page_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Получает данные страницы из кэша.
        
        Args:
            url: URL страницы
            
        Returns:
            Dict: Данные страницы или None, если страница не в кэше
        """
        async with self.lock:
            if url in self.page_cache:
                # Обновляем timestamp для LRU
                self.page_cache[url]["timestamp"] = datetime.datetime.now()
                return self.page_cache[url]
        return None
    
    async def clear_cache(self) -> None:
        """Очищает кэш страниц."""
        async with self.lock:
            self.page_cache.clear()
            logger.info("Page cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику кэша.
        
        Returns:
            Dict: Статистика кэша
        """
        return {
            "cache_size": len(self.page_cache),
            "max_cache_size": self.max_cache_size,
            "active_tasks": len(self.processing_tasks),
            "cached_urls": list(self.page_cache.keys())
        }


class ContentOptimizer:
    """
    Оптимизирует обработку веб-контента для ИИ.
    """
    
    def __init__(self):
        """Инициализирует оптимизатор контента."""
        self.logger = get_logger().logger
    
    async def optimize_content(self, html_content: str, goal: Optional[str] = None) -> Dict[str, Any]:
        """
        Оптимизирует HTML-контент для эффективной обработки.
        
        Args:
            html_content: HTML-содержимое страницы
            goal: Цель обработки (например, "extract_prices", "find_contacts")
            
        Returns:
            Dict: Оптимизированный контент с разными уровнями приоритета
        """
        # Разбиваем страницу на смысловые блоки
        blocks = self._split_into_blocks(html_content)
        
        # Расставляем приоритеты блокам в зависимости от цели
        prioritized_blocks = await self._prioritize_blocks(blocks, goal)
        
        # Возвращаем оптимизированный контент
        return {
            "high_priority": prioritized_blocks["high"],
            "medium_priority": prioritized_blocks["medium"],
            "low_priority": prioritized_blocks["low"]
        }
    
    def _split_into_blocks(self, html_content: str) -> List[Dict[str, str]]:
        """
        Разбивает HTML на смысловые блоки.
        
        Args:
            html_content: HTML-содержимое
            
        Returns:
            List: Список блоков контента
        """
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            blocks = []
            
            # Приоритетные элементы (основной контент)
            for element in soup.select('main, article, .content, #content'):
                blocks.append({
                    "type": element.name,
                    "content": element.get_text(strip=True),
                    "html": str(element),
                    "attributes": {
                        "id": element.get("id", ""),
                        "class": " ".join(element.get("class", [])),
                    }
                })
            
            # Заголовки страницы
            for element in soup.select('h1, h2, h3'):
                blocks.append({
                    "type": element.name,
                    "content": element.get_text(strip=True),
                    "html": str(element),
                    "attributes": {
                        "id": element.get("id", ""),
                        "class": " ".join(element.get("class", [])),
                    }
                })
            
            # Навигационные элементы
            for element in soup.select('nav, .navigation, .menu'):
                blocks.append({
                    "type": element.name,
                    "content": element.get_text(strip=True),
                    "html": str(element),
                    "attributes": {
                        "id": element.get("id", ""),
                        "class": " ".join(element.get("class", [])),
                    }
                })
            
            # Параграфы текста
            for element in soup.select('p'):
                # Пропускаем пустые параграфы
                text = element.get_text(strip=True)
                if text and len(text) > 10:  # Минимальная длина для значимого параграфа
                    blocks.append({
                        "type": element.name,
                        "content": text,
                        "html": str(element),
                        "attributes": {
                            "id": element.get("id", ""),
                            "class": " ".join(element.get("class", [])),
                        }
                    })
            
            # Списки
            for element in soup.select('ul, ol'):
                blocks.append({
                    "type": element.name,
                    "content": element.get_text(strip=True),
                    "html": str(element),
                    "attributes": {
                        "id": element.get("id", ""),
                        "class": " ".join(element.get("class", [])),
                    }
                })
            
            # Таблицы
            for element in soup.select('table'):
                blocks.append({
                    "type": element.name,
                    "content": element.get_text(strip=True),
                    "html": str(element),
                    "attributes": {
                        "id": element.get("id", ""),
                        "class": " ".join(element.get("class", [])),
                    }
                })
            
            # Формы и кнопки
            for element in soup.select('form, button'):
                blocks.append({
                    "type": element.name,
                    "content": element.get_text(strip=True),
                    "html": str(element),
                    "attributes": {
                        "id": element.get("id", ""),
                        "class": " ".join(element.get("class", [])),
                        "action": element.get("action", "") if element.name == "form" else "",
                        "method": element.get("method", "") if element.name == "form" else "",
                    }
                })
            
            # Если блоков не нашлось, добавляем весь body
            if not blocks and soup.body:
                blocks.append({
                    "type": "body",
                    "content": soup.body.get_text(strip=True),
                    "html": str(soup.body),
                    "attributes": {
                        "id": soup.body.get("id", ""),
                        "class": " ".join(soup.body.get("class", [])),
                    }
                })
            
            return blocks
            
        except Exception as e:
            self.logger.error(f"Error splitting content into blocks: {str(e)}")
            # Возвращаем весь контент как один блок
            return [{
                "type": "full_page",
                "content": html_content,
                "html": html_content,
                "attributes": {}
            }]
    
    async def _prioritize_blocks(self, blocks: List[Dict[str, str]], goal: Optional[str] = None) -> Dict[str, List[Dict[str, str]]]:
        """
        Расставляет приоритеты блокам на основе цели.
        
        Args:
            blocks: Список блоков контента
            goal: Цель обработки
            
        Returns:
            Dict: Блоки, разделенные по приоритетам
        """
        prioritized = {"high": [], "medium": [], "low": []}
        
        if not blocks:
            return prioritized
        
        # Если нет цели, используем стандартную приоритизацию
        if not goal:
            return self._default_prioritize(blocks)
        
        # Ключевые слова для разных типов целей
        goal_keywords = {
            "prices": ["price", "cost", "buy", "purchase", "€", "$", "руб", "rub", "₽", "cart", "корзина", "цена", "стоимость", "купить"],
            "contacts": ["contact", "email", "phone", "address", "контакты", "почта", "телефон", "адрес"],
            "products": ["product", "item", "good", "товар", "продукт", "каталог", "catalog"],
            "news": ["news", "article", "post", "новости", "статья", "публикация"],
            "reviews": ["review", "rating", "opinion", "отзыв", "рейтинг", "оценка"],
            "login": ["login", "sign in", "register", "account", "вход", "регистрация", "аккаунт"],
            "search": ["search", "find", "query", "поиск", "найти", "запрос"],
        }
        
        # Определяем тип цели по ключевым словам
        goal_type = None
        goal_lower = goal.lower()
        
        for gtype, keywords in goal_keywords.items():
            if any(keyword in goal_lower for keyword in keywords):
                goal_type = gtype
                break
        
        # Если тип цели определен, применяем специфическую приоритизацию
        if goal_type:
            self.logger.info(f"Using specialized prioritization for goal type: {goal_type}")
            return self._specialized_prioritize(blocks, goal_type, goal_keywords)
        
        # Если тип цели не определен, делаем интеллектуальную приоритизацию
        self.logger.info("Using intelligent prioritization for custom goal")
        return await self._intelligent_prioritize(blocks, goal)
    
    def _default_prioritize(self, blocks: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
        """
        Стандартная приоритизация без цели.
        
        Args:
            blocks: Список блоков контента
            
        Returns:
            Dict: Блоки, разделенные по приоритетам
        """
        prioritized = {"high": [], "medium": [], "low": []}
        
        for block in blocks:
            block_type = block.get("type", "")
            
            # Высокий приоритет для основного контента и заголовков
            if block_type in ["h1", "h2", "article", "main"] or "content" in block.get("attributes", {}).get("id", ""):
                prioritized["high"].append(block)
                
            # Средний приоритет для навигации, меню, списков и параграфов
            elif block_type in ["nav", "p", "ul", "ol", "h3", "table"]:
                prioritized["medium"].append(block)
                
            # Низкий приоритет для всего остального
            else:
                prioritized["low"].append(block)
        
        return prioritized
    
    def _specialized_prioritize(self, blocks: List[Dict[str, str]], goal_type: str, goal_keywords: Dict[str, List[str]]) -> Dict[str, List[Dict[str, str]]]:
        """
        Специализированная приоритизация для конкретного типа цели.
        
        Args:
            blocks: Список блоков контента
            goal_type: Тип цели
            goal_keywords: Словарь ключевых слов
            
        Returns:
            Dict: Блоки, разделенные по приоритетам
        """
        prioritized = {"high": [], "medium": [], "low": []}
        
        # Получаем ключевые слова для данного типа цели
        keywords = goal_keywords.get(goal_type, [])
        
        for block in blocks:
            content = block.get("content", "").lower()
            block_type = block.get("type", "")
            
            # Проверяем, содержит ли блок ключевые слова для цели
            contains_keywords = any(keyword in content for keyword in keywords)
            
            # Высокий приоритет для блоков с ключевыми словами и основных блоков
            if contains_keywords or (goal_type == "prices" and block_type == "table"):
                prioritized["high"].append(block)
                
            # Средний приоритет для основных структурных элементов
            elif block_type in ["h1", "h2", "h3", "article", "main"]:
                prioritized["medium"].append(block)
                
            # Низкий приоритет для всего остального
            else:
                prioritized["low"].append(block)
        
        return prioritized
    
    async def _intelligent_prioritize(self, blocks: List[Dict[str, str]], goal: str) -> Dict[str, List[Dict[str, str]]]:
        """
        Интеллектуальная приоритизация на основе пользовательской цели.
        
        Args:
            blocks: Список блоков контента
            goal: Цель обработки
            
        Returns:
            Dict: Блоки, разделенные по приоритетам
        """
        # Пока просто используем стандартную приоритизацию
        # В будущем можно добавить вызов LLM для определения приоритетов
        return self._default_prioritize(blocks)
