"""
Скрипт для запуска RAG Memory сервера
"""
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    from rag_memory_system.api import start_server
    
    print("🧠 GopiAI RAG Memory System")
    print("=" * 40)
    
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)
