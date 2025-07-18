#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для автоматического исправления проблем с чатом в GopiAI
Выявленные проблемы:
1. Отсутствие модели spaCy для русского языка
2. Ошибка инициализации embeddings из-за отсутствия model_type в config.json
3. Проблемы с кодировкой в логах
"""

import os
import sys
import json
import logging
import subprocess
import io
from pathlib import Path

# Настройка логирования с явным указанием кодировки UTF-8 для консоли
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('fix_chat_issues.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Пути к файлам и директориям
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
MEMORY_VECTORS_DIR = BASE_DIR / "GopiAI-CrewAI" / "memory" / "vectors"
CONFIG_JSON_PATH = MEMORY_VECTORS_DIR / "config.json"

def check_spacy_model():
    """Проверка и установка модели spaCy для русского языка"""
    logger.info("Проверка наличия модели spaCy для русского языка...")
    
    try:
        # Проверяем, установлена ли модель
        result = subprocess.run(
            [sys.executable, "-c", "import spacy; nlp = spacy.load('ru_core_news_sm'); print('Model loaded successfully')"],
            capture_output=True,
            text=True
        )
        
        if "Model loaded successfully" in result.stdout:
            logger.info("Модель spaCy для русского языка уже установлена")
            return True
        else:
            logger.warning("Модель spaCy для русского языка не установлена. Устанавливаем...")
            
            # Устанавливаем модель
            install_result = subprocess.run(
                [sys.executable, "-m", "spacy", "download", "ru_core_news_sm"],
                capture_output=True,
                text=True
            )
            
            if install_result.returncode == 0:
                logger.info("Модель spaCy для русского языка успешно установлена")
                return True
            else:
                logger.error(f"Ошибка установки модели spaCy: {install_result.stderr}")
                return False
    
    except Exception as e:
        logger.error(f"Ошибка при проверке/установке модели spaCy: {e}")
        return False

def fix_vectors_config():
    """Исправление config.json для векторной базы данных"""
    logger.info("Проверка и исправление конфигурации векторной базы данных...")
    
    try:
        if not CONFIG_JSON_PATH.exists():
            logger.error(f"Файл конфигурации не найден: {CONFIG_JSON_PATH}")
            return False
        
        # Читаем текущую конфигурацию
        with open(CONFIG_JSON_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Проверяем наличие model_type
        if 'model_type' not in config:
            logger.warning("В config.json отсутствует ключ 'model_type'. Добавляем...")
            
            # Добавляем model_type (используем sentence-transformers/nli-mpnet-base-v2 как стандартную модель)
            config['model_type'] = 'sentence-transformers/nli-mpnet-base-v2'
            
            # Сохраняем обновленную конфигурацию
            with open(CONFIG_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info("Конфигурация векторной базы данных успешно обновлена")
            return True
        else:
            logger.info(f"Ключ 'model_type' уже присутствует в config.json: {config['model_type']}")
            return True
    
    except Exception as e:
        logger.error(f"Ошибка при исправлении конфигурации векторной базы данных: {e}")
        return False

def check_encoding_settings():
    """Проверка настроек кодировки в файлах логирования"""
    logger.info("Проверка настроек кодировки в файлах логирования...")
    
    try:
        # Проверяем файлы логгеров
        logger_files = [
            BASE_DIR / "GopiAI-UI" / "gopiai" / "ui" / "utils" / "logging_config.py",
            BASE_DIR / "GopiAI-CrewAI" / "utils" / "logging_config.py"
        ]
        
        for log_file in logger_files:
            if not log_file.exists():
                logger.warning(f"Файл настроек логирования не найден: {log_file}")
                continue
            
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем, указана ли кодировка UTF-8 для FileHandler
            if 'encoding' not in content or 'utf-8' not in content.lower():
                logger.warning(f"В файле {log_file} не указана кодировка UTF-8 для FileHandler")
                
                # Заменяем FileHandler на FileHandler с явным указанием кодировки
                if 'FileHandler(' in content:
                    new_content = content.replace(
                        'FileHandler(',
                        "FileHandler(encoding='utf-8', "
                    )
                    
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    logger.info(f"Файл {log_file} обновлен с указанием кодировки UTF-8")
            else:
                logger.info(f"В файле {log_file} уже указана кодировка UTF-8")
        
        return True
    
    except Exception as e:
        logger.error(f"Ошибка при проверке настроек кодировки: {e}")
        return False

def backup_file(file_path):
    """Создание резервной копии файла"""
    try:
        backup_path = f"{file_path}.bak"
        if os.path.exists(file_path):
            with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            logger.info(f"Создана резервная копия файла: {backup_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Ошибка при создании резервной копии: {e}")
        return False

def main():
    """Основная функция скрипта"""
    logger.info("=== Запуск скрипта исправления проблем с чатом GopiAI ===")
    
    # Создаем резервные копии важных файлов
    if CONFIG_JSON_PATH.exists():
        backup_file(CONFIG_JSON_PATH)
    
    # Шаг 1: Проверка и установка модели spaCy
    spacy_result = check_spacy_model()
    
    # Шаг 2: Исправление конфигурации векторной базы данных
    vectors_result = fix_vectors_config()
    
    # Шаг 3: Проверка настроек кодировки
    encoding_result = check_encoding_settings()
    
    # Выводим итоговый результат
    logger.info("=== Результаты исправления проблем ===")
    logger.info(f"1. Модель spaCy для русского языка: {'[OK]' if spacy_result else '[FAIL]'}")
    logger.info(f"2. Конфигурация векторной базы данных: {'[OK]' if vectors_result else '[FAIL]'}")
    logger.info(f"3. Настройки кодировки: {'[OK]' if encoding_result else '[FAIL]'}")
    
    if spacy_result and vectors_result and encoding_result:
        logger.info("[SUCCESS] Все проблемы успешно исправлены!")
        logger.info("Рекомендуется перезапустить приложение GopiAI для применения изменений")
        return True
    else:
        logger.warning("[WARNING] Не все проблемы были исправлены. Проверьте лог для деталей.")
        return False

if __name__ == "__main__":
    main()
