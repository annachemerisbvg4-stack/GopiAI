"""
🛠️ CrewAI Tools Integrator
Интегратор для подключения и управления инструментами из CrewAI Toolkit
"""

import logging
import importlib
from typing import Dict, List, Optional, Any, Type
from pathlib import Path
import sys
import os

logger = logging.getLogger(__name__)

class CrewAIToolsIntegrator:
    """
    Интегратор для управления инструментами CrewAI Toolkit
    
    Возможности:
    - Автоматическое обнаружение доступных инструментов
    - Ленивая загрузка инструментов по требованию
    - Категоризация инструментов по типам
    - Fallback между различными инструментами
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_tools = {}
        self.loaded_tools = {}
        self.tool_categories = {}
        
        # Добавляем путь к crewai_toolkit
        toolkit_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crewai_toolkit")
        if toolkit_path not in sys.path:
            sys.path.insert(0, toolkit_path)
        
        self._discover_tools()
        self.logger.info(f"✅ CrewAI Tools Integrator инициализирован. Найдено {len(self.available_tools)} инструментов")
    
    def _discover_tools(self):
        """Обнаруживает доступные CrewAI инструменты"""
        
        # Приоритетные инструменты для интеграции
        priority_tools = {
            # Выполнение кода
            'code_interpreter': {
                'module': 'tools.code_interpreter_tool.code_interpreter_tool',
                'class': 'CodeInterpreterTool',
                'category': 'code_execution',
                'description': 'Выполнение Python кода в безопасной среде'
            },
            
            # Веб-скрапинг (улучшенный)
            'selenium_scraping': {
                'module': 'tools.selenium_scraping_tool.selenium_scraping_tool',
                'class': 'SeleniumScrapingTool',
                'category': 'web_scraping',
                'description': 'Продвинутый веб-скрапинг с Selenium'
            },
            
            # Поиск в интернете
            'serper_dev': {
                'module': 'tools.serper_dev_tool.serper_dev_tool',
                'class': 'SerperDevTool',
                'category': 'web_search',
                'description': 'Поиск в интернете через Serper API'
            },
            
            'brave_search': {
                'module': 'tools.brave_search_tool.brave_search_tool',
                'class': 'BraveSearchTool',
                'category': 'web_search',
                'description': 'Поиск через Brave Search API'
            },
            
            # Файловые операции (улучшенные)
            'file_read': {
                'module': 'tools.file_read_tool.file_read_tool',
                'class': 'FileReadTool',
                'category': 'file_operations',
                'description': 'Чтение файлов с поддержкой различных форматов'
            },
            
            'file_writer': {
                'module': 'tools.file_writer_tool.file_writer_tool',
                'class': 'FileWriterTool',
                'category': 'file_operations',
                'description': 'Запись файлов с поддержкой различных форматов'
            },
            
            'directory_read': {
                'module': 'tools.directory_read_tool.directory_read_tool',
                'class': 'DirectoryReadTool',
                'category': 'file_operations',
                'description': 'Чтение содержимого директорий'
            },
            
            # Поиск в файлах
            'csv_search': {
                'module': 'tools.csv_search_tool.csv_search_tool',
                'class': 'CSVSearchTool',
                'category': 'file_search',
                'description': 'Поиск в CSV файлах'
            },
            
            'json_search': {
                'module': 'tools.json_search_tool.json_search_tool',
                'class': 'JSONSearchTool',
                'category': 'file_search',
                'description': 'Поиск в JSON файлах'
            },
            
            'pdf_search': {
                'module': 'tools.pdf_search_tool.pdf_search_tool',
                'class': 'PDFSearchTool',
                'category': 'file_search',
                'description': 'Поиск в PDF файлах'
            },
            
            # Веб-скрапинг альтернативы
            'scrape_website': {
                'module': 'tools.scrape_website_tool.scrape_website_tool',
                'class': 'ScrapeWebsiteTool',
                'category': 'web_scraping',
                'description': 'Базовый веб-скрапинг'
            },
            
            'firecrawl_scrape': {
                'module': 'tools.firecrawl_scrape_website_tool.firecrawl_scrape_website_tool',
                'class': 'FirecrawlScrapeWebsiteTool',
                'category': 'web_scraping',
                'description': 'Веб-скрапинг через Firecrawl API'
            },
            
            # GitHub интеграция
            'github_search': {
                'module': 'tools.github_search_tool.github_search_tool',
                'class': 'GithubSearchTool',
                'category': 'code_search',
                'description': 'Поиск в GitHub репозиториях'
            },
            
            # AI инструменты
            'dalle': {
                'module': 'tools.dalle_tool.dalle_tool',
                'class': 'DallETool',
                'category': 'ai_generation',
                'description': 'Генерация изображений через DALL-E'
            },
            
            'vision': {
                'module': 'tools.vision_tool.vision_tool',
                'class': 'VisionTool',
                'category': 'ai_analysis',
                'description': 'Анализ изображений с помощью AI'
            }
        }
        
        # Проверяем доступность каждого инструмента
        for tool_name, tool_info in priority_tools.items():
            try:
                # Пробуем импортировать модуль
                module = importlib.import_module(tool_info['module'])
                tool_class = getattr(module, tool_info['class'])
                
                self.available_tools[tool_name] = {
                    'class': tool_class,
                    'module_path': tool_info['module'],
                    'category': tool_info['category'],
                    'description': tool_info['description'],
                    'available': True
                }
                
                # Добавляем в категории
                category = tool_info['category']
                if category not in self.tool_categories:
                    self.tool_categories[category] = []
                self.tool_categories[category].append(tool_name)
                
                self.logger.debug(f"✅ Инструмент {tool_name} доступен")
                
            except Exception as e:
                self.available_tools[tool_name] = {
                    'class': None,
                    'module_path': tool_info['module'],
                    'category': tool_info['category'],
                    'description': tool_info['description'],
                    'available': False,
                    'error': str(e)
                }
                self.logger.debug(f"❌ Инструмент {tool_name} недоступен: {e}")
    
    def get_available_tools(self) -> Dict[str, Dict]:
        """Возвращает список доступных инструментов"""
        return {name: info for name, info in self.available_tools.items() if info['available']}
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """Возвращает инструменты по категории"""
        return self.tool_categories.get(category, [])
    
    def get_tool_instance(self, tool_name: str, **kwargs) -> Optional[Any]:
        """
        Получает экземпляр инструмента (ленивая загрузка)
        
        Args:
            tool_name: Название инструмента
            **kwargs: Параметры для инициализации инструмента
            
        Returns:
            Экземпляр инструмента или None
        """
        if tool_name not in self.available_tools:
            self.logger.error(f"Инструмент {tool_name} не найден")
            return None
        
        tool_info = self.available_tools[tool_name]
        if not tool_info['available']:
            self.logger.error(f"Инструмент {tool_name} недоступен: {tool_info.get('error', 'Unknown error')}")
            return None
        
        # Проверяем кеш
        cache_key = f"{tool_name}_{hash(str(sorted(kwargs.items())))}"
        if cache_key in self.loaded_tools:
            return self.loaded_tools[cache_key]
        
        try:
            # Создаем экземпляр инструмента
            tool_class = tool_info['class']
            tool_instance = tool_class(**kwargs)
            
            # Кешируем экземпляр
            self.loaded_tools[cache_key] = tool_instance
            
            self.logger.info(f"✅ Создан экземпляр инструмента {tool_name}")
            return tool_instance
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания экземпляра {tool_name}: {e}")
            return None
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any], **tool_kwargs) -> Dict[str, Any]:
        """
        Выполняет инструмент с заданными параметрами
        
        Args:
            tool_name: Название инструмента
            params: Параметры для выполнения
            **tool_kwargs: Параметры для инициализации инструмента
            
        Returns:
            Результат выполнения инструмента
        """
        try:
            tool_instance = self.get_tool_instance(tool_name, **tool_kwargs)
            if not tool_instance:
                return {"error": f"Не удалось получить экземпляр инструмента {tool_name}"}
            
            # Выполняем инструмент
            if hasattr(tool_instance, '_run'):
                result = tool_instance._run(**params)
            elif hasattr(tool_instance, 'run'):
                result = tool_instance.run(**params)
            else:
                return {"error": f"Инструмент {tool_name} не имеет метода выполнения"}
            
            return {"success": True, "result": result, "tool": tool_name}
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка выполнения инструмента {tool_name}: {e}")
            return {"error": f"Ошибка выполнения {tool_name}: {str(e)}"}
    
    def get_best_tool_for_task(self, task_type: str, task_description: str = "") -> Optional[str]:
        """
        Выбирает лучший инструмент для задачи
        
        Args:
            task_type: Тип задачи (web_search, file_operations, code_execution и т.д.)
            task_description: Описание задачи для более точного выбора
            
        Returns:
            Название лучшего инструмента или None
        """
        available_tools = self.get_tools_by_category(task_type)
        if not available_tools:
            return None
        
        # Простая логика выбора (можно улучшить)
        task_lower = task_description.lower()
        
        if task_type == 'web_search':
            if 'google' in task_lower or 'search' in task_lower:
                return 'serper_dev' if 'serper_dev' in available_tools else available_tools[0]
            return available_tools[0]
        
        elif task_type == 'web_scraping':
            if 'javascript' in task_lower or 'dynamic' in task_lower:
                return 'selenium_scraping' if 'selenium_scraping' in available_tools else available_tools[0]
            return available_tools[0]
        
        elif task_type == 'code_execution':
            return 'code_interpreter' if 'code_interpreter' in available_tools else available_tools[0]
        
        elif task_type == 'file_operations':
            if 'read' in task_lower:
                return 'file_read' if 'file_read' in available_tools else available_tools[0]
            elif 'write' in task_lower:
                return 'file_writer' if 'file_writer' in available_tools else available_tools[0]
            return available_tools[0]
        
        # По умолчанию возвращаем первый доступный
        return available_tools[0] if available_tools else None
    
    def get_tools_summary(self) -> Dict[str, List[Dict]]:
        """Возвращает сводку по категориям инструментов"""
        summary = {}
        for category, tool_names in self.tool_categories.items():
            summary[category] = []
            for tool_name in tool_names:
                tool_info = self.available_tools[tool_name]
                if tool_info['available']:
                    summary[category].append({
                        'name': tool_name,
                        'description': tool_info['description'],
                        'available': True
                    })
        return summary


# Глобальный экземпляр интегратора
_crewai_tools_integrator = None

def get_crewai_tools_integrator() -> CrewAIToolsIntegrator:
    """Возвращает глобальный экземпляр интегратора CrewAI инструментов"""
    global _crewai_tools_integrator
    if _crewai_tools_integrator is None:
        _crewai_tools_integrator = CrewAIToolsIntegrator()
    return _crewai_tools_integrator
