# Проверка импортов для CrewAI API сервера
import os
import sys

# Путь к файлу для записи
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imports_check.txt")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(f"Python версия: {sys.version}\n")
    f.write(f"Путь к Python: {sys.executable}\n")
    f.write(f"Текущая директория: {os.getcwd()}\n\n")
    
    # Список модулей для проверки
    modules = [
        "flask", "flask_cors", "txtai", "faiss", "numpy", "torch", 
        "sentence_transformers", "langchain", "crewai", "json", "os", "sys",
        "threading", "time", "datetime", "pathlib", "logging"
    ]
    
    for module in modules:
        try:
            __import__(module)
            f.write(f"✅ Модуль {module} успешно импортирован\n")
        except ImportError as e:
            f.write(f"❌ Ошибка импорта модуля {module}: {e}\n")
        except Exception as e:
            f.write(f"⚠️ Другая ошибка при импорте {module}: {e}\n")
    
    # Проверка импорта локальных модулей
    local_modules = [
        "rag_system", "rag_config", "smart_delegator", "chat_async_handler"
    ]
    
    f.write("\nПроверка локальных модулей:\n")
    for module in local_modules:
        try:
            __import__(module)
            f.write(f"✅ Локальный модуль {module} успешно импортирован\n")
        except ImportError as e:
            f.write(f"❌ Ошибка импорта локального модуля {module}: {e}\n")
        except Exception as e:
            f.write(f"⚠️ Другая ошибка при импорте {module}: {e}\n")
    
print(f"Результаты проверки импортов записаны в {file_path}")
