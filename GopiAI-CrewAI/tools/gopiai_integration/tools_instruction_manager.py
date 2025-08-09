"""
🛠️ Tools Instruction Manager
Система динамической подгрузки инструкций для инструментов GopiAI
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolsInstructionManager:
    """
    Менеджер для управления инструкциями по использованию инструментов.
    Обеспечивает динамическую подгрузку детальных инструкций только при необходимости.
    """
    
    def __init__(self):
        """Инициализация менеджера инструкций"""
        self.logger = logging.getLogger(__name__)
        self._tools_cache = {}
        self._last_update = None
        
        # Определяем пути к файлам
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.instructions_dir = os.path.join(self.base_dir, "tool_instructions")
        
        # Создаем директорию для инструкций если её нет
        os.makedirs(self.instructions_dir, exist_ok=True)
        
        self.logger.info("✅ ToolsInstructionManager инициализирован")
    
    def get_tools_summary(self) -> Dict[str, str]:
        """
        Возвращает краткий список доступных инструментов для системного промпта.
        Используется для первоначального ознакомления ИИ с доступными инструментами.
        
        Returns:
            Dict[str, str]: Словарь {tool_name: brief_description}
        """
        return {
            # 💻 Основные инструменты (с CrewAI улучшениями)
            "execute_shell": "Выполнение команд терминала (через CodeInterpreterTool): ls, dir, git, npm, pip, docker, curl",
            "web_scraper": "Продвинутый веб-скрапинг (через SeleniumScrapingTool): динамические страницы, JavaScript",
            "web_search": "Поиск в интернете (через Brave/Tavily): быстрые и дешевые SERP, структурированные результаты",
            "file_operations": "Улучшенные файловые операции (через FileReadTool/FileWriterTool): множество форматов",
            
            # 🌐 Веб и API
            "api_client": "HTTP API клиент: GET, POST, PUT, DELETE запросы к любым API",
            "url_analyzer": "Анализ веб-ресурсов: проверка статуса, заголовков, robots.txt, sitemap",
            "browser_tools": "Автоматизация браузера: навигация, клики, ввод, скриншоты, JavaScript",
            
            # 🔍 Поиск в файлах (CrewAI инструменты)
            "csv_search": "Поиск в CSV файлах (через CSVSearchTool): структурированные данные",
            "json_search": "Поиск в JSON файлах (через JSONSearchTool): словари, массивы",
            "pdf_search": "Поиск в PDF файлах (через PDFSearchTool): текст, метаданные",
            
            # 💻 Код и разработка
            "code_interpreter": "Выполнение Python кода (через CodeInterpreterTool): безопасная среда",
            "github_search": "Поиск в GitHub (через GithubSearchTool): репозитории, код, issues",
            
            # 🎨 AI инструменты
            "dalle_tool": "Генерация изображений (через DallETool): DALL-E 3, высокое качество",
            "vision_tool": "Анализ изображений (через VisionTool): описание, распознавание объектов",
            
            # ℹ️ Системные инструменты
            "system_info": "Информация о системе: ОС, архитектура, ресурсы",
            "process_manager": "Управление процессами: запуск, остановка, мониторинг",
            "time_helper": "Работа со временем: текущее время, форматирование, timestamp",
            "project_helper": "Управление проектом GopiAI: статус, здоровье системы, логи"
        }
    
    def get_tool_detailed_instructions(self, tool_name: str) -> Optional[str]:
        """
        Возвращает детальные инструкции по использованию конкретного инструмента.
        Подгружается динамически только при выборе инструмента ИИ.
        
        Args:
            tool_name (str): Название инструмента
            
        Returns:
            Optional[str]: Детальные инструкции или None если инструмент не найден
        """
        instructions = {
            "execute_shell": self._get_execute_shell_instructions(),
            "web_scraper": self._get_web_scraper_instructions(),
            "web_search": self._get_web_search_instructions(),
            "api_client": self._get_api_client_instructions(),
            "url_analyzer": self._get_url_analyzer_instructions(),
            "browser_tools": self._get_browser_instructions(),
            "file_operations": self._get_file_operations_instructions(),
            "system_info": self._get_system_info_instructions(),
            "process_manager": self._get_process_manager_instructions(),
            "time_helper": self._get_time_helper_instructions(),
            "project_helper": self._get_project_helper_instructions()
        }
        
        if tool_name in instructions:
            self.logger.info(f"📖 Загружены детальные инструкции для {tool_name}")
            return instructions[tool_name]
        
        self.logger.warning(f"⚠️ Инструкции для {tool_name} не найдены")
        return None
    
    def _get_execute_shell_instructions(self) -> str:
        """Детальные инструкции для execute_shell"""
        return """
