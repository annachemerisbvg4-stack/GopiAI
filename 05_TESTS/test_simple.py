#!/usr/bin/env python3
import sys
import os

# Добавляем пути для импорта модулей GopiAI
sys.path.insert(0, os.path.join(os.getcwd(), 'rag_memory_system'))

print("Тест SimpleMemoryManager")
print("=" * 40)

try:
    from simple_memory_manager import SimpleMemoryManager, get_memory_manager
    
    print("Создаем SimpleMemoryManager напрямую:")
    manager = SimpleMemoryManager()
    
    print("Получаем статистику:")
    stats = manager.get_stats()
    print(f"Статистика: {stats}")
    
    print("\nТестируем get_memory_manager():")
    manager2 = get_memory_manager()
    stats2 = manager2.get_stats()
    print(f"Статистика через get_memory_manager: {stats2}")
    
    print("\nВывод: SimpleMemoryManager работает корректно!")
    
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
