#!/usr/bin/env python3
"""
🧪 Тестирование интеграции CrewAI с чатом
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# Настройки API сервера
API_URL = "http://127.0.0.1:5050"

def test_health():
    """Проверка работоспособности API"""
    try:
        response = requests.get(f"{API_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ API сервер доступен")
            print(f"Статус: {data.get('status', 'неизвестно').upper()}")
            print(f"CrewAI доступен: {'✅' if data.get('crewai_available', False) else '❌'}")
            print(f"txtai доступен: {'✅' if data.get('txtai_available', False) else '❌'}")
            return data
        else:
            print(f"❌ Ошибка при обращении к API: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Ошибка при подключении к API: {e}")
        return None

def test_simple_request():
    """Тестирование простого запроса"""
    try:
        message = "Привет! Расскажи, что такое CrewAI?"
        
        print(f"\n📝 Отправка простого запроса: '{message}'")
        
        # Отправляем запрос
        response = requests.post(
            f"{API_URL}/api/process", 
            json={"message": message}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Запрос успешно обработан")
            print(f"Ответ обработан через CrewAI: {'✅' if data.get('processed_with_crewai', False) else '❌'}")
            print("\nОтвет:")
            print("-" * 50)
            print(data.get("response", "Ответ не получен"))
            print("-" * 50)
            return data
        else:
            print(f"❌ Ошибка при отправке запроса: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Ошибка при тестировании простого запроса: {e}")
        return None

def test_crewai_request():
    """Тестирование запроса через CrewAI"""
    try:
        message = "Разработай стратегию для запуска нового продукта в сфере ИИ. Нужен подробный поэтапный план с анализом рынка и целевой аудитории."
        
        print(f"\n📝 Отправка сложного запроса через CrewAI: '{message}'")
        
        # Отправляем запрос с принудительным использованием CrewAI
        response = requests.post(
            f"{API_URL}/api/process", 
            json={"message": message, "force_crewai": True}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Запрос успешно обработан")
            print(f"Ответ обработан через CrewAI: {'✅' if data.get('processed_with_crewai', False) else '❌'}")
            print("\nОтвет:")
            print("-" * 50)
            print(data.get("response", "Ответ не получен"))
            print("-" * 50)
            return data
        else:
            print(f"❌ Ошибка при отправке запроса: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Ошибка при тестировании запроса через CrewAI: {e}")
        return None

def test_index_docs():
    """Тестирование индексации документов"""
    try:
        print("\n📚 Запуск индексации документов")
        
        # Отправляем запрос на индексацию
        response = requests.post(f"{API_URL}/api/index_docs")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Результат индексации: {'успешно' if data.get('success', False) else 'неудачно'}")
            if 'error' in data:
                print(f"⚠️ Ошибка: {data['error']}")
            return data
        else:
            print(f"❌ Ошибка при индексации: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Ошибка при тестировании индексации: {e}")
        return None

def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ CrewAI с чатом")
    print("=" * 60)
    
    # Проверяем доступность API
    health_data = test_health()
    if not health_data:
        print("\n❌ API сервер недоступен. Убедитесь, что он запущен на http://127.0.0.1:5050")
        return
    
    # Тестируем индексацию документов
    test_index_docs()
    
    # Тестируем простой запрос
    test_simple_request()
    
    # Тестируем запрос через CrewAI
    test_crewai_request()
    
    print("\n" + "=" * 60)
    print("✅ Тестирование завершено")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()