#!/usr/bin/env python3
"""
Тестовый клиент для API сервера CrewAI
"""

import requests
import json
import time
import sys

# Настройки API
API_URL = "http://127.0.0.1:5050"

def check_server_health():
    """Проверка доступности сервера"""
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Сервер доступен!")
            print(f"⭐ Статус: {data.get('status', 'unknown')}")
            print(f"⭐ CrewAI: {'доступен' if data.get('crewai_available', False) else 'недоступен'}")
            print(f"⭐ txtai: {'доступен' if data.get('txtai_available', False) else 'недоступен'}")
            return True
        else:
            print(f"❌ Сервер вернул код {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при подключении к серверу: {e}")
        return False

def send_message(message, force_crewai=False):
    """Отправка сообщения на сервер"""
    print(f"📤 Отправка: {message[:50]}...")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/api/process",
            json={"message": message, "force_crewai": force_crewai},
            timeout=30  # 30 секунд таймаут
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ получен за {elapsed:.2f} сек")
            print(f"📊 Обработан через CrewAI: {data.get('processed_with_crewai', False)}")
            print(f"\n{'='*50}\n{data.get('response', 'Нет ответа')}\n{'='*50}")
            return data.get('response')
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Ошибка при отправке сообщения: {e}")
        return None

def main():
    """Основная функция"""
    print("🤖 Тестовый клиент CrewAI API")
    
    # Проверяем доступность сервера
    if not check_server_health():
        print("❌ Сервер недоступен. Убедитесь, что он запущен на http://127.0.0.1:5050")
        sys.exit(1)
        
    # Простой интерактивный режим
    print("\n💬 Введите сообщение (или 'exit' для выхода, 'crew' для принудительного использования CrewAI):")
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ["exit", "quit", "q", "выход"]:
                break
                
            force_crewai = False
            if user_input.startswith("crew:"):
                force_crewai = True
                user_input = user_input[5:].strip()
                print("🤖 Принудительное использование CrewAI")
                
            if user_input:
                send_message(user_input, force_crewai)
        except KeyboardInterrupt:
            print("\n👋 Работа завершена")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    print("👋 Тест завершен")

if __name__ == "__main__":
    main() 