"""
Скрипт для демонстрации и тестирования RAG Memory системы
"""
import sys
import time
import threading
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

def start_server_background():
    """Запустить сервер в фоновом режиме"""
    try:
        from rag_memory_system.api import start_server
        start_server()
    except Exception as e:
        print(f"Ошибка запуска сервера: {e}")

def run_demo():
    """Запустить демонстрацию"""
    print("🧠 GopiAI RAG Memory System - Демонстрация")
    print("=" * 50)
    
    # Запускаем сервер в отдельном потоке
    print("🚀 Запуск сервера...")
    server_thread = threading.Thread(target=start_server_background, daemon=True)
    server_thread.start()
    
    # Ждем, пока сервер запустится
    print("⏳ Ожидание запуска сервера...")
    time.sleep(3)
    
    # Запускаем демо
    from rag_memory_system.client import demo_conversation
    demo_conversation()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        print("Использование:")
        print("  python run_demo.py --demo    # Запуск полной демонстрации")
        print("  python run_server.py         # Только сервер")
        print("  python client.py             # Только клиент (требует запущенный сервер)")
