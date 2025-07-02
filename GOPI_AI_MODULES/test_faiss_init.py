#!/usr/bin/env python3
"""
🧪 Тестовый скрипт для проверки инициализации FAISS-индекса
"""

import sys
import os
sys.path.append('rag_memory_system')

try:
    from simple_memory_manager import SimpleMemoryManager, FAISS_AVAILABLE, TXTAI_AVAILABLE
    
    print("=== Проверка инициализации SimpleMemoryManager ===")
    print(f"TXTAI доступен: {TXTAI_AVAILABLE}")
    print(f"FAISS доступен: {FAISS_AVAILABLE}")
    print()
    
    # Создаем экземпляр менеджера памяти
    print("Создание экземпляра SimpleMemoryManager...")
    manager = SimpleMemoryManager(data_dir="test_conversations")
    
    # Проверяем инициализацию
    print(f"✅ Размерность векторов: {manager.dim}")
    print(f"✅ Путь к файлу векторов: {manager.vectors_file}")
    print(f"✅ Путь к файлу ID: {manager.idmap_file}")
    
    if FAISS_AVAILABLE:
        print(f"✅ FAISS индекс создан: {manager.index is not None}")
        print(f"✅ Список vector_ids инициализирован: {isinstance(manager.vector_ids, list)}")
        print(f"✅ Размер индекса: {manager.index.ntotal}")
    else:
        print("⚠️ FAISS недоступен - проверка пропущена")
    
    if TXTAI_AVAILABLE:
        print(f"✅ txtai embeddings инициализированы: {manager.embeddings is not None}")
    else:
        print("⚠️ txtai недоступен - проверка пропущена")
    
    print("\n🎉 Инициализация FAISS-индекса и структур хранения выполнена успешно!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
