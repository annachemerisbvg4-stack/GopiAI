# GopiAI WebView

Модуль для интеграции веб-чата с ИИ через puter.js в приложениях GopiAI. Предоставляет современный веб-интерфейс для общения с Claude Sonnet 4 и Opus 4 моделями с поддержкой стриминга, экспорта истории и двусторонней связи Python ↔ JavaScript.

## Возможности

- 🤖 **Интеграция с puter.js** - Бесплатный доступ к Claude моделям без API ключей
- 🎯 **Две модели ИИ** - Claude Sonnet 4 и Claude Opus 4
- 🌊 **Стриминг ответов** - Получение ответов в реальном времени
- 💾 **Экспорт истории** - JSON, TXT, Markdown форматы
- 🎨 **Современный интерфейс** - Темная/светлая тема, адаптивный дизайн
- 🔗 **Python ↔ JS мост** - Двусторонняя связь через QWebChannel
- 📊 **Статистика чата** - Отслеживание сообщений и использования моделей
- ⚙️ **Настройки** - Конфигурируемые параметры интерфейса
- 🧪 **Полное тестирование** - Pytest тесты для всех компонентов

## Архитектура

```
GopiAI-WebView/
├── gopiai/
│   ├── __init__.py              # Namespace package
│   └── webview/
│       ├── __init__.py          # Основные экспорты модуля
│       ├── webview_widget.py    # Qt виджет с QWebEngineView
│       ├── js_bridge.py         # JavaScript ↔ Python мост
│       ├── puter_interface.py   # Python API для управления чатом
│       └── assets/
│           ├── chat.html        # HTML интерфейс чата
│           ├── chat.css         # CSS стили
│           └── chat.js          # JavaScript функциональность
├── tests/
│   ├── test_webview_widget.py   # Тесты WebView виджета
│   └── test_puter_interface.py  # Тесты Python API
├── examples/
│   └── simple_chat.py           # Пример использования
├── pyproject.toml               # Конфигурация пакета
└── README.md                    # Документация
```

## Установка

### Зависимости

```bash
pip install PySide6>=6.5.0
pip install gopiai-core>=0.1.0  # Базовый модуль GopiAI
```

### Установка модуля

```bash
# Из исходного кода
cd GopiAI-WebView
pip install -e .

# Или с зависимостями для разработки
pip install -e .[dev]
```

## Быстрый старт

### Базовое использование

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from gopiai.webview import WebViewWidget

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GopiAI Chat")
        self.setGeometry(100, 100, 1000, 700)
        
        # Создание WebView виджета
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        self.chat_widget = WebViewWidget()
        layout.addWidget(self.chat_widget)
        
        self.setCentralWidget(central_widget)
        
        # Подключение сигналов
        self.chat_widget.message_sent.connect(self.on_message_sent)
        self.chat_widget.message_received.connect(self.on_message_received)
    
    def on_message_sent(self, message):
        print(f"User sent: {message}")
    
    def on_message_received(self, model, message):
        print(f"{model} replied: {message[:100]}...")

app = QApplication(sys.argv)
window = ChatWindow()
window.show()
app.exec()
```

### Использование Python API

```python
from gopiai.webview import PuterChatInterface, WebViewWidget

# Создание компонентов
webview = WebViewWidget()
chat_interface = PuterChatInterface(webview)

# Отправка сообщения
chat_interface.send_message("Привет! Расскажи о квантовых компьютерах.")

# Смена модели
chat_interface.set_model("claude-opus-4")

# Получение истории
history = chat_interface.get_chat_history()

# Экспорт в файл
exported_path = chat_interface.export_chat("json", "chat_history.json")

# Получение статистики
stats = chat_interface.get_statistics()
print(f"Всего сообщений: {stats['total_messages']}")
```

## API Reference

### WebViewWidget

Основной Qt виджет для отображения веб-интерфейса чата.

#### Методы

```python
# Отправка сообщения в чат
webview.send_message_to_chat("Hello, AI!")

# Очистка чата
webview.clear_chat()

# Установка модели ИИ
webview.set_model("claude-sonnet-4")  # или "claude-opus-4"

# Получение истории чата
history = webview.get_chat_history()

# Экспорт чата
exported_data = webview.export_chat("json")  # "json", "txt", "md"
```

#### Сигналы

```python
# Сообщение отправлено пользователем
webview.message_sent.connect(lambda msg: print(f"Sent: {msg}"))

# Получен ответ ИИ
webview.message_received.connect(lambda model, msg: print(f"{model}: {msg}"))

# Чат очищен
webview.chat_cleared.connect(lambda: print("Chat cleared"))

