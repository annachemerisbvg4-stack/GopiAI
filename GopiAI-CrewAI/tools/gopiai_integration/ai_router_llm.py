"""
🤖 AI Router LLM для CrewAI
Интеграция CrewAI с системой AI Router GopiAI
"""

import os
import sys
import json
import subprocess
from typing import Any, Dict, List, Optional
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import LLMResult

class GopiAIRouterLLM(LLM):
    """
    Кастомный LLM для CrewAI, использующий AI Router систему GopiAI
    """
    
    ai_router_path: str = "../../01_AI_ROUTER_SYSTEM/ai_router_system.js"
    task_type: str = "chat"
    
    @property
    def _llm_type(self) -> str:
        return "gopiai_router"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Отправка запроса через AI Router
        """
        try:
            # Путь к AI Router системе
            router_path = os.path.join(os.path.dirname(__file__), self.ai_router_path)
            
            # Команда для запуска AI Router через Node.js
            cmd = [
                "node", 
                "-e", 
                f"""
                const AIRouter = require('{router_path}');
                const config = require('../../01_AI_ROUTER_SYSTEM/ai_rotation_config.js');
                
                async function processRequest() {{
                    const router = new AIRouter(config.AI_PROVIDERS_CONFIG);
                    try {{
                        const result = await router.chat('{prompt.replace("'", "\\'")}', '{self.task_type}');
                        console.log(JSON.stringify({{ success: true, response: result.response }}));
                    }} catch (error) {{
                        console.log(JSON.stringify({{ success: false, error: error.message }}));
                    }}
                }}
                
                processRequest();
                """
            ]
            
            # Выполнение команды
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=os.path.dirname(__file__)
            )
            
            if result.returncode == 0:
                # Парсинг ответа
                try:
                    response_data = json.loads(result.stdout.strip())
                    if response_data.get("success"):
                        return response_data["response"]
                    else:
                        return f"Ошибка AI Router: {response_data.get('error', 'Неизвестная ошибка')}"
                except json.JSONDecodeError:
                    return f"Ошибка парсинга ответа AI Router: {result.stdout}"
            else:
                return f"Ошибка выполнения AI Router: {result.stderr}"
                
        except Exception as e:
            return f"Ошибка интеграции с AI Router: {str(e)}"

class GopiAICodingLLM(GopiAIRouterLLM):
    """Специализированный LLM для задач программирования"""
    task_type: str = "code"

class GopiAICreativeLLM(GopiAIRouterLLM):
    """Специализированный LLM для творческих задач"""
    task_type: str = "creative"

class GopiAIAnalysisLLM(GopiAIRouterLLM):
    """Специализированный LLM для аналитических задач"""
    task_type: str = "analysis"


# 🎯 Упрощенная версия через прямое использование ключей (fallback)
class SimpleGopiAILLM(LLM):
    """
    Упрощенная версия, использующая ключи напрямую
    """
    
    provider: str = "groq"  # groq, openai, gemini
    
    @property
    def _llm_type(self) -> str:
        return f"gopiai_simple_{self.provider}"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Простая отправка через выбранного провайдера
        """
        try:
            if self.provider == "groq":
                return self._call_groq(prompt)
            elif self.provider == "openai":
                return self._call_openai(prompt)
            # Добавить других провайдеров при необходимости
            else:
                return "Провайдер не поддерживается"
                
        except Exception as e:
            return f"Ошибка {self.provider}: {str(e)}"
    
    def _call_groq(self, prompt: str) -> str:
        """Вызов через Groq API"""
        try:
            import openai
            client = openai.OpenAI(
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1"
            )
            
            # Используем актуальную модель из .env
            model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            
            response = client.chat.completions.create(
                model=model,  # ✅ Теперь использует актуальную модель
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Ошибка Groq API: {str(e)}"
    
    def _call_openai(self, prompt: str) -> str:
        """Вызов через OpenAI API"""
        try:
            import openai
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Ошибка OpenAI API: {str(e)}"


# 🎯 Фабрика для создания LLM
def create_gopiai_llm(provider: str = "router", task_type: str = "chat"):
    """
    Создает подходящий LLM для CrewAI
    
    Args:
        provider: "router" (AI Router), "groq", "openai", "simple"
        task_type: "chat", "code", "creative", "analysis"
    """
    
    if provider == "router":
        if task_type == "code":
            return GopiAICodingLLM()
        elif task_type == "creative":
            return GopiAICreativeLLM()
        elif task_type == "analysis":
            return GopiAIAnalysisLLM()
        else:
            return GopiAIRouterLLM()
    
    elif provider in ["groq", "openai"]:
        return SimpleGopiAILLM(provider=provider)
    
    else:
        # Fallback к Groq
        return SimpleGopiAILLM(provider="groq")


if __name__ == "__main__":
    # Тест LLM
    print("🧪 Тестирование GopiAI LLM...")
    
    # Тест простого LLM
    llm = create_gopiai_llm("groq")
    response = llm("Привет! Как дела?")
    print(f"Ответ Groq: {response}")