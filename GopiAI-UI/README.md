# GopiAI UI Module 

Модуль пользовательского интерфейса для GopiAI.

## Структура

```
gopiai/
  ui/
    base/           # Базовые классы окон и компонентов
    components/     # UI компоненты
    dialogs/        # Диалоговые окна
    utils/          # Утилиты (иконки, темы)
    windows/        # Основные окна
    assets/         # Ресурсы (иконки, стили)
```

## Использование

```python
from gopiai.ui.base import BaseWindow
from gopiai.ui.components import TextEditorWidget
from gopiai.ui.utils import UniversalIconManager
```

## Зависимости

Основные зависимости:
- PySide6 - графический интерфейс
- txtai - поиск и анализ текста
- sentence-transformers - векторизация текста

## Установка

```bash
# Установка зависимостей
pip install txtai sentence-transformers

# Установка для разработки
pip install -e .
```
