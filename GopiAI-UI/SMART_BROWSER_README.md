# 🧠 Smart Browser Agent

Умный агент браузера с автоматическим определением URL через Brave API.

## ✨ Особенности

- **Автоматическое определение URL** из естественных команд
- **Поддержка русского и английского языков**
- **Интеграция с Brave Search API** для поиска сайтов
- **Простая интеграция** с существующими браузерными виджетами
- **История команд** и логирование

## 🚀 Быстрый старт

### 1. Базовое использование

```python
from SmartBrowserAgent import SmartBrowserAgent

# Инициализация с вашим Brave API ключом
agent = SmartBrowserAgent("ваш_brave_api_ключ")

# Обработка команд
result = agent.process_command("зайди на сайт leonardo ai")
print(f"URL найден: {result['url']}")  # https://leonardo.ai
```

### 2. Интеграция с существующим браузерным виджетом

```python
from browser_integration import enhance_browser_widget_with_smart_navigation

# Добавляем умную навигацию к вашему браузерному виджету
enhance_browser_widget_with_smart_navigation(your_browser_widget, "ваш_brave_api_ключ")

# Теперь можно использовать естественные команды
your_browser_widget.smart_navigate("открой github")
your_browser_widget.smart_navigate("перейди на stackoverflow")
```

### 3. Автоматический патч для GopiAI-UI

```python
from browser_integration import patch_enhanced_browser_widget

# Автоматически добавляет умную навигацию ко всем браузерным виджетам
patch_enhanced_browser_widget()
```

## 📝 Поддерживаемые команды

### Русский язык:
- `зайди на сайт leonardo ai`
- `открой сайт github`
- `перейди на stackoverflow`
- `найди документацию python`
- `поищи react tutorials`

### English:
- `go to leonardo ai`
- `open github`
- `visit stackoverflow`
- `navigate to google`
- `search for python docs`

### Прямые URL:
- `https://leonardo.ai`
- `http://github.com`

## 🔧 Как это работает

1. **Анализ команды**: Система разбирает естественную команду с помощью регулярных выражений
2. **Извлечение запроса**: Выделяет ключевые слова для поиска (убирает "сайт", "website", etc.)
3. **Поиск через Brave API**: Ищет наиболее релевантный сайт
4. **Возврат URL**: Возвращает URL первого результата поиска

## 🛠 Конфигурация

### Получение Brave API ключа:
1. Зарегистрируйтесь на [Brave Search API](https://api.search.brave.com/)
2. Получите API ключ
3. Используйте его при инициализации агента

### Настройка паттернов команд:
```python
# В SmartURLDetector можно добавить свои паттерны
command_patterns = {
    'go_to_site': [
        r'зайди на сайт (.+)',
        r'твой_новый_паттерн (.+)',
        # ...
    ]
}
```

## 📊 API Reference

### SmartBrowserAgent

#### `__init__(brave_api_key: str, browser_use_agent=None)`
- `brave_api_key`: Ваш Brave API ключ
- `browser_use_agent`: Опциональный браузерный агент для выполнения навигации

#### `process_command(command: str) -> Dict[str, Any]`
Обрабатывает команду и возвращает результат:
```python
{
    'success': bool,
    'url': str | None,
    'message': str,
    'browser_result': Any  # если browser_agent подключен
}
```

#### `get_session_history() -> List[Dict]`
Возвращает историю команд сессии.

### SmartURLDetector

#### `detect_url(command: str) -> Optional[str]`
Основной метод для определения URL из команды.

#### `search_url_with_brave(query: str) -> Optional[str]`
Поиск URL через Brave API.

## 🧪 Тестирование

```bash
# Запуск тестов для SmartBrowserAgent
python SmartBrowserAgent.py

# Тест интеграции
python browser_integration.py
```

## 📝 Примеры результатов

```
Команда: зайди на сайт leonardo ai
✅ URL найден: https://leonardo.ai

Команда: открой github
✅ URL найден: https://github.com

Команда: visit stackoverflow
✅ URL найден: https://stackoverflow.com

Команда: найди документацию python
✅ URL найден: https://docs.python.org
```

## 🚧 Ограничения

- Требует интернет-соединение для работы с Brave API
- Лимиты API Brave Search (зависят от вашего плана)
- Может не найти очень специфичные или новые сайты

## 🔮 Будущие улучшения

- [ ] Поддержка fallback на другие поисковые системы
- [ ] Кэширование популярных запросов
- [ ] Улучшение NLP для более сложных команд
- [ ] Поддержка контекстных команд ("открой тот же сайт, что и вчера")
- [ ] Интеграция с голосовыми командами

## 🤝 Вклад в проект

Если хотите улучшить Smart Browser Agent:
1. Добавьте новые паттерны команд
2. Улучшите логику определения URL
3. Добавьте поддержку новых языков
4. Оптимизируйте работу с API

---

**Автор:** Твой любимый AI помощник ❤️  
**Версия:** 1.0.0  
**Лицензия:** MIT
