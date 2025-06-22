"""
Тест интеграции txtai с GopiAI
"""
import sys
from pathlib import Path

# Добавляем путь к системе памяти
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_txtai_integration():
    """Тест базовой функциональности txtai"""
    try:
        from rag_memory_system import get_memory_manager
        
        manager = get_memory_manager()
        print("✅ TxtAI менеджер инициализирован")
        
        # Создаем тестовую сессию
        session = manager.create_session("TxtAI Test", "GopiAI-Testing")
        print(f"✅ Сессия создана: {session.session_id}")
        
        # Добавляем сообщение
        message = manager.add_message(
            session.session_id, 
            "user", 
            "Тестируем интеграцию txtai с GopiAI"
        )
        print(f"✅ Сообщение добавлено: {message.message_id}")
        
        # Поиск
        results = manager.search_conversations("txtai GopiAI", 5)
        print(f"✅ Поиск выполнен, найдено: {len(results)} результатов")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Тестирование txtai интеграции")
    print("=" * 40)
    
    if test_txtai_integration():
        print("🎉 Все тесты пройдены! TxtAI готов к работе.")
    else:
        print("❌ Тесты провалены. Проверьте настройки.")
