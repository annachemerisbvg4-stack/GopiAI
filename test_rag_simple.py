#!/usr/bin/env python3
"""
Простой тест RAG системы GopiAI
"""
import sys
import os
from pathlib import Path

# Добавляем путь к RAG системе
current_dir = Path(__file__).parent
rag_path = current_dir / "rag_memory_system"
sys.path.insert(0, str(rag_path))

def test_imports():
    """Тест импортов RAG системы"""
    try:
        print("🔍 Testing imports...")
        from models import ConversationSession, MessageRole, SearchResult
        print("✅ Models imported successfully")
        
        from memory_manager import RAGMemoryManager
        print("✅ RAGMemoryManager imported successfully")
        
        from api import start_server, app
        print("✅ API imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_memory_manager():
    """Тест создания memory manager"""
    try:
        print("\n🧠 Testing memory manager...")
        from memory_manager import RAGMemoryManager
        
        manager = RAGMemoryManager()
        print("✅ RAGMemoryManager created successfully")
        
        # Тест создания сессии
        session = manager.create_session("Test Session", "GopiAI-Test", ["test", "integration"])
        print(f"✅ Session created: {session.session_id}")
        
        # Тест добавления сообщения
        from models import MessageRole
        message = manager.add_message(session.session_id, MessageRole.USER, "Hello RAG system")
        print(f"✅ Message added: {message.id}")
        
        # Тест поиска
        results = manager.search_conversations("RAG system", 3)
        print(f"✅ Search completed: {len(results)} results")
        
        return True
    except Exception as e:
        print(f"❌ Memory manager error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server_start():
    """Тест запуска сервера"""
    try:
        print("\n🚀 Testing server start...")
        from api import app
        print("✅ FastAPI app created successfully")
        
        # Не запускаем сервер, только проверяем что он может быть создан
        print("✅ Server ready to start")
        return True
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 GopiAI RAG System Test")
    print("=" * 40)
    
    success = True
    
    # Тест импортов
    if not test_imports():
        success = False
    
    # Тест memory manager
    if not test_memory_manager():
        success = False
    
    # Тест сервера
    if not test_server_start():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! RAG system is ready.")
        print("💡 To start the server: python start_rag_server.py")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    print("🔚 Test completed.")