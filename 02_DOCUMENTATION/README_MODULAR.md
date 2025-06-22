# Модульная структура проекта GopiAI

Этот документ описывает модульную структуру проекта GopiAI и инструкции по работе с ней.

## Структура проекта

Проект GopiAI разделен на следующие модули:

1. **gopiai-core** - базовый модуль с минимальным функционалом
   - Содержит основные компоненты для запуска приложения
   - Включает minimal_app.py, main.py, simple_theme_manager.py

2. **gopiai-widgets** - модуль с пользовательскими виджетами
   - Содержит виджеты, используемые в приложении
   - Включает text_editor.py, custom_grips и другие виджеты

3. **gopiai-extensions** - модуль с расширениями для основного приложения
   - Содержит расширения, такие как проводник проектов, терминал, браузер, чат
   - Включает систему подключения расширений

4. **gopiai-app** - модуль с основной логикой приложения
   - Содержит логику, интерфейсы и инструменты для работы приложения
   - Включает подмодули app/agent, app/logic, app/ui, app/tool, app/utils

5. **gopiai-assets** - модуль с ресурсами
   - Содержит изображения, иконки, шрифты и другие ресурсы
   - Включает titlebar_with_menu.py и другие компоненты интерфейса

Каждый модуль представляет собой отдельный Python-пакет, который можно разрабатывать независимо от других модулей.

## Разработка модулей

### Создание нового модуля

1. Создайте папку для модуля, например `gopiai-mymodule`
2. Создайте структуру пакета:
   ```
   gopiai-mymodule/
   ├── gopiai/
   │   ├── __init__.py  # namespace package
   │   └── mymodule/
   │       ├── __init__.py
   │       └── ...
   ├── tests/
   │   └── test_mymodule.py
   ├── examples/
   │   └── run_mymodule.py
   └── pyproject.toml
   ```
3. В файле `gopiai/__init__.py` добавьте:
   ```python
   __path__ = __import__('pkgutil').extend_path(__path__, __name__)
   ```
4. В файле `pyproject.toml` укажите зависимости и информацию о пакете:
   ```toml
   [build-system]
   requires = ["setuptools>=42", "wheel"]
   build-backend = "setuptools.build_meta"

   [project]
   name = "gopiai-mymodule"
   version = "0.1.0"
   description = "Мой модуль для GopiAI"
   requires-python = ">=3.8"
   dependencies = [
       "PySide6>=6.5.0",
       "gopiai-core>=0.1.0",
   ]

   [tool.setuptools]
   packages = ["gopiai.mymodule"]
   ```

### Импорты в модулях

Все импорты должны быть абсолютными через namespace `gopiai`:

```python
# Правильно
from gopiai.widgets.text_editor import TextEditorWidget
from gopiai.core.minimal_app import FramelessMainWindow

# Неправильно
from widgets.text_editor import TextEditorWidget
from core.minimal_app import FramelessMainWindow
```

## Тестирование модулей

### Модульные тесты

Для каждого модуля создаются модульные тесты в папке `tests`:

```python
# gopiai-extensions/tests/test_project_explorer.py
import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QApplication, QMainWindow
from gopiai.extensions.project_explorer_integration import add_project_explorer_dock

def test_add_project_explorer_dock():
    app = QApplication([])
    main_window = MagicMock(spec=QMainWindow)
    add_project_explorer_dock(main_window)
    main_window.addDockWidget.assert_called_once()
```

Запуск тестов:

```bash
cd gopiai-extensions
pytest tests/
```

Или запуск всех тестов:

```bash
python run_tests.py
```

### Тестовые приложения

Для каждого модуля создаются тестовые приложения в папке `examples`:

```python
# gopiai-extensions/examples/run_project_explorer.py
import sys
from PySide6.QtWidgets import QApplication
from gopiai.core.minimal_app import FramelessMainWindow
from gopiai.extensions.project_explorer_integration import add_project_explorer_dock

def main():
    app = QApplication(sys.argv)
    main_window = FramelessMainWindow()
    main_window.show()
    add_project_explorer_dock(main_window)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

Запуск тестового приложения:

```bash
cd gopiai-extensions
python examples/run_project_explorer.py
```

## Сборка проекта

Для сборки проекта из отдельных модулей используйте скрипт `build_project.py`:

```bash
python build_project.py
```

Скрипт создаст папку `build` с собранным проектом, который можно запустить:

```bash
cd build
python main.py
```

## Локальная разработка

Для локальной разработки модулей есть несколько вариантов:

1. **Установка в режиме разработки**:
   ```bash
   pip install -e ./gopiai-mymodule
   ```

2. **Добавление в PYTHONPATH**:
   ```bash
   export PYTHONPATH=$PYTHONPATH:/path/to/gopiai-project
   ```

3. **Использование скрипта сборки**:
   ```bash
   python build_project.py
   cd build
   python main.py
   ```

## Добавление нового функционала

1. Определите, к какому модулю относится новый функционал
2. Разработайте функционал в соответствующем модуле
3. Используйте абсолютные импорты через namespace `gopiai`
4. Соберите проект для тестирования

## Пример: добавление нового виджета

1. Создайте файл `gopiai-widgets/gopiai/widgets/my_widget.py`:
   ```python
   from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

   class MyWidget(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self.layout = QVBoxLayout(self)
           self.label = QLabel("Мой виджет", self)
           self.layout.addWidget(self.label)
   ```

2. Добавьте импорт в `gopiai-widgets/gopiai/widgets/__init__.py`:
   ```python
   from gopiai.widgets.my_widget import MyWidget
   ```

3. Используйте виджет в другом модуле:
   ```python
   from gopiai.widgets import MyWidget
   
   widget = MyWidget()
   ```

4. Соберите проект и протестируйте новый функционал.

## Заключение

Модульная структура проекта GopiAI позволяет разрабатывать отдельные компоненты независимо друг от друга, а затем объединять их в единый проект. Это упрощает разработку, тестирование и поддержку кода.
