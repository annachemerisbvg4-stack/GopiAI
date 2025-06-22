"""
🧪 Быстрый тест простого менеджера памяти
"""

def test_simple_memory():
    """Тест всех функций"""
    print("🧪 Тестируем Simple Memory Manager...")
    
    try:
        from rag_memory_system.simple_memory_manager import get_memory_manager
        
        # Получаем менеджер
        manager = get_memory_manager()
        print("✅ Менеджер получен")
        
        # Создаем сессию
        session_id = manager.create_session("Тест GopiAI")
        print(f"✅ Сессия создана: {session_id}")
        
        # Добавляем диалог
        manager.add_message(session_id, "user", "Как работает txtai в GopiAI?")
        manager.add_message(session_id, "assistant", "txtai обеспечивает семантический поиск по истории чатов")
        manager.add_message(session_id, "user", "А что с интеграцией в веб-интерфейс?")
        manager.add_message(session_id, "assistant", "Интеграция происходит через WebViewChatBridge и JavaScript")
        
        print("✅ Диалог добавлен")
        
        # Тестируем поиск
        results = manager.search_memory("интеграция txtai")
        print(f"✅ Поиск: найдено {len(results)} результатов")
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['content'][:50]}... (score: {result['score']:.3f})")
        
        # Тестируем обогащение
        enriched = manager.enrich_message("Расскажи про веб-интерфейс")
        print(f"✅ Обогащение: {len(enriched)} символов")
        
        # Статистика
        stats = manager.get_stats()
        print(f"✅ Статистика: {stats}")
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_memory()
    print(f"\n{'✅ УСПЕХ' if success else '❌ ПРОВАЛ'}")