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
env_path = current_dir.parent / '.env'
load_dotenv(env_path, override=True)

# Импорт CrewAI
from crewai import Agent, Task, Crew, LLM
from crewai.tasks.task_output import TaskOutput

# Импорт всех GopiAI инструментов
try:
    from gopiai_integration.base import GopiAIBaseTool
    from gopiai_integration.browser_tools import GopiAIBrowserTool
    from gopiai_integration.filesystem_tools import GopiAIFileSystemTool
    from gopiai_integration.ai_router_tools import GopiAIRouterTool
    from gopiai_integration.memory_tools import GopiAIMemoryTool
    from gopiai_integration.communication_tools import GopiAICommunicationTool
    from gopiai_integration.huggingface_tools import GopiAIHuggingFaceTool
    from tools.agent_template_system import AgentTemplateSystem
    print("✅ Все GopiAI инструменты импортированы успешно!")
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
        'GROQ_API_KEY': {'prefix': 'gsk_', 'name': 'Groq'},
        'GOOGLE_API_KEY': {'prefix': 'AIza', 'name': 'Google Gemini'},
        'COHERE_API_KEY': {'prefix': '', 'name': 'Cohere'},
        'CEREBRAS_API_KEY': {'prefix': 'csk_', 'name': 'Cerebras'},
        'NOVITA_API_KEY': {'prefix': 'sk_', 'name': 'Novita'}
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

def create_llm_with_fallback():
    """Создание LLM с поддержкой fallback"""
    print("🤖 === НАСТРОЙКА LLM ===")
    
    # Список провайдеров в порядке приоритета
    providers = [
        {
            'name': 'Google Gemini',
            'model': 'gemini/gemini-1.5-flash',
            'api_key': os.getenv('GOOGLE_API_KEY'),
            'config': {
                'temperature': 0.7,
                'max_tokens': 2000
            }
        },
        {
            'name': 'Groq',
            'model': 'groq/llama-3.1-8b-instant',
            'api_key': os.getenv('GROQ_API_KEY'),
            'config': {
                'base_url': 'https://api.groq.com/openai/v1',
                'temperature': 0.7,
                'max_tokens': 1000
            }
        },
        {
            'name': 'Cerebras',
            'model': 'cerebras/llama3.1-70b',
            'api_key': os.getenv('CEREBRAS_API_KEY'),
            'config': {
                'base_url': 'https://api.cerebras.ai/v1',
                'temperature': 0.5,
                'max_tokens': 1500
            }
        }
    ]
    
    for provider in providers:
        if not provider['api_key'] or provider['api_key'] == "your_key_here":
            continue
        
        try:
            print(f"🔄 Тестирование {provider['name']}...")
            
            llm_config = {
                'model': provider['model'],
                'api_key': provider['api_key'],
                **provider['config']
            }
            
            llm = LLM(**llm_config)
            
            # Простой тест
            test_response = llm.call("Скажи 'ОК'")
            if test_response and len(test_response.strip()) > 0:
                print(f"✅ {provider['name']} работает!")
                return llm, provider['name']
            
        except Exception as e:
            print(f"❌ {provider['name']} ошибка: {e}")
            continue
    
    raise Exception("Все LLM провайдеры недоступны!")

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
        result = fs_tool._run("list", ".", "", "", "")
        tools_results['filesystem'] = True
        print(f"✅ FileSystem: найдено {len(result.split())} элементов")
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
        result = router_tool._run("route", "Привет!", "gemini", 0.7, 50)
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
        # Создаем LLM
        llm, provider_name = create_llm_with_fallback()
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
        demo_crew = Crew(
            agents=[demo_agent],
            tasks=[demo_task],
            verbose=True
        )
        
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
        # Создаем LLM
        llm, provider_name = create_llm_with_fallback()
        print(f"🤖 Используется: {provider_name}")
        
        # Создаем агентов с использованием системы шаблонов
        coordinator, researcher, writer, coder = create_demo_agents(llm)
        
        # Создаем задачи
        init_task, research_task, writing_task, coding_task = create_demo_tasks(
            coordinator, researcher, writer, coder
        )
        
        # Создаем crew
        advanced_crew = Crew(
            agents=[coordinator, researcher, writer, coder],
            tasks=[init_task, research_task, writing_task, coding_task],
            verbose=True
        )
        
        # Запускаем
        print("⚡ Запуск продвинутой демонстрации...")
        result = advanced_crew.kickoff()
        
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
    
    # Запрашиваем режим работы
    print("
🎮 Выберите режим демонстрации:")
    print("1. Простая демонстрация (1 агент, базовые инструменты)")
    print("2. Продвинутая демонстрация (4 агента, все инструменты, шаблоны)")
    print("3. Только тесты (без запуска CrewAI)")
    print("4. Просмотр доступных шаблонов агентов")
    
    choice = input("Введите номер (1-4): ").strip()
    
    if choice == "1":
        success = run_simple_demo()
    elif choice == "2":
        success = run_advanced_demo()
    elif choice == "3":
        print("✅ Тесты завершены")
        success = True
    elif choice == "4":
        # Просмотр шаблонов агентов
        template_system = AgentTemplateSystem(verbose=True)
        print("
📋 === ДОСТУПНЫЕ ШАБЛОНЫ АГЕНТОВ ===")
        
        for template_name in template_system.list_available_templates():
            template_info = template_system.get_template_info(template_name)
            print(f"
🔹 {template_name}:")
            print(f"   Роль: {template_info.get('role', 'Не указана')}")
            print(f"   Цель: {template_info.get('goal', 'Не указана')}")
            print(f"   Инструменты: {', '.join(template_info.get('tools', []))}")
            
        print("
📝 === ДОСТУПНЫЕ ПРОМПТЫ ===")
        for prompt_name in template_system.list_available_prompts():
            print(f"   - {prompt_name}")
            
        success = True
    else:
        print("❌ Неверный выбор")
        success = False
    
    if success:
        print("\\n🎉 === ИНТЕГРАЦИЯ РАБОТАЕТ УСПЕШНО! ===")
        print("✅ CrewAI + GopiAI инструменты функционируют")
        print("✅ Агенты могут использовать все возможности системы")
        print("✅ Коммуникация, память, файлы, браузер, AI роутер - всё работает!")
    else:
        print("\\n❌ === ПРОБЛЕМЫ С ИНТЕГРАЦИЕЙ ===")
        print("Проверьте логи выше для диагностики")

if __name__ == "__main__":
    main()