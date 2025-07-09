# 🚀 GopiAI-CrewAI Complete Integration Guide

## 📋 Обзор

Полная интеграция многоагентной системы CrewAI с платформой GopiAI, включающая:

- ✅ **5 специализированных инструментов** для агентов CrewAI
- ✅ **Поддержка бесплатных LLM** (Gemini и Gemma от Google)
- ✅ **Автоматическая ротация моделей** при лимитах
- ✅ **Интеграция с GopiAI UI** через систему уведомлений
- ✅ **Долговременная память** и RAG система
- ✅ **Межагентная коммуникация** в реальном времени

## 🛠 Установленные компоненты

### 📦 Основные пакеты
```
crewai==0.130.0           # Многоагентная система
langchain-groq            # Groq LLM интеграция
langchain-google-genai    # Google Gemini интеграция
langchain-openai          # OpenAI совместимые LLM
python-dotenv             # Управление переменными окружения
requests                  # HTTP запросы для браузера
```

### 🔧 GopiAI инструменты

#### 1. 🌐 Browser Tool (`browser_tools.py`)
**Возможности:**
- Поиск информации в интернете
- Получение контента веб-страниц
- Извлечение текста из HTML
- Кеширование результатов

**Примеры использования:**
```python
# Поиск информации
browser_tool.run("search", "CrewAI best practices", "", 5)

# Получение контента страницы
browser_tool.run("fetch", "https://docs.crewai.com", "", 0)

# Извлечение текста
browser_tool.run("extract", "https://example.com", "title", 0)
```

#### 2. 📁 FileSystem Tool (`filesystem_tools.py`)
**Возможности:**
- Чтение и запись файлов
- Создание и удаление файлов/папок
- Поиск файлов по паттернам
- Безопасная работа с файловой системой

**Примеры использования:**
```python
# Чтение файла
fs_tool.run("read", "config.json", "", "", "")

# Запись файла
fs_tool.run("write", "report.md", "# Report\\nContent", "utf-8", "")

# Поиск файлов
fs_tool.run("find", "*.py", "src/", "", "")
```

#### 3. 🔀 AI Router Tool (`ai_router_tools.py`)
**Возможности:**
- Ротация между LLM провайдерами
- Автоматический fallback при лимитах
- Мониторинг использования API
- Оптимизация под задачи

**Примеры использования:**
```python
# Маршрутизация запроса
router_tool.run("route", "Переведи на английский", "auto", 0.7, 100)

# Принудительный выбор модели
router_tool.run("route", "Creative task", "gemma", 0.9, 500)

# Проверка статуса провайдеров
router_tool.run("status", "", "", 0, 0)
```

#### 4. 🧠 Memory Tool (`memory_tools.py`)
**Возможности:**
- Долговременное хранение информации
- Семантический поиск по данным
- Категоризация знаний
- Интеграция с RAG системой GopiAI

**Примеры использования:**
```python
# Сохранение информации
memory_tool.run("store", "project_config", "Настройки проекта", "config", 8)

# Поиск в памяти
memory_tool.run("search", "CrewAI settings", "all")

# Создание сводки
memory_tool.run("summarize", "project status", "", "", 0)
```

#### 5. 📡 Communication Tool (`communication_tools.py`)
**Возможности:**
- Обмен сообщениями между агентами
- Уведомления пользователя через UI
- Мониторинг статуса агентов
- Broadcast сообщения

**Примеры использования:**
```python
# Отправка сообщения агенту
comm_tool.run("send", "researcher_agent", "Найди информацию о X", "task", 4)

# Уведомление пользователя
comm_tool.run("notify", "", "Задача выполнена", "result", 3)

# Проверка статуса агентов
comm_tool.run("list_agents", "", "", "", 0)
```

## 🔑 Настройка API ключей

### .env файл
```env
# Бесплатные провайдеры (рекомендуется)
GOOGLE_API_KEY=AIza_ваш_ключ_gemini

# Дополнительные настройки
GOPIAI_BROWSER_CACHE=true
GOPIAI_MEMORY_PATH=./memory/
GOPIAI_COMM_PATH=./communication/
```

### 📝 Как получить ключи

#### 1. **Google Gemini (стабильный)** ⭐
- Сайт: https://aistudio.google.com
- Бесплатно: 15 запросов/минуту
- Модель: `gemini-1.5-flash`
- Ключ начинается с `AIza`

## 🚀 Запуск и использование

### Базовый запуск
```bash
cd GopiAI-CrewAI
python main.py
```

### Варианты демонстраций
1. **Простая демонстрация** - 1 агент, базовые инструменты
2. **Продвинутая демонстрация** - 3 агента, все инструменты  
3. **Только тесты** - проверка всех компонентов

