#!/usr/bin/env python3
"""
Скрипт для безопасного перезапуска сервера
"""

import subprocess
import time
import requests
import signal
import os
import sys

def stop_existing_server():
    """Останавливает существующий сервер"""
    try:
        # Проверяем есть ли запущенный сервер
        response = requests.get("http://127.0.0.1:5051/api/health", timeout=2)
        if response.status_code == 200:
            print("[INFO] Сервер работает, останавливаем...")
            
            # Пытаемся остановить через taskkill
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                         capture_output=True, text=True)
            time.sleep(2)
            
            # Проверяем что сервер остановлен
            try:
                requests.get("http://127.0.0.1:5051/api/health", timeout=2)
                print("[ERROR] Сервер все еще работает")
                return False
            except:
                print("[OK] Сервер остановлен")
                return True
        else:
            print("[INFO] Сервер не запущен")
            return True
            
    except:
        print("[INFO] Сервер не отвечает, считаем остановленным")
        return True

def start_server():
    """Запускает сервер"""
    print("[INFO] Запускаем сервер...")
    
    # Запускаем сервер в фоновом режиме
    process = subprocess.Popen([
        'cmd', '/c', 
        'call crewai_env\\Scripts\\activate.bat && python crewai_api_server.py --port 5051'
    ], cwd=os.getcwd(), creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    # Ждем запуска
    for i in range(30):
        time.sleep(1)
        try:
            response = requests.get("http://127.0.0.1:5051/api/health", timeout=2)
            if response.status_code == 200:
                print(f"[OK] Сервер запущен успешно за {i+1} секунд")
                return True
        except:
            continue
    
    print("[ERROR] Сервер не запустился за 30 секунд")
    return False

def main():
    print("=== Перезапуск сервера ===")
    
    # Останавливаем существующий сервер
    if not stop_existing_server():
        print("[ERROR] Не удалось остановить сервер")
        return False
    
    # Запускаем новый сервер
    if not start_server():
        print("[ERROR] Не удалось запустить сервер")
        return False
    
    print("[SUCCESS] Сервер успешно перезапущен!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
