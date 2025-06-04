"""
Отладочный тест поиска RAG Memory системы
"""
import sys
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent.parent))

def debug_search_test():
    """Отладочный тест поиска"""
    print("🔍 Отладка поиска RAG Memory системы")
    print("=" * 50)
    
    try:
        from rag_memory_system import RAGMemoryManager, MessageRole
        
        # Создание менеджера памяти
        memory = RAGMemoryManager()
        print("✅ RAG Memory Manager создан")
        
        # Создание тестовой сессии
        session = memory.create_session(
            title="Тест отладки поиска", 
            project_context="GopiAI-Core",
            tags=["отладка", "поиск", "архитектура"]
        )
        print(f"✅ Сессия создана: {session.session_id}")
        
        # Добавляем точное содержимое для поиска
        memory.add_message(session.session_id, MessageRole.USER, 
                          "Расскажи про модульную архитектуру GopiAI. Какие модули есть?")
        
        memory.add_message(session.session_id, MessageRole.ASSISTANT, 
                          "GopiAI построен с модульной архитектурой. Основные модули включают: "
                          "GopiAI-Core с базовыми агентами, GopiAI-Extensions для расширений, "
                          "GopiAI-Widgets для UI компонентов, GopiAI-Assets для ресурсов.")
        
        print("✅ Сообщения добавлены")
        
        # Проверяем что сохранилось
        conversation = memory.get_conversation_history(session.session_id)
        print(f"📝 Проверка сохранения: {len(conversation.messages)} сообщений")
        
        # Выводим содержимое для анализа
        context_string = conversation.get_context_string()
        print("\n📄 Содержимое для индексации:")
        print("-" * 30)
        print(context_string[:500] + "..." if len(context_string) > 500 else context_string)
        print("-" * 30)
        
        # Тестируем разные запросы с разными порогами
        test_queries = [
            "модульная архитектура",
            "GopiAI модули", 
            "архитектура GopiAI",
            "расскажи про архитектуру",
            "какие модули есть",
            "GopiAI-Core"
        ]
        
        print("\n🔍 Тестирование запросов:")
        print("-" * 30)
        
        for query in test_queries:
            print(f"\n🔎 Запрос: '{query}'")
            
            # Получаем результаты с низким порогом
            results = memory.vector_store.similarity_search_with_score(query=query, k=3)
            
            if results:
                for i, (doc, score) in enumerate(results, 1):
                    relevance = max(0, 1 - score)
                    print(f"  {i}. Релевантность: {relevance:.3f} (distance: {score:.3f})")
                    print(f"     Контент: {doc.page_content[:100]}...")
                    print(f"     Метаданные: {doc.metadata.get('title', 'N/A')}")
            else:
                print("  Ничего не найдено")
        
        # Проверим количество документов в базе
        doc_count = memory.collection.count()
        print(f"\n📊 Документов в ChromaDB: {doc_count}")
        
        # Попробуем получить все документы
        if doc_count > 0:
            all_docs = memory.collection.get()
            print(f"📋 Первые документы:")
            for i, doc_id in enumerate(all_docs['ids'][:3]):
                print(f"  {i+1}. ID: {doc_id}")
                if i < len(all_docs['documents']):
                    doc_content = all_docs['documents'][i]
                    print(f"      Содержимое: {doc_content[:100]}...")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_search_test()
