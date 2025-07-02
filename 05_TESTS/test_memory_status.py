#!/usr/bin/env python3
"""
Тестовый скрипт для проверки статуса памяти GopiAI
"""

import sys
import os
from pathlib import Path

# Добавляем пути к модулям
script_dir = os.path.dirname(os.path.abspath(__file__))
module_paths = [
    os.path.join(script_dir, "GopiAI-Core"),
    os.path.join(script_dir, "GopiAI-UI"),
    os.path.join(script_dir, "rag_memory_system"),
    script_dir,
]

for path in module_paths:
    if path not in sys.path:
        sys.path.insert(0, path)

print("=== GOPI_AI MEMORY STATUS TEST ===")
print("Добавленные пути для модулей:")
for p in module_paths:
    print(f"- {p} (существует: {os.path.exists(p)})")

# Проверяем импорт базовых модулей
print("\n=== ПРОВЕРКА БАЗОВЫХ МОДУЛЕЙ ===")
try:
    import sqlite3
    print("[OK] sqlite3 доступен")
except ImportError as e:
    print(f"[ERROR] sqlite3 недоступен: {e}")

try:
    import json
    print("[OK] json доступен")
except ImportError as e:
    print(f"[ERROR] json недоступен: {e}")

# Проверяем доступность txtai
print("\n=== ПРОВЕРКА TXTAI ===")
try:
    import txtai
    print("[OK] txtai доступен")
    
    # Пробуем создать индекс для проверки работоспособности
    try:
        from txtai.embeddings import Embeddings
        embeddings = Embeddings({"path": "sentence-transformers/all-MiniLM-L6-v2"})
        print("[OK] txtai полностью функционален")
    except Exception as e:
        print(f"[WARNING] txtai импортирован, но не полностью функционален: {e}")
        
except ImportError as e:
    print(f"[WARNING] txtai недоступен: {e}")
    print("[WARNING] Приложение будет работать без семантического поиска")

# Проверяем инициализацию системы памяти
print("\n=== ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ ПАМЯТИ ===")
try:
    # Попробуем импортировать memory_initializer
    from gopiai.ui.memory_initializer import init_memory_system
    
    print("Инициализируем систему памяти...")
    init_ok = init_memory_system(silent=False)
    print(f"Результат инициализации памяти: {init_ok}")
    
    if init_ok:
        print("[OK] Система памяти успешно инициализирована")
    else:
        print("[WARNING] Система памяти инициализирована с предупреждениями")
        
except ImportError as e:
    print(f"[WARNING] Не удалось импортировать memory_initializer: {e}")
    print("Попробуем простую инициализацию памяти...")
    
    # Fallback инициализация
    try:
        memory_dir = os.path.join(script_dir, "rag_memory_system")
        if os.path.exists(memory_dir):
            print(f"[OK] Папка системы памяти найдена: {memory_dir}")
            
            # Проверяем базу данных
            db_path = os.path.join(memory_dir, "memory.db")
            if os.path.exists(db_path):
                print(f"[OK] База данных памяти найдена: {db_path}")
                
                # Простая проверка подключения к БД
                try:
                    import sqlite3
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    conn.close()
                    print(f"[OK] База данных доступна, таблицы: {[t[0] for t in tables]}")
                except Exception as e:
                    print(f"[WARNING] Ошибка доступа к базе данных: {e}")
            else:
                print(f"[WARNING] База данных памяти не найдена: {db_path}")
        else:
            print(f"[WARNING] Папка системы памяти не найдена: {memory_dir}")
            
    except Exception as e:
        print(f"[ERROR] Ошибка fallback инициализации: {e}")

except Exception as e:
    print(f"[ERROR] Неожиданная ошибка: {e}")

# Проверяем функции поиска памяти
print("\n=== ТЕСТИРОВАНИЕ ФУНКЦИЙ ПОИСКА ПАМЯТИ ===")
try:
    # Попробуем импортировать и использовать модули поиска
    sys.path.insert(0, os.path.join(script_dir, "rag_memory_system"))
    
    # Простой тест поиска
    print("Пытаемся выполнить простой поиск...")
    
    # Проверяем наличие файлов поиска
    search_files = [
        "rag_memory_system/search_memory.py",
        "rag_memory_system/memory_search.py",
        "rag_memory_system/memory_manager.py"
    ]
    
    for search_file in search_files:
        full_path = os.path.join(script_dir, search_file)
        if os.path.exists(full_path):
            print(f"[OK] Найден файл поиска: {search_file}")
        else:
            print(f"[WARNING] Файл поиска не найден: {search_file}")
            
    # Попробуем загрузить модуль поиска
    try:
        if os.path.exists(os.path.join(script_dir, "rag_memory_system", "search_memory.py")):
            import search_memory
            print("[OK] Модуль search_memory загружен")
            
            # Попробуем выполнить тестовый поиск
            if hasattr(search_memory, 'search_memories'):
                print("[OK] Функция search_memories доступна")
                # Можно добавить тестовый вызов, если нужно
            else:
                print("[WARNING] Функция search_memories недоступна")
        else:
            print("[WARNING] Модуль search_memory не найден")
    except Exception as e:
        print(f"[WARNING] Ошибка загрузки модуля поиска: {e}")
        
except Exception as e:
    print(f"[ERROR] Ошибка тестирования поиска: {e}")

print("\n=== ИТОГИ ТЕСТИРОВАНИЯ ===")
print("1. [OK] Проверка статуса памяти в консоли выполнена")
print("2. [WARNING] Для полного тестирования UI требуется GUI окружение")
print("3. [NOTE] Рекомендуется запустить полное приложение для проверки UI")
print("\n=== КОНЕЦ ТЕСТИРОВАНИЯ ===")
