#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль гибридного браузерного агента.

Предоставляет реализацию специализированного агента, который использует
различные браузерные инструменты (BrowserMCP, Browser-use) для автоматизации
браузера.
"""

import json
from typing import Dict, List, Any, Optional

from pydantic import Field

from gopiai.app.agent.specialized_agent import SpecializedAgent
from gopiai.core.logging import get_logger
logger = get_logger().logger
from gopiai.app.utils.browser_adapters import get_browser_adapter


class HybridBrowserAgent(SpecializedAgent):
    """
    Гибридный браузерный агент.
    
    Специализированный агент, который использует различные браузерные
    инструменты для автоматизации браузера.
    """
    
    name: str = "hybrid_browser"
    description: str = "Гибридный браузерный агент для автоматизации браузера"
    
    # Браузерный адаптер
    browser_adapter = None
    
    # Предпочтительный инструмент
    preferred_tool: str = Field(default="auto")
    
    # История браузерных операций
    # Инициализируется в __init__
    
    def __init__(self, preferred_tool="auto", browser=None, **data):
        """
        Инициализирует гибридного браузерного агента.
        
        Args:
            preferred_tool: Предпочтительный инструмент ("mcp", "browser_use" или "auto")
            browser: Экземпляр встроенного браузера (опционально)
            **data: Дополнительные параметры для инициализации
        """
        # Сохраняем параметры
        self.preferred_tool = preferred_tool
        self.browser = browser
        self.browser_history = []
        
        super().__init__(**data)
        
        # Инициализируем браузерный адаптер
        try:
            self.browser_adapter = get_browser_adapter(
                preferred_tool=self.preferred_tool,
                browser=self.browser
            )
        except Exception as e:
            logger.warning(f"Не удалось создать браузерный адаптер: {str(e)}")
            # Создаем заглушку для адаптера
            from gopiai.app.utils.browser_adapters import BrowserAdapter
            self.browser_adapter = BrowserAdapter(name="stub")
        
        # Добавляем информацию о браузере в системный промпт
        self._update_system_prompt_with_browser_info()
        
        logger.info(f"Инициализирован {self.name}")
        
    def _update_system_prompt_with_browser_info(self):
        """Обновляет системный промпт с информацией о браузере."""
        browser_info = (
            "Вы специализированный браузерный агент. "
            "Вы можете управлять браузером и анализировать веб-страницы. "
            "Используйте браузерные инструменты для выполнения задач, связанных с веб-страницами."
        )
        
        if self.system_prompt:
            self.system_prompt = f"{self.system_prompt}\n\n{browser_info}"
        else:
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
                    
    async def get_browser_state(self) -> Optional[Dict[str, Any]]:
        """
        Получает текущее состояние браузера.
        
        Returns:
            Dict: Состояние браузера или None, если информация недоступна
        """
        try:
            # Инициализируем адаптер, если он еще не инициализирован
            if not self.browser_adapter.initialized:
                try:
                    await self.browser_adapter.initialize()
                except Exception as e:
                    logger.warning(f"Не удалось инициализировать браузерный адаптер: {str(e)}")
                    return {
                        "current_url": "about:blank",
                        "page_title": "No page loaded",
                        "browser_history": [],
                        "status": "browser_not_available"
                    }
                
            # Получаем текущий URL
            try:
                url_result = await self.browser_adapter.get_current_url()
                current_url = url_result.get("data", {}).get("url", "unknown")
            except Exception as e:
                logger.warning(f"Не удалось получить текущий URL: {str(e)}")
                current_url = "unknown"
            
            # Получаем заголовок страницы
            try:
                title_result = await self.browser_adapter.get_page_title()
                page_title = title_result.get("data", {}).get("title", "unknown")
            except Exception as e:
                logger.warning(f"Не удалось получить заголовок страницы: {str(e)}")
                page_title = "unknown"
            
            # Формируем состояние браузера
            state = {
                "current_url": current_url,
                "page_title": page_title,
                "browser_history": self.browser_history[-5:] if self.browser_history else []
            }
            
            return state
        except Exception as e:
            logger.error(f"Ошибка при получении состояния браузера: {str(e)}")
            return {
                "error": str(e),
                "status": "error"
            }
        
    async def process(self, query):
        """
        Обрабатывает запрос с использованием браузера.
        
        Args:
            query: Запрос для обработки
            
        Returns:
            str: Результат обработки запроса
        """
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
            
            # Добавляем действие в историю браузера
            self.browser_history.append({
                "type": action_type,
                "params": action
            })
            
            # Выполняем действие
            if action_type == "navigate":
                result = await self.browser_adapter.navigate(action.get("url"))
            elif action_type == "click":
                result = await self.browser_adapter.click(action.get("selector"))
            elif action_type == "type":
                result = await self.browser_adapter.type(
                    action.get("selector"), 
                    action.get("text")
                )
            elif action_type == "extract":
                result = await self.browser_adapter.extract_content(
                    action.get("selector")
                )
            else:
                result = {
                    "success": False,
                    "message": f"Неизвестное действие: {action_type}",
                    "data": action
                }
                
            results.append(result)
            
        # Сохраняем результаты в контекст
        if "browser_results" not in self.context:
            self.context["browser_results"] = []
        self.context["browser_results"].extend(results)
        
        # Формируем ответ
        response = self._format_response(results)
        
        return response
        
    async def _analyze_query(self, query):
        """
        Анализирует запрос и определяет необходимые действия.
        
        Args:
            query: Запрос для анализа
            
        Returns:
            List[Dict]: Список действий для выполнения
        """
        # Простой анализ запроса на основе ключевых слов
        actions = []
        
        # Проверяем наличие URL в запросе
        import re
        url_match = re.search(r'https?://[^\s]+', query)
        if url_match or "перейти" in query.lower() or "открыть" in query.lower() or "go to" in query.lower():
            # Если есть URL, добавляем действие навигации
            url = url_match.group(0) if url_match else None
            
            if not url:
                # Пытаемся извлечь URL из текста
                words = query.split()
                for i, word in enumerate(words):
                    if word.lower() in ["перейти", "открыть", "go", "navigate", "open"]:
                        if i + 1 < len(words) and words[i+1].lower() in ["на", "по", "to", "on"]:
                            if i + 2 < len(words):
                                url = words[i+2]
                                # Если URL не содержит протокол, добавляем его
                                if not url.startswith(("http://", "https://")):
                                    url = "https://" + url
                                break
            
            if url:
                actions.append({
                    "type": "navigate",
                    "url": url
                })
                
        # Проверяем наличие действий клика
        if "кликнуть" in query.lower() or "нажать" in query.lower() or "click" in query.lower():
            # Пытаемся извлечь селектор
            selector = None
            
            # Простой поиск селектора
            selector_match = re.search(r'селектор[:\s]+([^\s]+)', query)
            if selector_match:
                selector = selector_match.group(1)
                
            if not selector:
                # Пытаемся найти селектор в кавычках
                selector_match = re.search(r'[\'"]([^\'"]+)[\'"]', query)
                if selector_match:
                    selector = selector_match.group(1)
                    
            if selector:
                actions.append({
                    "type": "click",
                    "selector": selector
                })
                
        # Проверяем наличие действий ввода текста
        if "ввести" in query.lower() or "напечатать" in query.lower() or "type" in query.lower():
            # Пытаемся извлечь селектор и текст
            selector = None
            text = None
            
            # Простой поиск селектора
            selector_match = re.search(r'селектор[:\s]+([^\s]+)', query)
            if selector_match:
                selector = selector_match.group(1)
                
            # Поиск текста в кавычках
            text_match = re.search(r'[\'"]([^\'"]+)[\'"]', query)
            if text_match:
                text = text_match.group(1)
                
            if selector and text:
                actions.append({
                    "type": "type",
                    "selector": selector,
                    "text": text
                })
                
        # Проверяем наличие действий извлечения содержимого
        if "извлечь" in query.lower() or "получить" in query.lower() or "extract" in query.lower():
            # Пытаемся извлечь селектор
            selector = None
            
            # Простой поиск селектора
            selector_match = re.search(r'селектор[:\s]+([^\s]+)', query)
            if selector_match:
                selector = selector_match.group(1)
                
            actions.append({
                "type": "extract",
                "selector": selector
            })
            
        # Если не удалось определить действия, используем запрос как есть
        if not actions:
            # Если запрос похож на URL, добавляем действие навигации
            if re.match(r'^[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', query):
                actions.append({
                    "type": "navigate",
                    "url": "https://" + query
                })
            else:
                # Иначе добавляем действие извлечения содержимого
                actions.append({
                    "type": "extract",
                    "selector": None
                })
                
        return actions
        
    def _format_response(self, results):
        """
        Форматирует результаты выполнения действий в ответ.
        
        Args:
            results: Результаты выполнения действий
            
        Returns:
            str: Отформатированный ответ
        """
        response_parts = []
        
        for result in results:
            if result.get("success"):
                response_parts.append(result.get("message"))
                
                # Добавляем данные результата, если они есть
                data = result.get("data")
                if data:
                    if "content" in data:
                        response_parts.append(f"Содержимое: {data['content']}")
                    elif "result" in data:
                        response_parts.append(f"Результат: {data['result']}")
            else:
                response_parts.append(f"Ошибка: {result.get('message')}")
                
        return "\n".join(response_parts)
        
    async def receive_guidance(self, guidance):
        """
        Получает руководство от оркестратора.
        
        Args:
            guidance: Руководство от оркестратора
        """
        await super().receive_guidance(guidance)
        
        # Если руководство содержит инструкции по смене инструмента,
        # меняем активный инструмент
        if "использовать browsermcp" in guidance.lower():
            self.browser_adapter = get_browser_adapter(preferred_tool="mcp")
            await self.browser_adapter.initialize()
            logger.info("Переключение на BrowserMCP по руководству оркестратора")
        elif "использовать browser-use" in guidance.lower():
            self.browser_adapter = get_browser_adapter(preferred_tool="browser_use")
            await self.browser_adapter.initialize()
            logger.info("Переключение на Browser-use по руководству оркестратора")
            
    def get_current_state(self):
        """
        Возвращает текущее состояние агента.
        
        Returns:
            dict: Текущее состояние агента
        """
        # Получаем базовое состояние от специализированного агента
        state = super().get_current_state()
        
        # Добавляем информацию о браузере
        state["browser_adapter"] = self.browser_adapter.name if self.browser_adapter else None
        state["browser_history"] = self.browser_history[-5:] if self.browser_history else []
        
        return state
        
    async def cleanup(self):
        """
        Очищает ресурсы агента.
        
        Закрывает браузер и освобождает ресурсы.
        """
        if self.browser_adapter:
            await self.browser_adapter.close()
            
        logger.info(f"Ресурсы агента {self.name} очищены")
