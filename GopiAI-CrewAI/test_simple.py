#!/usr/bin/env python3
"""
🤖 Простой тест CrewAI с Groq
Используем стандартный подход CrewAI без кастомного LLM
"""

import os
import sys
from pathlib import Path

# Добавляем пути для импорта
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent))  # GOPI_AI_MODULES
sys.path.append(str(current_dir))  # GopiAI-CrewAI

# Загружаем переменные окружения
from dotenv import load_dotenv
env_path = current_dir.parent / '.env'
print(f"🔍 Загружаем .env из: {env_path}")
if env_path.exists():
    load_dotenv(env_path, override=True)
    print("✅ .env файл найден")
else:
    print("❌ .env файл не найден")

def test_with_standard_groq():
    """Тест с стандартным ChatGroq"""
    print("🧪 Тест с стандартным ChatGroq...")
    
    try:
        from langchain_groq import ChatGroq
        from crewai import Agent, Task, Crew
        
        # Создаем стандартный Groq LLM
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile",  # Обновленная модель
            temperature=0.7,
            max_tokens=1000
        )
        
        print("✅ ChatGroq LLM создан")
        
        # Создаем агента
        agent = Agent(
            role="Помощник",
            goal="Дать краткий ответ",
            backstory="Ты дружелюбный помощник",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Создаем задачу
        task = Task(
            description="Скажи 'Привет от CrewAI!' и объясни в одном предложении что такое CrewAI",
            expected_output="Краткое приветствие и объяснение",
            agent=agent
        )
        
        # Создаем crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        print("🚀 Запуск crew...")
        result = crew.kickoff()
        
        print(f"✅ Результат: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_groq():
    """Простой тест Groq API"""
    print("🔧 Простой тест Groq API...")
    
    try:
        from langchain_groq import ChatGroq
        
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile"
        )
        
        response = llm.invoke("Привет! Скажи кратко: как дела?")
        print(f"✅ Простой Groq ответ: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Простой тест не прошел: {e}")
        return False

def main():
    """Основная функция"""
    print("🎯 === ПРОСТОЙ CREWAI-GROQ ТЕСТ ===")
    
    # Проверяем ключи
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key or not groq_key.startswith("gsk_"):
        print("❌ GROQ_API_KEY не найден")
        return
    
    print(f"✅ GROQ_API_KEY найден: {groq_key[:12]}...")
    
    # Простой тест
    if not test_simple_groq():
        print("❌ Простой тест не прошел")
        return
    
    # Тест с CrewAI
    if not test_with_standard_groq():
        print("❌ CrewAI тест не прошел")
        return
    
    print("🎉 Все тесты прошли!")

if __name__ == "__main__":
    main()