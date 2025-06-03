# GopiAI App Module

Это основной модуль приложения GopiAI, содержащий логику, интерфейсы и инструменты для работы приложения.

## Структура модуля

```
gopiai-app/
├── gopiai/
│   ├── __init__.py  # namespace package
│   └── app/
│       ├── __init__.py
│       ├── agent/                # Агенты для работы с ИИ
│       ├── logic/                # Бизнес-логика приложения
│       ├── ui/                   # Компоненты пользовательского интерфейса
│       │   ├── icon_adapter.py   # Адаптер для работы с иконками
│       │   └── ...
│       ├── tool/                 # Инструменты для работы с внешними сервисами
│       └── utils/                # Утилиты
│           ├── theme_loader.py   # Загрузчик тем
│           └── ...
├── tests/                        # Тесты модуля
├── examples/                     # Примеры использования
└── pyproject.toml                # Конфигурация пакета
```

## Разработка

1. Этот модуль содержит основную логику приложения и компоненты пользовательского интерфейса.
2. Модуль разделен на подмодули по функциональности.
3. Используйте абсолютные импорты через namespace `gopiai`:
   ```python
   from gopiai.app.ui.icon_adapter import IconAdapter
   ```

## Добавление новой функциональности

1. Определите, к какому подмодулю относится новая функциональность:
   - `agent` - для работы с ИИ
   - `logic` - для бизнес-логики
   - `ui` - для компонентов интерфейса
   - `tool` - для инструментов
   - `utils` - для утилит

2. Создайте новый файл в соответствующей папке, например `gopiai/app/ui/my_component.py`:
   ```python
   from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

   class MyComponent(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self.layout = QVBoxLayout(self)
           self.label = QLabel("Мой компонент", self)
           self.layout.addWidget(self.label)
   ```

3. Создайте тесты для компонента в папке `tests/`:
   ```python
   # tests/test_my_component.py
   import pytest
   from PySide6.QtWidgets import QApplication
   from gopiai.app.ui.my_component import MyComponent

   def test_my_component():
       app = QApplication([])
       component = MyComponent()
       assert component is not None
   ```

4. Создайте пример использования в папке `examples/`:
   ```python
   # examples/run_my_component.py
   import sys
   from PySide6.QtWidgets import QApplication
   from gopiai.app.ui.my_component import MyComponent

   def main():
       app = QApplication(sys.argv)
       component = MyComponent()
       component.show()
       sys.exit(app.exec())

   if __name__ == "__main__":
       main()
   ```

## Тестирование

Запуск тестов:
```bash
cd gopiai-app
pytest tests/
```

## Запуск примеров

```bash
cd gopiai-app
python examples/run_my_component.py
```

## Интеграция с другими модулями

Этот модуль зависит от модулей `gopiai-core`, `gopiai-widgets` и `gopiai-extensions`. Он содержит основную логику приложения и компоненты пользовательского интерфейса.

## Важные замечания

1. Разделяйте код на логические компоненты и размещайте их в соответствующих подмодулях.
2. Используйте паттерны проектирования для организации кода.
3. Пишите тесты для всех компонентов.
4. Документируйте публичные API.
