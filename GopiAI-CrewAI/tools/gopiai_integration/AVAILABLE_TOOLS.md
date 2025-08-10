# 🔧 Доступные инструменты GopiAI

## 📋 Обзор

Система GopiAI предоставляет набор специализированных инструментов для работы с CrewAI. Все инструменты разделены на категории по важности и функциональности.

## ✅ ОСНОВНЫЕ ИНСТРУМЕНТЫ (рекомендуемые)

Это минимальный набор инструментов, который покрывает основные потребности LLM:

### 1. 📁 GopiAIFileSystemTool
**Класс:** `GopiAIFileSystemTool`  
**Описание:** Безопасная работа с файловой системой  
**Возможности:**
- Чтение и запись файлов
- Создание и удаление файлов/папок
- Работа с JSON и CSV
- Поиск файлов
- Архивирование
- Создание резервных копий
- Поиск текста в файлах

**Пример использования:**
```python
from tools.gopiai_integration import GopiAIFileSystemTool

tool = GopiAIFileSystemTool()
result = tool._run(action="read", path="/path/to/file.txt")
```

### 2. 💻 TerminalTool
**Класс:** `TerminalTool`  
**Описание:** Выполнение команд в терминале с отображением в UI  
**Возможности:**
- Безопасное выполнение команд
- Логирование в UI
- Режим безопасности
- Валидация команд

**Пример использования:**
```python
from tools.gopiai_integration import TerminalTool

tool = TerminalTool()
result = tool._run(command="ls -la")
```

### 3. 🔍 GopiAIWebSearchTool
**Класс:** `GopiAIWebSearchTool`  
**Описание:** Поиск информации в интернете через разные поисковые системы  
**Возможности:**
- DuckDuckGo (без API ключа)
- Google (скрапинг)
- Serper API (с ключом)
- SerpAPI (с ключом)
- Автоматический выбор лучшего метода

**Пример использования:**
```python
from tools.gopiai_integration import GopiAIWebSearchTool

tool = GopiAIWebSearchTool()
result = tool._run(query="Python programming", num_results=10)
```

### 4. 🌐 GopiAIWebViewerTool
**Класс:** `GopiAIWebViewerTool`  
**Описание:** Просмотр веб-страниц и извлечение контента  
**Возможности:**
- Загрузка веб-страниц
- Извлечение текста
- Поиск ссылок
- Получение метаданных
- Кэширование страниц

**Пример использования:**
```python
from tools.gopiai_integration import GopiAIWebViewerTool

tool = GopiAIWebViewerTool()
result = tool._run(action="fetch", url="https://example.com")
```

## 🔧 ДОПОЛНИТЕЛЬНЫЕ ИНСТРУМЕНТЫ

### 5. 🧠 GopiAIMemoryTool
**Класс:** `GopiAIMemoryTool`  
**Описание:** Система долговременной памяти и RAG  
**Возможности:**
- Сохранение информации
- Поиск по памяти
- Категоризация
- Суммаризация

### 6. 📡 GopiAICommunicationTool
**Класс:** `GopiAICommunicationTool`  
**Описание:** Коммуникация между агентами и с UI  
**Возможности:**
- Отправка сообщений
- Получение сообщений
- Широковещание
- Уведомления

## ❌ ОТКЛЮЧЕННЫЕ ИНСТРУМЕНТЫ

### GopiAIBrowserTool (ОТКЛЮЧЕНО)
**Причина отключения:** По решению команды браузерная автоматизация отключена  
**Альтернатива:** Используйте `GopiAIWebViewerTool` для просмотра веб-страниц

## 🚀 Быстрый старт

### Получение всех основных инструментов:
```python
from tools.gopiai_integration import get_essential_tools

tools = get_essential_tools()
```

### Получение конкретного инструмента:
```python
from tools.gopiai_integration import get_tool_by_name

filesystem_tool = get_tool_by_name('filesystem')
search_tool = get_tool_by_name('web_search')
```

### Создание агента с основными инструментами:
```python
from crewai import Agent
from tools.gopiai_integration import get_essential_tools

agent = Agent(
    role='Research Assistant',
    goal='Help with research and file management',
    backstory='I am a helpful assistant with access to essential tools',
    tools=get_essential_tools(),
    verbose=True
)
```

## 📊 Статус инструментов

| Инструмент | Статус | Описание |
|------------|--------|----------|
| GopiAIFileSystemTool | ✅ Активен | Работа с файлами |
| TerminalTool | ✅ Активен | Выполнение команд |
| GopiAIWebSearchTool | ✅ Активен | Поиск в интернете |
| GopiAIWebViewerTool | ✅ Активен | Просмотр веб-страниц |
| GopiAIMemoryTool | 🔧 Дополнительный | Система памяти |
| GopiAICommunicationTool | 🔧 Дополнительный | Коммуникация |
| GopiAIBrowserTool | ❌ Отключен | Браузерная автоматизация |

## 🔒 Безопасность

Все инструменты имеют встроенные механизмы безопасности:
- Валидация входных данных
- Ограничения на выполнение опасных операций
- Логирование всех действий
- Таймауты для предотвращения зависания

## 🐛 Устранение неполадок

### LLM галлюцинирует несуществующие инструменты
**Решение:** Используйте только инструменты из списка выше. Проверьте импорты.

### Ошибки импорта
**Решение:** Убедитесь, что все зависимости установлены:
```bash
pip install requests beautifulsoup4 crewai
```

### Браузерная автоматизация не работает
**Решение:** Браузерная автоматизация отключена. Используйте `GopiAIWebViewerTool`.

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в консоли
2. Убедитесь в правильности параметров
3. Используйте только активные инструменты
4. Обратитесь к документации конкретного инструмента