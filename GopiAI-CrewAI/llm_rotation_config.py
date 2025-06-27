import time
import threading

# Конфиг моделей Gemini/Gemma для ротации и задач
LLM_MODELS_CONFIG = [
    {
        "name": "Gemma 3",
        "id": "gemma-3",
        "rpm": 30,
        "tpm": 60000,  # примерное значение, уточнить по API
        "type": ["simple", "lookup", "short_answer"],
        "multimodal": False,
        "embedding": False,
        "priority": 1
    },
    {
        "name": "Gemma 3n",
        "id": "gemma-3n",
        "rpm": 30,
        "tpm": 60000,
        "type": ["simple", "lookup", "short_answer"],
        "multimodal": False,
        "embedding": False,
        "priority": 2
    },
    {
        "name": "Gemini 2.0 Flash-Lite",
        "id": "gemini-2.0-flash-lite",
        "rpm": 30,
        "tpm": 120000,
        "type": ["simple", "dialog", "code", "summarize"],
        "multimodal": False,
        "embedding": False,
        "priority": 3
    },
    {
        "name": "Gemini 2.5 Flash-Lite Preview",
        "id": "gemini-2.5-flash-lite-preview",
        "rpm": 15,
        "tpm": 60000,
        "type": ["dialog", "code", "summarize"],
        "multimodal": False,
        "embedding": False,
        "priority": 4
    },
    {
        "name": "Gemini 2.5 Flash",
        "id": "gemini-2.5-flash",
        "rpm": 10,
        "tpm": 60000,
        "type": ["dialog", "code", "multimodal", "vision", "long_answer"],
        "multimodal": True,
        "embedding": False,
        "priority": 5
    },
    {
        "name": "Gemini Embedding Experimental",
        "id": "gemini-embedding-experimental",
        "rpm": 5,
        "tpm": 10000,
        "type": ["embedding"],
        "multimodal": False,
        "embedding": True,
        "priority": 10
    }
]

# Глобальный монитор лимитов (можно заменить на Redis/БД для продакшена)
class RateLimitMonitor:
    def __init__(self, models_config):
        self.models = {m["id"]: m for m in models_config}
        self.usage = {m["id"]: {"rpm": 0, "tpm": 0, "last_reset": time.time()} for m in models_config}
        self.lock = threading.Lock()

    def _reset_if_needed(self, model_id):
        now = time.time()
        # Сброс usage каждую минуту
        if now - self.usage[model_id]["last_reset"] > 60:
            self.usage[model_id]["rpm"] = 0
            self.usage[model_id]["tpm"] = 0
            self.usage[model_id]["last_reset"] = now

    def can_use(self, model_id, tokens=0):
        with self.lock:
            self._reset_if_needed(model_id)
            model = self.models[model_id]
            usage = self.usage[model_id]
            return usage["rpm"] < model["rpm"] and usage["tpm"] + tokens < model["tpm"]

    def register_use(self, model_id, tokens=0):
        with self.lock:
            self._reset_if_needed(model_id)
            self.usage[model_id]["rpm"] += 1
            self.usage[model_id]["tpm"] += tokens

    def wait_for_slot(self, model_id, tokens=0):
        # Ждать, пока не появится слот для запроса
        while not self.can_use(model_id, tokens):
            time.sleep(1)

# Инициализация глобального монитора
rate_limit_monitor = RateLimitMonitor(LLM_MODELS_CONFIG)

# Обновлённая функция выбора модели с учётом лимитов и ожиданием слота
def select_llm_model_safe(task_type, tokens=0):
    for model in sorted(LLM_MODELS_CONFIG, key=lambda m: m["priority"]):
        if task_type in model["type"]:
            if rate_limit_monitor.can_use(model["id"], tokens):
                return model["id"]
    # Если ни одна модель не доступна — ждём ближайший слот (rate limiting)
    # Можно сделать умную очередь, но для примера — просто ждём первую подходящую
    for model in sorted(LLM_MODELS_CONFIG, key=lambda m: m["priority"]):
        if task_type in model["type"]:
            rate_limit_monitor.wait_for_slot(model["id"], tokens)
            return model["id"]
    return None

# Пример функции выбора модели по типу задачи и лимитам
# (заготовка, интеграция с учётом текущего использования и очереди)
def select_llm_model(task_type, current_usage):
    """
    task_type: str (например, 'simple', 'dialog', 'embedding', 'multimodal')
    current_usage: dict {model_id: {"rpm": int, "tpm": int}}
    """
    # Сортируем по приоритету (от меньшего к большему)
    for model in sorted(LLM_MODELS_CONFIG, key=lambda m: m["priority"]):
        if task_type in model["type"]:
            usage = current_usage.get(model["id"], {"rpm": 0, "tpm": 0})
            if usage["rpm"] < model["rpm"] and usage["tpm"] < model["tpm"]:
                return model["id"]
    return None  # если все лимиты исчерпаны

# Пример безопасного вызова LLM с учётом лимитов
def safe_llm_call(prompt, llm_call_func, task_type, tokens=0):
    model_id = select_llm_model_safe(task_type, tokens)
    rate_limit_monitor.register_use(model_id, tokens)
    return llm_call_func(prompt, model=model_id)

# Пример интеграции txtai + LLM
# (поиск по базе txtai, генерация ответа через выбранную LLM)
def rag_answer(query, txtai_index, llm_call_func, llm_model_id):
    """
    query: str
    txtai_index: объект txtai (или API)
    llm_call_func: функция для вызова LLM (например, llm.call)
    llm_model_id: id выбранной модели
    """
    # 1. Поиск по базе txtai
    results = txtai_index.search(query, limit=3)
    context = "\n".join([r["text"] for r in results])
    # 2. Генерация ответа через LLM
    prompt = f"Ответь на вопрос, используя только этот контекст:\n{context}\n\nВопрос: {query}"
    answer = llm_call_func(prompt, model=llm_model_id)
    return answer
