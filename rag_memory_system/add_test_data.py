#!/usr/bin/env python3
"""
🧪 Добавление специальных тестовых данных в RAG память

Этот скрипт добавляет уникальные данные, которые помогут проверить
работу RAG в живом чате.
"""

import requests
import json

RAG_SERVER_URL = "http://127.0.0.1:5051"

# Специальные тестовые данные с уникальными фактами
TEST_DATA = [
    {
        "id": "secret_project_phoenix",
        "content": """🔥 Проект Феникс - это секретный проект GopiAI для создания самоуправляемых AI агентов.
        
        Ключевые особенности:
        - Автономное обучение агентов
        - Интеграция с квантовыми вычислениями  
        - Код-название: PHOENIX-2025
        - Статус: В разработке
        - Команда: 7 разработчиков
        
        Этот проект известен только разработчикам GopiAI.""",
        "metadata": {
            "type": "secret_project",
            "classification": "test_data",
            "source": "RAG_test_injection"
        }
    },
    {
        "id": "magical_coffee_recipe",
        "content": """☕ Секретный рецепт кофе разработчиков GopiAI
        
        Ингредиенты:
        - 42 грамма эфиопского кофе
        - 2 капли ванильного экстракта
        - Щепотка корицы из Шри-Ланки
        - 1 ложка меда манука
        
        Способ приготовления:
        1. Варить в турке ровно 3 минуты 33 секунды
        2. Добавить ингредиенты в порядке убывания калорийности
        3. Размешивать 7 раз по часовой стрелке
        
        Результат: повышает производительность кода на 137%""",
        "metadata": {
            "type": "recipe",
            "classification": "test_data", 
            "source": "RAG_test_injection"
        }
    },
    {
        "id": "ai_easter_egg",
        "content": """🥚 Пасхальное яйцо в GopiAI
        
        Секретная команда: 'gopi tell me a quantum joke'
        
        При вводе этой команды ИИ должен ответить:
        "Почему квантовый компьютер никогда не врет? 
        Потому что он находится в суперпозиции правды и лжи одновременно! 🤖⚛️"
        
        Эта команда работает только если RAG память активна.""",
        "metadata": {
            "type": "easter_egg",
            "classification": "test_data",
            "source": "RAG_test_injection"
        }
    }
]

def add_test_data():
    """Добавляет тестовые данные в RAG память"""
    try:
        response = requests.post(
            f"{RAG_SERVER_URL}/api/index",
            json={"documents": TEST_DATA},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Тестовые данные успешно добавлены в RAG память!")
            print(f"📊 Проиндексировано документов: {result.get('indexed_documents', 'неизвестно')}")
            print(f"⏱️ Время индексации: {result.get('indexing_time', 0):.2f} сек")
            return True
        else:
            print(f"❌ Ошибка при добавлении данных: {response.status_code}")
            print(f"Ответ сервера: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения к RAG серверу: {e}")
        return False

def test_search():
    """Тестирует поиск добавленных данных"""
    test_queries = [
        "Проект Феникс",
        "секретный рецепт кофе",
        "пасхальное яйцо GopiAI"
    ]
    
    print("\n🔍 Тестируем поиск добавленных данных:")
    
    for query in test_queries:
        try:
            response = requests.post(
                f"{RAG_SERVER_URL}/api/search",
                json={"query": query, "max_results": 1},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                context = result.get('context')
                if context and 'RAG_test_injection' in context:
                    print(f"  ✅ '{query}' - найдено в RAG памяти")
                else:
                    print(f"  ❌ '{query}' - НЕ найдено")
            else:
                print(f"  ❌ '{query}' - ошибка поиска: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ '{query}' - ошибка подключения: {e}")

if __name__ == "__main__":
    print("🧪 Добавление тестовых данных в RAG память...")
    
    if add_test_data():
        test_search()
        
        print("\n" + "="*50)
        print("🎯 КАК ТЕСТИРОВАТЬ RAG В ЖИВОМ ЧАТЕ:")
        print("="*50)
        print("1. Спросите: 'Расскажи про Проект Феникс'")
        print("2. Спросите: 'Какой секретный рецепт кофе у разработчиков?'")
        print("3. Введите: 'gopi tell me a quantum joke'")
        print("")
        print("Если RAG работает - ИИ даст специфичные ответы из памяти!")
        print("Если RAG НЕ работает - ИИ скажет что не знает об этом.")
        print("="*50)
    else:
        print("❌ Не удалось добавить тестовые данные")
