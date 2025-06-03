# GopiAI Extensions Module

Это модуль расширений для приложения GopiAI, содержащий различные интеграции и расширения для базового приложения, такие как файловый проводник, терминал, браузер и др.

## Структура модуля

```
gopiai-extensions/
├── gopiai/
│   ├── __init__.py  # namespace package
│   └── extensions/
│       ├── __init__.py                    # Система подключения расширений
│       ├── project_explorer_integration.py  # Интеграция проводника проектов
│       ├── terminal_integration.py        # Интеграция терминала
│       ├── browser_integration.py         # Интеграция браузера
│       ├── simple_chat_integration.py     # Интеграция чата
│       ├── status_bar_extension.py        # Расширение статусной строки
│       ├── notification_center_extension.py # Центр уведомлений
│       └── dock_manager_extension.py      # Менеджер док-виджетов
├── tests/                                 # Тесты модуля
│   ├── test_extensions_loading.py
│   ├── test_status_bar_extension.py
│   └── test_notification_center_extension.py
├── examples/                              # Примеры использования
│   ├── run_project_explorer.py
│   ├── run_status_bar.py
│   └── run_notification_center.py
└── pyproject.toml                         # Конфигурация пакета
```

## Разработка

1. Этот модуль содержит расширения, которые добавляют функциональность к базовому приложению.
2. Каждое расширение должно быть независимым и подключаться через систему расширений.
3. Используйте абсолютные импорты через namespace `gopiai`:
   ```python
   from gopiai.extensions.project_explorer_integration import add_project_explorer_dock
   ```

## Добавление нового расширения

1. Создайте новый файл в папке `gopiai/extensions/`, например `my_extension.py`:
   ```python
   from PySide6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel

   def add_my_extension_dock(main_window):
       """Добавляет док-виджет с моим расширением."""
       dock = QDockWidget("Моё расширение", main_window)
       dock.setObjectName("myExtensionDock")
       
       # Создаем содержимое дока
       content = QWidget()
       layout = QVBoxLayout(content)
       layout.addWidget(QLabel("Содержимое моего расширения"))
       
       dock.setWidget(content)
       main_window.addDockWidget(Qt.RightDockWidgetArea, dock)
       return dock
   ```

2. Добавьте функцию инициализации в `gopiai/extensions/__init__.py`:
   ```python
   def init_my_extension(main_window):
       """Инициализирует моё расширение."""
       try:
           module = _safely_import("gopiai.extensions.my_extension")
           if module and hasattr(module, "add_my_extension_dock"):
               module.add_my_extension_dock(main_window)
           else:
               logger.warning("Функция add_my_extension_dock не найдена")
       except Exception as e:
           logger.error(f"Ошибка при инициализации моего расширения: {e}")
   ```

3. Добавьте вызов функции в `init_all_extensions`:
   ```python
   def init_all_extensions(main_window):
       # ...
       try:
           logger.info("Инициализация моего расширения...")
           init_my_extension(main_window)
       except Exception as e:
           logger.error(f"Ошибка при инициализации моего расширения: {e}")
       # ...
   ```

4. Создайте тесты для расширения в папке `tests/`:
   ```python
   # tests/test_my_extension.py
   import pytest
   from unittest.mock import MagicMock
   from PySide6.QtWidgets import QApplication, QMainWindow
   from gopiai.extensions.my_extension import add_my_extension_dock

   def test_add_my_extension_dock():
       app = QApplication([])
       main_window = MagicMock(spec=QMainWindow)
       dock = add_my_extension_dock(main_window)
       assert dock is not None
       main_window.addDockWidget.assert_called_once()
   ```

5. Создайте пример использования в папке `examples/`:
   ```python
   # examples/run_my_extension.py
   import sys
   from PySide6.QtWidgets import QApplication
   from gopiai.core.minimal_app import FramelessMainWindow
   from gopiai.extensions.my_extension import add_my_extension_dock

   def main():
       app = QApplication(sys.argv)
       main_window = FramelessMainWindow()
       main_window.show()
       add_my_extension_dock(main_window)
       sys.exit(app.exec())

   if __name__ == "__main__":
       main()
   ```

## Тестирование

Запуск тестов:
```bash
cd gopiai-extensions
pytest tests/
```

## Запуск примеров

```bash
cd gopiai-extensions
python examples/run_project_explorer.py
```

## Интеграция с другими модулями

Этот модуль зависит от модулей `gopiai-core` и `gopiai-widgets`. Он используется в основном приложении для добавления функциональности.

## Важные замечания

1. Расширения должны быть независимыми друг от друга.
2. Каждое расширение должно корректно обрабатывать ошибки и не приводить к падению всего приложения.
3. Расширения должны использовать систему сигналов и слотов Qt для взаимодействия с основным приложением.
