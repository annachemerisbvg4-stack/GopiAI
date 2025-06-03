# GopiAI Widgets Module

Это модуль пользовательских виджетов для приложения GopiAI, содержащий различные виджеты, используемые в приложении.

## Структура модуля

```
gopiai-widgets/
├── gopiai/
│   ├── __init__.py  # namespace package
│   └── widgets/
│       ├── __init__.py
│       ├── text_editor.py     # Текстовый редактор с нумерацией строк
│       ├── simple_label.py    # Расширенная метка с автообновлением и анимацией
│       ├── card_widget.py     # Виджет карточки с заголовком, содержимым и кнопками
│       └── custom_grips/      # Компоненты для изменения размера окна
│           ├── __init__.py
│           └── custom_grips.py
├── tests/                     # Тесты модуля
│   ├── test_text_editor.py
│   ├── test_simple_label.py
│   └── test_card_widget.py
├── examples/                  # Примеры использования
│   ├── run_text_editor.py
│   ├── run_simple_label.py
│   └── run_card_widget.py
└── pyproject.toml             # Конфигурация пакета
```

## Разработка

1. Этот модуль содержит пользовательские виджеты, которые могут быть использованы в приложении.
2. Каждый виджет должен быть самодостаточным и не зависеть от других модулей (кроме core).
3. Используйте абсолютные импорты через namespace `gopiai`:
   ```python
   from gopiai.widgets.text_editor import TextEditorWidget
   ```

## Добавление нового виджета

1. Создайте новый файл в папке `gopiai/widgets/`, например `my_widget.py`:
   ```python
   from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

   class MyWidget(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self.layout = QVBoxLayout(self)
           self.label = QLabel("Мой виджет", self)
           self.layout.addWidget(self.label)
   ```

2. Добавьте импорт в `gopiai/widgets/__init__.py`:
   ```python
   from gopiai.widgets.my_widget import MyWidget
   ```

3. Создайте тесты для виджета в папке `tests/`:
   ```python
   # tests/test_my_widget.py
   import pytest
   from PySide6.QtWidgets import QApplication
   from gopiai.widgets.my_widget import MyWidget

   def test_my_widget():
       app = QApplication([])
       widget = MyWidget()
       assert widget is not None
   ```

4. Создайте пример использования в папке `examples/`:
   ```python
   # examples/run_my_widget.py
   import sys
   from PySide6.QtWidgets import QApplication
   from gopiai.widgets.my_widget import MyWidget

   def main():
       app = QApplication(sys.argv)
       widget = MyWidget()
       widget.show()
       sys.exit(app.exec())

   if __name__ == "__main__":
       main()
   ```

## Тестирование

Запуск тестов:
```bash
cd gopiai-widgets
pytest tests/
```

## Запуск примеров

```bash
cd gopiai-widgets
python examples/run_text_editor.py
```

## Интеграция с другими модулями

Этот модуль зависит только от модуля `gopiai-core`. Другие модули могут использовать виджеты из этого модуля.

## Важные замечания

1. Виджеты должны быть максимально независимыми и переиспользуемыми.
2. Каждый виджет должен иметь тесты и примеры использования.
3. Не добавляйте в виджеты бизнес-логику, которая должна быть в модуле `gopiai-app`.
