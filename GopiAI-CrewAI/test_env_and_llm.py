#!/usr/bin/env python3
"""
Тестовый скрипт для проверки переменных окружения и LLM
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Загружаем переменные окружения
load_dotenv(dotenv_path="../.env")

def check_env_vars():
    """Проверяем наличие необходимых переменных окружения"""
    print("=== Проверка переменных окружения ===")
    
    # Проверяем основные переменные
    env_vars = [
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY", 
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "SMITHERY_API_KEY"
    ]
    
    found_keys = []
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Показываем только первые и последние символы для безопасности
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"[OK] {var}: {masked_value}")
            found_keys.append(var)
        else:
            print(f"[MISS] {var}: не найден")
    
    if not found_keys:
        print("[ERROR] Не найдено ни одного API ключа!")
        return False
    
    return True

def test_litellm_import():
    """Тестируем импорт litellm"""
    print("\n=== Тест импорта litellm ===")
    try:
        import litellm
        print("[OK] litellm импортирован успешно")
        return True
    except ImportError as e:
        print(f"[ERROR] Не удается импортировать litellm: {e}")
        return False

def test_simple_llm_call():
    """Тестируем простой вызов LLM"""
    print("\n=== Тест вызова LLM ===")
    
    if not test_litellm_import():
        return False
    
    try:
        import litellm
        
        # Пробуем простой вызов
        messages = [
            {"role": "user", "content": "Привет! Ответь одним словом: работает?"}
        ]
        
        print("[TEST] Отправляем тестовый запрос в Gemini...")
        response = litellm.completion(
            model="gemini/gemini-1.5-flash",
            messages=messages,
            temperature=0.1,
            max_tokens=10
        )
        
        if response and response.choices:
            answer = response.choices[0].message.content
            print(f"[OK] Получен ответ: {answer}")
            return True
        else:
            print("[ERROR] Пустой ответ от LLM")
            return False
            
    except Exception as e:
        print(f"[ERROR] Ошибка при вызове LLM: {e}")
        return False

def main():
    print("=== Диагностика окружения и LLM ===")
    
    # Проверяем переменные окружения
    env_ok = check_env_vars()
    
    # Проверяем LLM
    llm_ok = test_simple_llm_call()
    
    print(f"\n=== Результаты ===")
    print(f"Переменные окружения: {'OK' if env_ok else 'FAIL'}")
    print(f"LLM вызов: {'OK' if llm_ok else 'FAIL'}")
    
    if env_ok and llm_ok:
        print("[SUCCESS] Все проверки пройдены!")
        return True
    else:
        print("[FAIL] Есть проблемы с конфигурацией")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
