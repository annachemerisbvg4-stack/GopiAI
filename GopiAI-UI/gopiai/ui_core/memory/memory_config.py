"""
Конфигурация памяти для GopiAI UI

Этот модуль определяет пути к файлам памяти, используемые в UI-клиенте.
Пути синхронизированы с серверной частью (GopiAI-CrewAI).
"""

import os
from pathlib import Path

# Определяем путь к корню проекта GopiAI-CrewAI
CREWAI_ROOT = Path(os.path.abspath(os.path.join(
    os.path.dirname(__file__),  # текущая директория (memory)
    "../../../..",              # поднимаемся на 4 уровня вверх (до GOPI_AI_MODULES)
    "GopiAI-CrewAI"             # переходим в директорию GopiAI-CrewAI
)))

# Используем те же пути, что и в серверной части
MEMORY_BASE_DIR = CREWAI_ROOT / "memory"
CHATS_FILE_PATH = MEMORY_BASE_DIR / "chats.json"
VECTOR_INDEX_PATH = MEMORY_BASE_DIR / "vectors"

# Проверяем существование директорий
if not MEMORY_BASE_DIR.exists():
    raise FileNotFoundError(f"Директория памяти не найдена: {MEMORY_BASE_DIR}")

if __name__ == "__main__":
    print("--- Memory Configuration ---")
    print(f"CrewAI Root: {CREWAI_ROOT}")
    print(f"Memory Directory: {MEMORY_BASE_DIR}")
    print(f"Chats File: {CHATS_FILE_PATH}")
    print(f"Vector Index: {VECTOR_INDEX_PATH}")
