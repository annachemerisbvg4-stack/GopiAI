"""
Простая проверка исправления ошибки 422
"""
import requests
import json
import time

def check_rag_server():
    """Проверяем, что RAG сервер запущен"""
    try:
        response = requests.get("http://127.0.0.1:8080/health", timeout=3)
        print(f"✅ RAG сервер доступен (статус: {response.status_code})")
        return True
    except requests.ConnectionError:
        print("❌ RAG сервер не запущен на порту 8080")
        return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def test_session_creation():
    """Тестируем создание сессии"""
    print("\n🧪 Тест создания сессии:")
    print("-" * 40)
    
    # Данные в правильном формате согласно CreateSessionRequest
    data = {
        "title": "Test Session",
        "project_context": "GopiAI-WebView",
        "tags": ["test", "webview"]
    }
    
    print(f"📤 Отправляем POST /sessions")
    print(f"📦 Данные: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:8080/sessions",
            json=data,
            timeout=10
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        print(f"📄 Ответ сервера: {response.text}")
        
        if response.status_code == 200:
            print("✅ УСПЕХ! Сессия создана без ошибки 422")
            return response.json().get("session_id")
        elif response.status_code == 422:
            print("❌ ОШИБКА 422! Проблема с валидацией данных")
            print("🔍 Возможные причины:")
            print("   - Неправильный формат JSON")
            print("   - Отсутствие обязательных полей")
            print("   - Неправильные типы данных")
            return None
        else:
            print(f"❌ Другая ошибка: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return None

def test_message_creation(session_id):
    """Тестируем добавление сообщения"""
    if not session_id:
        print("\n❌ Нет session_id для тестирования сообщений")
        return False
        
    print(f"\n🧪 Тест добавления сообщения в сессию {session_id}:")
    print("-" * 60)
    
    # Данные в правильном формате согласно AddMessageRequest
    data = {
        "content": "Привет! Это тестовое сообщение для проверки API",
        "role": "user",
        "metadata": {"test": True, "source": "api_test"}
    }
    
    print(f"📤 Отправляем POST /sessions/{session_id}/messages")
    print(f"📦 Данные: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"http://127.0.0.1:8080/sessions/{session_id}/messages",
            json=data,
            timeout=10
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        print(f"📄 Ответ сервера: {response.text}")
        
        if response.status_code == 200:
            print("✅ УСПЕХ! Сообщение добавлено без ошибки 422")
            return True
        elif response.status_code == 422:
            print("❌ ОШИБКА 422! Проблема с валидацией данных")
            return False
        else:
            print(f"❌ Другая ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False

def explain_fix():
    """Объясняем что было исправлено"""
    print("\n" + "="*60)
    print("🔧 ЧТО БЫЛО ИСПРАВЛЕНО В API:")
    print("="*60)
    
    print("\n❌ ДО ИСПРАВЛЕНИЯ:")
    print("   - Эндпоинты принимали 'сырой' JSON")
    print("   - Отсутствовала валидация данных")
    print("   - FastAPI не знал структуру запросов")
    print("   - Результат: ошибка 422 (Unprocessable Entity)")
    
    print("\n✅ ПОСЛЕ ИСПРАВЛЕНИЯ:")
    print("   - Добавлены Pydantic модели:")
    print("     • CreateSessionRequest (title, project_context, tags)")
    print("     • AddMessageRequest (content, role, metadata)")
    print("   - Эндпоинты теперь принимают типизированные модели")
    print("   - Автоматическая валидация входных данных")
    print("   - Четкая документация API в /docs")
    
    print("\n🔍 ОШИБКА 422 ОЗНАЧАЕТ:")
    print("   'Unprocessable Entity' - сервер понимает запрос,")
    print("   но не может обработать из-за ошибок валидации")
    
    print("\n📝 ПРАВИЛЬНЫЕ ФОРМАТЫ ЗАПРОСОВ:")
    print("\n   Создание сессии:")
    print(json.dumps({
        "title": "Название разговора",
        "project_context": "GopiAI-WebView",
        "tags": ["webview", "chat"]
    }, indent=6, ensure_ascii=False))
    
    print("\n   Добавление сообщения:")
    print(json.dumps({
        "content": "Текст сообщения",
        "role": "user",
        "metadata": {"extra": "info"}
    }, indent=6, ensure_ascii=False))

def main():
    """Основная функция"""
    print("🚀 ПРОВЕРКА ИСПРАВЛЕНИЯ ОШИБКИ 422 В RAG API")
    print("="*60)
    
    # Проверяем сервер
    if not check_rag_server():
        print("\n💡 Для запуска сервера выполните:")
        print("   cd rag_memory_system")
        print("   python api.py")
        return
    
    # Тестируем исправления
    session_id = test_session_creation()
    message_ok = test_message_creation(session_id)
    
    # Объясняем исправления
    explain_fix()
    
    # Итоговый результат
    print("\n" + "="*60)
    print("📋 РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ:")
    print("="*60)
    
    if session_id and message_ok:
        print("🎉 ОТЛИЧНО! Ошибка 422 полностью исправлена!")
        print("✅ API работает корректно")
        print("✅ Сессии создаются без проблем")
        print("✅ Сообщения сохраняются успешно")
        print(f"\n🌐 Дашборд: http://127.0.0.1:8080")
        print(f"📚 API документация: http://127.0.0.1:8080/docs")
    else:
        print("⚠️ Есть проблемы, требующие дополнительного анализа")

if __name__ == "__main__":
    main()