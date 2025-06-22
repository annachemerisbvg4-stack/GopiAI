#!/usr/bin/env python3
"""
🚀 Простейший тест CrewAI без кастомных LLM
Минимальная проверка работоспособности
"""

import os
import sys
from pathlib import Path

# Добавляем пути для импорта
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent))

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv(current_dir.parent / '.env')

def test_minimal_crew():
    """Минимальный тест без кастомных настроек"""
    print("🧪 Тест минимального crew...")
    
    try:
        from crewai import Agent, Task, Crew
        
        # Агент БЕЗ кастомного LLM - пусть CrewAI сам выберет
        agent = Agent(
            role="Помощник",
            goal="Ответить на вопрос",
            backstory="Ты помощник.",
            verbose=True
        )
        
        # Простая задача
        task = Task(
            description="Скажи просто 'Привет!'",
            expected_output="Слово 'Привет!'",
            agent=agent
        )
        
        # Crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        print("🚀 Запуск минимального crew...")
        result = crew.kickoff()
        
        print(f"✅ Результат: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_openai():
    """Тест с OpenAI (если есть ключ)"""
    print("🧪 Тест с OpenAI...")
    
    try:
        from crewai import Agent, Task, Crew
        
        # Проверяем ключ OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key or "your_" in openai_key:
            print("⚠️ OpenAI ключ не настроен, пропускаем тест")
            return True
            
        # Устанавливаем переменную для CrewAI
        os.environ["OPENAI_API_KEY"] = openai_key
        
        agent = Agent(
            role="Помощник",
            goal="Ответить на вопрос",
            backstory="Ты умный помощник.",
            verbose=True
        )
        
        task = Task(
            description="Скажи 'Привет от OpenAI!'",
            expected_output="Приветствие",
            agent=agent
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        print("🚀 Запуск OpenAI crew...")
        result = crew.kickoff()
        
        print(f"✅ OpenAI результат: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка OpenAI: {e}")
        return False

def main():
    """Простое тестирование"""
    print("🎯 === ПРОСТОЙ CREWAI ТЕСТ ===")
    
    # Проверяем установку
    try:
        import crewai
        print(f"✅ CrewAI установлен: {crewai.__version__}")
    except ImportError:
        print("❌ CrewAI не установлен!")
        return
    
    # Тест 1: Минимальный
    if test_minimal_crew():
        print("✅ Минимальный тест прошел!")
    else:
        print("❌ Минимальный тест провалился")
        
    # Тест 2: С OpenAI
    if test_with_openai():
        print("✅ OpenAI тест прошел!")
    else:
        print("❌ OpenAI тест провалился")
    
    print("🎉 Тестирование завершено!")

if __name__ == "__main__":
    main()