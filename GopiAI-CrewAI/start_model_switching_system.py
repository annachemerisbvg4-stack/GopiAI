#!/usr/bin/env python3
"""
Скрипт для запуска всей системы переключения провайдеров LLM.
Запускает REST API сервер и открывает UI для взаимодействия.
"""
import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def start_api_server():
    """Запуск REST API сервера."""
    print("🚀 Запуск REST API сервера...")
    try:
        # Переходим в директорию с сервером
        server_dir = Path(__file__).parent
        os.chdir(server_dir)
        
        # Запускаем сервер
        result = subprocess.run([
            sys.executable, 
            "crewai_api_server.py"
        ])
        
        if result.returncode == 0:
            print("✅ REST API сервер успешно запущен")
        else:
            print("❌ Ошибка запуска REST API сервера")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при запуске сервера: {e}")
        return False
    
    return True

def start_ui():
    """Запуск UI приложения."""
    print("🎨 Запуск UI приложения...")
    try:
        # Переходим в директорию UI
        ui_dir = Path(__file__).parent.parent / "GopiAI-UI"
        os.chdir(ui_dir)
        
        # Здесь должен быть код для запуска UI приложения
        # Пока просто выводим информацию
        print("ℹ️  UI приложение готово к запуску")
        print("   Для запуска UI используйте соответствующий скрипт из GopiAI-UI")
        
    except Exception as e:
        print(f"❌ Ошибка при подготовке UI: {e}")
        return False
    
    return True

def run_tests():
    """Запуск тестов системы."""
    print("🧪 Запуск тестов...")
    try:
        # Переходим в директорию с тестами
        test_dir = Path(__file__).parent
        os.chdir(test_dir)
        
        # Запускаем тесты
        result = subprocess.run([
            sys.executable, 
            "run_all_tests.py"
        ])
        
        if result.returncode == 0:
            print("✅ Все тесты успешно пройдены")
        else:
            print("❌ Некоторые тесты провалены")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при запуске тестов: {e}")
        return False
    
    return True

def main():
    """Основная функция."""
    print("🌟 Система переключения провайдеров LLM для GopiAI")
    print("=" * 60)
    
    # Проверяем текущую директорию
    current_dir = Path(__file__).parent.absolute()
    print(f"📂 Рабочая директория: {current_dir}")
    
    # Создаем директорию для состояния если её нет
    state_dir = Path.home() / ".gopiai"
    state_dir.mkdir(exist_ok=True)
    print(f"📁 Директория состояния: {state_dir}")
    
    # Запускаем тесты
    print("\n📋 Этап 1: Проверка системы...")
    if not run_tests():
        print("❌ Система не прошла проверку. Запуск отменен.")
        return 1
    
    print("\n🚀 Этап 2: Запуск компонентов...")
    
    # Запускаем API сервер в отдельном потоке
    print("📡 Запуск REST API сервера в фоновом режиме...")
    server_process = subprocess.Popen([
        sys.executable, 
        str(current_dir / "crewai_api_server.py")
    ])
    
    # Ждем немного для запуска сервера
    time.sleep(3)
    
    # Проверяем, запущен ли сервер
    if server_process.poll() is None:
        print("✅ REST API сервер запущен успешно (порт 5051)")
    else:
        print("❌ Ошибка запуска REST API сервера")
        return 1
    
    print("\n🎨 Этап 3: Готовность к работе")
    print("✅ Система переключения провайдеров готова к использованию!")
    print("   - REST API сервер: http://localhost:5051")
    print("   - Для запуска UI используйте соответствующий скрипт")
    print("   - Для остановки сервера нажмите Ctrl+C")
    
    try:
        # Держим сервер запущенным
        server_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервера...")
        server_process.terminate()
        server_process.wait()
        print("✅ Сервер остановлен")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
