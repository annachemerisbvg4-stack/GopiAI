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
        
        # Динамически формируем список инструментов, исходя из доступных ключей в окружении
        has_brave = bool(os.environ.get("BRAVE_API_KEY"))
        has_tavily = bool(os.environ.get("TAVILY_API_KEY"))
        has_firecrawl = bool(os.environ.get("FIRECRAWL_API_KEY"))
        has_github = bool(os.environ.get("GITHUB_TOKEN"))
        has_exa = bool(os.environ.get("EXA_API_KEY"))
        has_jina = bool(os.environ.get("JINA_API_KEY"))
        has_apify = bool(os.environ.get("APIFY_API_TOKEN"))
        has_composio = bool(os.environ.get("COMPOSIO_API_KEY"))
        has_patronus = bool(os.environ.get("PATRONUS_API_KEY"))
        has_qdrant = bool(os.environ.get("QDRANT_API_KEY"))

        # Базовый набор (не требуют внешних ключей)
        priority_tools = {
            # Выполнение кода
            'code_interpreter': {
                'module': 'tools.crewai_toolkit.tools.code_interpreter_tool.code_interpreter_tool',
                'class': 'CodeInterpreterTool',
                'category': 'code_execution',
                'description': 'Выполнение Python кода в безопасной среде'
            },

            # Веб-скрапинг (улучшенный)
            'selenium_scraping': {
                'module': 'tools.crewai_toolkit.tools.selenium_scraping_tool.selenium_scraping_tool',
                'class': 'SeleniumScrapingTool',
                'category': 'web_scraping',
                'description': 'Продвинутый веб-скрапинг с Selenium'
            },

            # Файловые операции (улучшенные)
            'file_read': {
                'module': 'tools.crewai_toolkit.tools.file_read_tool.file_read_tool',
                'class': 'FileReadTool',
                'category': 'file_operations',
                'description': 'Чтение файлов с поддержкой различных форматов'
            },

            'file_writer': {
                'module': 'tools.crewai_toolkit.tools.file_writer_tool.file_writer_tool',
                'class': 'FileWriterTool',
                'category': 'file_operations',
                'description': 'Запись файлов с поддержкой различных форматов'
            },

            'directory_read': {
                'module': 'tools.crewai_toolkit.tools.directory_read_tool.directory_read_tool',
                'class': 'DirectoryReadTool',
                'category': 'file_operations',
                'description': 'Чтение содержимого директорий'
            },

            # Поиск в файлах
            'csv_search': {
                'module': 'tools.crewai_toolkit.tools.csv_search_tool.csv_search_tool',
                'class': 'CSVSearchTool',
                'category': 'file_search',
                'description': 'Поиск в CSV файлах'
            },

            'json_search': {
                'module': 'tools.crewai_toolkit.tools.json_search_tool.json_search_tool',
                'class': 'JSONSearchTool',
                'category': 'file_search',
                'description': 'Поиск в JSON файлах'
            },

            'pdf_search': {
                'module': 'tools.crewai_toolkit.tools.pdf_search_tool.pdf_search_tool',
                'class': 'PDFSearchTool',
                'category': 'file_search',
                'description': 'Поиск в PDF файлах'
            },

            # Веб-скрапинг базовый
            'scrape_website': {
                'module': 'tools.crewai_toolkit.tools.scrape_website_tool.scrape_website_tool',
                'class': 'ScrapeWebsiteTool',
                'category': 'web_scraping',
                'description': 'Базовый веб-скрапинг сайтов'
            },
        }

        # Опциональные инструменты, зависящие от ключей
        if has_firecrawl:
            priority_tools['firecrawl_scrape'] = {
                'module': 'tools.crewai_toolkit.tools.firecrawl_scrape_website_tool.firecrawl_scrape_website_tool',
                'class': 'FirecrawlScrapeWebsiteTool',
                'category': 'web_scraping',
                'description': 'Веб-скрапинг через Firecrawl API'
            }

        if has_brave:
            priority_tools['brave_search'] = {
                'module': 'tools.crewai_toolkit.tools.brave_search_tool.brave_search_tool',
                'class': 'BraveSearchTool',
                'category': 'web_search',
                'description': 'Поиск через Brave Search API'
            }

        if has_tavily:
            priority_tools['tavily_search'] = {
                'module': 'tools.crewai_toolkit.tools.tavily_search_tool.tavily_search_tool',
                'class': 'TavilySearchTool',
                'category': 'web_search',
                'description': 'Поиск через Tavily API (ориентация на RAG)'
            }

        if has_github:
            priority_tools['github_search'] = {
                'module': 'tools.gopiai_integration.github_integration_tool',
                'class': 'GitHubIntegrationTool',
                'category': 'development',
                'description': 'Поиск в GitHub репозиториях, коде, issues (рабочая реализация)'
            }

        # Поисковые/скрапинг инструменты сторонних провайдеров
        if has_exa:
            priority_tools['exa_search'] = {
                'module': 'tools.crewai_toolkit.tools.exa_tools.exa_search_tool',
                'class': 'ExaSearchTool',
                'category': 'web_search',
                'description': 'Поиск/извлечение через Exa API'
            }

        if has_jina:
            priority_tools['jina_scrape'] = {
                'module': 'tools.crewai_toolkit.tools.jina_scrape_website_tool.jina_scrape_website_tool',
                'class': 'JinaScrapeWebsiteTool',
                'category': 'web_scraping',
                'description': 'Скрапинг через Jina AI Reader'
            }

        if has_apify:
            priority_tools['apify_actors'] = {
                'module': 'tools.crewai_toolkit.tools.apify_actors_tool.apify_actors_tool',
                'class': 'ApifyActorsTool',
                'category': 'web_scraping',
                'description': 'Запуск акторов Apify'
            }

        if has_composio:
            priority_tools['composio'] = {
                'module': 'tools.crewai_toolkit.tools.composio_tool.composio_tool',
                'class': 'ComposioTool',
                'category': 'automation',
                'description': 'Интеграции через Composio'
            }

        if has_patronus:
            priority_tools['patronus_eval'] = {
                'module': 'tools.crewai_toolkit.tools.patronus_eval_tool.patronus_eval_tool',
                'class': 'PatronusEvalTool',
                'category': 'evaluation',
                'description': 'Оценка качества ответов Patronus'
            }

        if has_qdrant:
            priority_tools['qdrant_search'] = {
                'module': 'tools.crewai_toolkit.tools.qdrant_vector_search_tool.qdrant_search_tool',
                'class': 'QdrantVectorSearchTool',
                'category': 'rag',
                'description': 'Векторный поиск в Qdrant'
            }

        # Проверяем доступность каждого инструмента
        for tool_name, tool_info in priority_tools.items():
            base_module_path = tool_info['module']
            # Кандидаты модулей: локальный путь, автоматически выведенный путь официального пакета, и корневой модуль
            candidates = [base_module_path]
            try_official = base_module_path.replace('tools.crewai_toolkit.tools.', 'crewai_tools.tools.')
            if try_official != base_module_path:
                candidates.append(try_official)
            # Часто классы доступны прямо из корня crewai_tools
            candidates.append('crewai_tools')

            import_errors = []
            resolved = False
            chosen_module_path = None
            chosen_class = None

            for candidate in candidates:
                try:
                    module = importlib.import_module(candidate)
                    tool_class = getattr(module, tool_info['class'])
                    chosen_module_path = candidate
                    chosen_class = tool_class
                    resolved = True
                    break
                except Exception as e:
                    import_errors.append(f"{candidate}: {e}")

            if resolved:
                self.available_tools[tool_name] = {
                    'class': chosen_class,
                    'module_path': chosen_module_path,
                    'category': tool_info['category'],
                    'description': tool_info['description'],
                    'available': True
                }

                # Добавляем в категории
                category = tool_info['category']
                if category not in self.tool_categories:
                    self.tool_categories[category] = []
                self.tool_categories[category].append(tool_name)

                self.logger.debug(f"✅ Инструмент {tool_name} доступен (используется модуль: {chosen_module_path})")
            else:
                self.available_tools[tool_name] = {
                    'class': None,
                    'module_path': base_module_path,
                    'category': tool_info['category'],
                    'description': tool_info['description'],
                    'available': False,
                    'error': '\n'.join(import_errors)
                }
                self.logger.debug(f"❌ Инструмент {tool_name} недоступен. Причины:\n- " + "\n- ".join(import_errors))
    
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
            # Приоритет: Brave -> Tavily -> первый доступный
            if 'brave_search' in available_tools:
                return 'brave_search'
            if 'tavily_search' in available_tools:
                return 'tavily_search'
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
