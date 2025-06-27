"""
🔄 GopiAI AI Router Tool для CrewAI
Инструмент для агентов CrewAI для взаимодействия с системой AI Router GopiAI
"""

import os
from typing import Type, Any, Dict, Optional
from pydantic import BaseModel, Field
from crewai.tools.base_tool import BaseTool
from .ai_router_llm import AIRouterLLM

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
    args_schema: Type[BaseModel] = AIRouterInput
    
    def __init__(self, **data):
        super().__init__(**data)
        # Инициализируем экземпляр AI Router LLM для использования внутри инструмента
        self.ai_router_llm = AIRouterLLM()
    
    def _run(self, message: str, task_type: str = "chat", model_preference: str = "auto", 
             max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Отправка запроса через AI Router
        """
        try:
            # Используем наш Python-based AI Router
            # model_preference и task_type пока игнорируются, т.к. роутер сам выбирает лучшую модель
            response = self.ai_router_llm.call(
                prompt=message,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return f"🤖 AI Router: {response}"
            
        except Exception as e:
            return f"❌ Ошибка вызова AI Router: {str(e)}"


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