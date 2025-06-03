#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Пример использования внешних ИИ-сервисов через браузер.

Демонстрирует взаимодействие с различными внешними ИИ-сервисами
(ChatGPT, Claude, Leonardo, Midjourney и др.) через браузер.
"""

import asyncio
from gopiai.core.logging import get_logger
logger = get_logger().logger
import sys
import os
import argparse

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = get_logger().logger

# Импортируем необходимые модули
from gopiai.app.agent.orchestrator import get_orchestrator
from gopiai.app.tool.hybrid_browser_tools import BrowserExternalAITool

# Каталог ИИ-сервисов
AI_SERVICES = {
    "chatgpt": {
        "url": "https://chat.openai.com/",
        "description": "Чат-бот на основе GPT от OpenAI",
        "capabilities": ["text", "code", "reasoning"],
        "instructions": "Перейти на сайт, ввести промпт, дождаться ответа, скопировать результат"
    },
    "claude": {
        "url": "https://claude.ai/",
        "description": "Чат-бот от Anthropic",
        "capabilities": ["text", "code", "reasoning", "long-context"],
        "instructions": "Перейти на сайт, создать новый чат, ввести промпт, дождаться ответа"
    },
    "leonardo": {
        "url": "https://app.leonardo.ai/",
        "description": "Генератор изображений от Leonardo AI",
        "capabilities": ["image", "realistic", "artistic"],
        "instructions": "Перейти на сайт, ввести промпт, выбрать модель, дождаться генерации, скачать результат"
    },
    "midjourney": {
        "url": "https://www.midjourney.com/",
        "description": "Генератор изображений Midjourney",
        "capabilities": ["image", "realistic", "artistic", "concept-art"],
        "instructions": "Перейти на сайт, ввести /imagine, ввести промпт, выбрать вариант, скачать"
    },
    "perplexity": {
        "url": "https://www.perplexity.ai/",
        "description": "Поисковый ИИ-ассистент",
        "capabilities": ["search", "research", "summarization"],
        "instructions": "Перейти на сайт, ввести запрос, дождаться ответа"
    }
}

async def use_external_ai_service(service_name, prompt, preferred_tool="auto"):
    """
    Использует внешний ИИ-сервис через браузер.
    
    Args:
        service_name: Название сервиса
        prompt: Промпт для ИИ-сервиса
        preferred_tool: Предпочтительный инструмент
        
    Returns:
        str: Результат взаимодействия с ИИ-сервисом
    """
    logger.info(f"Использование сервиса {service_name} с промптом: {prompt}")
    
    # Проверяем, есть ли сервис в каталоге
    if service_name not in AI_SERVICES:
        logger.error(f"Сервис {service_name} не найден в каталоге")
        return f"Ошибка: Сервис {service_name} не найден в каталоге"
    
    # Получаем информацию о сервисе
    service_info = AI_SERVICES[service_name]
    logger.info(f"Информация о сервисе: {service_info}")
    
    # Создаем инструмент для взаимодействия с внешним ИИ-сервисом
    tool = BrowserExternalAITool()
    
    # Выполняем запрос
    result = await tool.execute(service=service_name, prompt=prompt, preferred_tool=preferred_tool)
    
    if result.success:
        logger.info(f"Успешно получен результат от сервиса {service_name}")
        return result.data.get("result", "Результат не найден")
    else:
        logger.error(f"Ошибка при взаимодействии с сервисом {service_name}: {result.message}")
        return f"Ошибка: {result.message}"

async def list_services():
    """Выводит список доступных ИИ-сервисов."""
    logger.info("Список доступных ИИ-сервисов:")
    
    for name, info in AI_SERVICES.items():
        logger.info(f"- {name}: {info['description']}")
        logger.info(f"  URL: {info['url']}")
        logger.info(f"  Возможности: {', '.join(info['capabilities'])}")
        logger.info(f"  Инструкции: {info['instructions']}")
        logger.info("")

async def main():
    """Основная функция."""
    # Создаем парсер аргументов командной строки
    parser = argparse.ArgumentParser(description="Пример использования внешних ИИ-сервисов через браузер")
    parser.add_argument("--service", "-s", type=str, help="Название сервиса")
    parser.add_argument("--prompt", "-p", type=str, help="Промпт для ИИ-сервиса")
    parser.add_argument("--tool", "-t", type=str, default="auto", choices=["mcp", "browser_use", "auto"], help="Предпочтительный инструмент")
    parser.add_argument("--list", "-l", action="store_true", help="Вывести список доступных сервисов")
    
    # Парсим аргументы
    args = parser.parse_args()
    
    # Выводим список сервисов, если указан флаг --list
    if args.list:
        await list_services()
        return
    
    # Проверяем наличие обязательных аргументов
    if not args.service or not args.prompt:
        logger.error("Необходимо указать название сервиса и промпт")
        parser.print_help()
        return
    
    # Используем внешний ИИ-сервис
    result = await use_external_ai_service(args.service, args.prompt, args.tool)
    
    # Выводим результат
    logger.info(f"Результат: {result}")

if __name__ == "__main__":
    asyncio.run(main())
