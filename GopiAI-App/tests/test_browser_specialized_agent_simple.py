#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Простое тестирование специализированного браузерного агента.

Скрипт для тестирования специализированного браузерного агента без графического интерфейса.
"""

import sys
import os
import asyncio
from gopiai.core.logging import get_logger
logger = get_logger().logger
from typing import Optional, Dict, Any

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = get_logger().logger

# Импортируем необходимые модули
from gopiai.app.agent.browser_specialized_agent import BrowserSpecializedAgent
from gopiai.app.utils.browsermcp_setup import setup_browsermcp

async def test_browser_specialized_agent():
    """Тестирует специализированного браузерного агента."""
    logger.info("Начало тестирования специализированного браузерного агента")
    
    # Настраиваем BrowserMCP
    logger.info("Настройка BrowserMCP...")
    try:
        result = await setup_browsermcp()
        if result:
            logger.info("BrowserMCP успешно настроен")
        else:
            logger.warning("Не удалось настроить BrowserMCP, но продолжаем тест")
    except Exception as e:
        logger.error(f"Ошибка при настройке BrowserMCP: {str(e)}")
        logger.warning("Продолжаем тест без BrowserMCP")
    
    # Создаем агента
    logger.info("Создание агента...")
    agent = BrowserSpecializedAgent(preferred_tool="auto")
    
    # Устанавливаем контекст
    logger.info("Установка контекста...")
    await agent.set_context({
        "task": "Работа с браузером",
        "relevant_files": {
            "browser_specialized_agent.py": {
                "summary": "Специализированный агент для работы с браузером"
            }
        }
    })
    
    # Получаем состояние агента
    logger.info("Получение состояния агента...")
    state = agent.get_current_state()
    logger.info(f"Состояние агента: {state}")
    
    # Обрабатываем запрос
    logger.info("Обработка запроса...")
    query = "Какие возможности у браузерного агента?"
    result = await agent.process(query)
    logger.info(f"Результат обработки запроса: {result}")
    
    # Очищаем ресурсы
    logger.info("Очистка ресурсов...")
    await agent.cleanup()
    
    logger.info("Тестирование завершено")

def main():
    """Основная функция."""
    asyncio.run(test_browser_specialized_agent())

if __name__ == "__main__":
    main()
