# Инструкции по тестированию AutoGen интеграции в GopiAI

Эта инструкция поможет проверить работу AutoGen extension с GopiAI.

## Шаг 1: Проверьте конфигурацию

1. Убедитесь, что вы добавили API ключи в `.env` файл в корне GOPI_AI_MODULES:
   ```
   CEREBRAS_API_KEY=csk-your-cerebras-key
   OPENAI_API_KEY=sk-your-openai-key
   ```

2. Убедитесь, что AutoGen установлен в вашем окружении:
   ```bash
   pip install "pyautogen[cerebras]"
   ```

## Шаг 2: Проверьте структуру файлов

Структура должна быть следующей:
```
GOPI_AI_MODULES/
├── GopiAI-Extensions/
│   ├── autogen/
│   │   ├── __init__.py
│   │   ├── autogen_core.py
│   │   ├── autogen_extension.py
│   │   └── README.md
│   └── gopiai/
│       └── extensions/
│           └── __init__.py  # С добавленной функцией init_autogen_extension
```

## Шаг 3: Запустите GopiAI

Запустите основную программу GopiAI. Расширение должно автоматически загрузиться.

```bash
cd GOPI_AI_MODULES
python -m gopiai
```

## Шаг 4: Проверьте работу расширения

1. В главном окне GopiAI должен появиться новый док-виджет "AutoGen Мультиагенты"
2. Откройте док-виджет и отправьте тестовое сообщение
3. Проверьте лог приложения на наличие ошибок

## Шаг 5: Устранение проблем

Если расширение не загружается:

1. Проверьте логи на наличие ошибок
2. Убедитесь, что в `gopiai/extensions/__init__.py` вызывается функция `init_autogen_extension`
3. Проверьте, что в pyproject.toml добавлен пакет "autogen"

## Дополнительная информация

- Тестовые примеры можно найти в папке `C:/Users/crazy/AutoGen/examples/`
- При успешной интеграции вы должны увидеть сообщение "✅ AutoGen расширение инициализировано" в логах
