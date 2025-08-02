#!/usr/bin/env python3
"""Тестирование REST API эндпоинтов для синхронизации состояния провайдеров."""
import requests
import json
import time
import sys
from pathlib import Path

# Конфигурация
BASE_URL = "http://localhost:5051"
TIMEOUT = 10

def test_health_check():
    """Тест эндпоинта здоровья."""
    print("Тест 1: Проверка состояния сервера...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Сервер доступен. Статус: {data.get('status')}")
            return True
        else:
            print(f"✗ Неожиданный статус: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Сервер недоступен. Убедитесь, что backend запущен.")
        return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False

def test_get_current_state():
    """Тест получения текущего состояния."""
    print("\nТест 2: Получение текущего состояния...")
    try:
        response = requests.get(f"{BASE_URL}/internal/state", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Текущее состояние: {data}")
            return True
        else:
            print(f"✗ Неожиданный статус: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False

def test_get_models_by_provider():
    """Тест получения моделей по провайдеру."""
    print("\nТест 3: Получение моделей для провайдера...")
    try:
        # Тестируем Gemini
        response = requests.get(f"{BASE_URL}/internal/models?provider=gemini", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Модели Gemini: {len(data)} моделей найдено")
        else:
            print(f"✗ Ошибка получения моделей Gemini: {response.status_code}")
            return False
            
        # Тестируем OpenRouter
        response = requests.get(f"{BASE_URL}/internal/models?provider=openrouter", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Модели OpenRouter: {len(data)} моделей найдено")
            return True
        else:
            print(f"✗ Ошибка получения моделей OpenRouter: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False

def test_update_state():
    """Тест обновления состояния."""
    print("\nТест 4: Обновление состояния...")
    try:
        # Тестовые данные
        test_data = {
            "provider": "gemini",
            "model_id": "gemini/gemini-1.5-flash"
        }
        
        response = requests.post(
            f"{BASE_URL}/internal/state",
            json=test_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Состояние обновлено: {data.get('message')}")
            
            # Проверяем, что состояние действительно обновилось
            response = requests.get(f"{BASE_URL}/internal/state", timeout=TIMEOUT)
            if response.status_code == 200:
                current_state = response.json()
                if (current_state.get("provider") == test_data["provider"] and 
                    current_state.get("model_id") == test_data["model_id"]):
                    print("✓ Состояние корректно сохранено")
                    return True
                else:
                    print("✗ Состояние не совпадает с отправленным")
                    return False
            else:
                print("✗ Не удалось проверить сохраненное состояние")
                return False
        else:
            print(f"✗ Ошибка обновления состояния: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False

def test_switch_provider():
    """Тест переключения провайдера."""
    print("\nТест 5: Переключение провайдера...")
    try:
        # Переключаемся на OpenRouter
        test_data = {
            "provider": "openrouter",
            "model_id": "openrouter/mistralai-mistral-7b-instruct"
        }
        
        response = requests.post(
            f"{BASE_URL}/internal/state",
            json=test_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Переключение на OpenRouter: {data.get('message')}")
            
            # Проверяем состояние
            response = requests.get(f"{BASE_URL}/internal/state", timeout=TIMEOUT)
            if response.status_code == 200:
                current_state = response.json()
                if (current_state.get("provider") == test_data["provider"] and 
                    current_state.get("model_id") == test_data["model_id"]):
                    print("✓ Переключение успешно")
                    return True
                else:
                    print("✗ Состояние не обновилось корректно")
                    return False
            else:
                print("✗ Не удалось проверить состояние после переключения")
                return False
        else:
            print(f"✗ Ошибка переключения: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False

def run_all_tests():
    """Запуск всех тестов."""
    print("Запуск тестов REST API эндпоинтов...")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_get_current_state,
        test_get_models_by_provider,
        test_update_state,
        test_switch_provider
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("-" * 30)
    
    print("\n" + "=" * 50)
    print(f"Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты успешно пройдены!")
        return True
    else:
        print("❌ Некоторые тесты провалены!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
