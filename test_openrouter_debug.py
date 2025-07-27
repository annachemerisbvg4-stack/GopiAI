#!/usr/bin/env python3
"""
Тестовый скрипт для диагностики проблемы с OpenRouter API
Проверяет подключение и получение списка моделей
"""

import os
import sys
import json
import requests
from datetime import datetime

# Загружаем .env файл
def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        print(f"📁 Загружаем .env из: {env_path}")
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ .env файл загружен")
    else:
        print(f"⚠️ .env файл не найден: {env_path}")

def test_openrouter_api():
    """Тестируем OpenRouter API"""
    print("🧪 === ТЕСТИРОВАНИЕ OPENROUTER API ===")
    print(f"🕐 Время: {datetime.now()}")
    
    # Загружаем переменные окружения
    load_env_file()
    
    # Проверяем API ключ
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY не найден в переменных окружения")
        return
    
    print(f"🔑 API ключ найден: {api_key[:10]}...{api_key[-4:]}")
    
    # Формируем запрос
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "GopiAI/1.0"
    }
    
    print(f"🌐 URL: {url}")
    print(f"📋 Заголовки: {json.dumps({k: v if k != 'Authorization' else f'Bearer {api_key[:10]}...' for k, v in headers.items()}, indent=2)}")
    
    try:
        print("🚀 Отправляем запрос...")
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Статус код: {response.status_code}")
        print(f"📝 Заголовки ответа: {dict(response.headers)}")
        
        if response.status_code == 401:
            print("❌ Ошибка аутентификации (401)")
            print(f"📄 Ответ: {response.text}")
            return
        
        if response.status_code != 200:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return
        
        # Парсим JSON
        try:
            data = response.json()
            print("✅ JSON успешно распарсен")
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            print(f"📄 Сырой ответ: {response.text[:500]}...")
            return
        
        # Анализируем структуру ответа
        print(f"🔍 Ключи в ответе: {list(data.keys())}")
        
        models_data = data.get('data', [])
        print(f"📊 Всего моделей в ответе: {len(models_data)}")
        
        if len(models_data) == 0:
            print("⚠️ API вернул 0 моделей!")
            print(f"📄 Полный ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return
        
        # Анализируем первые несколько моделей
        active_count = 0
        inactive_count = 0
        
        print("\n📋 Анализ первых 5 моделей:")
        for i, model_data in enumerate(models_data[:5]):
            model_id = model_data.get('id', 'unknown')
            is_active = model_data.get('is_active', False)
            pricing = model_data.get('pricing', {})
            
            print(f"  {i+1}. ID: {model_id}")
            print(f"     Активна: {is_active}")
            print(f"     Цены: {pricing}")
            
            if is_active:
                active_count += 1
            else:
                inactive_count += 1
        
        # Подсчитываем общую статистику
        total_active = sum(1 for m in models_data if m.get('is_active', False))
        total_inactive = len(models_data) - total_active
        
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   Всего моделей: {len(models_data)}")
        print(f"   Активных: {total_active}")
        print(f"   Неактивных: {total_inactive}")
        
        if total_active == 0:
            print("❌ ПРОБЛЕМА: Все модели неактивны!")
            print("🔍 Возможные причины:")
            print("   1. Изменилась структура API OpenRouter")
            print("   2. Проблемы с аккаунтом или API ключом")
            print("   3. Фильтрация на стороне OpenRouter")
        else:
            print("✅ Найдены активные модели")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openrouter_api()
