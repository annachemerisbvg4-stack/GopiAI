import logging
import traceback
from typing import List, Optional, Any, Mapping, ClassVar

from pydantic import Field

from langchain.llms.base import BaseLLM
from langchain.schema import LLMResult, Generation

from llm_rotation_config import select_llm_model_safe, rate_limit_monitor, get_api_key_for_provider, LLM_MODELS_CONFIG
from crewai import LLM # Assuming this is litellm's LLM
from .base.base_tool import GopiAIBaseTool # Keeping this for now, as _run method might use it

class AIRouterLLM(BaseLLM):
    """
    A custom LLM that routes requests to the AI Router.
    """
    logger: ClassVar[logging.Logger] = logging.getLogger(__name__) # Аннотируем logger как ClassVar
    model_configs: dict = Field(default_factory=dict) # Define as class attribute

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_configs = {m['id']: m for m in LLM_MODELS_CONFIG} # Initialize in __init__

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
        generations = []
        for prompt in prompts:
            response_text = "" # Initialize response_text for each prompt
            try:
                # 1. Выбираем лучшую доступную модель
                # Приблизительно оцениваем количество токенов в промпте
                prompt_tokens = len(prompt) // 3
                model_id = select_llm_model_safe("dialog", tokens=prompt_tokens)

                if not model_id:
                    response_text = "❌ Все LLM провайдеры временно недоступны из-за лимитов. Пожалуйста, подождите."
                else:
                    model_config = self.model_configs.get(model_id)
                    if not model_config:
                        response_text = f"❌ Конфигурация для модели {model_id} не найдена."
                    else:
                        provider_name = model_config['provider']
                        api_key = get_api_key_for_provider(provider_name)

                        if not api_key:
                            response_text = f"❌ API ключ для провайдера {provider_name} не найден."
                        else:
                            self.logger.info(f"🔄 AI Router: Выбрана модель '{model_id}' от провайдера '{provider_name}'.")

                            # 2. Создаем экземпляр LLM
                            llm_params = {
                                'model': model_id,
                                'api_key': api_key,
                                'config': {
                                    'temperature': 0.7, # Using default temperature from original call method
                                    'max_tokens': 2000, # Using default max_tokens from original call method
                                }
                            }
                            llm_instance = LLM(**llm_params)

                            # 3. Выполняем запрос
                            response = llm_instance.call(prompt)
                            response_text = response

                            # 4. Регистрируем использование
                            response_tokens = len(response) // 3
                            rate_limit_monitor.register_use(model_id, tokens=prompt_tokens + response_tokens)

            except Exception as e:
                self.logger.error(f"❌ Ошибка при вызове AI Router: {e}")
                traceback.print_exc()
                response_text = f"Произошла критическая ошибка в AI Router: {e}"

            generations.append([Generation(text=response_text)])
        return LLMResult(generations=generations)

    @property
    def _llm_type(self) -> str:
        return "ai_router"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """
        Возвращает идентификационные параметры LLM.
        """
        return {"model": self._llm_type}

    # Keeping _run method as it's part of GopiAIBaseTool
    def _run(self, message: str, **kwargs) -> str:
        """
        Обязательный метод для наследников GopiAIBaseTool
        Перенаправляет вызов на основной метод `call`.
        """
        # Since `call` method is removed, we need to adapt this.
        # For now, I'll make it call _generate with a single prompt.
        # This might need further refinement depending on how _run is used.
        result = self._generate(prompts=[message])
        return result.generations[0][0].text
