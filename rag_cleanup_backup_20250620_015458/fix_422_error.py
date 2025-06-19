"""
Скрипт для исправления и тестирования ошибки 422 в RAG API
"""
import subprocess
import time
import requests
import json
import sys
import os
from threading import Thread

def start_rag_server():
    """Запустить RAG сервер в отдельном процессе"""
    try:
        env_python = r"C:\Users\crazy\GOPI_AI_MODULES\rag_memory_env\Scripts\python.exe"
        api_path = r"C:\Users\crazy\GOPI_AI_MODULES\rag_memory_system\api.py"
        
        print("🚀 Запускаем RAG сервер...")
        
        # Запускаем сервер в фоне
        process = subprocess.Popen(
            [env_python, api_path],
            cwd=r"C:\Users\crazy\GOPI_AI_MODULES\rag_memory_system",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        # Даем серверу время на запуск
        print("⏳ Ждем запуска сервера...")
        time.sleep(5)
        
        return process
        
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        return None

def test_server_connection():
    """Проверить соединение с сервером"""
    try:
        response = requests.get("http://127.0.0.1:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ Сервер доступен")
            return True
        else:
            print(f"❌ Сервер вернул код {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Сервер недоступен")
        return False
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
        return False

def test_session_creation():
    """Тест создания сессии с правильным форматом JSON"""
    url = "http://127.0.0.1:8080/sessions"
    
    # Правильный формат данных согласно CreateSessionRequest
    data = {
        "title": "GopiAI Chat Session Test",
        "project_context": "GopiAI-WebView",
        "tags": ["webview", "chat", "test"]
    }
    
    try:
        print("\n🧪 Тестируем создание сессии...")
        print(f"📡 POST {url}")
        print(f"📦 Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Сессия создана успешно!")
            response_data = response.json()
            return response_data.get("session_id")
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def test_message_creation(session_id):
    """Тест добавления сообщения в сессию"""
    if not session_id:
        print("❌ Нет session_id для тестирования сообщений")
        return False
    
    try:
        # Тестируем добавление сообщения
        message_url = f"http://127.0.0.1:8080/sessions/{session_id}/messages"
        message_data = {
            "content": "Привет! Это тестовое сообщение",
            "role": "user",
            "metadata": {"test": True}
        }
        
        print(f"\n🧪 Тестируем добавление сообщения...")
        print(f"📡 POST {message_url}")
        print(f"📦 Data: {json.dumps(message_data, indent=2)}")
        
        message_response = requests.post(message_url, json=message_data, timeout=10)
        
        print(f"📊 Status: {message_response.status_code}")
        print(f"📄 Response: {message_response.text}")
        
        if message_response.status_code == 200:
            print("✅ Сообщение добавлено успешно!")
            return True
        else:
            print(f"❌ Ошибка {message_response.status_code}: {message_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при добавлении сообщения: {e}")
        return False

def analyze_422_error():
    """Анализ ошибки 422 и возможных причин"""
    print("\n📋 Анализ ошибки 422 (Unprocessable Entity):")
    print("=" * 60)
    print("🔍 Возможные причины:")
    print("   1. Неправильный формат JSON в запросе")
    print("   2. Отсутствие обязательных полей в Pydantic модели")
    print("   3. Неправильные типы данных в полях")
    print("   4. Проблемы валидации в FastAPI")
    print("   5. Ошибки в определении эндпоинтов")
    
    print("\n🛠️ Что было исправлено:")
    print("   ✅ Добавлены Pydantic модели CreateSessionRequest и AddMessageRequest")
    print("   ✅ Эндпоинты теперь принимают эти модели вместо сырого JSON")
    print("   ✅ Правильная валидация данных в FastAPI")
    
    print("\n📝 Формат запроса для создания сессии:")
    print(json.dumps({
        "title": "Название разговора",
        "project_context": "GopiAI-WebView", 
        "tags": ["webview", "chat"]
    }, indent=2))
    
    print("\n📝 Формат запроса для добавления сообщения:")
    print(json.dumps({
        "content": "Текст сообщения",
        "role": "user",  # user, assistant, system
        "metadata": {"extra": "info"}
    }, indent=2))

def main():
    """Основная функция"""
    print("🔧 Исправление и тестирование ошибки 422 в RAG API")
    print("=" * 60)
    
    # Анализируем ошибку
    analyze_422_error()
    
    # Запускаем сервер
    server_process = start_rag_server()
    if not server_process:
        print("❌ Не удалось запустить сервер")
        return
    
    try:
        # Проверяем соединение
        if not test_server_connection():
            print("❌ Сервер недоступен для тестирования")
            return
        
        # Тестируем создание сессии
        session_id = test_session_creation()
        
        # Тестируем добавление сообщения
        message_ok = test_message_creation(session_id)
        
        # Результаты
        print("\n" + "=" * 60)
        print("📋 Результаты тестирования:")
        print(f"   Создание сессии: {'✅' if session_id else '❌'}")
        print(f"   Добавление сообщения: {'✅' if message_ok else '❌'}")
        
        if session_id and message_ok:
            print("\n🎉 Ошибка 422 исправлена! API работает корректно!")
        else:
            print("\n⚠️ Есть проблемы с API")
        
        # Показываем дашборд
        print(f"\n📊 Dashboard доступен: http://127.0.0.1:8080")
        print(f"📚 API документация: http://127.0.0.1:8080/docs")
        
    finally:
        # Останавливаем сервер
        if server_process:
            print("\n🛑 Останавливаем сервер...")
            server_process.terminate()
            time.sleep(1)
            if server_process.poll() is None:
                server_process.kill()

if __name__ == "__main__":
    main()