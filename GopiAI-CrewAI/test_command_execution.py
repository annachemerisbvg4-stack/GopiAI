#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности CommandExecutor
"""

import sys
import os
import logging

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_command_executor():
    """Тестируем CommandExecutor напрямую"""
    
    try:
        from tools.gopiai_integration.command_executor import CommandExecutor
        
        print("🔧 Инициализируем CommandExecutor...")
        executor = CommandExecutor()
        
        # Тестовый ответ от Gemini с командой
        test_response = """
        Конечно! Создаю папку TEST_EXECUTION для тестирования.
        
        ```json
        {'tool': 'terminal', 'params': {'command': 'mkdir C:\\\\Users\\\\crazy\\\\GOPI_AI_MODULES\\\\TEST_EXECUTION'}}
        ```
        
        Папка создана успешно!
        """
        
        print("📝 Тестируем парсинг ответа Gemini...")
        commands = executor.parse_gemini_response(test_response)
        print(f"Найдено команд: {len(commands)}")
        
        for i, cmd in enumerate(commands):
            print(f"Команда {i+1}: {cmd}")
        
        if commands:
            print("⚡ Выполняем команды...")
            results = executor.execute_commands(commands)
            
            for i, result in enumerate(results):
                print(f"Результат команды {i+1}:")
                print(f"  Успех: {result.get('success', False)}")
                print(f"  Вывод: {result.get('output', 'Нет вывода')[:100]}...")
                if not result.get('success', False):
                    print(f"  Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        
        # Проверяем, была ли создана папка
        test_folder = r"C:\Users\crazy\GOPI_AI_MODULES\TEST_EXECUTION"
        if os.path.exists(test_folder):
            print("✅ УСПЕХ! Папка TEST_EXECUTION была создана!")
        else:
            print("❌ ОШИБКА! Папка TEST_EXECUTION не была создана!")
        
        # Тестируем полную обработку
        print("\n🔄 Тестируем полную обработку ответа...")
        updated_response, command_results = executor.process_gemini_response(test_response)
        
        print("Обновленный ответ:")
        print(updated_response)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании CommandExecutor: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_smart_delegator():
    """Тестируем SmartDelegator с CommandExecutor"""
    
    try:
        from tools.gopiai_integration.smart_delegator import SmartDelegator
        
        print("\n🧠 Инициализируем SmartDelegator...")
        delegator = SmartDelegator()
        
        # Проверяем, что CommandExecutor инициализирован
        if hasattr(delegator, 'command_executor') and delegator.command_executor:
            print("✅ CommandExecutor успешно интегрирован в SmartDelegator!")
        else:
            print("❌ CommandExecutor НЕ интегрирован в SmartDelegator!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании SmartDelegator: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов CommandExecutor...")
    print("=" * 50)
    
    # Тест 1: CommandExecutor
    success1 = test_command_executor()
    
    # Тест 2: SmartDelegator
    success2 = test_smart_delegator()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ:")
    print(f"CommandExecutor: {'✅ УСПЕХ' if success1 else '❌ ОШИБКА'}")
    print(f"SmartDelegator: {'✅ УСПЕХ' if success2 else '❌ ОШИБКА'}")
    
    if success1 and success2:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("Система выполнения команд готова к работе!")
    else:
        print("\n⚠️ ЕСТЬ ПРОБЛЕМЫ, ТРЕБУЮЩИЕ ИСПРАВЛЕНИЯ!")
    
    print("=" * 50)
