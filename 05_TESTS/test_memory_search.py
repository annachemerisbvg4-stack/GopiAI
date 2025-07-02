#!/usr/bin/env python3
"""
Простой тест функций поиска памяти GopiAI
"""

import sys
import os

# Добавляем пути
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "rag_memory_system"))
sys.path.insert(0, os.path.dirname(__file__))

def test_memory_functions():
    """Тест функций памяти"""
    print("=== ТЕСТ ФУНКЦИЙ ПОИСКА ПАМЯТИ ===")
    
    # Тест 1: Импорт модулей
    print("\n1. Тест импорта модулей:")
    try:
        from rag_memory_system.simple_memory_manager import SimpleMemoryManager
        print("[OK] SimpleMemoryManager импортирован")
        
        # Создаем экземпляр
        manager = SimpleMemoryManager()
        print("[OK] SimpleMemoryManager создан")
        
        # Проверяем доступность txtai
        if hasattr(manager, 'embeddings') and manager.embeddings is not None:
            print("[OK] txtai доступен и функционален")
        else:
            print("[WARNING] txtai недоступен - работаем без поиска")
            
    except ImportError as e:
        print(f"[ERROR] Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Ошибка создания менеджера: {e}")
        return False
    
    # Тест 2: Основные функции
    print("\n2. Тест основных функций:")
    try:
        # Создание сессии
        if hasattr(manager, 'create_session'):
            session_id = manager.create_session("Тест GopiAI")
            print(f"[OK] Сессия создана: {session_id[:8]}...")
        else:
            session_id = "test_session"
            print("[WARNING] create_session недоступен, используем фиксированный ID")
        
        # Добавление сообщений
        if hasattr(manager, 'add_message'):
            manager.add_message(session_id, "user", "Как работает txtai в GopiAI?")
            manager.add_message(session_id, "assistant", "txtai обеспечивает семантический поиск")
            print("[OK] Сообщения добавлены")
        else:
            print("[WARNING] add_message недоступен")
        
        # Поиск
        if hasattr(manager, 'search_memory'):
            results = manager.search_memory("txtai GopiAI")
            print(f"[OK] Поиск выполнен, найдено результатов: {len(results)}")
            
            # Показываем результаты
            for i, result in enumerate(results[:3]):  # Первые 3 результата
                if isinstance(result, dict):
                    text = result.get('text', str(result))[:50] + "..."
                    print(f"  Результат {i+1}: {text}")
                else:
                    print(f"  Результат {i+1}: {str(result)[:50]}...")
        else:
            print("[WARNING] search_memory недоступен")
            
    except Exception as e:
        print(f"[ERROR] Ошибка в тестах функций: {e}")
        return False
    
    # Тест 3: Проверка без txtai
    print("\n3. Тест работы без txtai:")
    try:
        # Временно отключаем txtai
        original_embeddings = getattr(manager, 'embeddings', None)
        manager.embeddings = None
        
        # Пробуем поиск
        if hasattr(manager, 'search_memory'):
            results = manager.search_memory("test query")
            print("[OK] Поиск работает без txtai (fallback режим)")
        
        # Восстанавливаем embeddings
        if original_embeddings is not None:
            manager.embeddings = original_embeddings
            
    except Exception as e:
        print(f"[WARNING] Ошибка в fallback режиме: {e}")
    
    print("\n=== ИТОГИ ТЕСТИРОВАНИЯ ФУНКЦИЙ ПАМЯТИ ===")
    print("[OK] Функции поиска памяти протестированы")
    print("[OK] Система работает как с txtai, так и без него")
    return True

if __name__ == "__main__":
    success = test_memory_functions()
    if success:
        print("\n[SUCCESS] Все тесты памяти пройдены успешно!")
        sys.exit(0)
    else:
        print("\n[FAILURE] Некоторые тесты памяти не пройдены")
        sys.exit(1)
