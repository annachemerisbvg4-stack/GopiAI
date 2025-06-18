#!/usr/bin/env python3
"""
Тест интеграции новой RAG системы
=================================
Проверка работы всех компонентов с новой simple_rag_server.py
"""

import sys
import time
import requests
import subprocess
from pathlib import Path

def test_memory_initializer():
    """Тест memory_initializer.py"""
    print("🧪 Тестируем memory_initializer.py...")
    
    try:
        # Добавляем путь к UI модулю
        ui_path = Path("GopiAI-UI")
        if ui_path.exists():
            sys.path.insert(0, str(ui_path))
        
        from gopiai.ui.memory_initializer import init_memory_system, get_memory_status
        
        # Инициализируем систему
        print("  - Инициализация системы памяти...")
        success = init_memory_system(silent=False)
        
        if success:
            print("  ✅ Система памяти запущена")
            
            # Проверяем статус
            status = get_memory_status()
            print(f"  📊 Статус: {status}")
            
            return True
        else:
            print("  ❌ Не удалось запустить систему памяти")
            return False
            
    except Exception as e:
        print(f"  ❌ Ошибка тестирования memory_initializer: {e}")
        return False

def test_rag_api():
    """Тест RAG API endpoints"""
    print("🧪 Тестируем RAG API...")
    
    base_url = "http://127.0.0.1:8080"
    
    try:
        # Тест health check
        print("  - Проверка /health...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"  ✅ Health check: {response.json()}")
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
        
        # Тест создания сессии
        print("  - Создание сессии...")
        session_data = {
            "title": "Test Session",
            "project_context": "test",
            "tags": ["test", "integration"]
        }
        response = requests.post(f"{base_url}/sessions", json=session_data, timeout=5)
        if response.status_code == 200:
            session_id = response.json()["session_id"]
            print(f"  ✅ Сессия создана: {session_id}")
        else:
            print(f"  ❌ Не удалось создать сессию: {response.status_code}")
            return False
        
        # Тест добавления сообщения
        print("  - Добавление сообщения...")
        message_data = {
            "role": "user",
            "content": "Это тестовое сообщение для проверки RAG интеграции",
            "metadata": {"test": True}
        }
        response = requests.post(f"{base_url}/sessions/{session_id}/messages", json=message_data, timeout=5)
        if response.status_code == 200:
            print("  ✅ Сообщение добавлено")
        else:
            print(f"  ❌ Не удалось добавить сообщение: {response.status_code}")
            return False
        
        # Тест поиска
        print("  - Тест поиска...")
        response = requests.get(f"{base_url}/search", params={"q": "тестовое", "limit": 3}, timeout=5)
        if response.status_code == 200:
            results = response.json()["results"]
            print(f"  ✅ Поиск выполнен: найдено {len(results)} результатов")
            if results:
                print(f"     Первый результат: {results[0]['matched_content'][:50]}...")
        else:
            print(f"  ❌ Ошибка поиска: {response.status_code}")
            return False
        
        # Тест статистики
        print("  - Проверка статистики...")
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"  ✅ Статистика: {stats}")
        else:
            print(f"  ❌ Ошибка получения статистики: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка тестирования API: {e}")
        return False

def test_chat_memory():
    """Тест chat_memory.py"""
    print("🧪 Тестируем chat_memory.py...")
    
    try:
        # Добавляем путь к WebView модулю
        webview_path = Path("GopiAI-WebView")
        if webview_path.exists():
            sys.path.insert(0, str(webview_path))
        
        from gopiai.webview.chat_memory import create_memory_manager
        
        # Создаем менеджер памяти
        memory_manager = create_memory_manager()
        print("  ✅ Менеджер памяти создан")
        
        # Тест обогащения сообщения
        test_message = "Как дела с интеграцией RAG?"
        enriched = memory_manager.enrich_message(test_message)
        print(f"  ✅ Обогащение сообщения: {len(enriched)} символов")
        
        # Тест сохранения обмена
        success = memory_manager.save_chat_exchange(
            "Тестовый вопрос пользователя",
            "Тестовый ответ ассистента"
        )
        print(f"  ✅ Сохранение обмена: {success}")
        
        # Тест статистики
        stats = memory_manager.get_memory_stats()
        print(f"  ✅ Статистика памяти: {stats}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка тестирования chat_memory: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование интеграции новой RAG системы")
    print("=" * 50)
    
    # Сначала проверим, запущен ли сервер
    try:
        response = requests.get("http://127.0.0.1:8080/health", timeout=2)
        if response.status_code == 200:
            print("✅ RAG сервер уже запущен")
        else:
            print("❌ RAG сервер не отвечает")
            return
    except:
        print("🚀 RAG сервер не запущен, попробуем инициализировать...")
        if not test_memory_initializer():
            print("❌ Не удалось запустить RAG сервер")
            return
    
    # Даем серверу время на запуск
    time.sleep(2)
    
    # Запускаем тесты
    tests = [
        ("RAG API", test_rag_api),
        ("Chat Memory", test_chat_memory),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'─' * 20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте {test_name}: {e}")
            results[test_name] = False
    
    # Итоги
    print(f"\n{'=' * 50}")
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ:")
    
    for test_name, result in results.items():
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Интеграция RAG работает корректно.")
    else:
        print("\n⚠️ Некоторые тесты провалены. Нужны доработки.")

if __name__ == "__main__":
    main()