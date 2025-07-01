#!/usr/bin/env python3
"""
Симулированный тест функции get_rag_context
Этот тест пытается подключиться к RAG серверу напрямую
"""

import requests
import json

def test_direct_rag_connection():
    """Тестирует прямое подключение к RAG серверу"""
    print("[TEST] Тестирование прямого подключения к RAG серверу")
    print("=" * 50)
    
    # Тестируем подключение к RAG серверу
    rag_url = "http://127.0.0.1:5051/api/search"
    test_query = "Как настроить CrewAI агентов?"
    
    try:
        print(f"🔍 Отправляем запрос к RAG серверу: {rag_url}")
        print(f"📝 Запрос: {test_query}")
        
        response = requests.post(
            rag_url,
            json={"query": test_query, "max_results": 3},
            timeout=5
        )
        
        print(f"📊 Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ RAG сервер ответил успешно!")
            print(f"📄 Полученные данные: {data}")
            
            context_items = data.get("context", [])
            if context_items:
                print(f"📚 Найдено контекстных элементов: {len(context_items)}")
                for i, item in enumerate(context_items, 1):
                    print(f"   {i}. {item[:100]}...")
            else:
                print("⚠️ Контекстные элементы пусты")
        else:
            print(f"❌ RAG сервер вернул ошибку: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к RAG серверу")
        print("💡 Убедитесь, что RAG сервер запущен на порту 5051")
        print("🔧 Для запуска RAG сервера используйте:")
        print("   python rag_memory_system/rag_server.py")
        
    except requests.exceptions.Timeout:
        print("❌ Таймаут подключения к RAG серверу")
        
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()

def test_rag_server_status():
    """Проверяет статус RAG сервера"""
    print("\n[TEST] Проверка статуса RAG сервера")
    print("=" * 50)
    
    status_urls = [
        "http://127.0.0.1:5051/",
        "http://127.0.0.1:5051/health",
        "http://127.0.0.1:5051/api/"
    ]
    
    for url in status_urls:
        try:
            response = requests.get(url, timeout=2)
            print(f"✅ {url} - Статус: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} - Недоступен")
        except Exception as e:
            print(f"⚠️ {url} - Ошибка: {e}")

def check_rag_processes():
    """Проверяет, запущены ли процессы RAG сервера"""
    print("\n[TEST] Проверка процессов RAG сервера")
    print("=" * 50)
    
    import subprocess
    import platform
    
    try:
        if platform.system() == "Windows":
            # Ищем процессы Python, которые могут быть RAG сервером
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe"],
                capture_output=True, text=True
            )
            print("🔍 Активные процессы Python:")
            print(result.stdout)
        else:
            # Для Linux/Mac
            result = subprocess.run(
                ["ps", "aux", "|", "grep", "python"],
                capture_output=True, text=True, shell=True
            )
            print("🔍 Активные процессы Python:")
            print(result.stdout)
            
    except Exception as e:
        print(f"❌ Ошибка при проверке процессов: {e}")

def main():
    print("🧪 Диагностика RAG системы")
    print("=" * 60)
    
    # Тест 1: Прямое подключение
    test_direct_rag_connection()
    
    # Тест 2: Статус сервера
    test_rag_server_status()
    
    # Тест 3: Проверка процессов
    check_rag_processes()
    
    print("\n" + "=" * 60)
    print("✅ Диагностика завершена!")
    print("\n💡 Если RAG сервер недоступен, попробуйте:")
    print("   1. cd rag_memory_system")
    print("   2. python rag_server.py")

if __name__ == "__main__":
    main()