# 💻 Execute Shell - Подробные инструкции

## Основные возможности:
- **Выполнение команд терминала**: любые команды оболочки (bash, cmd, powershell)
- **Навигация по файловой системе**: ls, dir, cd, pwd
- **Операции с файлами**: cat, type, mkdir, rmdir, cp, mv, rm
- **Системные команды**: ps, top, netstat, ipconfig, ping
- **Инструменты разработки**: git, npm, pip, python, node, docker
- **Сетевые утилиты**: curl, wget, ssh, scp

## Примеры использования:

### Навигация и просмотр файлов:
```bash
# Просмотр содержимого директории
ls -la
dir

# Переход в директорию
cd /path/to/directory

# Текущая директория
pwd

# Просмотр содержимого файла
cat filename.txt
type filename.txt
```

### Операции с файлами:
```bash
# Создание директории
mkdir new_folder

# Копирование файлов
cp source.txt destination.txt

# Перемещение файлов
mv old_name.txt new_name.txt

# Удаление файлов
rm unwanted_file.txt
```

### Git операции:
```bash
# Статус репозитория
git status

# Добавление файлов
git add .

# Коммит
git commit -m "Commit message"

# Пуш
git push origin main

# Клонирование
git clone https://github.com/user/repo.git
```

### Python и Node.js:
```bash
# Установка пакетов Python
pip install package_name

# Запуск Python скрипта
python script.py

# Установка пакетов Node.js
npm install package_name

# Запуск Node.js приложения
node app.js
```

### Docker:
```bash
# Список контейнеров
docker ps

# Запуск контейнера
docker run -d nginx

# Остановка контейнера
docker stop container_id
```

### Сетевые команды:
```bash
# Проверка соединения
ping google.com

# Скачивание файла
curl -O https://example.com/file.zip
wget https://example.com/file.zip

# Проверка портов
netstat -tulpn
```

## ⚠️ Важные замечания:
- Команды выполняются в текущей рабочей директории
- Используй абсолютные пути для надежности
- Некоторые команды могут требовать прав администратора
- Длительные команды могут иметь таймаут
- Всегда проверяй результат выполнения команды

## 🔥 АВТОМАТИЧЕСКОЕ ВЫПОЛНЕНИЕ:
Когда пользователь пишет команду терминала (например: `ls`, `git status`, `npm install`), 
я АВТОМАТИЧЕСКИ выполняю её через этот инструмент БЕЗ дополнительных вопросов!
"""
    
    def _get_web_scraper_instructions(self) -> str:
        """Детальные инструкции для web_scraper"""
        return """
# 🌐 Web Scraper - Подробные инструкции

## Основные возможности:
- **Извлечение текста**: get_text - весь текстовый контент страницы
- **Извлечение ссылок**: get_links - все ссылки на странице
- **Извлечение изображений**: get_images - все изображения
- **Извлечение таблиц**: get_tables - структурированные данные таблиц
- **Извлечение форм**: get_forms - формы и их поля
- **Метаданные**: get_metadata - title, description, keywords
- **Кастомные селекторы**: custom_selector - извлечение по CSS селектору

## Примеры использования:

### Извлечение основного контента:
```python
# Извлечение всего текста
web_scraper.call_tool("web_scraper", {
    "url": "https://example.com",
    "action": "get_text"
})

# Извлечение ссылок
web_scraper.call_tool("web_scraper", {
    "url": "https://example.com",
    "action": "get_links"
})
```

### Извлечение структурированных данных:
```python
# Извлечение таблиц
web_scraper.call_tool("web_scraper", {
    "url": "https://example.com/data",
    "action": "get_tables"
})

# Извлечение по CSS селектору
web_scraper.call_tool("web_scraper", {
    "url": "https://example.com",
    "action": "custom_selector",
    "selector": "h1, .content, #main"
})
```

### С кастомными заголовками:
```python
web_scraper.call_tool("web_scraper", {
    "url": "https://api.example.com",
    "action": "get_text",
    "headers": {
        "User-Agent": "Mozilla/5.0...",
        "Authorization": "Bearer token"
    }
})
```

