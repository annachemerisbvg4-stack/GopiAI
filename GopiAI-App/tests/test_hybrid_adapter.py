#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестирование гибридного браузерного адаптера.

Простой скрипт для тестирования гибридного браузерного адаптера.
"""

import asyncio
from gopiai.core.logging import get_logger
logger = get_logger().logger
import sys
import os
import subprocess
import time

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = get_logger().logger

# Базовый класс адаптера
class BrowserAdapter:
    """Базовый класс адаптера для браузерных инструментов."""
    
    def __init__(self, name="base"):
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

# Адаптер для BrowserMCP
class BrowserMCPAdapter(BrowserAdapter):
    """Адаптер для работы с BrowserMCP."""
    
    def __init__(self):
        """Инициализирует адаптер для BrowserMCP."""
        super().__init__(name="browsermcp")
        self.mcp_server_process = None
        self.mcp_server_url = "http://localhost:9009"
        self.mcp_server_running = False
        
    async def initialize(self):
        """Инициализирует адаптер для BrowserMCP."""
        if self.initialized:
            return True
            
        try:
            # Проверяем, установлен ли BrowserMCP
            if not self._is_mcp_installed():
                logger.warning("BrowserMCP не установлен")
                return False
                
            # Проверяем, запущен ли MCP сервер
            if not await self._is_mcp_server_running():
                # Запускаем MCP сервер
                if not await self._start_mcp_server():
                    logger.warning("Не удалось запустить MCP сервер")
                    return False
            
            self.initialized = True
            logger.info("Адаптер BrowserMCP инициализирован")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации адаптера BrowserMCP: {str(e)}")
            return False
            
    def _is_mcp_installed(self):
        """Проверяет, установлен ли BrowserMCP."""
        try:
            # Проверяем наличие пакета @browsermcp/mcp
            result = subprocess.run(
                ["npm", "list", "-g", "@browsermcp/mcp"],
                capture_output=True,
                text=True
            )
            
            if "@browsermcp/mcp" in result.stdout:
                logger.info("BrowserMCP установлен глобально")
                return True
                
            # Проверяем наличие локального пакета
            result = subprocess.run(
                ["npm", "list", "@browsermcp/mcp"],
                capture_output=True,
                text=True
            )
            
            if "@browsermcp/mcp" in result.stdout:
                logger.info("BrowserMCP установлен локально")
                return True
                
            logger.warning("BrowserMCP не найден")
            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке установки BrowserMCP: {str(e)}")
            return False
            
    async def _is_mcp_server_running(self):
        """Проверяет, запущен ли MCP сервер."""
        try:
            # Простая проверка через HTTP-запрос
            # В реальном коде здесь будет использоваться aiohttp
            logger.info("Проверка статуса MCP сервера")
            
            # Имитация проверки
            self.mcp_server_running = False
            logger.info("MCP сервер не запущен")
            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке статуса MCP сервера: {str(e)}")
            return False
            
    async def _start_mcp_server(self):
        """Запускает MCP сервер."""
        try:
            # Запускаем MCP сервер
            logger.info("Запуск MCP сервера...")
            
            # Имитация запуска сервера
            logger.info("MCP сервер запущен (имитация)")
            self.mcp_server_running = True
            return True
        except Exception as e:
            logger.error(f"Ошибка при запуске MCP сервера: {str(e)}")
            return False

# Адаптер для Browser-use
class BrowserUseAdapter(BrowserAdapter):
    """Адаптер для работы с Browser-use."""
    
    def __init__(self):
        """Инициализирует адаптер для Browser-use."""
        super().__init__(name="browser_use")
        self.agent = None
        
    async def initialize(self):
        """Инициализирует адаптер для Browser-use."""
        if self.initialized:
            return True
            
        try:
            # Проверяем, установлен ли Browser-use
            try:
                # Имитация проверки
                logger.info("Проверка установки Browser-use")
                # В реальном коде здесь будет импорт browser_use
                
                # Имитация успешной проверки
                logger.info("Browser-use установлен (имитация)")
                
                # Создаем агента (имитация)
                self.agent = "browser_use_agent"
                
                self.initialized = True
                logger.info("Адаптер Browser-use инициализирован")
                return True
            except ImportError:
                logger.warning("Browser-use не установлен")
                return False
        except Exception as e:
            logger.error(f"Ошибка инициализации адаптера Browser-use: {str(e)}")
            return False

# Гибридный адаптер
class HybridBrowserAdapter(BrowserAdapter):
    """Гибридный адаптер для работы с различными браузерными инструментами."""
    
    def __init__(self, preferred_tool="auto"):
        """Инициализирует гибридный адаптер."""
        super().__init__(name="hybrid")
        self.preferred_tool = preferred_tool
        self.mcp_adapter = BrowserMCPAdapter()
        self.browser_use_adapter = BrowserUseAdapter()
        self.active_adapter = None
        
    async def initialize(self):
        """Инициализирует гибридный адаптер."""
        if self.initialized:
            return True
            
        try:
            # Пытаемся инициализировать предпочтительный адаптер
            if self.preferred_tool == "mcp":
                if await self.mcp_adapter.initialize():
                    self.active_adapter = self.mcp_adapter
                    logger.info("Активирован адаптер BrowserMCP")
                else:
                    logger.warning("Не удалось инициализировать BrowserMCP, пробуем Browser-use")
                    if await self.browser_use_adapter.initialize():
                        self.active_adapter = self.browser_use_adapter
                        logger.info("Активирован адаптер Browser-use")
                    else:
                        logger.error("Не удалось инициализировать ни один адаптер")
                        return False
            elif self.preferred_tool == "browser_use":
                if await self.browser_use_adapter.initialize():
                    self.active_adapter = self.browser_use_adapter
                    logger.info("Активирован адаптер Browser-use")
                else:
                    logger.warning("Не удалось инициализировать Browser-use, пробуем BrowserMCP")
                    if await self.mcp_adapter.initialize():
                        self.active_adapter = self.mcp_adapter
                        logger.info("Активирован адаптер BrowserMCP")
                    else:
                        logger.error("Не удалось инициализировать ни один адаптер")
                        return False
            else:  # auto
                # Пробуем сначала BrowserMCP, затем Browser-use
                if await self.mcp_adapter.initialize():
                    self.active_adapter = self.mcp_adapter
                    logger.info("Активирован адаптер BrowserMCP")
                elif await self.browser_use_adapter.initialize():
                    self.active_adapter = self.browser_use_adapter
                    logger.info("Активирован адаптер Browser-use")
                else:
                    logger.error("Не удалось инициализировать ни один адаптер")
                    return False
                    
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации гибридного адаптера: {str(e)}")
            return False
            
    async def navigate(self, url):
        """Переходит по указанному URL."""
        if not self.initialized and not await self.initialize():
            return {
                "success": False,
                "message": "Адаптер не инициализирован",
                "data": {}
            }
            
        if not self.active_adapter:
            return {
                "success": False,
                "message": "Нет активного адаптера",
                "data": {}
            }
            
        return await self.active_adapter.navigate(url)
        
    async def extract_content(self, selector=None):
        """Извлекает содержимое страницы или элемента."""
        if not self.initialized and not await self.initialize():
            return {
                "success": False,
                "message": "Адаптер не инициализирован",
                "data": {}
            }
            
        if not self.active_adapter:
            return {
                "success": False,
                "message": "Нет активного адаптера",
                "data": {}
            }
            
        return await self.active_adapter.extract_content(selector)
        
    async def close(self):
        """Закрывает браузер или соединение."""
        results = []
        
        # Закрываем оба адаптера
        if self.mcp_adapter.initialized:
            results.append(await self.mcp_adapter.close())
            
        if self.browser_use_adapter.initialized:
            results.append(await self.browser_use_adapter.close())
            
        self.active_adapter = None
        self.initialized = False
        
        return {
            "success": True,
            "message": "Все адаптеры закрыты",
            "data": {"results": results}
        }

async def main():
    """Основная функция."""
    logger.info("Запуск тестирования гибридного браузерного адаптера")
    
    # Создаем гибридный адаптер
    adapter = HybridBrowserAdapter(preferred_tool="auto")
    
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
    
    logger.info("Тестирование завершено")

if __name__ == "__main__":
    asyncio.run(main())
