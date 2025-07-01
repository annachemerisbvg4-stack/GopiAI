"""
Конфигурация приложения.
"""

import json
import os
from pathlib import Path

# Корневая директория проекта
PROJECT_ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Рабочая директория
WORKSPACE_ROOT = PROJECT_ROOT / "workspace"

# Создаем рабочую директорию, если она не существует
WORKSPACE_ROOT.mkdir(exist_ok=True)

# Конфигурация по умолчанию
DEFAULT_CONFIG = {
    "app": {
        "name": "GopiAI",
        "version": "0.1.0",
        "debug": True
    },
    "ui": {
        "theme": "dark",
        "language": "ru"
    },
    "agents": {
        "default": "reactive"
    },
    "tools": {
        "enabled": ["browser", "code", "web_search"]
    }
}

# Путь к файлу конфигурации
CONFIG_PATH = PROJECT_ROOT / "config.json"

# Загружаем конфигурацию из файла или используем значения по умолчанию
def load_config():
    """Загружает конфигурацию из файла."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
    return DEFAULT_CONFIG

# Сохраняем конфигурацию в файл
def save_config(config_data):
    """Сохраняет конфигурацию в файл."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении конфигурации: {e}")
        return False

# Загружаем конфигурацию
config = load_config()
# Конфигурация для reasoning агентов
reasoning_config = {
    "enabled": True,
    "temperature": 0.7,
    "max_tokens": 2000
}
