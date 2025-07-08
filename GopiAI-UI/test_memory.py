"""
Тестирование встроенной системы памяти GopiAI

Этот скрипт проверяет работу встроенной системы памяти на основе txtai.
"""

import sys
import os
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent))

def test_memory_system():
    """Тестирование базовой функциональности памяти"""
    try:
        from gopiai.ui.memory_initializer import init_memory_system, get_memory_status
        from rag_memory_system import get_memory_manager
        
        print("🧪 Тестирование системы памяти GopiAI")
        print("=" * 50 + "\n")
        
        # 1. Инициализация памяти
        print("1. Инициализация системы памяти...")
        if not init_memory_system(silent=False):
            print("❌ Не удалось инициализировать систему памяти")
            return False
        
        # 2. Получение менеджера памяти
        try:
            manager = get_memory_manager()
            print("✅ Менеджер памяти успешно загружен")
        except Exception as e:
            print(f"❌ Ошибка при загрузке менеджера памяти: {e}")
            return False
        
        # 3. Проверка базовой функциональности
        print("\n2. Проверка базовой функциональности...")
        
        # Создаем тестовую сессию
        session_id = manager.create_session("Тестовая сессия")
        print(f"✅ Создана тестовая сессия: {session_id}")
        
        # Добавляем тестовые сообщения
        test_messages = [
            ("user", "Привет! Это тестовое сообщение."),
            ("assistant", "Здравствуйте! Я ваш ассистент."),
            ("user", "Как настроена система памяти в GopiAI?"),
            ("assistant", "GopiAI использует txtai для семантического поиска и хранения контекста.")
        ]
        
        for role, content in test_messages:
            manager.add_message(session_id, role, content)
        print("✅ Добавлены тестовые сообщения")
        
        # 4. Проверка поиска
        print("\n3. Тестирование семантического поиска...")
        
        test_queries = [
            "Как работает память?",
            "Что такое txtai?",
            "Технические детали"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Поиск: '{query}'")
            results = manager.search_memory(query, limit=2)
            
            if not results:
                print("   ❌ Результаты не найдены")
                continue
                
            for i, result in enumerate(results, 1):
                print(f"   {i}. Скоринг: {result.get('score', 0):.3f}")
                print(f"      {result.get('content', '')[:100]}...")
        
        # 5. Проверка статистики
        print("\n4. Проверка статистики...")
        stats = manager.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Все тесты успешно завершены!")
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_memory_system()
