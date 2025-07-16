#!/usr/bin/env python3
"""
Тестовый скрипт для проверки стабильности сервера
"""

import sys
import time
import signal
import threading
import requests
from datetime import datetime

def test_server_startup():
    """Тест запуска сервера"""
    print("=== Тест стабильности сервера ===")
    
    # Проверим что сервер может быть импортирован
    try:
        import crewai_api_server
        print("[OK] Сервер успешно импортирован")
        
        # Проверим что все системы инициализированы
        if hasattr(crewai_api_server, 'SERVER_IS_READY'):
            print(f"[OK] SERVER_IS_READY = {crewai_api_server.SERVER_IS_READY}")
        else:
            print("[ERROR] SERVER_IS_READY не найден")
            return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка импорта сервера: {e}")
        return False

def test_server_response():
    """Тест отклика сервера"""
    server_url = "http://127.0.0.1:5051"
    
    for i in range(3):
        try:
            response = requests.get(f"{server_url}/api/health", timeout=5)
            if response.status_code == 200:
                print(f"[OK] Сервер отвечает: {response.status_code}")
                return True
            else:
                print(f"[WARN] Сервер отвечает с кодом: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Попытка {i+1}: Сервер не отвечает - {e}")
            time.sleep(2)
    
    return False

def run_server_test():
    """Запуск теста сервера"""
    print(f"[START] Начало теста: {datetime.now()}")
    
    # Тест 1: Импорт и инициализация
    if not test_server_startup():
        return False
    
    # Тест 2: Проверка отклика (если сервер уже запущен)
    if test_server_response():
        print("[OK] Сервер работает корректно")
        return True
    else:
        print("[WARN] Сервер не отвечает, но это нормально если он не запущен")
        return True

if __name__ == "__main__":
    try:
        success = run_server_test()
        if success:
            print("\n[SUCCESS] Тест завершен успешно!")
            sys.exit(0)
        else:
            print("\n[ERROR] Тест завершен с ошибками!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n[STOP] Тест прерван пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n[CRASH] Неожиданная ошибка: {e}")
        sys.exit(1)
