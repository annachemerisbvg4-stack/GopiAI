# Инструкция по тестированию интеграции AutoGen в GopiAI

## Подготовка

1. **Проверьте файлы конфигурации:**
   - ✅ `C:\Users\crazy\GOPI_AI_MODULES\.env` должен содержать CEREBRAS_API_KEY и OPENAI_API_KEY
   - ✅ Пакет autogen добавлен в `pyproject.toml`
   - ✅ Функция `init_autogen_extension` добавлена в `gopiai/extensions/__init__.py`

2. **Установите зависимости:**
   ```bash
   cd C:\Users\crazy\GOPI_AI_MODULES
   pip install "pyautogen[cerebras]"
   ```

## Запуск тестов

1. **Тестирование автономной работы AutoGen модуля:**
   ```bash
   cd C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Extensions
   python -c "from autogen.autogen_core import autogen_manager; print(autogen_manager.simple_chat('Привет! Как дела?', 'best_first'))"
   ```

2. **Тестирование загрузки расширения:**
   ```bash
   cd C:\Users\crazy\GOPI_AI_MODULES\GopiAI-Extensions
   python -c "from autogen import init_autogen_extension; print('✅ init_autogen_extension загружен успешно')"
   ```

## Запуск GopiAI с AutoGen

1. **Запустите основное приложение GopiAI**
   ```bash
   cd C:\Users\crazy\GOPI_AI_MODULES
   python main.py
   ```

2. **Проверьте наличие нового док-виджета "AutoGen Мультиагенты"** в правой части интерфейса.

3. **Тестирование интеграции:**
   - Выберите стратегию "best_first (llama-3.3-70b)"
   - Введите в поле ввода: "Привет! Расскажи о возможностях AutoGen."
   - Нажмите "Отправить"
   - Дождитесь ответа от AutoGen (должен прийти быстро благодаря Cerebras)

## Проверка логов

Если возникли ошибки, проверьте журнал логов GopiAI на наличие сообщений об ошибках, связанных с AutoGen.

## Возможные проблемы и решения

1. **AutoGen не инициализируется:**
   - Проверьте правильность установки пакета `pyautogen[cerebras]`
   - Проверьте наличие и правильность API ключей в `.env`

2. **Док-виджет не появляется:**
   - Проверьте, добавлена ли функция инициализации в `init_all_extensions`
   - Проверьте, правильно ли интегрирован модуль в `pyproject.toml`

3. **Ошибки импорта:**
   - Убедитесь, что пакет `autogen` доступен в Python-окружении
   - Проверьте структуру импортов в `__init__.py`

4. **Ошибки при отправке сообщений:**
   - Проверьте, действительны ли API ключи
   - Проверьте подключение к интернету

## Проверка успешной интеграции

Если вы видите док-виджет и можете получать ответы на запросы, значит интеграция успешна! 🎉

---

**Готово к тестированию!** 📝
