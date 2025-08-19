# GopiAI - Интерфейс для Gemini CLI

Этот проект предоставляет удобный графический интерфейс для работы с Gemini CLI - официальным клиентским интерфейсом Google AI.

## Особенности

- Простой и интуитивно понятный интерфейс
- Поддержка чата с контекстом
- Выбор моделей Gemini
- Логирование и отладка

## Требования

- Python 3.8+
- Установленный Gemini CLI
- Зависимости из `GopiAI-UI/requirements.txt`

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd GopiAI
   ```

2. Установите зависимости:
   ```bash
   cd GopiAI-UI
   pip install -r requirements.txt
   ```

3. Убедитесь, что у вас установлен Gemini CLI:
   ```bash
   gemini --version
   ```

## Запуск

1. Запустите сервер:
   ```bash
   cd GopiAI-UI
   python -m gopiai.api.gemini_routes
   ```

2. В другом терминале запустите интерфейс:
   ```bash
   python main_with_logging.py
   ```

## Структура проекта

- `GopiAI-UI/` - Основное приложение с графическим интерфейсом
  - `gopiai/` - Исходный код приложения
    - `api/` - API эндпоинты
    - `services/` - Сервисные классы
    - `ui/` - Пользовательский интерфейс
- `gemini-cli/` - Копия репозитория Gemini CLI (опционально)
- `examples/` - Примеры использования

## Лицензия

MIT
