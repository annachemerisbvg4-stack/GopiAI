#!/usr/bin/env python3
"""
🤖 Демонстрация ассистента с доступом к файловой системе
Показывает, как предоставить ассистенту полный доступ к файловой системе
"""

import sys
import os
import json
from pathlib import Path

# Добавляем путь к модулям GopiAI
sys.path.append('GopiAI/GopiAI-CrewAI')

from crewai import Agent, Task, Crew
from tools.gopiai_integration import (
    GopiAIFileSystemTool, 
    TerminalTool, 
    GopiAIWebSearchTool,
    GopiAIWebViewerTool
)

def create_filesystem_assistant():
    """Создает ассистента с полным доступом к файловой системе"""
    
    # Создаем все основные инструменты
    tools = [
        GopiAIFileSystemTool(),  # Основной инструмент файловой системы
        TerminalTool(),          # Выполнение команд
        GopiAIWebSearchTool(),   # Поиск в интернете
        GopiAIWebViewerTool(),   # Просмотр веб-страниц
    ]
    
    assistant = Agent(
        role='File System Assistant',
        goal='Помочь пользователю с управлением файлами, анализом данных и организацией проектов',
        backstory="""Я - специализированный ассистент с полным доступом к файловой системе.
        
        Мои возможности:
        📁 ФАЙЛОВАЯ СИСТЕМА:
        - Чтение и запись файлов любых типов
        - Создание и удаление файлов и папок
        - Поиск файлов по шаблонам
        - Работа с JSON, CSV, архивами
        - Создание резервных копий
        - Анализ структуры проектов
        
        💻 ТЕРМИНАЛ:
        - Выполнение системных команд
        - Установка пакетов
        - Управление процессами
        - Работа с Git
        
        🌐 ИНТЕРНЕТ:
        - Поиск информации
        - Загрузка файлов
        - Анализ веб-страниц
        
        Я всегда работаю безопасно и спрашиваю подтверждение перед выполнением потенциально опасных операций.""",
        tools=tools,
        verbose=True,
        allow_delegation=False
    )
    
    return assistant

def demo_file_operations():
    """Демонстрация операций с файлами"""
    print("\n🔧 Демонстрация операций с файлами")
    print("=" * 50)
    
    # Создаем ассистента
    assistant = create_filesystem_assistant()
    
    # Создаем задачи для демонстрации
    tasks = [
        Task(
            description="""Выполни следующие операции с файловой системой:
            1. Создай папку 'demo_project' в текущей директории
            2. Создай в ней файл 'README.md' с описанием проекта
            3. Создай файл 'config.json' с базовой конфигурацией
            4. Создай файл 'data.csv' с тестовыми данными
            5. Покажи структуру созданного проекта
            6. Создай резервную копию всех файлов
            """,
            agent=assistant,
            expected_output="Отчет о выполненных операциях с файлами"
        ),
        
        Task(
            description="""Проанализируй текущую директорию проекта:
            1. Найди все Python файлы
            2. Подсчитай общее количество строк кода
            3. Найди файлы больше 1KB
            4. Создай отчет в формате JSON
            """,
            agent=assistant,
            expected_output="JSON отчет об анализе проекта"
        )
    ]
    
    # Создаем команду
    crew = Crew(
        agents=[assistant],
        tasks=tasks,
        verbose=True
    )
    
    print("🚀 Запуск демонстрации...")
    result = crew.kickoff()
    
    print("\n✅ Демонстрация завершена!")
    print(f"Результат: {result}")