### Пример создания агента
```python
from crewai import Agent, Task, Crew, LLM
from gopiai_integration.memory_tools import GopiAIMemoryTool
from gopiai_integration.communication_tools import GopiAICommunicationTool

# LLM с автоматическим fallback
llm = LLM(model="gemini/gemini-1.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))

# Агент с GopiAI инструментами
agent = Agent(
    role='Smart Assistant',
    goal='Помогать пользователю с использованием всех возможностей GopiAI',
    backstory='Ты умный ассистент с доступом к памяти, коммуникации и всем инструментам.',
    tools=[GopiAIMemoryTool(), GopiAICommunicationTool()],
    llm=llm,
    verbose=True
)

# Задача с использованием инструментов
task = Task(
    description="""
    1. Сохрани информацию о новом проекте в память
    2. Уведоми пользователя о начале работы
    3. Создай план дальнейших действий
    """,
    expected_output="Отчет о выполнении задачи",
    agent=agent
)

# Crew и запуск
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

## 📁 Структура проекта

```
GopiAI-CrewAI/
├── main.py                    # Основной модуль интеграции
├── requirements.txt           # Зависимости
├── .env.example              # Пример переменных окружения
├── tools/                    # GopiAI инструменты
│   └── gopiai_integration/
│       ├── __init__.py
│       ├── browser_tools.py      # 🌐 Браузер
│       ├── filesystem_tools.py   # 📁 Файловая система
│       ├── ai_router_tools.py    # 🔀 AI роутер
│       ├── memory_tools.py       # 🧠 Память
│       └── communication_tools.py # 📡 Коммуникация
├── memory/                   # Локальная память
├── communication/            # Сообщения и статусы
├── cache/                    # Кеш браузера
└── free-models-rate-limits/  # Справочники по лимитам
    ├── gemini_limits.md
```

## 🔄 Ротация LLM провайдеров

### Автоматическая ротация
Система автоматически переключается между провайдерами при:
- Превышении лимитов API
- Ошибках подключения
- Таймаутах запросов

### Приоритет провайдеров
1. **Google Gemini** - стабильный, большие лимиты

### Мониторинг использования
```python
# Проверка статуса всех провайдеров
router_tool.run("status", "", "", 0, 0)

# Статистика использования
router_tool.run("stats", "", "", 0, 0)
```

## 🔧 Расширение и кастомизация

### Добавление нового инструмента
```python
from crewai_tools import BaseTool
from pydantic import BaseModel, Field

class CustomInput(BaseModel):
    action: str = Field(description="Действие")
    data: str = Field(description="Данные")

class CustomGopiAITool(BaseTool):
    name: str = "custom_gopiai_tool"
    description: str = "Описание инструмента"
    args_schema: Type[BaseModel] = CustomInput
    
    def _run(self, action: str, data: str) -> str:
        # Ваша логика
        return f"Выполнено: {action} с {data}"
```

### Интеграция с GopiAI UI
```python
# Отправка уведомления в UI
comm_tool.run("notify", "", "Статус обновлен", "info", 3, 
              '{"module": "crewai", "progress": 75}')

# Сохранение результатов для UI
memory_tool.run("store", "ui_report", "Данные для отображения", "ui", 7)
```

## 🐛 Диагностика проблем

### Частые проблемы и решения

#### 1. Ошибки API ключей

**Решение:** Проверьте формат ключа (должен начинаться с `AIza`)

#### 2. Лимиты провайдеров

**Решение:** Система автоматически переключится на другой провайдер

#### 3. Ошибки инструментов
**Решение:** Проверьте интернет-соединение или используйте другие инструменты

### Логи и мониторинг
```python
# Включение подробного логирования
import logging
logging.basicConfig(level=logging.DEBUG)

# Проверка всех компонентов
python main.py  # Выберите режим "3" для тестов
```

## 🚀 Планы развития

### Ближайшие обновления
- [ ] Поддержка векторного поиска в Memory Tool
- [ ] Расширенные возможности Browser Tool (скриншоты, автоматизация)
- [ ] Интеграция с дополнительными LLM провайдерами

### Долгосрочные планы  
- [ ] Автоматическое обучение агентов на истории
- [ ] Интеграция с внешними сервисами (календари, почта, CRM)

## 📞 Поддержка

При возникновении проблем:

1. Проверьте настройку .env файла
2. Запустите тест всех компонентов: `python main.py` → режим "3"  
3. Изучите логи в консоли
4. Проверьте лимиты API в справочниках `free-models-rate-limits/`

---

**🎉 GopiAI + CrewAI = Мощная платформа для многоагентного ИИ!**

Полная интеграция готова к использованию. Система автоматически управляет LLM провайдерами, обеспечивает коммуникацию между агентами и предоставляет широкий набор инструментов для решения сложных задач.