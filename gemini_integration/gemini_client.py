"""
Клиент для работы с Google Gemini API.
Обеспечивает удобный интерфейс для отправки запросов к Gemini Pro.
"""

import os
from typing import Optional, Dict, Any, List, Union
import google.generativeai as genai
from dotenv import load_dotenv

class GeminiClient:
    """
    Клиент для работы с Google Gemini API.
    
    Пример использования:
        client = GeminiClient()
        response = client.generate("Привет, как дела?")
        print(response)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация клиента Gemini.
        
        Args:
            api_key: Ключ API Google AI Studio. Если не указан, будет загружен из переменной окружения GOOGLE_API_KEY.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Не указан API ключ для Gemini. Пожалуйста, укажите его в переменной окружения GOOGLE_API_KEY "
                "или передайте напрямую в конструктор."
            )
            
        # Настройка API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """
        Генерация текста с помощью Gemini Pro.
        
        Args:
            prompt: Текст промпта для модели
            temperature: Температура генерации (от 0 до 1)
            max_tokens: Максимальное количество токенов в ответе
            **kwargs: Дополнительные параметры для модели
            
        Returns:
            Сгенерированный текст
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    **kwargs
                }
            )
            return response.text
            
        except Exception as e:
            raise Exception(f"Ошибка при генерации текста: {str(e)}")
    
    def chat(
        self, 
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """
        Чат с сохранением контекста.
        
        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "..."}, ...]
            temperature: Температура генерации (от 0 до 1)
            max_tokens: Максимальное количество токенов в ответе
            **kwargs: Дополнительные параметры для модели
            
        Returns:
            Ответ модели
        """
        try:
            chat = self.model.start_chat(history=[])
            
            # Отправляем все сообщения по очереди
            for msg in messages:
                if msg["role"] == "user":
                    chat.send_message(msg["content"])
            
            # Генерируем ответ
            response = chat.send_message(
                messages[-1]["content"] if messages else "",
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    **kwargs
                }
            )
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Ошибка в чате: {str(e)}")