## 🔥 АВТОМАТИЧЕСКОЕ ИСПОЛЬЗОВАНИЕ:
Когда пользователь даёт URL и просит "проанализировать", "скачать", "извлечь данные" - 
я АВТОМАТИЧЕСКИ использую этот инструмент!
"""
    
    def _get_web_search_instructions(self) -> str:
        """Детальные инструкции для web_search (Brave/Tavily)"""
        return """
# 🔎 Web Search (Brave/Tavily) - Подробные инструкции

## Поддерживаемые провайдеры:
- Brave Search API (переменная окружения: BRAVE_API_KEY)
- Tavily API (переменная окружения: TAVILY_API_KEY)

## Основные параметры запроса:
- query (str, обязательно): поисковый запрос
- top_k (int, опц., по умолчанию 5-10): сколько результатов вернуть
- region / country (str, опц.): регион поиска (например, us, ru, de)
- freshness / time_range (str, опц.): период свежести (например, d7, d30)
- include_domains (list[str], опц.): приоритетные домены
- exclude_domains (list[str], опц.): исключаемые домены
- safe_search (bool/str, опц.): уровень безопасного поиска

## Примеры использования:

```python
# Базовый поиск (автовыбор провайдера: Brave → Tavily → остальные)
web_search.call_tool("web_search", {
    "query": "python asyncio tutorial",
    "top_k": 8
})

# Поиск с фильтрами доменов
web_search.call_tool("web_search", {
    "query": "fastapi background tasks",
    "include_domains": ["fastapi.tiangolo.com", "stackoverflow.com"],
    "top_k": 5
})

# Поиск с ограничением по свежести и региону
web_search.call_tool("web_search", {
    "query": "openai responses streaming chunking",
    "freshness": "d30",
    "region": "us",
    "top_k": 10
})
```

## Замечания:
- Провайдер выбирается маршрутизатором инструментов: приоритет Brave → Tavily.
- Если ключи отсутствуют, будет выбран первый доступный web_search инструмент.
- Возвращай краткий структурированный список результатов (title, url, snippet).
"""
    
    def _get_api_client_instructions(self) -> str:
        """Детальные инструкции для api_client"""
        return """
# 🔌 API Client - Подробные инструкции

## Основные возможности:
- **GET запросы**: получение данных
- **POST запросы**: создание ресурсов
- **PUT запросы**: обновление ресурсов
- **DELETE запросы**: удаление ресурсов
- **PATCH запросы**: частичное обновление
- **Кастомные заголовки**: авторизация, content-type
- **Параметры URL**: query parameters
- **JSON данные**: отправка структурированных данных

## Примеры использования:

### GET запросы:
```python
# Простой GET запрос
api_client.call_tool("api_client", {
    "url": "https://api.example.com/users",
    "method": "GET"
})

# GET с параметрами
api_client.call_tool("api_client", {
    "url": "https://api.example.com/search",
    "method": "GET",
    "params": {
        "q": "search term",
        "limit": 10
    }
})
```

### POST запросы:
```python
# Создание ресурса
api_client.call_tool("api_client", {
    "url": "https://api.example.com/users",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer your_token"
    },
    "data": {
        "name": "John Doe",
        "email": "john@example.com"
    }
})
```

### Авторизованные запросы:
```python
# С API ключом
api_client.call_tool("api_client", {
    "url": "https://api.example.com/protected",
    "method": "GET",
    "headers": {
        "Authorization": "Bearer your_token",
        "X-API-Key": "your_api_key"
    }
})
```

## 🔥 АВТОМАТИЧЕСКОЕ ИСПОЛЬЗОВАНИЕ:
Когда пользователь просит сделать API запрос или даёт URL API - 
я АВТОМАТИЧЕСКИ использую этот инструмент!
"""
    
    def _get_file_operations_instructions(self) -> str:
        """Детальные инструкции для filesystem_tools"""
        return """
# 📁 Filesystem Tools - Подробные инструкции

## Основные возможности:
- **Чтение/запись файлов**: read_file(), write_file(), append_file()
- **JSON/CSV операции**: read_json(), write_json(), read_csv(), write_csv()
- **Поиск файлов**: find_files(), search_in_files()
- **Архивирование**: create_zip(), extract_zip()
- **Резервное копирование**: backup_file(), restore_backup()
- **Сравнение файлов**: compare_files(), get_file_diff()
- **Метаданные**: get_file_info(), get_directory_tree()
- **Хеширование**: calculate_file_hash()

## Примеры использования:

