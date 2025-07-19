"""
Memory Configuration for GopiAI UI
Локальная конфигурация памяти (заменяет удаленный ui_core)
"""

import os
from pathlib import Path

# Базовая директория для хранения данных памяти
MEMORY_BASE_DIR = Path.home() / ".gopiai" / "memory"

# Файл для хранения чатов
CHATS_FILE_PATH = MEMORY_BASE_DIR / "chats.json"

# Путь к векторному индексу
VECTOR_INDEX_PATH = MEMORY_BASE_DIR / "vector_index"

# Создаем директории если они не существуют
MEMORY_BASE_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_INDEX_PATH.mkdir(parents=True, exist_ok=True)

# Инициализируем файл чатов если он не существует
if not CHATS_FILE_PATH.exists():
    import json
    with open(CHATS_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump([], f)
