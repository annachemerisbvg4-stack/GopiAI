#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции системы памяти в GopiAI
============================================================

Этот скрипт проверяет, что система памяти корректно интегрируется
с главным интерфейсом GopiAI.
"""

import sys
import os
from pathlib import Path

def test_memory_integration():
    """Тестирование интеграции системы памяти"""
    print("🧪 Тестирование интеграции системы памяти GopiAI\n")
    
    # Добавляем пути для импорта
    script_dir = Path(__file__).parent
    gopiai_ui_path = script_dir / "GopiAI-UI"
    
    if str(gopiai_ui_path) not in sys.path:
        sys.path.insert(0, str(gopiai_ui_path))
    
    try:
        print("1️⃣ Импорт модуля инициализации памяти...")
        from gopiai.ui.memory_initializer import init_memory_system, get_memory_status
        print("   ✅ Успешно")
        
        print("\n2️⃣ Инициализация системы памяти...")
        success = init_memory_system(silent=False)
        
        if success:
            print("   ✅ Система памяти запущена")
            
            print("\n3️⃣ Проверка статуса...")
            status = get_memory_status()
            print("   📊 Статус системы памяти:")
            for key, value in status.items():
                print(f"      {key}: {value}")
                
            return True
        else:
            print("   ❌ Не удалось запустить систему памяти")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bridge_integration():
    """Тестирование интеграции с мостом JavaScript"""
    print("\n4️⃣ Тестирование интеграции с JS мостом...")
    
    try:
        # Импортируем мост
        sys.path.insert(0, str(Path(__file__).parent / "GopiAI-WebView"))
        from gopiai.webview.js_bridge import JavaScriptBridge
        
        print("   ✅ JavaScriptBridge импортирован")
        
        # Создаем тестовый экземпляр (без webview)
        bridge = JavaScriptBridge(None)
        
        # Проверяем наличие методов памяти
        memory_methods = [
            'enrich_message',
            'save_chat_exchange', 
            'start_new_chat_session',
            'get_memory_stats',
            'is_memory_available'
        ]
        
        for method in memory_methods:
            if hasattr(bridge, method):
                print(f"   ✅ Метод {method} найден")
            else:
                print(f"   ❌ Метод {method} не найден")
                
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Тестирование интеграции системы памяти GopiAI\n")
    
    # Тест 1: Инициализация памяти
    memory_ok = test_memory_integration()
    
    # Тест 2: Интеграция с мостом
    bridge_ok = test_bridge_integration()
    
    print(f"\n📋 Результаты тестирования:")
    print(f"   Система памяти: {'✅ OK' if memory_ok else '❌ FAIL'}")
    print(f"   Интеграция с мостом: {'✅ OK' if bridge_ok else '❌ FAIL'}")
    
    if memory_ok and bridge_ok:
        print("\n🎉 Все тесты пройдены! Система памяти готова к использованию.")
        
        print("\n⏳ Система работает... (нажмите Ctrl+C для остановки)")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Остановка...")
            
            # Остановка системы памяти
            try:
                from gopiai.ui.memory_initializer import stop_memory_system
                stop_memory_system()
                print("✅ Система памяти остановлена")
            except:
                pass
            
    else:
        print("\n❌ Есть проблемы с интеграцией. Проверьте логи выше.")
        sys.exit(1)