### Чтение и запись файлов:
```python
# Чтение файла
content = filesystem_tools.read_file("/path/to/file.txt")

# Запись файла
filesystem_tools.write_file("/path/to/output.txt", "Содержимое файла")

# Добавление к файлу
filesystem_tools.append_file("/path/to/log.txt", "Новая запись")
```

### Работа с JSON:
```python
# Чтение JSON
data = filesystem_tools.read_json("/path/to/data.json")

# Запись JSON
filesystem_tools.write_json("/path/to/output.json", {"key": "value"})
```

### Поиск файлов:
```python
# Поиск файлов по маске
files = filesystem_tools.find_files("/directory", "*.py")

# Поиск текста в файлах
results = filesystem_tools.search_in_files("/directory", "search_pattern")
```

### Архивирование:
```python
# Создание архива
filesystem_tools.create_zip("/path/to/archive.zip", ["/file1.txt", "/file2.txt"])

# Извлечение архива
filesystem_tools.extract_zip("/path/to/archive.zip", "/extract/to/")
```

## ⚠️ Важные замечания:
- Всегда используйте абсолютные пути
- Проверяйте права доступа к файлам
- Для больших файлов используйте потоковое чтение
- Делайте резервные копии важных файлов перед изменением
"""
    
    def _get_url_analyzer_instructions(self) -> str:
        """Детальные инструкции для url_analyzer"""
        return """
# 🔍 URL Analyzer - Подробные инструкции

## Основные возможности:
- **check_status**: Проверка статуса URL (код ответа, время ответа)
- **get_headers**: Получение HTTP заголовков
- **check_robots**: Проверка robots.txt
- **get_sitemap**: Поиск и анализ sitemap.xml
- **analyze_performance**: Анализ производительности страницы

## Примеры использования:
```python
# Проверка статуса
url_analyzer.call_tool("url_analyzer", {
    "url": "https://example.com",
    "action": "check_status"
})

# Анализ производительности
url_analyzer.call_tool("url_analyzer", {
    "url": "https://example.com",
    "action": "analyze_performance"
})
```
"""
    
    def _get_system_info_instructions(self) -> str:
        """Детальные инструкции для system_info"""
        return """
# ℹ️ System Info - Подробные инструкции

## Основные возможности:
- Информация об операционной системе
- Архитектура процессора
- Версия Python
- Рабочая директория
- Системные ресурсы

## Пример использования:
```python
system_info.call_tool("system_info", {})
```
"""
    
    def _get_process_manager_instructions(self) -> str:
        """Детальные инструкции для process_manager"""
        return """
# 🔧 Process Manager - Подробные инструкции

## Основные возможности:
- **list**: Список запущенных процессов
- **kill**: Завершение процесса по имени
- **start**: Запуск нового процесса

## Примеры использования:
```python
# Список процессов
process_manager.call_tool("process_manager", {
    "action": "list"
})

# Запуск процесса
process_manager.call_tool("process_manager", {
    "action": "start",
    "command": "python script.py"
})
```
"""
    
    def _get_time_helper_instructions(self) -> str:
        """Детальные инструкции для time_helper"""
        return """
# ⏰ Time Helper - Подробные инструкции

## Основные возможности:
- **current_time**: Текущее время и дата
- **timestamp**: Unix timestamp
- **format_time**: Форматирование времени

## Примеры использования:
```python
# Текущее время
time_helper.call_tool("time_helper", {
    "operation": "current_time"
})

# Форматированное время
time_helper.call_tool("time_helper", {
    "operation": "format_time",
    "format": "%Y-%m-%d %H:%M:%S"
})
```
"""
    
    def _get_project_helper_instructions(self) -> str:
        """Детальные инструкции для project_helper"""
        return """
# 🏗️ Project Helper - Подробные инструкции

## Основные возможности:
- **status**: Статус компонентов GopiAI
- **health_check**: Полная проверка здоровья системы
- **check_logs**: Проверка логов
- **restart_server**: Перезапуск сервера

## Примеры использования:
```python
# Проверка здоровья
project_helper.call_tool("project_helper", {
    "action": "health_check"
})

# Статус компонентов
project_helper.call_tool("project_helper", {
    "action": "status",
    "component": "crewai"
})
```
"""
    
    def _get_local_mcp_instructions(self) -> str:
        """Детальные инструкции для local_mcp_tools"""
        return """
# 🌐 Local MCP Tools - Подробные инструкции

## Основные возможности:
- **Web Scraping**: извлечение текста, ссылок, изображений, таблиц, форм
- **HTTP API Client**: GET, POST, PUT, DELETE, PATCH запросы
- **URL Analyzer**: анализ статуса, заголовков, robots.txt, sitemap

