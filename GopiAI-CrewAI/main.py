#!/usr/bin/env python3
"""
🚀 GopiAI-CrewAI Advanced Integration
Полная интеграция CrewAI с GopiAI системой и всеми инструментами
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Добавляем пути для импорта
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent))  # GOPI_AI_MODULES
sys.path.append(str(current_dir))  # GopiAI-CrewAI
sys.path.append(str(current_dir / 'tools'))  # tools directory

# Загружаем переменные окружения
from dotenv import load_dotenv
env_path = current_dir / '.env'  # Исправляем путь - .env файл в текущей папке
load_dotenv(env_path, override=True)

# Импорт CrewAI
from crewai import Agent, Task, Crew, LLM
from tools.gopiai_integration.ai_router_llm import AIRouterLLM
from crewai.tasks.task_output import TaskOutput

# Импорт всех GopiAI инструментов
try:
    from tools.gopiai_integration.base.base_tool import GopiAIBaseTool
    from tools.gopiai_integration.browser_tools import GopiAIBrowserTool
    from tools.gopiai_integration.filesystem_tools import GopiAIFileSystemTool
    from tools.gopiai_integration.ai_router_tools import GopiAIRouterTool
    from tools.gopiai_integration.memory_tools import GopiAIMemoryTool
    from tools.gopiai_integration.communication_tools import GopiAICommunicationTool
    from tools.gopiai_integration.huggingface_tools import GopiAIHuggingFaceTool
    print("🔍 === ПРОВЕРКА ОКРУЖЕНИЯ ===")
except ImportError as e:
    print(f"❌ Ошибка импорта инструментов: {e}")
    sys.exit(1)

def check_environment():
    """Проверка окружения и ключей API"""
    print("🔍 === ПРОВЕРКА ОКРУЖЕНИЯ ===")
    
    # Проверяем .env файл
    if env_path.exists():
        print(f"✅ .env файл найден: {env_path}")
    else:
        print(f"❌ .env файл не найден: {env_path}")
        return False
    
    # Проверяем ключи API
    api_keys = {
        'GEMINI_API_KEY': {'prefix': 'AIza', 'name': 'Google Gemini'},
    }
    
    available_providers = []
    
    for key_name, config in api_keys.items():
        key_value = os.getenv(key_name)
        if key_value and key_value.strip() and key_value != "your_key_here":
            prefix_ok = True
            if config['prefix']:
                prefix_ok = key_value.startswith(config['prefix'])
            
            status = "✅" if prefix_ok else "⚠️"
            print(f"   {config['name']}: {status} {'(ключ найден)' if prefix_ok else '(неверный формат)'}")
            
            if prefix_ok:
                available_providers.append(config['name'])
        else:
            print(f"   {config['name']}: ❌ отсутствует")
    
    if not available_providers:
        print("❌ Нет доступных провайдеров!")
        return False
    
    print(f"✅ Доступные провайдеры: {', '.join(available_providers)}")
    return True

def test_all_tools():
    """Тестирование всех GopiAI инструментов"""
    print("🧪 === ТЕСТИРОВАНИЕ ИНСТРУМЕНТОВ ===")
    
    tools_results = {}
    
    # Тест Communication Tool
    try:
        print("📡 Тестирование Communication Tool...")
        comm_tool = GopiAICommunicationTool()
        result = comm_tool._run("notify", "", "Система запущена", "info", 3, "{}")
        tools_results['communication'] = True
        print(f"✅ Communication: {result}")
    except Exception as e:
        tools_results['communication'] = False
        print(f"❌ Communication ошибка: {e}")
    
    # Тест Memory Tool
    try:
        print("🧠 Тестирование Memory Tool...")
        memory_tool = GopiAIMemoryTool()
        result = memory_tool._run("store", "system_test", "Тест системы памяти", "general", 5)
        tools_results['memory'] = True
        print(f"✅ Memory: {result}")
    except Exception as e:
        tools_results['memory'] = False
        print(f"❌ Memory ошибка: {e}")
    
    # Тест FileSystem Tool
    try:
        print("📁 Тестирование FileSystem Tool...")
        fs_tool = GopiAIFileSystemTool()
        result = fs_tool._run("list", ".")
        tools_results['filesystem'] = True
        if isinstance(result, list):
            print(f"✅ FileSystem: найдено {len(result)} элементов")
        else:
            print(f"✅ FileSystem: {result}")
    except Exception as e:
        tools_results['filesystem'] = False
        print(f"❌ FileSystem ошибка: {e}")
    
    # Тест Browser Tool (может не работать без интернета)
    try:
        print("🌐 Тестирование Browser Tool...")
        browser_tool = GopiAIBrowserTool()
        result = browser_tool._run("search", "CrewAI", "", 3)
        tools_results['browser'] = True
        print(f"✅ Browser: {result[:50]}...")
    except Exception as e:
        tools_results['browser'] = False
        print(f"⚠️ Browser ошибка (нормально без интернета): {e}")
    
    # Тест AI Router Tool
    try:
        print("🔀 Тестирование AI Router Tool...")
        router_tool = GopiAIRouterTool()
        result = router_tool._run(message="Привет!", task_type="chat")
        tools_results['router'] = True
        print(f"✅ Router: {result[:50]}...")
    except Exception as e:
        tools_results['router'] = False
        print(f"❌ Router ошибка: {e}")
    
    # Тест HuggingFace Tool  
    try:
        print("🤗 Тестирование HuggingFace Tool...")
        hf_tool = GopiAIHuggingFaceTool()
        result = hf_tool._run("Привет!", "microsoft/DialoGPT-large", "conversational", 100, 0.7)
        tools_results['huggingface'] = True
        print(f"✅ HuggingFace: {result[:50]}...")
    except Exception as e:
        tools_results['huggingface'] = False
        print(f"❌ HuggingFace ошибка: {e}")
    
    working_tools = sum(tools_results.values())
    total_tools = len(tools_results)
    
    print(f"📊 Результат: {working_tools}/{total_tools} инструментов работают")
    return working_tools > 0

from tools.gopiai_integration.agent_templates import AgentTemplateSystem
from crewai import Agent
from llm_rotation_config import LLM_MODELS_CONFIG, select_llm_model, rag_answer

def create_demo_agents(llm):
    """Создание демонстрационных агентов с GopiAI инструментами"""
    print("👥 === СОЗДАНИЕ АГЕНТОВ ===")
    
    # Используем систему шаблонов для создания агентов
    template_system = AgentTemplateSystem(verbose=True)
    print(f"📋 Доступные шаблоны: {', '.join(template_system.list_available_templates())}")
    
    # Создаем агентов из шаблонов
    coordinator = template_system.create_agent_from_template(
        "coordinator_agent", 
        llm,
        team_size=3,
        verbose=True
    )
    
    researcher = template_system.create_agent_from_template(
        "researcher_agent",
        llm,
        topic="GopiAI интеграция с CrewAI",
        verbose=True
    )
    
    writer = template_system.create_agent_from_template(
        "writer_agent",
        llm,
        topic="Многоагентные системы",
        format="markdown",
        creativity_level="high",
        verbose=True
    )
    
    # Создаем агента-программиста вручную для демонстрации
    # Создаем все инструменты
    all_tools = [
        GopiAICommunicationTool(),
        GopiAIMemoryTool(),
        GopiAIFileSystemTool(),
        GopiAIBrowserTool(),
        GopiAIRouterTool(),
        GopiAIHuggingFaceTool()
    ]
    
    # Агент-программист (полный набор инструментов)
    coder = Agent(
        role='Code Developer',
        goal='Разрабатывать и оптимизировать код на Python',
        backstory="""Ты опытный Python-разработчик в GopiAI. Твоя задача - писать
        чистый, эффективный и хорошо документированный код для различных компонентов системы.""",
        tools=all_tools,
        llm=llm,
        verbose=True,
        allow_delegation=True,
        max_iter=5
    )
    
    print(f"✅ Создано {len([coordinator, researcher, writer, coder])} агентов")
    return coordinator, researcher, writer, coder

def create_demo_tasks(coordinator, researcher, writer, coder):
    """Создание демонстрационных задач"""
    print("📋 === СОЗДАНИЕ ЗАДАЧ ===")
    # Проверка на None для всех агентов
    if not all([coordinator, researcher, writer, coder]):
        print("❌ Ошибка: Один или несколько агентов не созданы. Проверьте шаблоны агентов!")
        return None, None, None, None
    # Задача 1: Инициализация проекта
    init_task = Task(
        description="""Инициализируй новый проект GopiAI-CrewAI интеграции.
        
        Выполни следующие действия:
        1. Отправь уведомление о запуске проекта
        2. Сохрани в память информацию о проекте (категория: "project")
        3. Проверь статус системы
        4. Создай список задач для команды
        
        Ключевая информация для сохранения:
        - Название: "GopiAI-CrewAI Integration Demo"
        - Дата запуска: текущая дата
        - Цель: демонстрация возможностей интеграции
        - Участники: координатор, аналитик, исследователь""",
        expected_output="Отчет об инициализации проекта с уведомлениями",
        agent=coordinator
    )
    
    # Задача 2: Исследование информации
    research_task = Task(
        description="""Проведи исследование о возможностях интеграции GopiAI-CrewAI.
        
        Выполни следующие действия:
        1. Изучи структуру проекта (используй filesystem tool)
        2. Найди и прочитай ключевые файлы документации
        3. Сохрани собранную информацию в память (категория: "research")
        4. Создай краткий отчет о возможностях системы
        5. Уведоми координатора о завершении исследования
        
        Обрати внимание на:
        - Документацию о CrewAI
        - Возможности инструментов
        - Примеры использования
        - Перспективные направления развития""",
        expected_output="Исследовательский отчет о возможностях системы",
        agent=researcher
    )
    
    # Задача 3: Создание документации
    writing_task = Task(
        description="""Создай документацию по улучшенной интеграции GopiAI и CrewAI.
        
        Выполни следующие действия:
        1. Изучи результаты исследования (из задачи исследования)
        2. Структурируй информацию в понятном формате
        3. Создай подробную документацию в формате markdown
        4. Сохрани документацию в файловой системе
        5. Уведоми команду о завершении документации
        
        Документация должна включать:
        - Обзор улучшенной архитектуры
        - Описание системы шаблонов агентов
        - Примеры использования базового класса инструментов
        - Рекомендации по созданию новых агентов
        - Лучшие практики интеграции""",
        expected_output="Полная документация по улучшенной интеграции",
        agent=writer,
        context=[research_task]  # Используем результаты предыдущей задачи
    )
    
    # Задача 4: Разработка улучшений
    coding_task = Task(
        description="""Разработай улучшения для системы интеграции GopiAI-CrewAI.
        
        Выполни следующие действия:
        1. Изучи существующий код инструментов
        2. Разработай прототип нового инструмента для работы с аудио
        3. Создай демонстрационный пример использования
        4. Сохрани код в файловой системе
        5. Уведоми команду о завершении разработки
        
        Требования к инструменту:
        - Наследование от базового класса GopiAIBaseTool
        - Поддержка записи и воспроизведения аудио
        - Интеграция с существующей системой
        - Документирование кода
        - Обработка ошибок""",
        expected_output="Код нового инструмента с демонстрацией",
        agent=coder
    )
    
    print(f"✅ Создано {len([init_task, research_task, writing_task, coding_task])} задач")
    return init_task, research_task, writing_task, coding_task

def run_simple_demo():
    """Простая демонстрация с одним агентом"""
    print("🚀 === ПРОСТАЯ ДЕМОНСТРАЦИЯ ===")
    
    try:
        # Создаем LLM через новый AI Router
        ai_router_llm = AIRouterLLM()
        llm = ai_router_llm.get_llm_instance()
        provider_name = "GopiAI Google Router"
        print(f"🤖 Используется: {provider_name}")
        
        # Простой агент с коммуникацией
        demo_agent = Agent(
            role='Demo Assistant',
            goal='Продемонстрировать работу GopiAI инструментов',
            backstory='Ты демонстрационный ассистент для показа возможностей системы.',
            tools=[GopiAICommunicationTool(), GopiAIMemoryTool()],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Простая задача
        demo_task = Task(
            description="""Выполни демонстрацию возможностей GopiAI:
            
            1. Отправь приветственное уведомление
            2. Сохрани информацию о демонстрации в память
            3. Отправь уведомление о завершении
            
            Информация для сохранения:
            - Тема: "GopiAI Demo"
            - Статус: "Успешно выполнено"
            - Время: текущее время""",
            expected_output="Отчет о выполнении демонстрации",
            agent=demo_agent
        )
        
        # Создаем crew
        demo_crew = Crew(**{
            "agents": [demo_agent],
            "tasks": [demo_task],
            "verbose": True
        })
        
        # Запускаем
        print("⚡ Запуск простой демонстрации...")
        result = demo_crew.kickoff()
        
        print(f"✅ Простая демонстрация завершена!")
        print(f"📋 Результат: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка простой демонстрации: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_advanced_demo():
    """Продвинутая демонстрация с несколькими агентами"""
    print("🚀 === ПРОДВИНУТАЯ ДЕМОНСТРАЦИЯ ===")
    
    try:
        # Создаем LLM через новый AI Router
        ai_router_llm = AIRouterLLM()
        llm = ai_router_llm.get_llm_instance()
        provider_name = "GopiAI Google Router"
        print(f"🤖 Используется: {provider_name}")
        coordinator, researcher, writer, coder = create_demo_agents(llm)
        agents = [coordinator, researcher, writer, coder]
        agents = [a for a in agents if a is not None]
        # Создаем задачи
        init_task, research_task, writing_task, coding_task = create_demo_tasks(
            coordinator, researcher, writer, coder
        )
        tasks = [init_task, research_task, writing_task, coding_task]
        tasks = [t for t in tasks if t is not None]
        # Создаем crew
        advanced_crew = Crew(**{
            "agents": agents,
            "tasks": tasks,
            "verbose": True
        })
        # Запускаем
        print("⚡ Запуск продвинутой демонстрации...")
        try:
            result = advanced_crew.kickoff()
        except Exception as e:
            print(f"[ERROR] Crew.kickoff() exception: {e}")
            import traceback
            traceback.print_exc()
            raise
        print(f"✅ Продвинутая демонстрация завершена!")
        print(f"📋 Итоговый результат: {result}")
        return True
    except Exception as e:
        print(f"❌ Ошибка продвинутой демонстрации: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция"""
    print("🎯 === GOPIAI-CREWAI ADVANCED INTEGRATION ===")
    print(f"⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Проверяем окружение
    if not check_environment():
        print("❌ Проблемы с окружением, остановка")
        return
    
    # Тестируем инструменты
    if not test_all_tools():
        print("❌ Критические проблемы с инструментами, остановка")
        return
    
    # Вместо input — всегда режим 2
    mode = "2"
    print("Выбран режим: 2 (Продвинутая демонстрация)")
    if mode == "1":
        run_simple_demo()
    elif mode == "2":
        run_advanced_demo()
    # elif mode == "3":
    #     run_tools_tests()
    # elif mode == "4":
    #     show_templates()
    else:
        print("❌ Неизвестный режим!")

# Пример: учёт использования моделей (rpm/tpm)
current_llm_usage = {}

# Пример функции для CrewAI/агентов: выбор модели и генерация ответа через txtai+LLM
# (можно вызывать из агента или инструмента)
def crewai_rag_query(query, txtai_index, llm, task_type="dialog"):
    model_id = select_llm_model(task_type, current_llm_usage)
    if not model_id:
        return "Все лимиты LLM исчерпаны, попробуйте позже."
    # Здесь llm_call_func должен быть функцией, принимающей prompt и model (id)
    # Например, можно сделать обёртку вокруг LLMLoggerWrapper или напрямую llm.call
    def llm_call_func(prompt, model=None):
        # Здесь пример для LLMLoggerWrapper (если он поддерживает model)
        # Если нет — доработать обёртку
        return llm.call(prompt, model=model) if model else llm.call(prompt)
    answer = rag_answer(query, txtai_index, llm_call_func, model_id)
    # Учёт использования (упрощённо)
    current_llm_usage.setdefault(model_id, {"rpm": 0, "tpm": 0})
    current_llm_usage[model_id]["rpm"] += 1
    # tpm можно считать по длине prompt+answer
    return answer

if __name__ == "__main__":
    main()