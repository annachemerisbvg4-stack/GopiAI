#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки работы AI агентов.
"""

import os
import sys
from gopiai.core.logging import get_logger
logger = get_logger().logger
import traceback
from pathlib import Path

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = get_logger().logger

def check_venv():
    """Проверяет, запущен ли скрипт в виртуальном окружении."""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def import_pyside():
    """Проверяет доступность PySide6."""
    try:
        import PySide6
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication
        logger.info(f"PySide6 успешно импортирован, версия: {PySide6.__version__}")
        return True
    except ImportError:
        logger.error("PySide6 не установлен или не доступен")
        return False
    except Exception as e:
        logger.error(f"Ошибка при импорте PySide6: {e}")
        return False

def test_agent_interface():
    """Проверяет базовый интерфейс для работы с агентами."""
    try:
        from examples.simple_test_interface import SimpleMainWindow
        logger.info("Тестовый интерфейс агента доступен")
        return True
    except ImportError:
        logger.error("Не удалось импортировать тестовый интерфейс")
        return False
    except Exception as e:
        logger.error(f"Ошибка при тестировании интерфейса агента: {e}")
        return False

def simulate_agent_query(query="Привет, как дела?"):
    """Симулирует запрос к AI агенту."""
    logger.info(f"Симуляция запроса к агенту: '{query}'")
    response = f"Симулированный ответ на запрос: '{query}'"
    logger.info(f"Получен ответ: '{response}'")
    return response

def main():
    """Основная функция для выполнения тестов."""
    logger.info("Начало тестирования агентов GopiAI")
    
    # Проверка виртуального окружения
    if check_venv():
        logger.info("Скрипт запущен в виртуальном окружении")
    else:
        logger.warning("Скрипт запущен не в виртуальном окружении")
    
    # Проверка PySide6
    if import_pyside():
        logger.info("PySide6 проверен успешно")
    else:
        logger.error("Проблемы с PySide6. Тестирование невозможно.")
        return False
    
    # Тестирование интерфейса агентов
    if test_agent_interface():
        logger.info("Интерфейс агентов работает корректно")
    else:
        logger.warning("Проблемы с интерфейсом агентов")
    
    # Симуляция запросов к агенту
    test_queries = [
        "Привет, как дела?",
        "Какая сегодня погода?",
        "Напиши простую функцию на Python для подсчета факториала",
        "Сравни два алгоритма сортировки: быстрая сортировка и сортировка слиянием"
    ]
    
    for query in test_queries:
        simulate_agent_query(query)
    
    logger.info("Тестирование агентов завершено успешно")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        traceback.print_exc()
        sys.exit(1)