## Web Scraper - Примеры использования:

### Извлечение контента:
```python
# Извлечение всего текста
text = local_mcp_tools.call_tool("web_scraper", {
    "action": "extract_text",
    "url": "https://example.com"
})

# Извлечение по CSS селектору
content = local_mcp_tools.call_tool("web_scraper", {
    "action": "extract_custom",
    "url": "https://example.com",
    "selector": "h1, .content"
})
```

### Извлечение структурированных данных:
```python
# Извлечение ссылок
links = local_mcp_tools.call_tool("web_scraper", {
    "action": "extract_links",
    "url": "https://example.com"
})

# Извлечение таблиц
tables = local_mcp_tools.call_tool("web_scraper", {
    "action": "extract_tables",
    "url": "https://example.com"
})
```

## API Client - Примеры использования:

### HTTP запросы:
```python
# GET запрос
response = local_mcp_tools.call_tool("api_client", {
    "method": "GET",
    "url": "https://api.example.com/data",
    "headers": {"Authorization": "Bearer token"}
})

# POST запрос
response = local_mcp_tools.call_tool("api_client", {
    "method": "POST",
    "url": "https://api.example.com/create",
    "data": {"name": "test", "value": 123},
    "headers": {"Content-Type": "application/json"}
})
```

## URL Analyzer - Примеры использования:

### Анализ URL:
```python
# Проверка статуса
status = local_mcp_tools.call_tool("url_analyzer", {
    "action": "check_status",
    "url": "https://example.com"
})

# Анализ производительности
performance = local_mcp_tools.call_tool("url_analyzer", {
    "action": "analyze_performance",
    "url": "https://example.com"
})
```

## ⚠️ Важные замечания:
- Соблюдайте robots.txt и условия использования сайтов
- Используйте разумные задержки между запросами
- Обрабатывайте ошибки сети и таймауты
- Для API запросов всегда проверяйте коды ответов
"""
    
    def _get_browser_instructions(self) -> str:
        """Детальные инструкции для browser_tools"""
        return """
# 🌐 Browser Tools - Подробные инструкции

## Основные возможности:
- **Автоматический выбор движка**: Playwright → Selenium → requests
- **Навигация и взаимодействие**: клики, ввод, прокрутка
- **Извлечение данных**: текст, элементы, скриншоты
- **JavaScript выполнение**: custom скрипты
- **Управление cookies**: получение и установка

## GopiAIBrowserTool - Примеры использования:

### Базовая навигация:
```python
# Переход на страницу
browser_tools._run("navigate", "https://example.com")

# Ожидание загрузки
browser_tools._run("wait", "", "", 3)
```

### Взаимодействие с элементами:
```python
# Клик по элементу
browser_tools._run("click", "button.submit")

# Ввод текста
browser_tools._run("type", "input[name='search']", "поисковый запрос")

# Прокрутка
browser_tools._run("scroll", "down")  # или "up", "top", "bottom"
```

### Извлечение данных:
```python
# Извлечение текста страницы
text = browser_tools._run("extract", "page")

# Извлечение по селектору
content = browser_tools._run("extract", "h1, .content")

# Скриншот
browser_tools._run("screenshot", "screenshot.png")
```

### JavaScript выполнение:
```python
# Выполнение JavaScript
result = browser_tools._run("execute_js", "", "return document.title")

# Получение данных через JS
data = browser_tools._run("execute_js", "", "return {title: document.title, url: window.location.href}")
```

## Web Search Tool - Примеры использования:

### Поиск в разных системах:
```python
# Поиск в Google
results = web_search._run("search", "google", "CrewAI documentation")

# Быстрый поиск в Bing
results = web_search._run("quick_search", "bing", "Python tutorials")
```

## Page Analyzer - Примеры использования:

### Различные типы анализа:
```python
# Общий анализ
summary = page_analyzer._run("summary", "https://example.com")

# SEO анализ
seo = page_analyzer._run("seo", "https://example.com")

# Анализ производительности
performance = page_analyzer._run("performance", "https://example.com")

# Анализ доступности
accessibility = page_analyzer._run("accessibility", "https://example.com")
```

## ⚠️ Важные замечания:
- **Выбор движка**: используйте browser_type="auto" для автоматического выбора
- **Headless режим**: по умолчанию включен, отключайте только при необходимости
- **Очистка ресурсов**: браузер автоматически очищается после использования
- **Селекторы**: используйте CSS селекторы или XPath
- **Таймауты**: устанавливайте разумные значения ожидания
"""
    
    def _get_web_search_instructions(self) -> str:
        """Детальные инструкции для web_search"""
        return """
