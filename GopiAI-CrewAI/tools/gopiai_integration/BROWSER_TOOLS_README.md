# 🌐 GopiAI Browser Tools - Расширенная документация

## 📋 Обзор

Полностью переработанные браузерные инструменты с поддержкой множественных движков и расширенной функциональности.

## 🚀 Основные возможности

### 1. **GopiAIBrowserTool** - Основной браузерный инструмент
- ✅ **Автоматический выбор движка**: Playwright → Selenium → requests
- ✅ **Полная функциональность**: навигация, клики, ввод, скриншоты, JavaScript
- ✅ **Управление cookies и прокрутка**
- ✅ **Headless и обычный режимы**

### 2. **GopiAIWebSearchTool** - Улучшенный веб-поиск
- ✅ **Множественные поисковые системы**: Google, Bing, DuckDuckGo, Yandex
- ✅ **Быстрый и полный поиск**
- ✅ **Структурированные результаты**

### 3. **GopiAIPageAnalyzerTool** - Мощный анализатор страниц
- ✅ **Комплексный анализ**: SEO, производительность, доступность, безопасность
- ✅ **Анализ контента**: ссылки, формы, изображения, метаданные
- ✅ **Детальные отчеты**

## 🔧 Установка зависимостей

```bash
# Базовые зависимости (обязательно)
pip install requests beautifulsoup4

# Playwright (рекомендуется)
pip install playwright
playwright install

# Selenium (альтернатива)
pip install selenium
# + ChromeDriver или GeckoDriver

# Все зависимости сразу
pip install -r browser_requirements.txt
```

## 📖 Примеры использования

### Основной браузерный инструмент
```python
from browser_tools import GopiAIBrowserTool

browser = GopiAIBrowserTool()

# Навигация
browser._run("navigate", "https://example.com")

# Клик по элементу
browser._run("click", "button.submit")

# Ввод текста
browser._run("type", "input[name='search']", "поисковый запрос")

# Скриншот
browser._run("screenshot", "screenshot.png")

# Выполнение JavaScript
browser._run("execute_js", "", "return document.title")

# Извлечение данных
browser._run("extract", "h1, h2, h3")
```

### Веб-поиск
```python
from browser_tools import GopiAIWebSearchTool

search = GopiAIWebSearchTool()

# Поиск в Google
search._run("search", "google", "CrewAI documentation")

# Быстрый поиск в Bing
search._run("quick_search", "bing", "Python tutorials")
```

### Анализ страниц
```python
from browser_tools import GopiAIPageAnalyzerTool

analyzer = GopiAIPageAnalyzerTool()

# Общий анализ
analyzer._run("summary", "https://example.com")

# SEO анализ
analyzer._run("seo", "https://example.com")

# Анализ производительности
analyzer._run("performance", "https://example.com")

# Анализ доступности
analyzer._run("accessibility", "https://example.com")
```

## 🎯 Типы действий

### GopiAIBrowserTool
- `navigate` - Переход на URL
- `click` - Клик по элементу
- `type` - Ввод текста
- `extract` - Извлечение данных
- `screenshot` - Создание скриншота
- `scroll` - Прокрутка страницы
- `execute_js` - Выполнение JavaScript
- `get_cookies` - Получение cookies
- `wait` - Ожидание

### GopiAIWebSearchTool
- `search` - Полный поиск через браузер
- `quick_search` - Быстрый поиск через requests

### GopiAIPageAnalyzerTool
- `summary` - Общий анализ страницы
- `links` - Анализ ссылок
- `forms` - Анализ форм
- `images` - Анализ изображений
- `metadata` - Анализ метаданных
- `seo` - SEO анализ
- `performance` - Анализ производительности
- `accessibility` - Анализ доступности
- `security` - Анализ безопасности
- `extract` - Извлечение контента

## 🔍 Проверка доступности движков

```python
from browser_tools import get_browser_capabilities, get_recommended_browser_engine

# Проверка доступных движков
print(get_browser_capabilities())
# {'selenium': True, 'playwright': True, 'requests': True}

# Рекомендуемый движок
print(get_recommended_browser_engine())
# 'playwright'
```

## ⚡ Производительность

1. **Playwright** - Лучшая производительность и стабильность
2. **Selenium** - Хорошая совместимость, средняя производительность
3. **requests** - Быстро, но ограниченная функциональность

## 🛠️ Отладка

Запустите тесты для проверки работоспособности:

```bash
python browser_tools.py
```

## 🔒 Безопасность

- Все инструменты поддерживают headless режим
- Автоматическая очистка ресурсов браузера
- Безопасная обработка ошибок
- Контроль таймаутов

## 📝 Логирование

Инструменты используют стандартное Python логирование:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🎉 Заключение

Обновленные браузерные инструменты обеспечивают:
- ✅ Максимальную совместимость
- ✅ Высокую производительность
- ✅ Расширенную функциональность
- ✅ Простоту использования
- ✅ Надежность и стабильность
