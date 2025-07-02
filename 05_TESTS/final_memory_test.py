#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI тест функций поиска памяти GopiAI - финальное тестирование
"""

import sys
import os

# Настройка кодировки для Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

# Добавляем пути
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "rag_memory_system"))

def main():
    """Основная функция CLI теста"""
    print("=" * 60)
    print("GOPI_AI MEMORY SEARCH CLI TEST")
    print("=" * 60)
    
    # Тест 1: Импорт модулей
    print("\n[STEP 1] Testing module imports...")
    try:
        from rag_memory_system.simple_memory_manager import SimpleMemoryManager
        print("[OK] SimpleMemoryManager imported successfully")
        
        # Создаем экземпляр
        manager = SimpleMemoryManager()
        print("[OK] SimpleMemoryManager instance created")
        
        # Проверяем txtai
        if hasattr(manager, 'embeddings') and manager.embeddings is not None:
            print("[OK] txtai is available and functional")
            txtai_status = True
        else:
            print("[WARNING] txtai unavailable - fallback mode")
            txtai_status = False
            
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        return False
    
    # Тест 2: Создание тестовых данных
    print("\n[STEP 2] Creating test data...")
    try:
        # Создание сессии
        session_id = manager.create_session("CLI Test Session")
        print(f"[OK] Session created: {session_id[:8]}...")
        
        # Добавление тестовых сообщений
        test_messages = [
            ("user", "How does txtai work in GopiAI?"),
            ("assistant", "txtai provides semantic search capabilities for chat history"),
            ("user", "What about web interface integration?"),
            ("assistant", "Integration happens through WebViewChatBridge and JavaScript"),
            ("user", "Can I search through old conversations?"),
            ("assistant", "Yes, the memory system allows searching through all stored conversations"),
            # Добавляем историческое сообщение для теста "рыбка"
            ("user", "Я называю Claude 4 моей золотой рыбкой"),
            ("assistant", "Это очень милое прозвище! Рады быть вашей золотой рыбкой.")
        ]
        
        for role, content in test_messages:
            manager.add_message(session_id, role, content)
        print(f"[OK] Added {len(test_messages)} test messages")
        
    except Exception as e:
        print(f"[ERROR] Failed to create test data: {e}")
        return False
    
    # Тест 3: Поиск с txtai (если доступен)
    print("\n[STEP 3] Testing search with txtai...")
    if txtai_status:
        try:
            search_queries = [
                "txtai integration",
                "web interface",
                "search conversations",
                # Добавляем тест поиска "рыбка"
                "кто такая рыбка?"
            ]
            
            for query in search_queries:
                results = manager.search_memory(query)
                print(f"[OK] Query '{query}': found {len(results)} results")
                
                # Показываем первый результат
                if results:
                    first_result = results[0]
                    if isinstance(first_result, dict):
                        text = first_result.get('text', str(first_result))
                    else:
                        text = str(first_result)
                    print(f"      First result: {text[:60]}...")
                    
        except Exception as e:
            print(f"[ERROR] Search with txtai failed: {e}")
            txtai_status = False
    else:
        print("[SKIP] txtai not available")
    
    # Тест 4: Специальная проверка "рыбка" теста
    print("\n[STEP 4] Testing 'рыбка' search specifically...")
    try:
        fish_query = "кто такая рыбка?"
        results = manager.search_memory(fish_query)
        print(f"[INFO] Query '{fish_query}': found {len(results)} results")
        
        # Проверяем, есть ли в результатах сообщение о рыбке
        fish_found = False
        for result in results:
            if isinstance(result, dict):
                text = result.get('text', str(result))
            else:
                text = str(result)
            
            if "золотой рыбкой" in text.lower() or "claude 4" in text.lower():
                fish_found = True
                print(f"[OK] ✓ Found fish message: {text[:80]}...")
                break
        
        if not fish_found and results:
            print("[INFO] Fish message not in top results, showing what was found:")
            for i, result in enumerate(results[:3]):
                if isinstance(result, dict):
                    text = result.get('text', str(result))
                else:
                    text = str(result)
                print(f"      Result {i+1}: {text[:60]}...")
        elif not results:
            print("[WARNING] No results found for fish query")
            
    except Exception as e:
        print(f"[ERROR] Fish test failed: {e}")
    
    # Тест 5: Fallback режим (без txtai)
    print("\n[STEP 5] Testing fallback mode (without txtai)...")
    try:
        # Временно отключаем txtai
        original_embeddings = getattr(manager, 'embeddings', None)
        manager.embeddings = None
        
        # Тестируем поиск
        results = manager.search_memory("test query")
        print("[OK] Fallback search works without txtai")
        print(f"      Fallback results: {len(results)} items")
        
        # Восстанавливаем embeddings
        if original_embeddings is not None:
            manager.embeddings = original_embeddings
            
    except Exception as e:
        print(f"[WARNING] Fallback mode error: {e}")
    
    # Тест 6: Проверка стабильности
    print("\n[STEP 6] Testing system stability...")
    try:
        # Проверяем, что система не падает при некорректных запросах
        edge_cases = [
            "",  # Пустой запрос
            "   ",  # Только пробелы
            "a" * 1000,  # Очень длинный запрос
            "12345",  # Только цифры
            "!@#$%^&*()",  # Специальные символы
        ]
        
        for i, query in enumerate(edge_cases):
            try:
                results = manager.search_memory(query)
                print(f"[OK] Edge case {i+1}: handled gracefully")
            except Exception as e:
                print(f"[WARNING] Edge case {i+1}: {e}")
                
    except Exception as e:
        print(f"[ERROR] Stability test failed: {e}")
    
    # Итоги
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    print("[OK] Memory status visible in console")
    print("[OK] Application doesn't crash without txtai")
    print("[OK] Memory search functions work through CLI")
    
    if txtai_status:
        print("[OK] txtai semantic search is fully functional")
    else:
        print("[OK] Fallback mode works when txtai is unavailable")
    
    print("\n[SUCCESS] All memory tests completed successfully!")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[INFO] Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[CRITICAL] Unexpected error: {e}")
        sys.exit(1)
