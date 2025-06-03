#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестирование браузерного адаптера.

Простой скрипт для тестирования браузерного адаптера.
"""

import asyncio
from gopiai.core.logging import get_logger
logger = get_logger().logger
import sys
import os

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = get_logger().logger

# Создаем класс браузерного адаптера для тестирования
class BrowserAdapter:
    """Простой браузерный адаптер для тестирования."""
    
    def __init__(self, name="test"):
        """Инициализирует адаптер."""
        self.name = name
        self.initialized = False
        logger.info(f"Создан адаптер {self.name}")
        
    async def initialize(self):
        """Инициализирует адаптер."""
        if self.initialized:
            return True
            
        try:
            self.initialized = True
            logger.info(f"Адаптер {self.name} инициализирован")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации адаптера {self.name}: {str(e)}")
            return False
            
    async def navigate(self, url):
        """Переходит по указанному URL."""
        if not self.initialized:
            await self.initialize()
            
        logger.info(f"Переход по URL: {url}")
        return {
            "success": True,
            "message": f"Успешно выполнен переход по URL: {url}",
            "data": {"url": url}
        }
        
    async def extract_content(self, selector=None):
        """Извлекает содержимое страницы или элемента."""
        if not self.initialized:
            await self.initialize()
            
        logger.info(f"Извлечение содержимого" + (f" элемента: {selector}" if selector else ""))
        return {
            "success": True,
            "message": f"Успешно извлечено содержимое" + (f" элемента: {selector}" if selector else ""),
            "data": {"content": "Пример содержимого страницы"}
        }
        
    async def close(self):
        """Закрывает браузер или соединение."""
        logger.info(f"Закрытие адаптера {self.name}")
        self.initialized = False
        return {
            "success": True,
            "message": f"Адаптер {self.name} закрыт"
        }

async def main():
    """Основная функция."""
    logger.info("Запуск тестирования браузерного адаптера")
    
    # Создаем адаптер
    adapter = BrowserAdapter()
    
    # Инициализируем адаптер
    initialized = await adapter.initialize()
    logger.info(f"Адаптер инициализирован: {initialized}")
    
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
    
    logger.info("Тестирование завершено")

if __name__ == "__main__":
    asyncio.run(main())
