#!/usr/bin/env python3
"""
Тестовый скрипт для проверки обработки задач
"""

import requests
import time
import json
from datetime import datetime

SERVER_URL = "http://127.0.0.1:5051"

def test_health():
    """Тест здоровья сервера"""
    try:
        response = requests.get(f"{SERVER_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"[OK] Сервер здоров: {response.json()}")
            return True
        else:
            print(f"[ERROR] Сервер не здоров: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Не удается связаться с сервером: {e}")
        return False

def test_task_processing():
    """Тест обработки задач"""
    print("[TEST] Отправляем тестовое сообщение...")
    
    # Отправляем сообщение
    payload = {
        "message": "Тестовое сообщение для проверки",
        "metadata": {
            "session_id": "test_session",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    try:
        # Отправляем POST запрос
        response = requests.post(f"{SERVER_URL}/api/process", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get("task_id")
            print(f"[OK] Задача создана: {task_id}")
            print(f"[INFO] Статус: {data.get('status')}")
            
            # Проверяем статус задачи
            for attempt in range(30):  # Ждем до 30 секунд
                time.sleep(1)
                
                try:
                    status_response = requests.get(f"{SERVER_URL}/api/task/{task_id}", timeout=5)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"[STATUS] Попытка {attempt + 1}: {status_data.get('status')}")
                        
                        if status_data.get('status') == 'completed':
                            print(f"[SUCCESS] Задача завершена успешно!")
                            print(f"[RESULT] Результат: {status_data.get('result')}")
                            return True
                        elif status_data.get('status') == 'failed':
                            print(f"[ERROR] Задача завершилась с ошибкой: {status_data.get('error')}")
                            return False
                    else:
                        print(f"[ERROR] Не удается получить статус задачи: {status_response.status_code}")
                        return False
                        
                except Exception as e:
                    print(f"[ERROR] Ошибка при проверке статуса: {e}")
                    return False
            
            print(f"[TIMEOUT] Задача не завершилась за 30 секунд")
            return False
            
        else:
            print(f"[ERROR] Не удается отправить сообщение: {response.status_code}")
            print(f"[ERROR] Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Ошибка при отправке сообщения: {e}")
        return False

def main():
    print("=== Тест обработки задач ===")
    print(f"[INFO] Время начала: {datetime.now()}")
    
    # Тест 1: Здоровье сервера
    if not test_health():
        print("[FAIL] Сервер недоступен")
        return
    
    # Тест 2: Обработка задач  
    if test_task_processing():
        print("[SUCCESS] Тест обработки задач прошел успешно!")
    else:
        print("[FAIL] Тест обработки задач провален")

if __name__ == "__main__":
    main()
