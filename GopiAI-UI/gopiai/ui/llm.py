"""
Local LLM Client for GopiAI UI
Простая замена для удаленного ui_core.llm
"""

import logging
import os
import sys
from pathlib import Path

# Добавляем путь к CrewAI модулям для доступа к llm_rotation_config
crewai_path = Path(__file__).parent.parent.parent.parent / "GopiAI-CrewAI"
if str(crewai_path) not in sys.path:
    sys.path.append(str(crewai_path))

try:
    from llm_rotation_config import select_llm_model_safe, safe_llm_call
except ImportError:
    # Fallback если не удается импортировать
    def select_llm_model_safe(task_type, **kwargs):
        return {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash"}
    
    def safe_llm_call(prompt, llm_call_func, task_type, **kwargs):
        return "LLM недоступен"

logger = logging.getLogger(__name__)

class SimpleLLMClient:
    """Простой LLM клиент для UI компонентов"""
    
    def __init__(self):
        self.current_model = None
        logger.info("LLM client initialized")
    
    def get_model(self, task_type="dialog"):
        """Получить подходящую модель для задачи"""
        try:
            model = select_llm_model_safe(task_type)
            self.current_model = model
            return model
        except Exception as e:
            logger.error(f"Error selecting LLM model: {e}")
            return {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash"}
    
    def call(self, prompt, task_type="dialog", **kwargs):
        """Вызов LLM с промптом"""
        try:
            model = self.get_model(task_type)
            
            # Простая заглушка для вызова LLM
            # В реальной реализации здесь был бы вызов API
            def mock_llm_call(prompt):
                return f"Mock response for: {prompt[:100]}..."
            
            return safe_llm_call(prompt, mock_llm_call, task_type, **kwargs)
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return f"Error: {str(e)}"
    
    def is_available(self):
        """Проверка доступности LLM"""
        return True

# Глобальный экземпляр клиента
_llm_client = None

def get_llm_client():
    """Получить экземпляр LLM клиента"""
    global _llm_client
    if _llm_client is None:
        _llm_client = SimpleLLMClient()
    return _llm_client
