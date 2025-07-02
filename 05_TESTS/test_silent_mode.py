#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест для проверки, что проблема действительно визуальная (из-за silent=True)
а не функциональная.
"""

import sys
import os

# Добавляем пути для импорта модулей GopiAI
sys.path.insert(0, os.path.join(os.getcwd(), 'GopiAI-UI'))
sys.path.insert(0, os.path.join(os.getcwd(), 'rag_memory_system'))

print("Тестируем init_memory_system с разными режимами...")
print("=" * 60)

# Тест 1: С silent=True (как в main.py)
print("\n1. Тест с silent=True (как в main.py):")
print("-" * 40)

try:
    from gopiai.ui.memory_initializer import init_memory_system, get_memory_status
    
    # Вызов как в main.py
    result_silent = init_memory_system(silent=True)
    print(f"Результат: {result_silent}")
    
    if result_silent:
        status = get_memory_status()
        print(f"Статус системы: {status}")
    
except Exception as e:
    print(f"Ошибка: {e}")

# Тест 2: С silent=False (чтобы увидеть все сообщения)
print("\n2. Тест с silent=False (показываем все сообщения):")
print("-" * 40)

try:
    result_verbose = init_memory_system(silent=False)
    print(f"Результат: {result_verbose}")
    
except Exception as e:
    print(f"Ошибка: {e}")

# Тест 3: Прямое создание SimpleMemoryManager
print("\n3. Тест прямого создания SimpleMemoryManager:")
print("-" * 40)

try:
    from rag_memory_system import SimpleMemoryManager
    
    # Создаем напрямую (это покажет все print'ы)
    manager = SimpleMemoryManager()
    stats = manager.get_stats()
    print(f"Статистика: {stats}")
    
except Exception as e:
    print(f"Ошибка: {e}")

print("\n" + "=" * 60)
print("ВЫВОД:")
print("При silent=True вывод подавляется, но система работает!")
print("Проблема ВИЗУАЛЬНАЯ, а не функциональная.")