# 🔍 Web Search - Подробные инструкции

## Поддерживаемые поисковые системы:
- **Google** - наиболее точные результаты
- **Bing** - хорошие результаты, быстрая работа
- **DuckDuckGo** - приватный поиск
- **Yandex** - лучше для русскоязычного контента

## Типы поиска:

### Полный поиск (через браузер):
```python
# Детальный поиск с полной обработкой
results = web_search._run("search", "google", "machine learning tutorials")
```

### Быстрый поиск (через requests):
```python
# Быстрый поиск без запуска браузера
results = web_search._run("quick_search", "bing", "Python documentation")
```

## Рекомендации по использованию:
- **Google**: лучший для технических запросов
- **Bing**: хорош для общих запросов
- **DuckDuckGo**: когда нужна приватность
- **Yandex**: для русскоязычного контента

## ⚠️ Важные замечания:
- Используйте конкретные ключевые слова
- Для быстрых запросов предпочитайте quick_search
- Результаты возвращаются в структурированном виде
"""
    
    def _get_page_analyzer_instructions(self) -> str:
        """Детальные инструкции для page_analyzer"""
        return """
# 📊 Page Analyzer - Подробные инструкции

## Типы анализа:

### summary - Общий анализ:
```python
analyzer._run("summary", "https://example.com")
```
Возвращает: заголовок, описание, количество ссылок и изображений

### seo - SEO анализ:
```python
analyzer._run("seo", "https://example.com")
```
Возвращает: анализ title, meta description, H1, alt атрибутов

### performance - Анализ производительности:
```python
analyzer._run("performance", "https://example.com")
```
Возвращает: время загрузки, количество ресурсов, DOM элементов

### accessibility - Анализ доступности:
```python
analyzer._run("accessibility", "https://example.com")
```
Возвращает: проблемы с alt, labels, структурой заголовков

### security - Анализ безопасности:
```python
analyzer._run("security", "https://example.com")
```
Возвращает: проверка HTTPS, CSRF защиты, внешних скриптов

### links - Анализ ссылок:
```python
analyzer._run("links", "https://example.com")
```
Возвращает: внутренние и внешние ссылки

### forms - Анализ форм:
```python
analyzer._run("forms", "https://example.com")
```
Возвращает: информацию о формах на странице

### images - Анализ изображений:
```python
analyzer._run("images", "https://example.com")
```
Возвращает: список изображений с метаданными

### metadata - Анализ метаданных:
```python
analyzer._run("metadata", "https://example.com")
```
Возвращает: все meta теги страницы

## ⚠️ Важные замечания:
- Анализ может занимать время для больших страниц
- Некоторые метрики требуют полной загрузки страницы
- Результаты зависят от доступности JavaScript на странице
"""
    
    def get_tools_for_prompt(self, include_detailed: bool = False) -> str:
        """
        Формирует текст о доступных инструментах для включения в промпт.
        
        Args:
            include_detailed (bool): Включать ли детальные инструкции
            
        Returns:
            str: Отформатированный текст об инструментах
        """
        tools_summary = self.get_tools_summary()
        
        prompt_text = "\n## 🛠️ Доступные инструменты:\n\n"
        
        for tool_name, description in tools_summary.items():
            prompt_text += f"**{tool_name}**: {description}\n"
        
        prompt_text += "\n💡 **Как использовать**: Когда выбираешь инструмент, я автоматически загружу детальные инструкции по его использованию.\n"
        
        return prompt_text
    
    def save_tools_cache(self) -> bool:
        """
        Сохраняет кеш инструментов в файл для быстрого доступа.
        
        Returns:
            bool: Успешность сохранения
        """
        try:
            cache_file = os.path.join(self.instructions_dir, "tools_cache.json")
            cache_data = {
                "tools_summary": self.get_tools_summary(),
                "last_update": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"💾 Кеш инструментов сохранен в {cache_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения кеша: {e}")
            return False

# Создаем глобальный экземпляр для использования в других модулях
tools_instruction_manager = ToolsInstructionManager()

def get_tools_instruction_manager() -> ToolsInstructionManager:
    """
    Возвращает глобальный экземпляр ToolsInstructionManager.
    
    Returns:
        ToolsInstructionManager: Экземпляр менеджера инструкций
    """
    return tools_instruction_manager
