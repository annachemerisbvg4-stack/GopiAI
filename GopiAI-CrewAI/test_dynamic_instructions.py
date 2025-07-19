"""
🧪 Тест системы динамических инструкций для CrewAI
Простой тест интеграции ToolsInstructionManager с CrewAI workflow
"""

import os
import sys
from pathlib import Path

# Добавляем пути для импорта
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir / 'tools'))

from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def test_tools_instruction_manager():
    """Тестирование ToolsInstructionManager"""
    print("[TEST] === ТЕСТИРОВАНИЕ TOOLS INSTRUCTION MANAGER ===")
    
    try:
        from tools.gopiai_integration.tools_instruction_manager import get_tools_instruction_manager
        
        manager = get_tools_instruction_manager()
        
        # Тестируем получение краткого списка инструментов
        tools_summary = manager.get_tools_summary()
        print(f"[INFO] Доступно инструментов: {len(tools_summary)}")
        for tool_name, description in tools_summary.items():
            print(f"  • {tool_name}: {description[:50]}...")
        
        # Тестируем получение детальных инструкций
        print("\n[INFO] Тестирование детальных инструкций:")
        for tool_name in tools_summary.keys():
            instructions = manager.get_tool_detailed_instructions(tool_name)
            if instructions:
                print(f"  [OK] {tool_name}: {len(instructions)} символов инструкций")
            else:
                print(f"  [ERROR] {tool_name}: инструкции не найдены")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании ToolsInstructionManager: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_crewai_integration():
    """Тестирование интеграции с CrewAI"""
    print("\n[TEST] === ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ С CREWAI ===")
    
    try:
        from crewai import Agent, LLM
        from tools.gopiai_integration.crewai_tools_integration import (
            enhance_agent_with_instructions,
            get_tools_integrator
        )
        from tools.gopiai_integration.filesystem_tools import GopiAIFileSystemTool
        from tools.gopiai_integration.browser_tools import GopiAIBrowserTool
        
        # Создаем простой LLM
        llm = LLM(
            model="gemini/gemini-1.5-flash",
            temperature=0.1
        )
        
        # Создаем агента с инструментами
        agent = Agent(
            role='Test Agent',
            goal='Тестировать динамические инструкции',
            backstory='Тестовый агент для проверки системы динамических инструкций',
            tools=[GopiAIFileSystemTool(), GopiAIBrowserTool()],
            llm=llm,
            verbose=True
        )
        
        print(f"[INFO] Создан агент с {len(agent.tools)} инструментами")
        
        # Улучшаем агента динамическими инструкциями
        enhanced_agent = enhance_agent_with_instructions(agent)
        
        print(f"[OK] Агент улучшен динамическими инструкциями")
        print(f"[INFO] Количество инструментов: {len(enhanced_agent.tools)}")
        
        # Проверяем интегратор
        integrator = get_tools_integrator()
        print(f"[INFO] Интегратор инициализирован: {integrator is not None}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании интеграции с CrewAI: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_system_prompts_integration():
    """Тестирование интеграции с system_prompts"""
    print("\n[TEST] === ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ С SYSTEM PROMPTS ===")
    
    try:
        from tools.gopiai_integration.system_prompts import SystemPrompts
        
        # Создаем экземпляр SystemPrompts
        prompts = SystemPrompts()
        
        # Тестируем получение краткого списка инструментов для промпта
        tools_for_prompt = prompts.get_tools_summary_for_prompt()
        print(f"[INFO] Получен список инструментов для промпта: {len(tools_for_prompt)} символов")
        print(f"Начало: {tools_for_prompt[:100]}...")
        
        # Тестируем получение детальных инструкций для конкретного инструмента
        detailed_instructions = prompts.get_tool_detailed_instructions('filesystem_tools')
        if detailed_instructions:
            print(f"[OK] Получены детальные инструкции для filesystem_tools: {len(detailed_instructions)} символов")
        else:
            print("[ERROR] Не удалось получить детальные инструкции")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании интеграции с system_prompts: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Запуск всех тестов"""
    print("=== ЗАПУСК ВСЕХ ТЕСТОВ СИСТЕМЫ ДИНАМИЧЕСКИХ ИНСТРУКЦИЙ ===\n")
    
    results = []
    
    # Тест 1: ToolsInstructionManager
    results.append(test_tools_instruction_manager())
    
    # Тест 2: Интеграция с CrewAI
    results.append(test_crewai_integration())
    
    # Тест 3: Интеграция с SystemPrompts
    results.append(test_system_prompts_integration())
    
    # Итоги
    print("\n" + "="*60)
    print("[RESULT] === ИТОГИ ТЕСТИРОВАНИЯ ===")
    
    passed = sum(results)
    total = len(results)
    
    print(f"[OK] Пройдено тестов: {passed}/{total}")
    
    if passed == total:
        print("[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Система динамических инструкций готова к использованию!")
    else:
        print(f"[WARNING] Некоторые тесты не прошли. Требуется доработка.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