# Модель изменена
webview.model_changed.connect(lambda model: print(f"Model: {model}"))
```

### PuterChatInterface

Высокоуровневый Python API для управления чатом.

#### Методы

```python
# Отправка сообщения
success = chat_interface.send_message("Сообщение")

# Очистка чата
success = chat_interface.clear_chat()

# Управление моделями
success = chat_interface.set_model("claude-opus-4")
current_model = chat_interface.get_current_model()
available_models = chat_interface.get_available_models()

# Работа с историей
history = chat_interface.get_chat_history()
exported_data = chat_interface.export_chat("json")
exported_path = chat_interface.export_chat("md", "/path/to/file.md")

# Статистика
stats = chat_interface.get_statistics()
is_connected = chat_interface.is_connected()

# Установка callback функций
chat_interface.setup_message_callback(lambda msg: print(f"Message: {msg}"))
chat_interface.setup_response_callback(lambda model, msg: print(f"Response: {msg}"))
chat_interface.setup_error_callback(lambda err: print(f"Error: {err}"))
```

### JavaScriptBridge

Мост для связи Python ↔ JavaScript (используется внутренне).

#### Слоты (вызываемые из JavaScript)

```python
# Отправка сообщения от пользователя
@Slot(str)
def send_message(message: str)

# Получение ответа ИИ
@Slot(str, str)
def receive_ai_message(model: str, message: str)

# Очистка чата
@Slot()
def clear_chat()

# Изменение модели
@Slot(str)
def change_model(model: str)

# Получение истории (возвращает JSON)
@Slot(result=str)
def get_chat_history_json() -> str
```

## Веб-интерфейс

### Возможности интерфейса

- **Выбор модели** - Переключение между Claude Sonnet 4 и Opus 4
- **Стриминг ответов** - Текст появляется в реальном времени
- **Экспорт чата** - JSON, TXT, Markdown форматы
- **Настройки** - Тема, автопрокрутка, стриминг
- **Адаптивный дизайн** - Работает на разных размерах экрана
- **Индикатор набора** - Показывает когда ИИ "думает"

### Горячие клавиши

- `Enter` - Отправить сообщение
- `Shift + Enter` - Новая строка
- `Ctrl + K` - Очистить чат (если реализовано)

### Темы

Интерфейс поддерживает светлую и темную темы с автоматическим переключением через настройки.

## Примеры использования

### Простой чат-бот

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from gopiai.webview import WebViewWidget, PuterChatInterface

class SimpleChatBot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Chat Bot")
        
        # Создание чата
        self.webview = WebViewWidget()
        self.chat = PuterChatInterface(self.webview)
        self.setCentralWidget(self.webview)
        
        # Автоответчик
        self.chat.message_sent.connect(self.auto_reply)
    
    def auto_reply(self, message):
        if "привет" in message.lower():
            # Отправляем предопределенный ответ
            self.webview.send_message_to_chat("Привет! Как дела?")

app = QApplication([])
bot = SimpleChatBot()
bot.show()
app.exec()
```

### Интеграция с другими модулями GopiAI

```python
from gopiai.core import BaseModule
from gopiai.webview import WebViewWidget, PuterChatInterface

class ChatModule(BaseModule):
    def __init__(self):
        super().__init__("chat_module")
        self.webview = WebViewWidget()
        self.chat_interface = PuterChatInterface(self.webview)
        
        # Интеграция с другими модулями
        self.setup_module_integration()
    
    def setup_module_integration(self):
        # Подключение к системе событий GopiAI
        self.chat_interface.message_received.connect(self.on_ai_response)
    
    def on_ai_response(self, model, message):
        # Обработка ответа ИИ в контексте других модулей
        self.emit_event("ai_response_received", {
            "model": model,
            "message": message
        })
    
    def get_widget(self):
        return self.webview
```

### Сохранение и загрузка сессий

```python
import json
from datetime import datetime
from gopiai.webview import PuterChatInterface

class SessionManager:
    def __init__(self, chat_interface: PuterChatInterface):
        self.chat = chat_interface
    
    def save_session(self, filename: str):
        """Сохранение текущей сессии чата."""
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "model": self.chat.get_current_model(),
            "history": self.chat.get_chat_history(),
            "statistics": self.chat.get_statistics()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    def load_session(self, filename: str):
        """Загрузка сессии чата (история только для просмотра)."""
        with open(filename, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # Установка модели из сессии
        self.chat.set_model(session_data["model"])
        
        # История загружается автоматически браузером
        return session_data

# Использование
session_manager = SessionManager(chat_interface)
session_manager.save_session("chat_session_2023.json")
```

