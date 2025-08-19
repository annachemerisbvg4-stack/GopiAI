"""
Простой пример использования Google Gemini API.
Перед запуском установите переменную окружения GOOGLE_API_KEY
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

def main():
    # Загрузка переменных окружения из .env файла
    load_dotenv()
    
    # Получаем API ключ из переменных окружения
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Ошибка: Не найден GOOGLE_API_KEY в переменных окружения")
        print("Пожалуйста, создайте .env файл с содержимым:")
        print("GOOGLE_API_KEY=ваш_api_ключ")
        return
    
    # Настройка API
    genai.configure(api_key=api_key)
    
    # Инициализация модели
    model = genai.GenerativeModel('gemini-pro')
    
    # Простой запрос
    print("Отправляю запрос к Gemini...\n")
    
    response = model.generate_content("Привет! Расскажи что-нибудь интересное о космосе.")
    
    print("Ответ от Gemini:")
    print("-" * 50)
    print(response.text)
    print("-" * 50)

if __name__ == "__main__":
    main()
