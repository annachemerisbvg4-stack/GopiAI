#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Пример использования гибридного браузерного агента.

Демонстрирует создание и использование гибридного браузерного агента
для автоматизации браузера с использованием различных инструментов.
"""

import asyncio
from gopiai.core.logging import get_logger
logger = get_logger().logger
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = get_logger().logger

# Импортируем необходимые модули
from gopiai.app.agent.orchestrator import get_orchestrator
from gopiai.app.tool.hybrid_browser_tools import get_hybrid_browser_tools
from gopiai.app.utils.browser_adapters import get_browser_adapter

async def test_browser_adapter():
    """Тестирует браузерный адаптер."""
    logger.info("Тестирование браузерного адаптера")
    
    # Создаем адаптер
    adapter = get_browser_adapter(preferred_tool="auto")
    
    # Инициализируем адаптер
    initialized = await adapter.initialize()
    logger.info(f"Адаптер инициализирован: {initialized}")
    
    if not initialized:
        logger.error("Не удалось инициализировать адаптер")
        return
        
    # Переходим по URL
    url = "https://www.example.com"
    result = await adapter.navigate(url)
    logger.info(f"Результат навигации: {result}")
    
    # Извлекаем содержимое страницы
    result = await adapter.extract_content()
    logger.info(f"Результат извлечения содержимого: {result}")
    
    # Закрываем адаптер
    result = await adapter.close()
    logger.info(f"Результат закрытия адаптера: {result}")

async def test_hybrid_browser_agent():
    """Тестирует гибридного браузерного агента."""
    logger.info("Тестирование гибридного браузерного агента")
    
    # Получаем оркестратор
    orchestrator = get_orchestrator()
    
    # Создаем гибридного браузерного агента
    agent = await orchestrator.create_hybrid_browser_agent(
        agent_id="test_agent",
        task_description="Тестирование браузерного агента",
        preferred_tool="auto"
    )
    
    if not agent:
        logger.error("Не удалось создать агента")
        return
        
    # Выполняем запрос
    result = await agent.process("Перейти на сайт example.com и извлечь заголовок страницы")
    logger.info(f"Результат запроса: {result}")
    
    # Получаем состояние агента
    state = agent.get_current_state()
    logger.info(f"Состояние агента: {state}")
    
    # Очищаем ресурсы агента
    await agent.cleanup()

async def test_browser_tools():
    """Тестирует инструменты для работы с браузером."""
    logger.info("Тестирование инструментов для работы с браузером")
    
    # Получаем инструменты
    tools = get_hybrid_browser_tools()
    
    # Тестируем инструмент навигации
    navigate_tool = tools[0]
    result = await navigate_tool.execute(url="https://www.example.com")
    logger.info(f"Результат навигации: {result}")
    
    # Тестируем инструмент извлечения содержимого
    extract_tool = tools[3]
    result = await extract_tool.execute()
    logger.info(f"Результат извлечения содержимого: {result}")

async def main():
    """Основная функция."""
    logger.info("Запуск примера использования гибридного браузерного агента")
    
    # Тестируем браузерный адаптер
    await test_browser_adapter()
    
    # Тестируем гибридного браузерного агента
    await test_hybrid_browser_agent()
    
    # Тестируем инструменты для работы с браузером
    await test_browser_tools()
    
    logger.info("Пример завершен")

if __name__ == "__main__":
    asyncio.run(main())