## Тестирование

### Запуск тестов

```bash
# Все тесты
pytest tests/

# Конкретный тест файл
pytest tests/test_webview_widget.py

# С покрытием кода
pytest tests/ --cov=gopiai.webview --cov-report=html

# Только быстрые тесты
pytest tests/ -m "not slow"
```

### Тестирование с QtBot

```python
import pytest
from PySide6.QtWidgets import QApplication
from gopiai.webview import WebViewWidget

@pytest.fixture
def app():
    return QApplication([])

@pytest.fixture
def webview_widget(app, qtbot):
    widget = WebViewWidget()
    qtbot.addWidget(widget)
    return widget

def test_widget_creation(webview_widget):
    assert webview_widget is not None
    assert hasattr(webview_widget, 'web_view')
```

## Разработка

### Настройка окружения разработки

```bash
# Клонирование репозитория
git clone <repo-url>
cd GopiAI-WebView

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -e .[dev]

# Установка pre-commit хуков
pre-commit install
```

### Структура кода

- **webview_widget.py** - Основной Qt виджет
- **js_bridge.py** - Мост Python ↔ JavaScript
- **puter_interface.py** - Высокоуровневый Python API
- **assets/** - HTML/CSS/JS файлы интерфейса
- **tests/** - Тесты модуля
- **examples/** - Примеры использования

### Добавление новых возможностей

1. **Новый метод в Python API:**
   ```python
   # В puter_interface.py
   def new_feature(self, param: str) -> bool:
       """Описание новой возможности."""
       try:
           # Реализация
           return True
       except Exception as e:
           self.error_occurred.emit(f"Error: {str(e)}")
           return False
   ```

2. **Новый слот в JavaScript Bridge:**
   ```python
   # В js_bridge.py
   @Slot(str, result=str)
   def new_js_method(self, data: str) -> str:
       """Новый метод для вызова из JavaScript."""
       # Обработка данных
       return "result"
   ```

3. **Расширение JavaScript интерфейса:**
   ```javascript
   // В chat.js
   newFeature(data) {
       if (this.bridge) {
           return this.bridge.new_js_method(data);
       }
   }
   ```

## Troubleshooting

### Частые проблемы

**1. WebEngine не загружается**
```bash
# Установка WebEngine зависимостей
pip install PySide6-Addons
# Или на Ubuntu/Debian
sudo apt-get install python3-pyside6.qtwebengine
```

**2. JavaScript ошибки**
- Проверьте консоль браузера в WebView
- Убедитесь что QWebChannel доступен
- Проверьте подключение bridge объекта

**3. puter.js не работает**
- Проверьте подключение к интернету
- Убедитесь что puter.js CDN доступен
- Проверьте CORS настройки

**4. Тесты не проходят**
```bash
# Установка тестовых зависимостей
pip install pytest pytest-qt pytest-mock

# Настройка дисплея для headless тестов
export QT_QPA_PLATFORM=offscreen
```

### Отладка

**Включение отладки:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Отладочный режим для WebEngine
from PySide6.QtWebEngineWidgets import QWebEngineView
QWebEngineView.settings().setAttribute(
    QWebEngineView.settings().JavascriptEnabled, True
)
```

**Просмотр JavaScript консоли:**
```python
# Включение dev tools
webview.web_view.page().setDevToolsPage(dev_tools_page)
```

## Интеграция с GopiAI

### Использование в модульной архитектуре

```python
# В основном приложении GopiAI
from gopiai.webview import WebViewWidget
from gopiai.core import ModuleManager

class MainApplication:
    def __init__(self):
        self.module_manager = ModuleManager()
        
        # Регистрация WebView модуля
        webview_widget = WebViewWidget()
        self.module_manager.register_widget("chat", webview_widget)
        
        # Интеграция с другими модулями
        self.setup_module_communication()
```

### Совместимость

- **GopiAI-Core**: ✅ Полная совместимость
- **GopiAI-Widgets**: ✅ Может использовать виджеты
- **GopiAI-Extensions**: ✅ Может быть расширен
- **GopiAI-App**: ✅ Интегрируется в основное приложение

## Лицензия

Модуль распространяется под той же лицензией, что и основной проект GopiAI.

## Контрибьютинг

1. Форк репозитория
2. Создание feature ветки
3. Внесение изменений с тестами
4. Создание Pull Request

## Changelog

### v0.1.0 (Initial Release)
- Базовая функциональность WebView интеграции
- Поддержка puter.js для Claude моделей
- Python ↔ JavaScript мост
- Экспорт истории чата
- Современный веб-интерфейс
- Полное тестирование
- Документация и примеры