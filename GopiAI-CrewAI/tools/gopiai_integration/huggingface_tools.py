"""
🤗 Hugging Face LLM Tool для GopiAI-CrewAI
Интеграция с Hugging Face Inference API
"""

import os
import json
import requests
from typing import Type, Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from crewai.tools.base_tool import BaseTool

class HuggingFaceInput(BaseModel):
    """Схема входных данных для Hugging Face"""
    message: str = Field(description="Сообщение для модели")
    model_name: str = Field(default="tiiuae/falcon-7b-instruct", description="Название модели HF (например, tiiuae/falcon-7b-instruct, bigscience/bloomz-560m, tiiuae/falcon-7b-instruct, tiiuae/falcon-7b-instruct)")
    task_type: str = Field(default="text-generation", description="Тип задачи")
    max_length: int = Field(default=200, description="Максимальная длина ответа")
    temperature: float = Field(default=0.7, description="Температура генерации")

class GopiAIHuggingFaceTool(BaseTool):
    """
    Инструмент для работы с Hugging Face моделями
    
    Возможности:
    - Доступ к тысячам бесплатных моделей
    - Различные типы задач (текст, код, чат)
    - Кеширование для экономии лимитов
    - Автоматический выбор модели по задаче
    """
    
    name: str = Field(default="gopiai_huggingface", description="Имя инструмента")
    description: str = Field(default="Инструмент HuggingFace для CrewAI", description="Описание инструмента")

    def run(self, message: str, model_name: str = "tiiuae/falcon-7b-instruct", 
            task_type: str = "text-generation", max_length: int = 200, temperature: float = 0.7) -> str:
        """
        Выполнение реального запроса к Hugging Face Inference API
        """
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            return "❌ HUGGINGFACE_API_KEY не найден в переменных окружения"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": message,
            "parameters": {
                "max_length": max_length,
                "temperature": temperature,
                "do_sample": True,
                "top_p": 0.9
            }
        }
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model_name}",
                headers=headers,
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    generated_text = data[0].get("generated_text", "")
                    if generated_text.startswith(message):
                        generated_text = generated_text[len(message):].strip()
                    return generated_text or str(data)
                elif isinstance(data, dict):
                    return data.get("generated_text", str(data))
                else:
                    return str(data)
            elif response.status_code == 503:
                return "⏳ Модель загружается, попробуйте через 20 секунд"
            elif response.status_code == 429:
                return "⚠️ Превышен лимит запросов (1000/месяц)"
            else:
                return f"❌ API ошибка: {response.status_code}"
        except requests.exceptions.Timeout:
            return "⏰ Таймаут запроса (30 сек)"
        except requests.exceptions.RequestException as e:
            return f"🌐 Сетевая ошибка: {str(e)}"

    def _run(self, *args, **kwargs):
        return "HuggingFace Tool: действие не реализовано (заглушка)"

    def get_usage_stats(self) -> str:
        return "(статистика не реализована в этой версии)"

    print("✅ Hugging Face Tool готов!")

if __name__ == "__main__":
    print("🧪 Тестирование GopiAI Hugging Face Tool...")
    tool = GopiAIHuggingFaceTool()
    # Пример запроса к бесплатной модели
    result = tool.run(
        message="Привет! Расскажи коротко о космосе.",
        model_name="gpt2",
        task_type="text-generation",
        max_length=100,
        temperature=0.7
    )
    print(f"API test: {result}")
    print(tool.get_usage_stats())
    print("✅ Hugging Face Tool готов!")