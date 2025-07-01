#!/usr/bin/env python3
"""
🧪 Тестирование txtchat интеграции с GopiAI

Этот скрипт тестирует:
1. Базовую функциональность агента
2. RAG интеграцию
3. Кэширование
4. Переключение персон
5. Обработку ошибок
"""

import os
import sys
import time
import json
import asyncio
import requests
from pathlib import Path

# Добавляем путь к нашему агенту
sys.path.append(str(Path(__file__).parent))

from gopiai_agent import GopiAIAgent, create_agent, quick_chat

def test_rag_server_connection():
    """Тест подключения к RAG серверу"""
    print("🔌 Тестирование подключения к RAG серверу...")
    
    try:
        response = requests.get("http://127.0.0.1:5051/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ RAG сервер онлайн")
            print(f"   Статус: {data.get('status', 'unknown')}")
            print(f"   Индексированных документов: {data.get('indexed_documents', 0)}")
            return True
        else:
            print(f"❌ RAG сервер вернул код {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к RAG серверу")
        print("   Убедитесь, что сервер запущен: python rag_server.py")
        return False
    except Exception as e:
        print(f"❌ Ошибка подключения к RAG: {e}")
        return False

def test_agent_initialization():
    """Тест инициализации агента"""
    print("\n🤖 Тестирование инициализации агента...")
    
    try:
        agent = create_agent()
        print(f"✅ Агент создан: {agent.config['agent']['name']}")
        print(f"   Персона: {agent.config['agent']['persona']}")
        print(f"   RAG включен: {agent.config['rag']['enabled']}")
        print(f"   Кэш включен: {agent.config['cache']['enabled']}")
        return agent
    except Exception as e:
        print(f"❌ Ошибка создания агента: {e}")
        return None

def test_health_check(agent):
    """Тест проверки состояния"""
    print("\n🩺 Проверка состояния агента...")
    
    try:
        health = agent.health_check()
        print(f"✅ Статус агента: {health['agent_status']}")
        print(f"   RAG статус: {health['rag_status']}")
        print(f"   Текущая персона: {health['current_persona']}")
        
        metrics = health['metrics']
        print(f"   Запросов обработано: {metrics['total_requests']}")
        print(f"   RAG вызовов: {metrics['rag_calls']}")
        print(f"   Попаданий в кэш: {metrics['cache_hits']}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка проверки состояния: {e}")
        return False

