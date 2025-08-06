"""
Memory Configuration for GopiAI UI
Локальная конфигурация памяти (заменяет удаленный ui_core)
"""

import os
import logging
from pathlib import Path

# Настраиваем логирование
logger = logging.getLogger(__name__)

# Определяем базовую директорию для хранения данных памяти
# Используем путь, совместимый с CrewAI
if os.name == 'nt':  # Windows
    MEMORY_BASE_DIR = Path("C:/Users/crazy/GOPI_AI_MODULES/GopiAI-CrewAI/memory")
else:  # Linux/Mac
    MEMORY_BASE_DIR = Path.home() / ".gopiai" / "memory"

logger.info(f"Используется директория памяти: {MEMORY_BASE_DIR}")

# Файл для хранения чатов
CHATS_FILE_PATH = MEMORY_BASE_DIR / "chats.json"

# Путь к векторному индексу
VECTOR_INDEX_PATH = MEMORY_BASE_DIR / "vectors"

# Создаем директории если они не существуют
MEMORY_BASE_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_INDEX_PATH.mkdir(parents=True, exist_ok=True)

# Инициализируем файл чатов если он не существует
if not CHATS_FILE_PATH.exists():
    import json
    logger.info(f"Создаем новый файл чатов: {CHATS_FILE_PATH}")
    with open(CHATS_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump([], f)
else:
    logger.info(f"Найден существующий файл чатов: {CHATS_FILE_PATH}")
