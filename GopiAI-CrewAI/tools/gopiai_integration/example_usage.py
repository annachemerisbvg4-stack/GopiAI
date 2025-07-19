"""
🚀 Пример использования новой системы промптов и инструкций GopiAI
Демонстрирует динамическую подгрузку инструкций для ИИ
"""

import logging
from system_prompts import get_system_prompts
from tools_instruction_manager import get_tools_instruction_manager

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def demo_new_prompt_system():
    """Демонстрация новой системы промптов и инструкций"""
    
    print("🤖 === ДЕМОНСТРАЦИЯ НОВОЙ СИСТЕМЫ GOPIАI ===\n")
    
    # 1. Получаем менеджер промптов
    prompts = get_system_prompts()
    tools_manager = get_tools_instruction_manager()
    
    # 2. Демонстрируем базовый промпт (без инструментов)
    print("📋 БАЗОВЫЙ ПРОМПТ ГИПАТИИ:")
    print("-" * 50)
    base_prompt = prompts.get_base_assistant_prompt()
    print(base_prompt[:500] + "..." if len(base_prompt) > 500 else base_prompt)
    print()
    
    # 3. Демонстрируем краткий список инструментов
    print("🛠️ КРАТКИЙ СПИСОК ИНСТРУМЕНТОВ ДЛЯ СИСТЕМНОГО ПРОМПТА:")
    print("-" * 60)
    tools_summary = tools_manager.get_tools_summary()
    for tool_name, description in tools_summary.items():
        print(f"• {tool_name}: {description}")
    print()
    
    # 4. Демонстрируем полный системный промпт
    print("🎯 ПОЛНЫЙ СИСТЕМНЫЙ ПРОМПТ (базовый + краткий список инструментов):")
    print("-" * 70)
    complete_prompt = prompts.get_complete_assistant_prompt(include_tools=True)
    # Показываем только конец, где инструменты
    lines = complete_prompt.split('\n')
    tools_section = '\n'.join(lines[-15:])  # Последние 15 строк
    print("... (базовый промпт) ...")
    print(tools_section)
    print()
    
    # 5. Демонстрируем динамическую подгрузку детальных инструкций
    print("📖 ДИНАМИЧЕСКАЯ ПОДГРУЗКА ДЕТАЛЬНЫХ ИНСТРУКЦИЙ:")
    print("-" * 55)
    
    for tool_name in ["filesystem_tools", "browser_tools", "local_mcp_tools"]:
        print(f"\n🔍 Загружаем инструкции для {tool_name}:")
        detailed = tools_manager.get_tool_detailed_instructions(tool_name)
        if detailed:
            # Показываем первые несколько строк
            lines = detailed.split('\n')
            preview = '\n'.join(lines[:10])
            print(preview)
            print(f"... (всего {len(lines)} строк инструкций)")
        else:
            print("❌ Инструкции не найдены")
    
    print("\n✅ === ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА ===")
    print("\n💡 Преимущества новой системы:")
    print("• Не перегружает системный промпт")
    print("• Актуальная информация об инструментах")
    print("• Быстрая загрузка базового контекста")
    print("• Подробные инструкции по требованию")

def demo_ai_workflow():
    """Демонстрация рабочего процесса ИИ с новой системой"""
    
    print("\n🔄 === СИМУЛЯЦИЯ РАБОЧЕГО ПРОЦЕССА ИИ ===\n")
    
    prompts = get_system_prompts()
    
    # Шаг 1: ИИ получает базовый промпт при запуске
    print("1️⃣ ИИ получает базовый системный промпт при запуске:")
    complete_prompt = prompts.get_complete_assistant_prompt()
    print(f"   Размер промпта: {len(complete_prompt)} символов")
    print("   ✅ Быстрая загрузка, личность Гипатии активна")
    print("   ✅ Краткий список инструментов загружен")
    print()
    
    # Шаг 2: Пользователь просит использовать конкретный инструмент
    print("2️⃣ Пользователь: 'Найди все Python файлы в проекте'")
    print("   🤖 ИИ: Выбираю filesystem_tools для поиска файлов")
    print()
    
    # Шаг 3: ИИ запрашивает детальные инструкции
    print("3️⃣ ИИ запрашивает детальные инструкции:")
    detailed = prompts.get_tool_detailed_instructions("filesystem_tools")
    if detailed:
        lines = detailed.split('\n')
        print(f"   📖 Загружено {len(lines)} строк детальных инструкций")
        print("   ✅ ИИ теперь знает все возможности filesystem_tools")
    print()
    
    # Шаг 4: ИИ выполняет задачу
    print("4️⃣ ИИ выполняет задачу с полным пониманием инструмента:")
    print("   🔍 Использует find_files() с маской '*.py'")
    print("   ✅ Задача выполнена эффективно")
    print()
    
    print("🎯 Результат: Эффективная работа без перегрузки системного промпта!")

if __name__ == "__main__":
    try:
        demo_new_prompt_system()
        demo_ai_workflow()
    except Exception as e:
        logger.error(f"❌ Ошибка в демонстрации: {e}")
        print(f"\n💡 Убедитесь, что все модули правильно импортированы и инициализированы")
