# GopiAI Assets Module

Это модуль ресурсов для приложения GopiAI, содержащий изображения, иконки, шрифты и другие ресурсы.

## Структура модуля

```
gopiai-assets/
├── gopiai/
│   ├── __init__.py  # namespace package
│   └── assets/
│       ├── __init__.py
│       ├── titlebar_with_menu.py  # Компонент заголовка окна с меню
│       ├── images/                # Изображения
│       ├── icons/                 # Иконки
│       └── fonts/                 # Шрифты
├── tests/                         # Тесты модуля
├── examples/                      # Примеры использования
└── pyproject.toml                 # Конфигурация пакета
```

## Разработка

1. Этот модуль содержит ресурсы и компоненты интерфейса, которые используются в приложении.
2. Ресурсы организованы по типам (изображения, иконки, шрифты).
3. Используйте абсолютные импорты через namespace `gopiai`:
   ```python
   from gopiai.assets.titlebar_with_menu import TitlebarWithMenu
   ```

## Добавление новых ресурсов

### Добавление изображения

1. Поместите файл изображения в папку `gopiai/assets/images/`.
2. Создайте функцию для загрузки изображения в `gopiai/assets/__init__.py`:
   ```python
   def get_image(name):
       """Возвращает путь к изображению по имени."""
       import os
       return os.path.join(os.path.dirname(__file__), "images", name)
   ```

### Добавление иконки

1. Поместите файл иконки в папку `gopiai/assets/icons/`.
2. Создайте функцию для загрузки иконки в `gopiai/assets/__init__.py`:
   ```python
   def get_icon(name):
       """Возвращает путь к иконке по имени."""
       import os
       return os.path.join(os.path.dirname(__file__), "icons", name)
   ```

### Добавление шрифта

1. Поместите файл шрифта в папку `gopiai/assets/fonts/`.
2. Создайте функцию для загрузки шрифта в `gopiai/assets/__init__.py`:
   ```python
   def get_font(name):
       """Возвращает путь к шрифту по имени."""
       import os
       return os.path.join(os.path.dirname(__file__), "fonts", name)
   ```

## Тестирование

Запуск тестов:
```bash
cd gopiai-assets
pytest tests/
```

## Запуск примеров

```bash
cd gopiai-assets
python examples/run_titlebar.py
```

## Интеграция с другими модулями

Этот модуль зависит только от модуля `gopiai-core`. Другие модули могут использовать ресурсы из этого модуля.

## Важные замечания

1. Ресурсы должны быть организованы по типам.
2. Используйте функции для доступа к ресурсам, а не прямые пути.
3. Следите за размером ресурсов, чтобы не увеличивать размер приложения без необходимости.
