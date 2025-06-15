# 🧠 Интеграция памяти ИИ в GopiAI WebView

Этот документ описывает интеграцию системы памяти RAG (Retrieval-Augmented Generation) в веб-чат GopiAI.

## 📋 Что было добавлено

### 1. **Модуль памяти чата** (`GopiAI-WebView/gopiai/webview/chat_memory.py`)
- `ChatMemoryManager` - основной класс управления памятью
- Краткосрочная память (последние 15 сообщений в деque)
- Интеграция с RAG системой через REST API
- Методы обогащения сообщений контекстом
- Автоматическое сохранение диалогов

### 2. **Обновленный JavaScript Bridge** (`GopiAI-WebView/gopiai/webview/js_bridge.py`)
- Новые слоты для работы с памятью:
  - `enrich_message(message)` - обогащение сообщения контекстом
  - `save_chat_exchange(user_msg, ai_response)` - сохранение диалога
  - `start_new_chat_session()` - начало новой сессии
  - `get_memory_stats()` - статистика памяти
  - `is_memory_available()` - проверка доступности

### 3. **Обновленный HTML интерфейс**
- Интеграция с системой памяти в JavaScript
- Индикатор состояния памяти
- Автоматическое обогащение сообщений
- Новая сессия при очистке чата

### 4. **Тестовый скрипт** (`test_memory_integration.py`)
- Проверка работоспособности всей системы
- Тестирование RAG сервера
- Валидация импортов

## 🚀 Как использовать

### Шаг 1: Запустите RAG сервер

```bash
cd rag_memory_system
python run_server.py
```

Сервер будет доступен на `http://127.0.0.1:8080`

### Шаг 2: Протестируйте интеграцию

```bash
python test_memory_integration.py
```

### Шаг 3: Запустите GopiAI UI

```bash
python GopiAI-UI/gopiai/ui/main.py
```

## 🔧 Как это работает

### JavaScript → Python

1. **Обогащение сообщения**:
   ```javascript
   // Вызывается перед отправкой к ИИ
   const enrichedMessage = await bridge.enrich_message(userMessage);
   ```

2. **Сохранение диалога**:
   ```javascript
   // Вызывается после получения ответа ИИ
   await bridge.save_chat_exchange(userMessage, aiResponse);
   ```

### Python → RAG API

1. **Поиск контекста**:
   ```python
   # GET /search?q=запрос
   relevant_docs = self._search_rag_memory(user_message)
   ```

2. **Сохранение**:
   ```python
   # POST /sessions/{session_id}/messages
   self._save_to_rag_memory(user_message, ai_response, timestamp)
   ```

## 🧠 Архитектура памяти

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   JavaScript    │    │     Python       │    │   RAG System    │
│   (WebView)     │    │   Bridge         │    │   (ChromaDB)    │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ • User input    │───▶│ • Memory Manager │───▶│ • Vector DB     │
│ • UI updates    │    │ • Context cache  │    │ • Semantic      │
│ • Memory status │◀───│ • API calls      │◀───│   search        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📊 Типы памяти

### 1. **Краткосрочная память**
- Последние 15 сообщений в RAM
- Быстрый доступ к недавнему контексту
- Автоматическая очистка при переполнении

### 2. **Долгосрочная память (RAG)**
- Векторная база данных ChromaDB
- Семантический поиск по истории
- Персистентное хранение

### 3. **Контекстное обогащение**
```python
def enrich_message(self, user_message: str) -> str:
    context_parts = []
    
    # Краткосрочная память
    recent_context = self._format_recent_context()
    if recent_context:
        context_parts.append(f"Недавний контекст:\n{recent_context}")
    
    # Долгосрочная память
    relevant_history = self._search_rag_memory(user_message)
    if relevant_history:
        context_parts.append(f"Релевантная информация:\n{relevant_history}")
    
    # Финальное сообщение
    if context_parts:
        return f"""Контекст из памяти:
{chr(10).join(context_parts)}

Новый вопрос: {user_message}"""
    else:
        return user_message
```

## ⚙️ Настройки

### В `chat_memory.py`:
```python
ChatMemoryManager(
    rag_api_url="http://127.0.0.1:8080",      # URL RAG API
    max_context_messages=15,                   # Размер краткосрочной памяти
    similarity_threshold=0.7                   # Порог релевантности поиска
)
```

### В RAG системе (`rag_memory_system/config.py`):
```python
chunk_size = 1000           # Размер фрагментов для векторизации
top_k_results = 5           # Количество результатов поиска
similarity_threshold = 0.7  # Порог релевантности
```

## 🎯 Преимущества интеграции

1. **Минимальные изменения**:
   - Всего 2-3 строчки в JavaScript
   - Обратная совместимость

2. **Умная память**:
   - Семантический поиск (не только ключевые слова)
   - Автоматическое ранжирование по релевантности

3. **Graceful Degradation**:
   - Работает даже если RAG сервер недоступен
   - Нет блокировки основного функционала

4. **Прозрачность**:
   - Индикатор состояния памяти
   - Логирование операций
   - Статистика использования

## 🐛 Отладка

### Проверка состояния:
```javascript
// В консоли браузера
console.log('Memory available:', await bridge.is_memory_available());
console.log('Memory stats:', await bridge.get_memory_stats());
```

### Логи Python:
```python
# В chat_memory.py включено логирование
logger.info(f"RAG сессия создана: {self.session_id}")
logger.error(f"Ошибка поиска в RAG памяти: {e}")
```

### Проверка RAG API:
```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/stats
```

## 📈 Следующие шаги

1. **Настройка эмбеддингов**: Переход на более мощные модели
2. **Категоризация памяти**: Разделение по проектам/темам  
3. **Экспорт памяти**: Функции бэкапа и восстановления
4. **Аналитика**: Детальная статистика использования
5. **Персонализация**: Настройки пользователя

---

🎉 **Система памяти готова к использованию!** Больше никаких дней сурка - ИИ теперь помнит всё! 🧠✨