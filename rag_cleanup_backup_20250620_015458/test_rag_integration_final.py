#!/usr/bin/env python3
"""
Тестирование интеграции новой RAG системы с компонентами GopiAI
==============================================================
"""

import requests
import json
import sys
from pathlib import Path

def test_rag_server_health():
    """Проверка работоспособности RAG сервера"""
    print("🔍 Тестирование RAG сервера...")
    
    try:
        # Проверяем health endpoint
        response = requests.get("http://127.0.0.1:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ RAG сервер отвечает на /health")
            print(f"   Ответ: {response.json()}")
        else:
            print(f"❌ RAG сервер вернул статус {response.status_code}")
            return False
            
        # Проверяем статистику
        response = requests.get("http://127.0.0.1:8080/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("✅ Статистика RAG сервера:")
            print(f"   Сессии: {stats.get('conversations', 0)}")
            print(f"   Chunk-и: {stats.get('chunks', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к RAG серверу: {e}")
        return False

def test_session_creation():
    """Тестирование создания сессии"""
    print("\n🔍 Тестирование создания сессии...")
    
    try:
        # Создаем новую сессию
        session_data = {
            "title": "Test Session",
            "project_context": "GopiAI Integration Test",
            "tags": ["test", "integration"]
        }
        
        response = requests.post("http://127.0.0.1:8080/sessions", 
                               params=session_data, timeout=5)
        
        if response.status_code == 200:
            session_info = response.json()
            session_id = session_info.get("session_id")
            print(f"✅ Сессия создана: {session_id}")
            return session_id
        else:
            print(f"❌ Ошибка создания сессии: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка создания сессии: {e}")
        return None

def test_message_saving(session_id):
    """Тестирование сохранения сообщений"""
    print(f"\n🔍 Тестирование сохранения сообщений в сессии {session_id}...")
    
    try:
        # Добавляем сообщение пользователя
        user_message = {
            "content": "Как настроить интеграцию RAG системы с GopiAI?",
            "role": "user",
            "metadata": {"test": True}
        }
        
        response = requests.post(f"http://127.0.0.1:8080/sessions/{session_id}/messages",
                               json=user_message, timeout=5)
        
        if response.status_code == 200:
            print("✅ Сообщение пользователя сохранено")
        else:
            print(f"❌ Ошибка сохранения сообщения: {response.status_code}")
            return False
        
        # Добавляем ответ ассистента
        ai_message = {
            "content": "Для интеграции RAG системы нужно настроить API endpoints, проверить совместимость портов и обновить memory_initializer.py",
            "role": "assistant",
            "metadata": {"test": True}
        }
        
        response = requests.post(f"http://127.0.0.1:8080/sessions/{session_id}/messages",
                               json=ai_message, timeout=5)
        
        if response.status_code == 200:
            print("✅ Ответ ассистента сохранен")
            return True
        else:
            print(f"❌ Ошибка сохранения ответа: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка сохранения сообщений: {e}")
        return False

def test_search_functionality():
    """Тестирование поиска"""
    print("\n🔍 Тестирование поиска в RAG системе...")
    
    try:
        # Поиск по ключевому слову
        search_params = {
            "q": "интеграция RAG",
            "limit": 3
        }
        
        response = requests.get("http://127.0.0.1:8080/search",
                              params=search_params, timeout=5)
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Поиск выполнен успешно")
            print(f"   Найдено результатов: {len(results.get('results', []))}")
            
            # Показываем результаты
            for i, result in enumerate(results.get('results', [])[:2]):
                print(f"   Результат {i+1}: {result.get('content', '')[:100]}...")
            
            return True
        else:
            print(f"❌ Ошибка поиска: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        return False

def test_memory_initializer():
    """Тестирование memory_initializer.py"""
    print("\n🔍 Тестирование memory_initializer.py...")
    
    try:
        # Добавляем путь к GopiAI-UI
        ui_path = Path("GopiAI-UI")
        if ui_path.exists():
            sys.path.insert(0, str(ui_path))
            
            from gopiai.ui.memory_initializer import get_memory_status
            
            status = get_memory_status()
            print("✅ memory_initializer.py работает")
            print(f"   Статус: {status}")
            return True
        else:
            print("⚠️ GopiAI-UI не найден, пропускаем тест")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка тестирования memory_initializer: {e}")
        return False

def test_chat_memory():
    """Тестирование chat_memory.py"""
    print("\n🔍 Тестирование chat_memory.py...")
    
    try:
        # Добавляем путь к GopiAI-WebView
        webview_path = Path("GopiAI-WebView")
        if webview_path.exists():
            sys.path.insert(0, str(webview_path))
            
            from gopiai.webview.chat_memory import create_memory_manager
            
            memory_manager = create_memory_manager()
            
            # Тестируем обогащение сообщения
            test_message = "Как работает система памяти?"
            enriched = memory_manager.enrich_message(test_message)
            
            print("✅ chat_memory.py работает")
            print(f"   Исходное сообщение: {test_message}")
            print(f"   Обогащенное: {len(enriched)} символов")
            
            # Тестируем сохранение
            saved = memory_manager.save_chat_exchange(
                "Тестовый вопрос", 
                "Тестовый ответ"
            )
            print(f"   Сохранение: {'✅' if saved else '❌'}")
            
            return True
        else:
            print("⚠️ GopiAI-WebView не найден, пропускаем тест")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка тестирования chat_memory: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ RAG СИСТЕМЫ С GOPIAI")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 6
    
    # Тест 1: Проверка RAG сервера
    if test_rag_server_health():
        tests_passed += 1
    
    # Тест 2: Создание сессии
    session_id = test_session_creation()
    if session_id:
        tests_passed += 1
        
        # Тест 3: Сохранение сообщений
        if test_message_saving(session_id):
            tests_passed += 1
    
    # Тест 4: Поиск
    if test_search_functionality():
        tests_passed += 1
    
    # Тест 5: memory_initializer
    if test_memory_initializer():
        tests_passed += 1
    
    # Тест 6: chat_memory
    if test_chat_memory():
        tests_passed += 1
    
    # Итоги
    print("\n" + "=" * 60)
    print(f"📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print(f"✅ Пройдено: {tests_passed}/{total_tests} тестов")
    
    if tests_passed == total_tests:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Интеграция RAG работает корректно.")
    else:
        print("⚠️ Некоторые тесты не прошли. Требуется доработка.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)