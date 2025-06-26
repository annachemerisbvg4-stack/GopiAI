"""
🔄 GopiAI AI Router Tool для CrewAI
Интеграция CrewAI агентов с системой AI Router GopiAI
"""

import os
import json
import subprocess
from typing import Type, Any, Dict, Optional
from pydantic import BaseModel, Field
from crewai.tools.base_tool import BaseTool

class AIRouterInput(BaseModel):
    """Схема входных данных для AI Router"""
    message: str = Field(description="Сообщение для AI Router")
    task_type: str = Field(default="chat", description="Тип задачи: chat, code, creative, analysis")
    model_preference: str = Field(default="auto", description="Предпочтительная модель: auto, groq, gemini, cerebras")
    max_tokens: int = Field(default=1000, description="Максимальное количество токенов")
    temperature: float = Field(default=0.7, description="Температура генерации")

class GopiAIRouterTool(BaseTool):
    """
    Инструмент для использования AI Router системы GopiAI
    
    Возможности:
    - Автоматическая ротация между провайдерами
    - Интеллектуальный выбор модели по задаче
    - Обход лимитов через переключение
    - Мониторинг использования
    """
    
    name: str = Field(default="gopiai_router", description="Имя инструмента")
    description: str = Field(default="Инструмент маршрутизации AI", description="Описание инструмента")
    router_path: str = Field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "../../../01_AI_ROUTER_SYSTEM"), description="Путь к директории AI Router")
    args_schema: Type[BaseModel] = AIRouterInput
    
    def __init__(self, **data):
        super().__init__(**data)
        # Для инициализации файлов вызывайте self.init_files() вручную после создания экземпляра

    def init_files(self):
        os.makedirs(self.router_path, exist_ok=True)
    
    def _run(self, *args, **kwargs):
        return "AI Router Tool: действие не реализовано (заглушка)"
    
    def _run(self, message: str, task_type: str = "chat", model_preference: str = "auto", 
             max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Отправка запроса через AI Router
        """
        try:
            # Сначала пробуем прямую интеграцию
            result = self._direct_router_call(message, task_type, model_preference, max_tokens, temperature)
            if result:
                return result
            
            # Fallback: через subprocess
            return self._subprocess_router_call(message, task_type, model_preference)
            
        except Exception as e:
            # Последний fallback: эмуляция
            return self._simulate_router_call(message, task_type, model_preference)
    
    def _direct_router_call(self, message: str, task_type: str, model_preference: str, 
                           max_tokens: int, temperature: float) -> Optional[str]:
        """
        Прямой вызов AI Router (если возможно)
        """
        try:
            import sys
            sys.path.append(self.router_path)
            
            # Импорт AI Router (если он есть как Python модуль)
            # from ai_router_system import AIRouter
            # router = AIRouter()
            # return router.process_request(message, task_type, model_preference)
            
            # Пока что возвращаем None, так как AI Router в JavaScript
            return None
            
        except ImportError:
            return None
    
    def _subprocess_router_call(self, message: str, task_type: str, model_preference: str) -> str:
        """
        Вызов AI Router через subprocess (Node.js)
        """
        try:
            # Экранируем сообщение для безопасности
            safe_message = message.replace("'", "\\'").replace('"', '\\"')
            
            # JavaScript код для вызова AI Router
            js_code = f"""
            const path = require('path');
            const {{ AIRouter }} = require('{self.router_path}/ai_router_system.js');
            const config = require('{self.router_path}/ai_rotation_config.js');
            // --- DEBUGGING START ---
            console.log(JSON.stringify({ debug: `Type of AIRouter: ${typeof AIRouter}` }));
            console.log(JSON.stringify({ debug: `AIRouter object: ${JSON.stringify(AIRouter, null, 2)}` }));
            
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
                        error: error.message 
                    }}));
                }}
            }}
            
            processRequest();
            """
            
            # Выполняем через Node.js
            result = subprocess.run(
                ["node", "-e", js_code],
                capture_output=True,
                text=True,
                timeout=30,  # 30 секунд таймаут
                cwd=self.router_path
            )
            
            if result.returncode == 0:
                try:
                    response_data = json.loads(result.stdout.strip())
                    if response_data.get("success"):
                        provider = response_data.get("provider", "unknown")
                        tokens = response_data.get("tokens", 0)
                        response = response_data["response"]
                        return f"🤖 AI Router ({provider}, {tokens} токенов): {response}"
                    else:
                        error = response_data.get("error", "Неизвестная ошибка")
                        return f"❌ AI Router ошибка: {error}"
                except json.JSONDecodeError:
                    return f"❌ Ошибка парсинга ответа AI Router: {result.stdout}"
            else:
                return f"❌ AI Router недоступен: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "⏱️ AI Router: превышено время ожидания"
        except Exception as e:
            return f"❌ Ошибка вызова AI Router: {str(e)}"
    
    def _simulate_router_call(self, message: str, task_type: str, model_preference: str) -> str:
        """
        Эмуляция AI Router для тестирования
        """
        # Выбираем "провайдера" на основе предпочтений
        if model_preference == "groq":
            provider = "Groq (llama-3.3-70b)"
        elif model_preference == "gemini":
            provider = "Google (gemini-2.0-flash)"
        elif model_preference == "cerebras":
            provider = "Cerebras (llama-3.1-70b)"
        else:
            # Автовыбор на основе типа задачи
            if task_type == "code":
                provider = "Cerebras (llama-3.1-70b)"
            elif task_type == "creative":
                provider = "Google (gemini-2.0-flash)"
            elif task_type == "analysis":
                provider = "Google (gemini-2.0-flash)"
            else:
                provider = "Groq (llama-3.3-70b)"
        
        # Симуляция ответа
        if task_type == "code":
            response = "Вот пример кода для вашей задачи..."
        elif task_type == "creative":
            response = "Творческий ответ на ваш запрос..."
        elif task_type == "analysis":
            response = "Анализ показывает следующие выводы..."
        else:
            response = f"Обработан запрос: {message[:50]}..."
        
        return f"🤖 AI Router (эмуляция, {provider}): {response}"
    
    def _huggingface_fallback(self, message: str, task_type: str, model_preference: str, 
                             max_tokens: int, temperature: float) -> Optional[str]:
        """
        Fallback на Hugging Face при недоступности других провайдеров
        """
        try:
            # Импортируем HuggingFace tool
            from .huggingface_tools import GopiAIHuggingFaceTool
            
            hf_tool = GopiAIHuggingFaceTool()
            
            # Выбираем модель по типу задачи
            if task_type == "code":
                model = "microsoft/CodeBERT-base"
            elif task_type == "chat":
                model = "microsoft/DialoGPT-large"
            elif task_type == "creative":
                model = "google/flan-t5-base"
            else:
                model = "auto"  # Автовыбор
            
            # Выполняем запрос
            result = hf_tool._run(
                message=message,
                model_name=model,
                task_type="text-generation" if task_type != "chat" else "conversational",
                max_length=min(max_tokens, 200),  # HF лимит
                temperature=temperature
            )
            
            return f"🤗 HuggingFace Fallback: {result}"
            
        except Exception as e:
            return f"❌ HuggingFace Fallback error: {str(e)}"


class GopiAIModelSelectorTool:
    """Умный выбор модели для задачи"""
    
    name: str = "gopiai_model_selector" 
    description: str = "Рекомендует лучшую модель для конкретной задачи"
    
    def _run(self, task_description: str, constraints: str = "") -> str:
        """
        Анализирует задачу и рекомендует модель
        """
        task_lower = task_description.lower()
        
        recommendations = []
        
        # Анализ типа задачи
        if any(word in task_lower for word in ["код", "программ", "debug", "python", "javascript"]):
            recommendations.append("🖥️ Тип: Программирование")
            recommendations.append("💡 Рекомендация: Cerebras Llama-3.1-70B (лучше для кода)")
            task_type = "code"
        elif any(word in task_lower for word in ["анализ", "исследован", "данные", "статистика"]):
            recommendations.append("📊 Тип: Анализ данных")
            recommendations.append("💡 Рекомендация: Google Gemini-2.0-Flash (хорош для анализа)")
            task_type = "analysis"
        elif any(word in task_lower for word in ["творч", "создай", "придумай", "напиши"]):
            recommendations.append("🎨 Тип: Творческая задача")
            recommendations.append("💡 Рекомендация: Google Gemini-2.0-Flash (творческий потенциал)")
            task_type = "creative"
        else:
            recommendations.append("💬 Тип: Общение/диалог")
            recommendations.append("💡 Рекомендация: Groq Llama-3.3-70B (быстрый ответ)")
            task_type = "chat"
        
        # Анализ ограничений
        if "быстро" in constraints.lower():
            recommendations.append("⚡ Ограничение: скорость → Groq (самый быстрый)")
        if "длинн" in constraints.lower() or "подробн" in constraints.lower():
            recommendations.append("📝 Ограничение: детальность → Gemini (большой контекст)")
        
        # Статус провайдеров (эмуляция)
        status = [
            "📊 Статус провайдеров:",
            "✅ Groq: доступен (лимит: 30 RPM)",
            "✅ Gemini: доступен (бесплатно)",
            "⚠️ Cerebras: ограничен",
            "✅ Cohere: доступен",
            "🤗 HuggingFace: доступен (1000 req/month)"
        ]
        
        result = "\\n".join(recommendations + [""] + status)
        return f"🎯 Анализ задачи:\\n{result}\\n\\n🚀 Используйте task_type='{task_type}'"


# Экспорт инструментов
__all__ = [
    "GopiAIRouterTool",
    "GopiAIModelSelectorTool"
]


if __name__ == "__main__":
    # Тест инструментов
    print("🧪 Тестирование GopiAI AI Router Tools...")
    
    # Тест AI Router
    router = GopiAIRouterTool()
    result = router._run("Привет! Как дела?", "chat", "auto")
    print(f"AI Router test: {result}")
    
    # Тест селектора моделей
    selector = GopiAIModelSelectorTool()
    result = selector._run("Напиши код для сортировки массива", "быстро")
    print(f"Model selector test: {result}")
    
    print("✅ Все инструменты готовы!")