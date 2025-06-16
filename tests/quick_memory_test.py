"""
Быстрый тест импорта системы памяти
"""

print("🧪 Быстрый тест памяти...")

try:
    # Тестируем импорт памяти
    import sys
    sys.path.append('C:/Users/crazy/GOPI_AI_MODULES')
    
    print("1️⃣ Проверяем файл memory_manager...")
    import rag_memory_system.memory_manager as mm
    print("   ✅ memory_manager импортирован")
    
    print("2️⃣ Проверяем server_manager...")
    import rag_memory_system.server_manager as sm
    print("   ✅ server_manager импортирован")
    
    print("3️⃣ Проверяем memory_init...")
    import rag_memory_system.memory_init as mi
    print("   ✅ memory_init импортирован")
    
    print("✅ Все модули памяти импортируются корректно!")
    
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()