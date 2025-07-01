import os
import logging
from crewai import LLM

# Настраиваем логирование в файл
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vertex_debug.log'),
        logging.StreamHandler()
    ]
)

# Получаем ключ из окружения
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY не найден в переменных окружения")
    exit(1)

print(f"✅ GEMINI_API_KEY найден: {api_key[:10]}...")

# Пробуем создать LLM и сделать простой запрос
try:
    print("🔄 Создаем LLM экземпляр...")
    llm = LLM(
        model='gemini/gemini-1.5-flash',
        api_key=api_key,
        config={
            'temperature': 0.7,
            'max_tokens': 100
        }
    )
    
    print("🔄 Делаем тестовый запрос...")
    response = llm.call("Просто скажи 'Привет!'")
    
    print(f"✅ Успешный ответ: {response}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    logging.error(f"Ошибка при вызове LLM: {e}")

print("📝 Логи сохранены в vertex_debug.log")
