#!/usr/bin/env python3
"""
Простой скрипт для запуска RAG сервера для GopiAI
"""
import sys
from pathlib import Path

# Добавляем путь к RAG системе
current_dir = Path(__file__).parent
rag_path = current_dir / "rag_memory_system"
sys.path.insert(0, str(rag_path))

try:
    from api import start_server
    print("🧠 GopiAI RAG Memory Server")
    print("=" * 40)
    print("🔗 Интеграция с веб-чатом на порту 8080")
    print("⚠️ Для остановки нажмите Ctrl+C")
    print()
    
    start_server()
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь что все зависимости установлены:")
    print("pip install -r requirements.txt")
    
except KeyboardInterrupt:
    print("\n👋 RAG сервер остановлен")
    
except Exception as e:
    print(f"❌ Ошибка запуска сервера: {e}")