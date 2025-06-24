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
        Поддержка задач: text-generation, text2text-generation, text-classification, conversational, code, chat
        """
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            return "❌ HUGGINGFACE_API_KEY не найден в переменных окружения"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {}
        # Формируем payload в зависимости от типа задачи
        if task_type in ["text-generation", "code-generation", "text2text-generation"]:
            payload = {
                "inputs": message,
                "parameters": {
                    "max_length": max_length,
                    "temperature": temperature,
                    "do_sample": True,
                    "top_p": 0.9
                }
            }
        elif task_type in ["conversational", "chat"]:
            # Для chat моделей (например, Llama-2-chat, Falcon-chat)
            payload = {
                "inputs": {
                    "text": message
                },
                "parameters": {
                    "max_length": max_length,
                    "temperature": temperature,
                    "do_sample": True,
                    "top_p": 0.9
                }
            }
        elif task_type == "text-classification":
            payload = {"inputs": message}
        else:
            payload = {"inputs": message}
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model_name}",
                headers=headers,
                json=payload,
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                # Обработка разных форматов ответа
                if isinstance(data, list):
                    if len(data) > 0 and "generated_text" in data[0]:
                        generated_text = data[0]["generated_text"]
                        if generated_text.startswith(message):
                            generated_text = generated_text[len(message):].strip()
                        return generated_text or str(data)
                    elif len(data) > 0 and "label" in data[0]:
                        # text-classification
                        return f"Класс: {data[0]['label']}, score: {data[0].get('score', '')}"
                    else:
                        return str(data)
                elif isinstance(data, dict):
                    if "generated_text" in data:
                        return data["generated_text"]
                    elif "conversation" in data:
                        # conversational/chat
                        return data["conversation"].get("generated_responses", [""])[-1]
                    elif "labels" in data:
                        return str(data["labels"])
                    else:
                        return str(data)
                else:
                    return str(data)
            elif response.status_code == 503:
                return "⏳ Модель загружается, попробуйте через 20 секунд"
            elif response.status_code == 429:
                return "⚠️ Превышен лимит запросов (1000/месяц)"
            else:
                return f"❌ API ошибка: {response.status_code} {response.text}"
        except requests.exceptions.Timeout:
            return "⏰ Таймаут запроса (60 сек)"
        except requests.exceptions.RequestException as e:
            return f"🌐 Сетевая ошибка: {str(e)}"
        except Exception as e:
            return f"❌ Ошибка HuggingFace Tool: {str(e)}"


    def _run(self, *args, **kwargs):
        """
        Универсальный запуск: поддержка всех задач HF (text, code, chat, classification)
        """
        message = kwargs.get('message') or (args[0] if args else None)
        if message is None:
            return "❌ Не передано сообщение для HuggingFace Tool"
        model_name = kwargs.get('model_name', "tiiuae/falcon-7b-instruct")
        task_type = kwargs.get('task_type', "text-generation")
        max_length = kwargs.get('max_length', 200)
        temperature = kwargs.get('temperature', 0.7)
        return self.run(str(message), model_name, task_type, max_length, temperature)
    def get_usage_stats(self) -> str:
        return "(статистика не реализована в этой версии)"

    # print("✅ Hugging Face Tool готов!")  # убрано из глобального пространства

