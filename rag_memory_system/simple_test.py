"""
Простой тест RAG Memory системы
"""
import sys
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent.parent))

def simple_test():
    """Простой тест без сервера"""
    print("🧠 Тест RAG Memory системы")
    print("=" * 40)
    
    try:
        # Импорт модулей
        from rag_memory_system import RAGMemoryManager, MessageRole
        print("✅ Модули импортированы успешно")
        
        # Создание менеджера памяти
        memory = RAGMemoryManager()
        print("✅ RAG Memory Manager создан")
        
        # Создание тестовой сессии
        session = memory.create_session(
            title="Тест RAG системы", 
            project_context="GopiAI-Core",
            tags=["тест", "память"]
        )
        print(f"✅ Сессия создана: {session.session_id}")
        
        # Добавление сообщений
        memory.add_message(session.session_id, MessageRole.USER, 
                          "Привет! Тестирую RAG Memory систему.")
        
        memory.add_message(session.session_id, MessageRole.ASSISTANT, 
                          "Отлично! Система работает. RAG Memory позволяет сохранять "
                          "и искать информацию из предыдущих разговоров.")
        
        memory.add_message(session.session_id, MessageRole.USER, 
                          "Расскажи про архитектуру GopiAI. Какие есть модули?")
        
        memory.add_message(session.session_id, MessageRole.ASSISTANT, 
                          "GopiAI имеет модульную архитектуру:\n"
                          "- GopiAI-Core: базовые компоненты\n"
                          "- GopiAI-Extensions: расширения\n"
                          "- GopiAI-Widgets: UI компоненты\n"
                          "- GopiAI-Assets: ресурсы")
        
        print("✅ Сообщения добавлены")
        
        # Сохранение сессии
        memory.save_session(session)
        print("✅ Сессия сохранена и проиндексирована")
        
        # Тест поиска
        print("\n🔍 Тестирование поиска:")
        results = memory.search_conversations("модульная архитектура GopiAI")
        print(f"Найдено {len(results)} результатов для запроса 'модульная архитектура GopiAI'")
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.title} (релевантность: {result.relevance_score:.2f})")
        
        # Статистика
        stats = memory.get_memory_stats()
        print(f"\n📊 Статистика:")
        print(f"  - Разговоров: {stats.total_sessions}")
        print(f"  - Сообщений: {stats.total_messages}")
        print(f"  - Документов в БД: {stats.total_documents}")
        print(f"  - Размер: {stats.storage_size_mb:.2f} МБ")
        
        print("\n🎉 Тест завершен успешно!")
        print("💡 Теперь можете запустить веб-сервер:")
        print("   python rag_memory_system\\run_server.py")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()
