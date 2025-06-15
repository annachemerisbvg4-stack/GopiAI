"""
Тест исправления API для создания сессий
"""
import requests
import json

def test_session_creation():
    """Тест создания сессии с правильным форматом JSON"""
    url = "http://127.0.0.1:8080/sessions"
    
    # Правильный формат данных согласно CreateSessionRequest
    data = {
        "title": f"GopiAI Chat Session Test",
        "project_context": "GopiAI-WebView",
        "tags": ["webview", "chat", "test"]
    }
    
    try:
        print("🧪 Тестируем создание сессии...")
        print(f"📡 POST {url}")
        print(f"📦 Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Сессия создана успешно!")
            return True
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ RAG сервер недоступен на 127.0.0.1:8080")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_message_creation():
    """Тест добавления сообщения в сессию"""
    # Сначала создаем сессию
    if not test_session_creation():
        return False
    
    # Получаем список сессий
    try:
        sessions_response = requests.get("http://127.0.0.1:8080/sessions", timeout=5)
        if sessions_response.status_code != 200:
            print("❌ Не удалось получить список сессий")
            return False
            
        sessions = sessions_response.json()
        if not sessions:
            print("❌ Нет доступных сессий")
            return False
            
        session_id = sessions[0].get("session_id")
        if not session_id:
            print("❌ Не удалось получить session_id")
            return False
            
        print(f"🆔 Используем session_id: {session_id}")
        
        # Тестируем добавление сообщения
        message_url = f"http://127.0.0.1:8080/sessions/{session_id}/messages"
        message_data = {
            "content": "Привет! Это тестовое сообщение",
            "role": "user",
            "metadata": {"test": True}
        }
        
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

if __name__ == "__main__":
    print("🧪 Тестирование исправленного RAG API")
    print("=" * 50)
    
    session_ok = test_session_creation()
    message_ok = test_message_creation()
    
    print("=" * 50)
    print("📋 Результаты:")
    print(f"   Создание сессии: {'✅' if session_ok else '❌'}")
    print(f"   Добавление сообщения: {'✅' if message_ok else '❌'}")
    
    if session_ok and message_ok:
        print("🎉 Все тесты прошли успешно!")
    else:
        print("⚠️ Есть проблемы с API")