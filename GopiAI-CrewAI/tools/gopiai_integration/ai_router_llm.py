"""
🔄 GopiAI AI Router LLM для CrewAI
Адаптер системы AI Router для использования с CrewAI
"""

import os
import subprocess
import json
from typing import Dict, List, Optional, Any, Mapping
import time
import random
from pathlib import Path

# Путь к директории AI Router
ROUTER_PATH = os.path.join(os.path.dirname(__file__), "../../../01_AI_ROUTER_SYSTEM")

class AIRouterLLM:
    """
    LLM-адаптер для использования AI Router с CrewAI.
    
    Преимущества:
    - Автоматическая ротация между провайдерами
    - Fallback при превышении лимитов
    - Логирование запросов
    - Оптимизация под задачу
    """
    
    def __init__(self, model_preference="auto"):
        self.model_preference = model_preference
        self.api_key = "api_key_not_needed_using_router"  # Фиктивный ключ
        self.last_call = 0
        
        # Проверяем наличие директории AI Router
        if not os.path.exists(ROUTER_PATH):
            print(f"⚠️ Директория AI Router не найдена: {ROUTER_PATH}")
    
    def call(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Вызов LLM через AI Router
        
        Этот метод соответствует интерфейсу, ожидаемому CrewAI
        """
        # Проверка времени с момента последнего вызова (защита от частых вызовов)
        current_time = time.time()
        if current_time - self.last_call < 1.0:
            time.sleep(1.0)
        self.last_call = time.time()
        
        # Определение типа задачи на основе промпта
        task_type = self._detect_task_type(prompt)
        
        try:
            # Сначала пытаемся вызвать через subprocess
            result = self._subprocess_router_call(prompt, task_type, self.model_preference)
            return result
            
        except Exception as e:
            print(f"⚠️ Ошибка при вызове AI Router: {e}")
            # Fallback: эмуляция для отладки
            return self._simulate_router_call(prompt, task_type)
    
    def _detect_task_type(self, prompt: str) -> str:
        """
        Определяет тип задачи на основе текста промпта
        """
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["код", "функц", "программ", "скрипт"]):
            return "code"
        elif any(word in prompt_lower for word in ["напиши", "создай", "творч"]):
            return "creative"
        elif any(word in prompt_lower for word in ["анализ", "оцен", "сравн"]):
            return "analysis"
        else:
            return "chat"
    
    def _subprocess_router_call(self, message: str, task_type: str, model_preference: str) -> str:
        """
        Вызов AI Router через subprocess (Node.js)
        """
        # Экранируем сообщение для безопасности
        safe_message = message.replace("'", "\\'").replace('"', '\\"')
        
        # JavaScript код для вызова AI Router
        js_code = f"""
        const path = require('path');
        try {{
            const {{ AIRouter }} = require('{ROUTER_PATH}/ai_router_system.js');
            const config = require('{ROUTER_PATH}/ai_rotation_config.js');
            
            async function processRequest() {{
                try {{
                    const router = new AIRouter(config.AI_PROVIDERS_CONFIG);
                    const result = await router.processRequest('{safe_message}', '{task_type}', '{model_preference}');
                    console.log(JSON.stringify({{ 
                        success: true, 
                        response: result.response,
                        provider: result.provider,
                        tokens: result.tokens
                    }}));
                }} catch (error) {{
                    console.log(JSON.stringify({{ 
                        success: false, 
                        error: error.message || "Неизвестная ошибка в processRequest" 
                    }}));
                }}
            }}
            
            processRequest();
        }} catch (error) {{
            console.log(JSON.stringify({{ 
                success: false, 
                error: `Failed to require modules: ${{error.message || "Unknown error"}}` 
            }}));
        }}
        """
        
        # Выполняем через Node.js
        try:
            result = subprocess.run(
                ["node", "-e", js_code],
                capture_output=True,
                text=True,
                timeout=30,  # 30 секунд таймаут
                cwd=ROUTER_PATH
            )
            
            if result.returncode == 0:
                try:
                    # Проверяем, что stdout не пустой
                    if not result.stdout.strip():
                        print("⚠️ Пустой ответ от AI Router")
                        return self._simulate_router_call(message, task_type)
                        
                    response_data = json.loads(result.stdout.strip())
                    if response_data.get("success"):
                        return response_data["response"]
                    else:
                        router_error = response_data.get("error", "Неизвестная ошибка")
                        print(f"⚠️ AI Router вернул ошибку: {router_error}")
                        return self._simulate_router_call(message, task_type)
                except json.JSONDecodeError:
                    print(f"⚠️ Ошибка парсинга ответа AI Router: {result.stdout}")
                    return self._simulate_router_call(message, task_type)
            else:
                print(f"⚠️ AI Router вернул ненулевой код: {result.stderr}")
                return self._simulate_router_call(message, task_type)
                
        except subprocess.TimeoutExpired:
            print("⚠️ AI Router: превышено время ожидания")
            return self._simulate_router_call(message, task_type)
        except Exception as e:
            print(f"⚠️ Ошибка вызова AI Router: {str(e)}")
            return self._simulate_router_call(message, task_type)
    
    def _simulate_router_call(self, message: str, task_type: str) -> str:
        """
        Эмуляция AI Router для тестирования/отладки
        """
        # ПРЕДУПРЕЖДЕНИЕ: Эта функция только для тестирования и отладки!
        # В продакшене всегда должен использоваться реальный AI Router
        
        prefix = f"[DEBUG ЭМУЛЯЦИЯ - НЕ ДЛЯ ПРОДАКШЕНА]\n\n"
        
        # Короткий ответ на основе типа задачи
        if task_type == "code":
            return prefix + f"Вот пример кода для решения вашей задачи:\n\n```python\n# Эмуляция ответа для запроса: {message[:50]}...\ndef example_function():\n    return 'Это эмуляция ответа'\n```"
        elif task_type == "creative":
            return prefix + f"Вот творческий ответ на ваш запрос:\n\n{message[:50]}...\n\nЭто эмуляция ответа, так как AI Router недоступен. Пожалуйста, проверьте настройки AI Router в директории 01_AI_ROUTER_SYSTEM."
        elif task_type == "analysis":
            return prefix + f"Вот результаты анализа по вашему запросу:\n\n1. Первый пункт анализа\n2. Второй пункт анализа\n3. Третий пункт анализа\n\nЭто эмуляция ответа, так как AI Router недоступен."
        else:
            return prefix + f"Я получил ваш запрос: '{message[:100]}...'\n\nЭто эмуляция ответа, так как AI Router недоступен. Пожалуйста, проверьте настройки AI Router в директории 01_AI_ROUTER_SYSTEM."
            
    def get_llm_instance(self):
        """
        Возвращает экземпляр LLM для использования с CrewAI
        
        Returns:
            LLM: Экземпляр LLM для CrewAI
        """
        try:
            # Создаем обертку для CrewAI
            from langchain.llms.base import LLM
            
            class AIRouterWrapper(LLM):
                """Обертка для AI Router, совместимая с LangChain"""
                
                ai_router: AIRouterLLM
                
                @property
                def _llm_type(self) -> str:
                    return "ai_router"
                
                def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
                    """Вызов AI Router"""
                    return self.ai_router.call(prompt)
                
                @property
                def _identifying_params(self) -> Mapping[str, Any]:
                    """Идентификационные параметры для LangChain"""
                    return {"model": "ai_router"}
            
            # Создаем и возвращаем экземпляр
            wrapper = AIRouterWrapper()
            wrapper.ai_router = self
            return wrapper
            
        except ImportError:
            print("⚠️ langchain не найден, возвращаем self")
            return self