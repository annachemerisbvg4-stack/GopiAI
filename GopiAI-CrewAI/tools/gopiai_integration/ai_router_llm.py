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
ROUTER_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_router"))

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
        
        # Создаем временный JS файл вместо передачи кода через -e
        temp_js_file = os.path.join(ROUTER_PATH, "temp_request.js")
        
        try:
            # JavaScript код для вызова AI Router
            js_code = f"""
            const path = require('path');
            try {{
                // Используем локальные пути относительно текущего файла
                const router = require('./ai_router_system.js').AIRouter;
                const config = require('./ai_rotation_config.js');
                
                // Оценка количества токенов
                function estimateTokens(text) {{
                    if (!text) return 0;
                    // Грубая оценка: ~4 символа = 1 токен для латиницы, ~2 для кириллицы
                    const latinChars = (text.match(/[a-zA-Z0-9\\s.,!?;:()\\-]/g) || []).length;
                    const cyrillicChars = text.length - latinChars;
                    return Math.ceil(latinChars / 4 + cyrillicChars / 2);
                }}
                
                async function processRequest() {{
                    try {{
                        const routerInstance = new router(config.AI_PROVIDERS_CONFIG);
                        const result = await routerInstance.chat('{safe_message}', {{ 
                            taskType: '{task_type}',
                            temperature: 0.7,
                            maxTokens: 1000
                        }});
                        console.log(JSON.stringify({{ 
                            success: true, 
                            response: result.response,
                            provider: result.provider,
                            tokens: result.tokens || estimateTokens(result.response) || 0
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
            
            # Записываем код во временный файл
            try:
                with open(temp_js_file, 'w', encoding='utf-8') as f:
                    f.write(js_code)
            except Exception as e:
                print(f"⚠️ Ошибка при создании временного JS файла: {e}")
                return self._simulate_router_call(message, task_type)
            
            # Выполняем через Node.js
            try:
                # Явно указываем кодировку UTF-8 для процесса
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                
                # Создаем временный файл для вывода
                output_file = os.path.join(ROUTER_PATH, "temp_output.json")
                
                # Модифицируем JS-код, чтобы записывать результат в файл
                with open(temp_js_file, 'r', encoding='utf-8') as f:
                    js_code = f.read()
                
                # Правильно экранируем обратные слэши в пути для JavaScript
                safe_output_path = output_file.replace('\\', '\\\\')
                
                js_code_with_file_output = js_code.replace(
                    'console.log(JSON.stringify(',
                    f'const fs = require("fs"); fs.writeFileSync("{safe_output_path}", JSON.stringify('
                ).replace(
                    '}));',
                    '}, null, 2));'
                )
                
                with open(temp_js_file, 'w', encoding='utf-8') as f:
                    f.write(js_code_with_file_output)
                
                # Запускаем Node.js
                result = subprocess.run(
                    ["node", temp_js_file],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=30,
                    cwd=ROUTER_PATH,
                    env=env
                )
                
                # Проверяем, был ли создан файл вывода
                if os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        output_content = f.read()
                    
                    # Удаляем временный файл вывода
                    try:
                        os.remove(output_file)
                    except Exception as e:
                        print(f"⚠️ Не удалось удалить временный файл вывода: {e}")
                    
                    # Парсим результат
                    if output_content and output_content.strip():
                        response_data = json.loads(output_content)
                        if response_data.get("success"):
                            return response_data["response"]
                        else:
                            router_error = response_data.get("error", "Неизвестная ошибка")
                            print(f"⚠️ AI Router вернул ошибку: {router_error}")
                            return self._simulate_router_call(message, task_type)
                
                # Если файл не был создан или пуст, проверяем стандартный вывод
                if result.returncode == 0 and result.stdout and result.stdout.strip():
                    print(f"📄 Получен ответ от Node.js через stdout ({len(result.stdout)} байт)")
                    try:
                        response_data = json.loads(result.stdout.strip())
                        if response_data.get("success"):
                            return response_data["response"]
                        else:
                            router_error = response_data.get("error", "Неизвестная ошибка")
                            print(f"⚠️ AI Router вернул ошибку: {router_error}")
                            return self._simulate_router_call(message, task_type)
                    except json.JSONDecodeError:
                        pass  # Продолжаем к fallback
                
                # Если все способы не сработали, используем fallback
                print("⚠️ Не удалось получить корректный ответ от AI Router")
                return self._simulate_router_call(message, task_type)
            except Exception as e:
                print(f"⚠️ Ошибка при выполнении Node.js: {e}")
                return self._simulate_router_call(message, task_type)
            finally:
                # Удаляем временный JS-файл в любом случае
                try:
                    if os.path.exists(temp_js_file):
                        os.remove(temp_js_file)
                except Exception as e:
                    print(f"⚠️ Не удалось удалить временный JS-файл: {e}")
                
        except subprocess.TimeoutExpired:
            print("⚠️ AI Router: превышено время ожидания")
            return self._simulate_router_call(message, task_type)
        except Exception as e:
            print(f"⚠️ Ошибка вызова AI Router: {str(e)}")
            return self._simulate_router_call(message, task_type)
    
    def _simulate_router_call(self, message: str, task_type: str) -> str:
        """
        Эмуляция AI Router для тестирования/отладки или когда Node.js недоступен
        """
        # ПРЕДУПРЕЖДЕНИЕ: Эта функция только для тестирования и отладки!
        # В продакшене всегда должен использоваться реальный AI Router
        
        import random
        import string
        
        prefix = f"[ЭМУЛЯЦИЯ AI ROUTER] "
        timestamp = time.strftime("%H:%M:%S")
        
        # Более детальный ответ на основе типа задачи
        if task_type == "code":
            return prefix + f"Вот пример кода для решения вашей задачи:\n\n```python\n# Код для: {message[:50]}...\ndef smart_function(input_data):\n    # Логика обработки\n    result = process_data(input_data)\n    return result\n```"
        elif task_type == "creative":
            return prefix + f"Творческий ответ на ваш запрос:\n\n{message[:50]}...\n\nЭто пример творческого текста, который был бы сгенерирован настоящим AI. В реальном ответе здесь был бы полноценный текст, соответствующий вашему запросу."
        elif task_type == "analysis":
            return prefix + f"Анализ по запросу: {message[:50]}...\n\n1. Первый важный аспект анализа\n2. Второй ключевой момент\n3. Третий пункт с дополнительными деталями\n\nЗаключение: Для полного анализа требуется более глубокое рассмотрение."
        else:
            return prefix + f"Получен запрос: '{message[:100]}...'\n\nЭто эмуляция ответа от AI Router. Чтобы получить настоящий ответ, убедитесь, что Node.js установлен и файлы ai_router_system.js доступны."
            
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
                
                def __init__(self, ai_router: AIRouterLLM, **kwargs):
                    super().__init__(**kwargs)
                    self.ai_router = ai_router
                
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
            wrapper = AIRouterWrapper(ai_router=self)
            return wrapper
            
        except ImportError:
            print("⚠️ langchain не найден, возвращаем self")
            return self