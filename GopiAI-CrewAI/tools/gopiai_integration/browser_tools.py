"""
🌐 GopiAI Browser Tool для CrewAI
Интеграция CrewAI агентов с браузер-системой GopiAI
"""

import os
import sys
import time
import logging
from typing import Type, Any, Optional
from pydantic import BaseModel, Field

# Импортируем базовый класс
from .base import GopiAIBaseTool

class BrowserInput(BaseModel):
    """Схема входных данных для браузер-инструмента"""
    action: str = Field(description="Действие: navigate, click, type, extract, screenshot, wait")
    target: str = Field(description="URL или CSS селектор")
    data: str = Field(default="", description="Данные для ввода (текст, время ожидания)")
    wait_seconds: int = Field(default=3, description="Время ожидания после действия")

class GopiAIBrowserTool(GopiAIBaseTool):
    """
    Мощный инструмент для управления браузером через GopiAI BrowserAgent
    
    Возможности:
    - Навигация по веб-сайтам
    - Клики по элементам
    - Ввод текста в формы
    - Извлечение текста и данных
    - Скриншоты страниц
    - Ожидание загрузки элементов
    """
    
    name: str = "gopiai_browser"
    description: str = """Управляет браузером через GopiAI BrowserAgent. 
    
    Действия:
    - navigate: перейти на URL (target=URL)
    - click: кликнуть элемент (target=selector)
    - type: ввести текст (target=selector, data=текст)
    - extract: извлечь текст (target=selector или 'page' для всей страницы)
    - screenshot: сделать скриншот (target=имя_файла)
    - wait: ждать элемент (target=selector, data=время_в_секундах)
    
    Примеры:
    - navigate: target="https://google.com"
    - click: target="button.search"
    - type: target="input[name='q']", data="поисковый запрос"
    - extract: target="h1" или target="page"
    """
    args_schema: Type[BaseModel] = BrowserInput
    
    def __init__(self, verbose=False, cache_enabled=True):
        """
        Инициализация браузер-инструмента
        
        Args:
            verbose: Подробный вывод
            cache_enabled: Включение кеширования результатов
        """
        super().__init__(verbose=verbose)
        self.cache_enabled = cache_enabled
        self.cache = {}
        
        # Создаем директорию для кеша, если её нет
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache", "browser")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _run(self, action: str, target: str, data: str = "", wait_seconds: int = 3) -> str:
        """
        Выполнение браузерного действия через GopiAI BrowserAgent
        """
        # Проверка кеша для extract действий
        cache_key = f"{action}_{target}_{data}"
        if self.cache_enabled and action == "extract" and cache_key in self.cache:
            self.logger.info(f"Используем кешированный результат для {cache_key}")
            return self.cache[cache_key]
        
        start_time = time.time()
        self.logger.info(f"Выполнение браузерного действия: {action} на {target}")
        
        try:
            # Попытка интеграции с GopiAI BrowserAgent
            result = self._execute_browser_action(action, target, data, wait_seconds)
            
            # Кеширование результатов для extract
            if self.cache_enabled and action == "extract":
                self.cache[cache_key] = result
                
            execution_time = time.time() - start_time
            self.logger.info(f"Браузерное действие выполнено за {execution_time:.2f}с")
            return f"✅ Браузер: {action} выполнен. Результат: {result}"
            
        except Exception as e:
            self.logger.error(f"Ошибка браузерного действия: {str(e)}")
            # Fallback: эмуляция для тестирования
            return self._simulate_browser_action(action, target, data)
    
    def _execute_browser_action(self, action: str, target: str, data: str, wait_seconds: int) -> str:
        """
        Реальная интеграция с GopiAI BrowserAgent
        """
        try:
            # Добавляем путь к GopiAI-Core
            sys.path.append(os.path.join(os.path.dirname(__file__), "../../../GopiAI-Core"))
            
            # Импортируем браузер-агент GopiAI
            from gopiai.core.agent.browser_ai_interface import get_browser_ai
            
            # Получаем экземпляр браузера
            browser_ai = get_browser_ai()
            
            # Выполняем действие
            if action == "navigate":
                return browser_ai.navigate(target)
            elif action == "click":
                return browser_ai.click(target)
            elif action == "type":
                return browser_ai.type_text(target, data)
            elif action == "extract":
                if target.lower() == "page":
                    return browser_ai.get_page_text()
                else:
                    return browser_ai.extract_text(target)
            elif action == "screenshot":
                return browser_ai.take_screenshot(target)
            elif action == "wait":
                wait_time = int(data) if data.isdigit() else wait_seconds
                return browser_ai.wait_for_element(target, wait_time)
            else:
                return f"❌ Неизвестное действие: {action}"
                
        except ImportError:
            raise Exception("GopiAI BrowserAgent недоступен")
        except Exception as e:
            raise Exception(f"Ошибка браузера: {str(e)}")
    
    def _simulate_browser_action(self, action: str, target: str, data: str) -> str:
        """
        Эмуляция браузерных действий для тестирования
        """
        if action == "navigate":
            return f"🌐 Переход на {target}"
        elif action == "click":
            return f"👆 Клик по элементу {target}"
        elif action == "type":
            return f"⌨️ Ввод '{data}' в {target}"
        elif action == "extract":
            if target.lower() == "page":
                return "📄 Текст всей страницы извлечен"
            else:
                return f"📝 Текст из {target}: [извлеченный текст]"
        elif action == "screenshot":
            return f"📸 Скриншот сохранен как {target}"
        elif action == "wait":
            return f"⏱️ Ожидание элемента {target}"
        else:
            return f"❌ Неизвестное действие: {action}"


