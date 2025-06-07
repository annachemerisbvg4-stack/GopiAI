# AutoGen Extension for GopiAI

Мультиагентное расширение для GopiAI на базе Microsoft AutoGen с поддержкой Cerebras AI и OpenAI.

## Возможности

- 🤖 **Мультиагентные чаты** с AutoGen
- ⚡ **Cerebras AI интеграция** (в 20x быстрее ChatGPT)
- 🔄 **Умная ротация моделей** с учетом Free Tier лимитов
- 🛡️ **OpenAI fallback** как запасной вариант
- 🎨 **Интеграция в GopiAI UI** через док-виджеты

## Поддерживаемые модели

### Cerebras (основные):
- `llama-3.3-70b` - мощная модель (рекомендуется)
- `llama3.1-8b` - быстрая базовая модель
- `llama-4-scout-17b-16e-instruct` - средняя модель
- `qwen-3-32b` - альтернативная модель

### OpenAI (резерв):
- `gpt-4o-mini` - экономичная модель

## Установка

Расширение требует AutoGen с поддержкой Cerebras:

```bash
pip install "pyautogen[cerebras]"
```

## Настройка

Добавьте API ключи в файл `.env`:

```env
CEREBRAS_API_KEY=csk-your-cerebras-key
OPENAI_API_KEY=sk-your-openai-key
```

## Интеграция в GopiAI

Расширение автоматически интегрируется в систему GopiAI через механизм расширений.

### Ручная активация:

```python
from autogen import init_autogen_extension

# В коде инициализации GopiAI
init_autogen_extension(main_window)
```

## Использование

После активации в GopiAI появится док-виджет "AutoGen Мультиагенты" с:

- Выбором стратегии модели
- Областью чата
- Полем ввода сообщений
- Индикатором статуса

## Стратегии моделей

- **best_first** - использует llama-3.3-70b (рекомендуется)
- **random** - случайная Cerebras модель
- **all_rotation** - ротация между всеми Cerebras моделями  
- **openai_fallback** - переключение на OpenAI

## Лимиты Free Tier

Все Cerebras модели имеют лимиты Free Tier:
- 30 запросов/минута
- 900 запросов/час
- 14400 запросов/день
- 60k токенов/минута

## Архитектура

```
autogen/
├── __init__.py           # Экспорт функций
├── autogen_core.py       # Ядро AutoGen (агенты, менеджер)
├── autogen_extension.py  # UI интеграция
└── README.md            # Документация
```

## Примеры

### Простой чат:
```python
from autogen.autogen_core import autogen_manager

response = autogen_manager.simple_chat(
    "Объясни что такое AutoGen", 
    strategy="best_first"
)
```

### Создание агентов:
```python
# Создаем агентов
user_agent = autogen_manager.create_agent("User", "user_proxy")
assistant_agent = autogen_manager.create_agent("Assistant", "assistant")

# Начинаем чат
result = user_agent.chat("Привет!", assistant_agent)
```

## Безопасность

- Все API ключи загружаются из переменных окружения
- Агенты изолированы и не выполняют код по умолчанию
- Graceful fallback при недоступности сервисов

---

**Интеграция готова! AutoGen теперь часть экосистемы GopiAI** 🚀