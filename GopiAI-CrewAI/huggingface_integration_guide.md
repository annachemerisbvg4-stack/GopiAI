# 🤗 Hugging Face Integration Guide для GopiAI-CrewAI

## 📋 Что такое Hugging Face

**Hugging Face** - крупнейшая платформа для машинного обучения с бесплатным доступом к тысячам моделей:
- 🆓 **Бесплатные модели** от разных производителей
- 🚀 **Inference API** для быстрого использования
- 🔄 **Много вариантов** моделей разного размера
- 📊 **Прозрачная статистика** использования

## 🔑 Как получить API ключ

### Пошаговая инструкция:

1. **Регистрация**: https://huggingface.co/join
2. **Профиль** → **Settings** → **Access Tokens**
3. **New token** → **Read** (достаточно для inference)
4. **Копируем ключ** (начинается с `hf_`)

### Ваш ключ:
```
HUGGINGFACE_API_KEY=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
```
✅ **Формат правильный!** (начинается с `hf_`)

## 📊 Лимиты Hugging Face (бесплатный план)

### 🆓 **Free Tier лимиты:**
- **1000 запросов в месяц** на аккаунт
- **Примерно 33 запроса в день** (если равномерно)
- **Нет лимита по токенам** - зависит от модели
- **Скорость**: 10-30 секунд на запрос (может быть медленнее платных API)

### ⚡ **Советы по использованию:**
- Используйте **легкие модели** для простых задач
- **Кешируйте результаты** (наш AI Router это делает)
- Используйте как **резервный провайдер** (не основной)

## 🤖 Рекомендуемые бесплатные модели

### 1. **Для чата и общих задач:**
```python
"microsoft/DialoGPT-large"           # Быстрый чат-бот
"microsoft/DialoGPT-medium"          # Еще быстрее
"facebook/blenderbot-400M-distill"   # Легкий разговорный
```

### 2. **Для программирования:**
```python
"microsoft/CodeBERT-base"            # Понимание кода
"huggingface/CodeBERTa-small-v1"    # Генерация кода
"Salesforce/codet5-small"           # Code T5 (легкий)
```

### 3. **Для текстовых задач:**
```python
"facebook/bart-large-cnn"           # Суммаризация
"t5-small"                         # Универсальная T5
"google/flan-t5-small"             # Instruction following
```

### 4. **Популярные открытые модели:**
```python
"microsoft/DialoGPT-large"          # 🔥 Рекомендуется
"google/flan-t5-base"              # 🔥 Хорошая для инструкций
"facebook/opt-350m"                 # 🔥 Быстрая генерация
```

## 🔧 Интеграция с GopiAI-CrewAI

### ✅ **Готово! HuggingFace уже интегрирован!**

Ваш API ключ уже добавлен в систему:
```
HUGGINGFACE_API_KEY=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 ✅
```

### 🚀 **Как использовать в CrewAI:**

#### 1. **Прямое использование HuggingFace Tool:**
```python
from gopiai_integration.huggingface_tools import GopiAIHuggingFaceTool

# Создаем агента с HuggingFace
agent = Agent(
    role='HF Assistant',
    goal='Использовать бесплатные HF модели',
    tools=[GopiAIHuggingFaceTool()],
    llm=llm
)

# В задаче агент может использовать:
# - message="Привет!", model_name="microsoft/DialoGPT-large"
# - message="Код для сортировки", model_name="auto" (автовыбор)
```

#### 2. **Через AI Router (автоматический fallback):**
```python
from gopiai_integration.ai_router_tools import GopiAIRouterTool

# AI Router автоматически использует HF если другие провайдеры недоступны
router_tool = GopiAIRouterTool()
# При превышении лимитов Groq/Gemini -> автоматически переключается на HF
```

### 🎯 **Рекомендованные модели для ваших задач:**

#### **Для диалогов и чата:**
- `microsoft/DialoGPT-large` - Лучший для разговоров 🔥
- `microsoft/DialoGPT-medium` - Быстрее, но проще
- `facebook/blenderbot-400M-distill` - Легкий чат-бот

#### **Для программирования:**
- `microsoft/CodeBERT-base` - Понимание кода 🔥
- `huggingface/CodeBERTa-small-v1` - Генерация кода
- `Salesforce/codet5-small` - Code T5

#### **Для инструкций и задач:**
- `google/flan-t5-base` - Отличный для команд 🔥
- `google/flan-t5-small` - Быстрее
- `t5-small` - Универсальная T5

#### **Для быстрой генерации:**
- `facebook/opt-350m` - Самая быстрая 🔥
- `facebook/opt-125m` - Еще быстрее, но проще

### 📊 **Управление лимитами:**

#### **Ваши лимиты:**
- ✅ **1000 запросов в месяц** (примерно 33 в день)
- ✅ **Без лимита по токенам** 
- ⏰ **10-30 секунд** на ответ (бесплатные модели)

#### **Советы по экономии:**
1. **Используйте кеш** - наша система автоматически кеширует ответы
2. **Выбирайте легкие модели** для простых задач
3. **Используйте как резерв** - основные: Groq, Gemini
4. **Короткие запросы** - длинные могут занимать много времени

### 🧪 **Тестирование интеграции:**

```bash
cd GopiAI-CrewAI
python main.py
# Выберите режим "3" для тестов
# Увидите: "🤗 Тестирование HuggingFace Tool..."
```

### 📈 **Статистика использования:**

HuggingFace Tool автоматически отслеживает:
- Общее количество запросов
- Кеш попадания (экономия лимитов)
- API вызовы vs кешированные ответы
- Ошибки и их причины

### ⚡ **Автоматический fallback в AI Router:**

Когда Groq или Gemini недоступны → система автоматически:
1. Пробует Cerebras
2. Если не работает → переключается на **HuggingFace**
3. Выбирает лучшую HF модель по типу задачи
4. Уведомляет вас: "🤗 HuggingFace Fallback: ..."

### 🔧 **Настройки в .env:**

```env
# Ваш ключ (уже настроен)
HUGGINGFACE_API_KEY=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

# Модели по умолчанию (добавлены)
HUGGINGFACE_MODEL=microsoft/DialoGPT-large       # Диалоги
HUGGINGFACE_CODE_MODEL=microsoft/CodeBERT-base   # Код  
HUGGINGFACE_CREATIVE_MODEL=google/flan-t5-base   # Творчество
HUGGINGFACE_FAST_MODEL=facebook/opt-350m         # Быстро
```

---

## 🎉 **Итого: У вас теперь 6 LLM провайдеров!**

1. **Google Gemini** - стабильный, основной ✅
2. **Groq** - быстрый для простых задач ✅  
3. **Cerebras** - мощный для сложного ✅
4. **Cohere** - специализированный ✅
5. **Novita** - дополнительный ✅
6. **🤗 HuggingFace** - тысячи моделей, резерв ✅

**Система автоматически выберет лучший провайдер и переключится при превышении лимитов!**
