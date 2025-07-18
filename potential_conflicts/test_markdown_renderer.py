#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы markdown рендерера.
"""

import sys
import os

# Добавляем путь к модулям GopiAI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gopiai'))

from gopiai.ui.utils.markdown_renderer import render_markdown

def test_markdown_rendering():
    """Тестирует различные элементы markdown."""
    
    test_cases = [
        # Заголовки
        "# Заголовок 1\n## Заголовок 2\n### Заголовок 3",
        
        # Жирный и курсив
        "Это **жирный текст** и *курсивный текст*.",
        "Также можно использовать __жирный__ и _курсивный_ текст.",
        
        # Код
        "Вот `inline код` в тексте.",
        "```python\ndef hello():\n    print('Hello, World!')\n```",
        
        # Списки
        "- Первый элемент\n- Второй элемент\n- Третий элемент",
        "1. Первый пункт\n2. Второй пункт\n3. Третий пункт",
        
        # Ссылки
        "Посетите [Google](https://google.com) для поиска.",
        
        # Смешанный контент
        """# Пример ответа ИИ

Привет! Вот что я могу сделать:

## Основные возможности

1. **Анализ кода** - проверка синтаксиса и логики
2. **Создание документации** - автоматическое описание функций
3. **Рефакторинг** - улучшение структуры кода

### Пример кода

```python
def process_data(data):
    # Обработка данных
    result = []
    for item in data:
        if item.is_valid():
            result.append(item.transform())
    return result
```

Для получения дополнительной информации посетите [документацию](https://example.com).

*Удачи в программировании!*"""
    ]
    
    print("=== ТЕСТИРОВАНИЕ MARKDOWN РЕНДЕРЕРА ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- Тест {i} ---")
        print("Исходный markdown:")
        print(repr(test_case))
        print("\nРезультат HTML:")
        result = render_markdown(test_case)
        print(result)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    test_markdown_rendering()