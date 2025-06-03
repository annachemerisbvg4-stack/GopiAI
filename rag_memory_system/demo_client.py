"""
Простой демонстрационный клиент RAG Memory системы
"""
import sys
from pathlib import Path

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent.parent))

def demo_client():
    """Демонстрация клиента RAG Memory"""
    print("🧠 Демо клиент RAG Memory системы")
    print("=" * 50)
    
    try:
        from rag_memory_system import RAGMemoryManager, MessageRole
        
        # Создание менеджера памяти
        memory = RAGMemoryManager()
        print("✅ RAG Memory Manager создан")
        
        # Создание тестовых разговоров с разными темами
        print("\n📝 Создание тестовых разговоров...")
        
        # Разговор 1: Архитектура GopiAI
        session1 = memory.create_session(
            title="Обсуждение архитектуры GopiAI", 
            project_context="GopiAI-Core",
            tags=["архитектура", "модули", "планирование"]
        )
        
        memory.add_message(session1.session_id, MessageRole.USER, 
                          "Расскажи про модульную архитектуру GopiAI. Какие основные компоненты?")
        
        memory.add_message(session1.session_id, MessageRole.ASSISTANT, 
                          "GopiAI построен по модульному принципу. Основные компоненты:\n"
                          "• GopiAI-Core: базовые интерфейсы, агенты и схемы\n"
                          "• GopiAI-Extensions: расширения для интеграций (браузер, код-анализ)\n"
                          "• GopiAI-Widgets: UI компоненты (чат, терминал, редактор)\n"
                          "• GopiAI-Assets: ресурсы, медиа файлы, статические данные\n"
                          "• GopiAI-App: главное приложение, объединяющее все модули")
        
        memory.add_message(session1.session_id, MessageRole.USER, 
                          "А как модули взаимодействуют между собой?")
        
        memory.add_message(session1.session_id, MessageRole.ASSISTANT, 
                          "Модули взаимодействуют через четко определенные интерфейсы:\n"
                          "• Агенты из Core используют расширения из Extensions\n"
                          "• Виджеты подключаются к агентам через стандартные сигналы\n"
                          "• Assets предоставляют ресурсы всем модулям\n"
                          "• App координирует работу и управляет жизненным циклом")
        
        print(f"  ✅ Создан разговор об архитектуре: {session1.session_id}")
        
        # Разговор 2: UI/UX разработка
        session2 = memory.create_session(
            title="Улучшения пользовательского интерфейса", 
            project_context="GopiAI-Widgets",
            tags=["ui", "ux", "дизайн", "виджеты"]
        )
        
        memory.add_message(session2.session_id, MessageRole.USER, 
                          "Какие UI компоненты есть в GopiAI и как их улучшить?")
        
        memory.add_message(session2.session_id, MessageRole.ASSISTANT, 
                          "В GopiAI есть несколько ключевых UI компонентов:\n"
                          "• ChatWidget: интерфейс для общения с агентами\n"
                          "• CodeEditorWidget: редактор кода с подсветкой синтаксиса\n"
                          "• TerminalWidget: встроенный терминал\n"
                          "• ThoughtTreeWidget: визуализация мыслительного процесса ИИ\n"
                          "• BrowserWidget: интегрированный браузер\n\n"
                          "Для улучшения рекомендую:\n"
                          "1. Добавить темную тему\n"
                          "2. Улучшить адаптивность\n"
                          "3. Добавить настраиваемые горячие клавиши\n"
                          "4. Создать единую дизайн-систему")
        
        print(f"  ✅ Создан разговор об UI: {session2.session_id}")
        
        # Разговор 3: Техническая реализация
        session3 = memory.create_session(
            title="Техническая реализация и интеграции", 
            project_context="GopiAI-Extensions",
            tags=["технологии", "интеграция", "api"]
        )
        
        memory.add_message(session3.session_id, MessageRole.USER, 
                          "Как реализованы интеграции с внешними сервисами?")
        
        memory.add_message(session3.session_id, MessageRole.ASSISTANT, 
                          "Интеграции реализованы через модуль Extensions:\n"
                          "• BrowserIntegrator: автоматизация веб-браузера через Playwright\n"
                          "• CodeAnalysisIntegration: анализ кода с помощью AST и статических анализаторов\n"
                          "• AgentUIIntegration: связь агентов с пользовательским интерфейсом\n\n"
                          "Все интеграции используют единый паттерн:\n"
                          "1. Адаптер для внешнего API\n"
                          "2. Кэширование результатов\n"
                          "3. Обработка ошибок и retry-логика\n"
                          "4. Логирование для отладки")
        
        print(f"  ✅ Создан разговор о технологиях: {session3.session_id}")
        
        print("\n🔍 Тестирование поиска по разным темам:")
        print("-" * 50)
        
        # Тестовые запросы
        search_queries = [
            ("модульная архитектура", "архитектурные вопросы"),
            ("UI компоненты виджеты", "интерфейсные решения"),
            ("интеграции API", "технические реализации"),
            ("GopiAI-Core", "ядро системы"),
            ("улучшения дизайна", "дизайн и UX"),
            ("браузер автоматизация", "веб-интеграции")
        ]
        
        for query, description in search_queries:
            print(f"\n🔎 Поиск: '{query}' ({description})")
            results = memory.search_conversations(query, limit=3)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result.title}")
                    print(f"     Релевантность: {result.relevance_score:.3f}")
                    print(f"     Теги: {', '.join(result.tags)}")
                    print(f"     Фрагмент: {result.context_preview}")
                    print()
            else:
                print("  ❌ Ничего не найдено")
        
        # Статистика
        stats = memory.get_memory_stats()
        print("📊 Итоговая статистика:")
        print(f"  • Разговоров: {stats.total_sessions}")
        print(f"  • Сообщений: {stats.total_messages}")
        print(f"  • Документов в БД: {stats.total_documents}")
        print(f"  • Размер хранилища: {stats.storage_size_mb:.2f} МБ")
        print(f"  • Популярные теги: {', '.join(stats.most_active_tags[:5])}")
        
        print("\n🎉 Демонстрация завершена!")
        print("💡 Система RAG Memory готова к использованию!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_client()
