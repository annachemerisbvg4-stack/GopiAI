"""
🔄 GopiAI AI Router LLM для CrewAI
Адаптер, использующий Python-based систему ротации моделей.
"""

import traceback
from typing import Dict, List, Optional, Any, Mapping

# Импортируем базовый класс и новую логику ротации
from .base.base_tool import GopiAIBaseTool
from llm_rotation_config import select_llm_model_safe, rate_limit_monitor, get_api_key_for_provider, LLM_MODELS_CONFIG
from crewai import Agent, Task, Crew, Process
from crewai import LLM

class AIRouterLLM(GopiAIBaseTool):
    """
    LLM-адаптер для использования AI Router с CrewAI.
    
    Преимущества:
    - Автоматическая ротация между провайдерами
    - Fallback при превышении лимитов
    - Оптимизация под задачу
    """
    
    def __init__(self, **kwargs):
        """Инициализирует AI Router LLM адаптер"""
        super().__init__()
        self.model_configs = {m['id']: m for m in LLM_MODELS_CONFIG}
        print("✅ Python-based AI Router LLM адаптер инициализирован.")
    
    def call(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        Вызов LLM через AI Router
        
        Этот метод соответствует интерфейсу, ожидаемому CrewAI
        """
        try:
            # 1. Выбираем лучшую доступную модель
            # Приблизительно оцениваем количество токенов в промпте
            prompt_tokens = len(prompt) // 3 
            model_id = select_llm_model_safe("dialog", tokens=prompt_tokens)
            
            if not model_id:
                return "❌ Все LLM провайдеры временно недоступны из-за лимитов. Пожалуйста, подождите."

            model_config = self.model_configs.get(model_id)
            if not model_config:
                 return f"❌ Конфигурация для модели {model_id} не найдена."

            provider_name = model_config['provider']
            api_key = get_api_key_for_provider(provider_name)

            if not api_key:
                return f"❌ API ключ для провайдера {provider_name} не найден."

            print(f"🔄 AI Router: Выбрана модель '{model_id}' от провайдера '{provider_name}'.")

            # 2. Создаем экземпляр LLM
            llm_params = {
                'model': model_id,
                'api_key': api_key,
                'config': {
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                }
            }
            # Для моделей Google (gemini) CrewAI не требует base_url,
            # он определяется автоматически по префиксу модели.

            llm_instance = LLM(**llm_params)

            # 3. Выполняем запрос
            response = llm_instance.call(prompt)
            
            # 4. Регистрируем использование
            response_tokens = len(response) // 3
            rate_limit_monitor.register_use(model_id, tokens=prompt_tokens + response_tokens)
            
            return response

        except Exception as e:
            print(f"❌ Ошибка при вызове AI Router: {e}")
            traceback.print_exc()
            return f"Произошла критическая ошибка в AI Router: {e}"
            
    def get_llm_instance(self):
        """
        Возвращает экземпляр LLM для использования с CrewAI
        
        Returns:
            LLM: Экземпляр LLM для CrewAI
        """
        try:
            from langchain.llms.base import LLM as LangChainLLM
            
            class AIRouterWrapper(LangChainLLM):
                """Обертка для AI Router, совместимая с LangChain/CrewAI"""
                
                def __init__(self, ai_router: 'AIRouterLLM', **kwargs):
                    super().__init__(**kwargs)
                    self.ai_router = ai_router
                
                @property
                def _llm_type(self) -> str:
                    return "gopiai_router"
                
                def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
                    """Вызов AI Router"""
                    # Передаем kwargs в основной метод call
                    return self.ai_router.call(prompt, **kwargs)
                
                @property
                def _identifying_params(self) -> Mapping[str, Any]:
                    """Идентификационные параметры для LangChain"""
                    return {"model": "gopiai_router"}
            
            return AIRouterWrapper(ai_router=self)
            
        except ImportError:
            print("⚠️ langchain не найден, возвращаем self. Это может вызвать проблемы в CrewAI.")
            return self

    def _run(self, message: str, **kwargs) -> str:
        """
        Обязательный метод для наследников GopiAIBaseTool
        Перенаправляет вызов на основной метод `call`.
        """
        return self.call(message, **kwargs)
