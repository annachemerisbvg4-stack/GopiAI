"""
Сервис для работы с Gemini API.
Обеспечивает взаимодействие с Google Gemini API напрямую.
"""

import os
import json
from typing import Dict, List, Optional, Union
import logging

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key: str = None):
        """
        Инициализация сервиса Gemini.
        
        Args:
            api_key: API ключ для Google Gemini. Если None, будет использован из переменной окружения GEMINI_API_KEY.
        """
        if not GENAI_AVAILABLE:
            raise ImportError("google-generativeai не установлен. Установите его: pip install google-generativeai")
        
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            logger.warning("API ключ не найден. Установите переменную окружения GEMINI_API_KEY или GOOGLE_API_KEY")
        else:
            genai.configure(api_key=self.api_key)
            logger.info("Gemini API настроен успешно")
        
        self._check_api_connection()
    
    def _check_api_connection(self) -> bool:
        """Проверяет подключение к Gemini API."""
        if not self.api_key:
            return False
            
        try:
            # Пытаемся получить список моделей для проверки подключения
            models = list(genai.list_models())
            logger.info(f"Подключение к Gemini API успешно. Доступно моделей: {len(models)}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при подключении к Gemini API: {e}")
            return False
    
    def generate_text(self, prompt: str, model: str = "gemini-pro", **kwargs) -> Dict:
        """
        Генерация текста с помощью Gemini.
        
        Args:
            prompt: Текст запроса
            model: Модель для генерации (по умолчанию: gemini-pro)
            **kwargs: Дополнительные параметры (temperature, max_output_tokens и т.д.)
            
        Returns:
            Словарь с результатом генерации
        """
        if not self.api_key:
            return {"status": "error", "message": "API ключ не настроен"}
        
        try:
            # Создаем модель
            model_instance = genai.GenerativeModel(model)
            
            # Настраиваем параметры генерации
            generation_config = {}
            if 'temperature' in kwargs:
                generation_config['temperature'] = kwargs['temperature']
            if 'max_output_tokens' in kwargs or 'max_tokens' in kwargs:
                generation_config['max_output_tokens'] = kwargs.get('max_output_tokens', kwargs.get('max_tokens'))
            if 'top_p' in kwargs:
                generation_config['top_p'] = kwargs['top_p']
            if 'top_k' in kwargs:
                generation_config['top_k'] = kwargs['top_k']
            
            # Генерируем ответ
            response = model_instance.generate_content(
                prompt,
                generation_config=generation_config if generation_config else None
            )
            
            return {
                "status": "success",
                "data": response.text,
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                    "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
                }
            }
            
        except Exception as e:
            error_msg = f"Ошибка при генерации текста: {str(e)}"
            logger.exception(error_msg)
            return {"status": "error", "message": error_msg}
    
    def chat(self, messages: List[Dict[str, str]], model: str = "gemini-pro", **kwargs) -> Dict:
        """
        Чат с сохранением контекста.
        
        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}, ...]
            model: Модель для чата (по умолчанию: gemini-pro)
            **kwargs: Дополнительные параметры
            
        Returns:
            Словарь с ответом модели
        """
        if not self.api_key:
            return {"status": "error", "message": "API ключ не настроен"}
        
        try:
            # Создаем модель
            model_instance = genai.GenerativeModel(model)
            
            # Преобразуем историю сообщений в формат Gemini
            history = []
            current_prompt = ""
            
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role in ["user", "human"]:
                    current_prompt = content
                elif role in ["assistant", "model", "ai"]:
                    if current_prompt:
                        history.append({"role": "user", "parts": [current_prompt]})
                        history.append({"role": "model", "parts": [content]})
                        current_prompt = ""
            
            # Если есть последнее сообщение пользователя без ответа
            if current_prompt:
                # Начинаем чат с историей
                chat = model_instance.start_chat(history=history)
                response = chat.send_message(current_prompt)
            else:
                # Если нет текущего промпта, используем последнее сообщение
                if messages:
                    last_message = messages[-1]["content"]
                    chat = model_instance.start_chat(history=history[:-1] if history else [])
                    response = chat.send_message(last_message)
                else:
                    return {"status": "error", "message": "Нет сообщений для обработки"}
            
            return {
                "status": "success",
                "data": response.text,
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                    "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
                }
            }
            
        except Exception as e:
            error_msg = f"Ошибка в чате: {str(e)}"
            logger.exception(error_msg)
            return {"status": "error", "message": error_msg}
    
    def get_models(self) -> Dict:
        """Получает список доступных моделей."""
        if not self.api_key:
            return {"status": "error", "message": "API ключ не настроен"}
        
        try:
            models = []
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    models.append({
                        "name": model.name,
                        "display_name": model.display_name,
                        "description": model.description,
                        "input_token_limit": model.input_token_limit,
                        "output_token_limit": model.output_token_limit
                    })
            
            return {"status": "success", "data": models}
            
        except Exception as e:
            error_msg = f"Ошибка при получении списка моделей: {str(e)}"
            logger.exception(error_msg)
            return {"status": "error", "message": error_msg}
    
    def get_model_info(self, model_id: str) -> Dict:
        """Получает информацию о конкретной модели."""
        if not self.api_key:
            return {"status": "error", "message": "API ключ не настроен"}
        
        try:
            model = genai.get_model(model_id)
            return {
                "status": "success",
                "data": {
                    "name": model.name,
                    "display_name": model.display_name,
                    "description": model.description,
                    "input_token_limit": model.input_token_limit,
                    "output_token_limit": model.output_token_limit,
                    "supported_generation_methods": model.supported_generation_methods
                }
            }
            
        except Exception as e:
            error_msg = f"Ошибка при получении информации о модели: {str(e)}"
            logger.exception(error_msg)
            return {"status": "error", "message": error_msg}

# Сиглтон экземпляр сервиса
gemini_service = GeminiService()