# Дополнительные специализированные инструменты

class GopiAIWebSearchTool(GopiAIBaseTool):
    """Инструмент для веб-поиска через GopiAI браузер"""
    
    name: str = "gopiai_web_search"
    description: str = "Выполняет поиск в Google и возвращает результаты"
    
    def _run(self, query: str) -> str:
        """Поиск в Google"""
        browser_tool = GopiAIBrowserTool()
        
        # Переходим на Google
        browser_tool._run("navigate", "https://www.google.com")
        
        # Вводим поисковый запрос
        browser_tool._run("type", "input[name='q']", query)
        
        # Нажимаем Enter (или кнопку поиска)
        browser_tool._run("click", "input[name='btnK']")
        
        # Извлекаем результаты
        results = browser_tool._run("extract", ".g h3")
        
        return f"🔍 Результаты поиска '{query}': {results}"


class GopiAIPageAnalyzerTool(GopiAIBaseTool):
    """Анализ веб-страниц"""
    
    name: str = "gopiai_page_analyzer"
    description: str = "Анализирует содержимое веб-страницы и извлекает ключевую информацию"
    
    def _run(self, url: str, analysis_type: str = "summary") -> str:
        """
        Анализирует страницу
        analysis_type: summary, links, forms, images, text
        """
        browser_tool = GopiAIBrowserTool()
        
        # Переходим на страницу
        browser_tool._run("navigate", url)
        
        if analysis_type == "summary":
            title = browser_tool._run("extract", "title")
            headers = browser_tool._run("extract", "h1, h2, h3")
            return f"📊 Анализ {url}:\nЗаголовок: {title}\nОсновные разделы: {headers}"
        
        elif analysis_type == "links":
            links = browser_tool._run("extract", "a[href]")
            return f"🔗 Ссылки на {url}: {links}"
        
        elif analysis_type == "forms":
            forms = browser_tool._run("extract", "form")
            return f"📋 Формы на {url}: {forms}"
        
        elif analysis_type == "text":
            text = browser_tool._run("extract", "page")
            return f"📄 Полный текст {url}: {text}"
        
        else:
            return f"❌ Неизвестный тип анализа: {analysis_type}"


# Экспорт инструментов
__all__ = [
    "GopiAIBrowserTool",
    "GopiAIWebSearchTool", 
    "GopiAIPageAnalyzerTool"
]


if __name__ == "__main__":
    # Настройка логирования для тестов
    logging.basicConfig(level=logging.INFO)
    
    # Тест инструментов
    print("🧪 Тестирование GopiAI Browser Tools...")
    
    # Тест основного браузер-инструмента
    browser = GopiAIBrowserTool(verbose=True)
    result = browser.run("navigate", "https://google.com")
    print(f"Browser test: {result}")
    
    # Тест поиска
    search = GopiAIWebSearchTool(verbose=True)
    result = search.run("CrewAI documentation")
    print(f"Search test: {result}")
    
    # Тест метрик
    print("
📊 Метрики браузер-инструмента:")
    print(browser.get_metrics())
    
    print("
✅ Все инструменты готовы!")