def test_basic_messages(agent):
    """Тест базовых сообщений"""
    print("\n💬 Тестирование базовых сообщений...")
    
    test_messages = [
        "Привет!",
        "Как дела?",
        "Расскажи о себе"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   Тест {i}: '{message}'")
        try:
            start_time = time.time()
            result = agent.process_message(message)
            processing_time = time.time() - start_time
            
            print(f"   ✅ Обработано за {processing_time:.3f}с")
            print(f"   📝 Ответ: {result['response'][:100]}...")
            print(f"   🧠 RAG использован: {result['metadata']['rag_used']}")
            print(f"   💾 Из кэша: {result['metadata']['cache_hit']}")
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

def test_rag_context_enrichment(agent):
    """Тест обогащения контекста через RAG"""
    print("\n🧠 Тестирование RAG обогащения контекста...")
    
    # Сообщения, которые должны найти контекст в RAG
    rag_test_messages = [
        "Что такое CrewAI?",
        "Расскажи о multi-agent системах",
        "Как работает GopiAI?",
        "Что такое RAG?"
    ]
    
    for i, message in enumerate(rag_test_messages, 1):
        print(f"\n   RAG тест {i}: '{message}'")
        try:
            result = agent.process_message(message)
            
            context_used = result.get('context_used')
            rag_used = result['metadata']['rag_used']
            
            if rag_used and context_used:
                print(f"   ✅ RAG контекст найден ({len(context_used)} символов)")
                print(f"   📄 Контекст: {context_used[:150]}...")
            elif rag_used and not context_used:
                print(f"   ⚠️ RAG вызван, но контекст не найден")
            else:
                print(f"   ℹ️ RAG не использован")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

def test_persona_switching(agent):
    """Тест переключения персон"""
    print("\n🎭 Тестирование переключения персон...")
    
    personas_to_test = ["technical_expert", "creative_writer", "helpful_assistant"]
    test_message = "Расскажи о машинном обучении"
    
    for persona in personas_to_test:
        print(f"\n   Переключение на персону: {persona}")
        
        if agent.switch_persona(persona):
            print(f"   ✅ Персона изменена на {persona}")
            
            try:
                result = agent.process_message(test_message)
                response = result['response']
                
                print(f"   📝 Ответ в стиле {persona}: {response[:100]}...")
                print(f"   🌡️ Temperature: {agent.config['personas'][persona]['temperature']}")
                
            except Exception as e:
                print(f"   ❌ Ошибка обработки: {e}")
        else:
            print(f"   ❌ Не удалось переключить персону")

def test_caching(agent):
    """Тест кэширования"""
    print("\n💾 Тестирование кэширования...")
    
    test_message = "Тестирование кэша - уникальное сообщение для кэша"
    
    # Первый запрос (должен пойти в RAG)
    print("   Первый запрос (без кэша):")
    result1 = agent.process_message(test_message)
    cache_hit1 = result1['metadata']['cache_hit']
    rag_used1 = result1['metadata']['rag_used']
    
    print(f"   📤 Из кэша: {cache_hit1}")
    print(f"   🧠 RAG использован: {rag_used1}")
    
    # Второй запрос (должен быть из кэша)
    print("\n   Второй запрос (с кэшем):")
    result2 = agent.process_message(test_message)
    cache_hit2 = result2['metadata']['cache_hit']
    rag_used2 = result2['metadata']['rag_used']
    
    print(f"   📤 Из кэша: {cache_hit2}")
    print(f"   🧠 RAG использован: {rag_used2}")
    
    if cache_hit2 and not cache_hit1:
        print("   ✅ Кэширование работает корректно!")
    else:
        print("   ⚠️ Кэширование работает не как ожидалось")

def test_error_handling(agent):
    """Тест обработки ошибок"""
    print("\n🚨 Тестирование обработки ошибок...")
    
    error_test_cases = [
        ("", "Пустое сообщение"),
        ("x" * 10000, "Слишком длинное сообщение"),
    ]
    
    for message, description in error_test_cases:
        print(f"\n   Тест: {description}")
        try:
            result = agent.process_message(message)
            
            if "error" in result:
                print(f"   ✅ Ошибка корректно обработана: {result['error']}")
            else:
                print(f"   ⚠️ Ошибка не была зафиксирована")
                
        except Exception as e:
            print(f"   ❌ Необработанная ошибка: {e}")

def print_final_metrics(agent):
    """Вывод финальных метрик"""
    print("\n📊 Финальные метрики агента:")
    print("="*50)
    
    metrics = agent.get_metrics()
    
    for key, value in metrics.items():
        if key == "avg_response_time":
            print(f"   {key}: {value:.3f}s")
        elif key == "rag_usage_rate":
            print(f"   {key}: {value:.1f}%")
        else:
            print(f"   {key}: {value}")

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование txtchat интеграции с GopiAI")
    print("="*60)
    
    # 1. Проверяем RAG сервер
    rag_available = test_rag_server_connection()
    
    # 2. Создаем агента
    agent = test_agent_initialization()
    if not agent:
        print("\n❌ Не удалось создать агента. Тестирование прервано.")
        return
    
    # 3. Проверяем состояние
    test_health_check(agent)
    
    # 4. Тестируем базовые сообщения
    test_basic_messages(agent)
    
    # 5. Тестируем RAG (только если сервер доступен)
    if rag_available:
        test_rag_context_enrichment(agent)
    else:
        print("\n⚠️ RAG сервер недоступен, пропускаем RAG тесты")
    
    # 6. Тестируем персоны
    test_persona_switching(agent)
    
    # 7. Тестируем кэширование
    test_caching(agent)
    
    # 8. Тестируем обработку ошибок
    test_error_handling(agent)
    
    # 9. Выводим финальные метрики
    print_final_metrics(agent)
    
    print("\n🎉 Тестирование завершено!")
    print("\nСледующие шаги:")
    print("1. Интегрируйте реальный LLM вместо заглушки")
    print("2. Настройте персоны под ваши потребности")
    print("3. Добавьте больше документов в RAG")
    print("4. Интегрируйте в ваш основной проект")

if __name__ == "__main__":
    main()