def interactive_assistant():
    """Интерактивный режим работы с ассистентом"""
    print("\n🤖 Интерактивный ассистент файловой системы")
    print("=" * 50)
    print("Введите 'help' для списка команд или 'exit' для выхода")
    
    assistant = create_filesystem_assistant()
    
    while True:
        try:
            user_input = input("\n👤 Вы: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'выход']:
                print("👋 До свидания!")
                break
            
            if user_input.lower() == 'help':
                print("""
📋 Доступные команды:
- list [путь] - показать содержимое папки
- read [файл] - прочитать файл
- write [файл] [текст] - записать в файл
- find [шаблон] - найти файлы
- info [файл] - информация о файле
- backup [файл] - создать резервную копию
- search [файл] [текст] - найти текст в файле
- tree [путь] - показать дерево папок
- help - эта справка
- exit - выход
                """)
                continue
            
            if not user_input:
                continue
            
            # Создаем задачу для ассистента
            task = Task(
                description=f"Выполни запрос пользователя: {user_input}",
                agent=assistant,
                expected_output="Результат выполнения запроса"
            )
            
            crew = Crew(
                agents=[assistant],
                tasks=[task],
                verbose=False
            )
            
            print("🤖 Ассистент работает...")
            result = crew.kickoff()
            print(f"🤖 Ассистент: {result}")
            
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def test_specific_operations():
    """Тест специфических операций файловой системы"""
    print("\n🧪 Тест специфических операций")
    print("=" * 50)
    
    # Прямое тестирование инструмента
    fs_tool = GopiAIFileSystemTool()
    
    # Создаем тестовые данные
    test_data = {
        "project": "GopiAI Demo",
        "version": "1.0.0",
        "features": ["filesystem", "terminal", "web_search"],
        "config": {
            "debug": True,
            "max_files": 1000
        }
    }
    
    print("1. Создание JSON файла...")
    result = fs_tool._run(
        action="write_json", 
        path="test_config.json",
        json_data=test_data
    )
    print(f"   {result}")
    
    print("2. Чтение JSON файла...")
    result = fs_tool._run(action="read_json", path="/workspace/project/test_config.json")
    print(f"   {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    print("3. Создание CSV файла...")
    csv_data = [
        {"name": "file1.txt", "size": 1024, "type": "text"},
        {"name": "file2.py", "size": 2048, "type": "python"},
        {"name": "file3.json", "size": 512, "type": "json"}
    ]
    result = fs_tool._run(
        action="write_csv",
        path="/workspace/project/test_files.csv",
        csv_data=csv_data,
        fieldnames=["name", "size", "type"]
    )
    print(f"   {result}")
    
    print("4. Поиск файлов...")
    result = fs_tool._run(
        action="find",
        path="/workspace/project",
        pattern="*.py",
        recursive=True
    )
    print(f"   Найдено Python файлов: {len(result)}")
    
    print("5. Создание архива...")
    files_to_zip = [
        "/workspace/project/test_config.json",
        "/workspace/project/test_files.csv"
    ]
    result = fs_tool._run(
        action="create_zip",
        path="/workspace/project/test_archive.zip",
        files=files_to_zip
    )
    print(f"   {result}")
    
    print("6. Хеширование файла...")
    result = fs_tool._run(
        action="hash",
        path="/workspace/project/test_config.json",
        algorithm="sha256"
    )
    print(f"   SHA256: {result[:16]}...")
    
    # Очистка
    for file in ["test_config.json", "test_files.csv", "test_archive.zip"]:
        try:
            os.remove(f"/workspace/project/{file}")
        except OSError as e:
            print(f"   Не удалось удалить файл {file}: {e}")
    
    print("✅ Тест завершен!")

def main():
    """Главная функция"""
    print("🚀 GopiAI - Ассистент с доступом к файловой системе")
    print("=" * 60)
    
    print("Выберите режим работы:")
    print("1. Демонстрация операций с файлами")
    print("2. Интерактивный ассистент")
    print("3. Тест специфических операций")
    print("4. Показать возможности инструментов")
    
    choice = input("\nВведите номер (1-4): ").strip()
    
    if choice == "1":
        demo_file_operations()
    elif choice == "2":
        interactive_assistant()
    elif choice == "3":
        test_specific_operations()
    elif choice == "4":
        show_tool_capabilities()
    else:
        print("❌ Неверный выбор")

def show_tool_capabilities():
    """Показать возможности инструментов"""
    print("\n🔧 Возможности инструментов GopiAI")
    print("=" * 50)
    
    fs_tool = GopiAIFileSystemTool()
    
    print("📁 GopiAI FileSystem Tool:")
    print("   Основные операции:")
    print("   - read, write, append - работа с содержимым файлов")
    print("   - list, exists, mkdir, remove - управление файлами и папками")
    print("   - copy, move - копирование и перемещение")
    print("   - find - поиск файлов по шаблонам")
    print("   - info - получение метаданных файлов")
    print("   - hash - вычисление хешей")
    print("   - backup - создание резервных копий")
    print("   - tree - отображение структуры папок")
    
    print("\n   Специальные форматы:")
    print("   - read_json, write_json - работа с JSON")
    print("   - read_csv, write_csv - работа с CSV")
    print("   - create_zip, extract_zip, list_zip - архивы")
    
    print("\n   Анализ текста:")
    print("   - search_text - поиск текста в файлах")
    print("   - replace_text - замена текста")
    print("   - count_lines - подсчет строк")
    print("   - compare - сравнение файлов")
    
    print("\n💻 Terminal Tool:")
    print("   - Выполнение системных команд")
    print("   - Безопасный режим работы")
    print("   - Логирование в UI")
    
    print("\n🌐 Web Tools:")
    print("   - Поиск в интернете (DuckDuckGo, Google)")
    print("   - Просмотр веб-страниц")
    print("   - Извлечение контента")
    
    print("\n✅ Все инструменты готовы к использованию!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()