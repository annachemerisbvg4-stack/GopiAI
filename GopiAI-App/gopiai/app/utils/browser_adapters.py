#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль адаптеров для различных браузерных инструментов.

Предоставляет унифицированный интерфейс для работы с различными
инструментами автоматизации браузера, такими как BrowserMCP и Browser-use.
"""

import time
from typing import Dict, Any, Optional

from gopiai.core.logging import get_logger
logger = get_logger().logger


class BrowserAdapter:
    """
    Базовый класс адаптера для браузерных инструментов.
    
    Предоставляет общий интерфейс для работы с различными
    инструментами автоматизации браузера.
    """
    
    def __init__(self, name: str = "base"):
        """
        Инициализирует адаптер.
        
        Args:
            name: Имя адаптера
        """
        self.name = name
        self.initialized = False
        logger.info(f"Создан адаптер {self.name}")
        
    async def initialize(self) -> bool:
        """
        Инициализирует адаптер.
        
        Returns:
            bool: True, если инициализация прошла успешно
        """
        if self.initialized:
            return True
            
        try:
            self.initialized = True
            logger.info(f"Адаптер {self.name} инициализирован")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации адаптера {self.name}: {str(e)}")
            return False
            
    async def navigate(self, url: str) -> Dict[str, Any]:
        """
        Переходит по указанному URL.
        
        Args:
            url: URL для перехода
            
        Returns:
            Dict: Результат операции
        """
        raise NotImplementedError("Метод должен быть переопределен в подклассе")
        
    async def click(self, selector: str) -> Dict[str, Any]:
        """
        Кликает по элементу с указанным селектором.
        
        Args:
            selector: CSS-селектор элемента
            
        Returns:
            Dict: Результат операции
        """
        raise NotImplementedError("Метод должен быть переопределен в подклассе")
        
    async def type(self, selector: str, text: str) -> Dict[str, Any]:
        """
        Вводит текст в элемент с указанным селектором.
        
        Args:
            selector: CSS-селектор элемента
            text: Текст для ввода
            
        Returns:
            Dict: Результат операции
        """
        raise NotImplementedError("Метод должен быть переопределен в подклассе")
        
    async def extract_content(self, selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Извлекает содержимое страницы или элемента.
        
        Args:
            selector: CSS-селектор элемента (опционально)
            
        Returns:
            Dict: Результат операции с извлеченным содержимым
        """
        raise NotImplementedError("Метод должен быть переопределен в подклассе")
        
    async def execute_javascript(self, code: str) -> Dict[str, Any]:
        """
        Выполняет JavaScript-код на странице.
        
        Args:
            code: JavaScript-код для выполнения
            
        Returns:
            Dict: Результат операции с результатом выполнения кода
        """
        raise NotImplementedError("Метод должен быть переопределен в подклассе")
        
    async def take_screenshot(self, selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Делает скриншот страницы или элемента.
        
        Args:
            selector: CSS-селектор элемента (опционально)
            
        Returns:
            Dict: Результат операции с путем к скриншоту
        """
        raise NotImplementedError("Метод должен быть переопределен в подклассе")
        
    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> Dict[str, Any]:
        """
        Ожидает появления элемента с указанным селектором.
        
        Args:
            selector: CSS-селектор элемента
            timeout: Таймаут в миллисекундах
            
        Returns:
            Dict: Результат операции
        """
        raise NotImplementedError("Метод должен быть переопределен в подклассе")
        
    async def get_current_url(self) -> Dict[str, Any]:
        """
        Получает текущий URL страницы.
        
        Returns:
            Dict: Результат операции с текущим URL
        """
        raise NotImplementedError("Метод должен быть переопределен в подклассе")
        
    async def get_page_title(self) -> Dict[str, Any]:
        """
        Получает заголовок текущей страницы.
        
        Returns:
            Dict: Результат операции с заголовком страницы
        """
        raise NotImplementedError("Метод должен быть переопределен в подклассе")
        
    async def close(self) -> Dict[str, Any]:
        """
        Закрывает браузер или соединение.
        
        Returns:
            Dict: Результат операции
        """
        raise NotImplementedError("Метод должен быть переопределен в подклассе")
        
    def _create_result(self, success: bool, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Создает стандартизированный результат операции.
        
        Args:
            success: Флаг успешности операции
            message: Сообщение о результате операции
            data: Дополнительные данные результата
            
        Returns:
            Dict: Стандартизированный результат операции
        """
        return {
            "success": success,
            "message": message,
            "data": data or {},
            "adapter": self.name,
            "timestamp": time.time()
        }


class BrowserMCPAdapter(BrowserAdapter):
    """
    Адаптер для работы с BrowserMCP.
    
    Предоставляет интерфейс для работы с BrowserMCP через
    локальный MCP сервер и встроенный браузер.
    """
    
    def __init__(self, browser=None):
        """
        Инициализирует адаптер для BrowserMCP.
        
        Args:
            browser: Экземпляр встроенного браузера (опционально)
        """
        super().__init__(name="browsermcp")
        self.browser = browser
        self.mcp_server_url = "http://localhost:9009"
        self.mcp_server_process = None
        self.mcp_server_running = False
        
    async def initialize(self) -> bool:
        """
        Инициализирует адаптер для BrowserMCP.
        
        Настраивает BrowserMCP и внедряет его в встроенный браузер.
        
        Returns:
            bool: True, если инициализация прошла успешно
        """
        if self.initialized:
            return True
            
        try:
            # Импортируем модули для настройки BrowserMCP
            from gopiai.app.utils.browsermcp_setup import setup_browsermcp
            
            # Настраиваем BrowserMCP
            if not await setup_browsermcp():
                logger.warning("Не удалось настроить BrowserMCP")
                return False
                
            # Если указан браузер, внедряем BrowserMCP
            if self.browser:
                from gopiai.app.utils.browsermcp_injector import inject_browsermcp
                
                # Внедряем BrowserMCP в браузер
                if not await inject_browsermcp(self.browser):
                    logger.warning("Не удалось внедрить BrowserMCP в браузер")
                    return False
            
            self.initialized = True
            logger.info("Адаптер BrowserMCP инициализирован")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации адаптера BrowserMCP: {str(e)}")
            return False
            
    async def navigate(self, url: str) -> Dict[str, Any]:
        """
        Переходит по указанному URL.
        
        Args:
            url: URL для перехода
            
        Returns:
            Dict: Результат операции
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        try:
            # Если указан браузер, используем его
            if self.browser:
                from gopiai.app.utils.browsermcp_injector import execute_browsermcp_command
                
                # Выполняем команду navigate через BrowserMCP
                result = await execute_browsermcp_command(
                    self.browser,
                    "navigate",
                    {"url": url}
                )
                
                if result.get("success"):
                    return self._create_result(
                        True,
                        f"Успешно выполнен переход по URL: {url}",
                        result.get("data", {})
                    )
                else:
                    return self._create_result(
                        False,
                        result.get("message", f"Ошибка при переходе по URL: {url}"),
                        {"url": url}
                    )
            else:
                # Используем MCP API напрямую
                import aiohttp
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.mcp_server_url}/api/navigate",
                        json={"url": url}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return self._create_result(
                                True,
                                f"Успешно выполнен переход по URL: {url}",
                                data
                            )
                        else:
                            error = await response.text()
                            return self._create_result(
                                False,
                                f"Ошибка при переходе по URL: {error}",
                                {"url": url, "status": response.status}
                            )
        except Exception as e:
            logger.error(f"Ошибка при навигации через BrowserMCP: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при навигации: {str(e)}",
                {"url": url}
            )
            
    async def click(self, selector: str) -> Dict[str, Any]:
        """
        Кликает по элементу с указанным селектором.
        
        Args:
            selector: CSS-селектор элемента
            
        Returns:
            Dict: Результат операции
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        try:
            # Если указан браузер, используем его
            if self.browser:
                from gopiai.app.utils.browsermcp_injector import execute_browsermcp_command
                
                # Выполняем команду click через BrowserMCP
                result = await execute_browsermcp_command(
                    self.browser,
                    "click",
                    {"selector": selector}
                )
                
                if result.get("success"):
                    return self._create_result(
                        True,
                        f"Успешно выполнен клик по элементу: {selector}",
                        result.get("data", {})
                    )
                else:
                    return self._create_result(
                        False,
                        result.get("message", f"Ошибка при клике по элементу: {selector}"),
                        {"selector": selector}
                    )
            else:
                # Используем MCP API напрямую
                import aiohttp
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.mcp_server_url}/api/click",
                        json={"selector": selector}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return self._create_result(
                                True,
                                f"Успешно выполнен клик по элементу: {selector}",
                                data
                            )
                        else:
                            error = await response.text()
                            return self._create_result(
                                False,
                                f"Ошибка при клике по элементу: {error}",
                                {"selector": selector, "status": response.status}
                            )
        except Exception as e:
            logger.error(f"Ошибка при клике через BrowserMCP: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при клике: {str(e)}",
                {"selector": selector}
            )
            
    async def type(self, selector: str, text: str) -> Dict[str, Any]:
        """
        Вводит текст в элемент с указанным селектором.
        
        Args:
            selector: CSS-селектор элемента
            text: Текст для ввода
            
        Returns:
            Dict: Результат операции
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        try:
            # Если указан браузер, используем его
            if self.browser:
                from gopiai.app.utils.browsermcp_injector import execute_browsermcp_command
                
                # Выполняем команду type через BrowserMCP
                result = await execute_browsermcp_command(
                    self.browser,
                    "type",
                    {"selector": selector, "text": text}
                )
                
                if result.get("success"):
                    return self._create_result(
                        True,
                        f"Успешно введен текст в элемент: {selector}",
                        result.get("data", {})
                    )
                else:
                    return self._create_result(
                        False,
                        result.get("message", f"Ошибка при вводе текста в элемент: {selector}"),
                        {"selector": selector, "text": text}
                    )
            else:
                # Используем MCP API напрямую
                import aiohttp
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.mcp_server_url}/api/type",
                        json={"selector": selector, "text": text}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return self._create_result(
                                True,
                                f"Успешно введен текст в элемент: {selector}",
                                data
                            )
                        else:
                            error = await response.text()
                            return self._create_result(
                                False,
                                f"Ошибка при вводе текста: {error}",
                                {"selector": selector, "text": text, "status": response.status}
                            )
        except Exception as e:
            logger.error(f"Ошибка при вводе текста через BrowserMCP: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при вводе текста: {str(e)}",
                {"selector": selector, "text": text}
            )
            
    async def extract_content(self, selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Извлекает содержимое страницы или элемента.
        
        Args:
            selector: CSS-селектор элемента (опционально)
            
        Returns:
            Dict: Результат операции с извлеченным содержимым
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        try:
            # Если указан браузер, используем его
            if self.browser:
                from gopiai.app.utils.browsermcp_injector import execute_browsermcp_command
                
                # Формируем аргументы
                args = {}
                if selector:
                    args["selector"] = selector
                
                # Выполняем команду extract через BrowserMCP
                result = await execute_browsermcp_command(
                    self.browser,
                    "extract",
                    args
                )
                
                if result.get("success"):
                    return self._create_result(
                        True,
                        f"Успешно извлечено содержимое" + (f" элемента: {selector}" if selector else ""),
                        result.get("data", {})
                    )
                else:
                    return self._create_result(
                        False,
                        result.get("message", f"Ошибка при извлечении содержимого"),
                        {"selector": selector}
                    )
            else:
                # Используем MCP API напрямую
                import aiohttp
                
                async with aiohttp.ClientSession() as session:
                    payload = {}
                    if selector:
                        payload["selector"] = selector
                        
                    async with session.post(
                        f"{self.mcp_server_url}/api/extract",
                        json=payload
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return self._create_result(
                                True,
                                f"Успешно извлечено содержимое" + (f" элемента: {selector}" if selector else ""),
                                data
                            )
                        else:
                            error = await response.text()
                            return self._create_result(
                                False,
                                f"Ошибка при извлечении содержимого: {error}",
                                {"selector": selector, "status": response.status}
                            )
        except Exception as e:
            logger.error(f"Ошибка при извлечении содержимого через BrowserMCP: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при извлечении содержимого: {str(e)}",
                {"selector": selector}
            )
            
    async def get_current_url(self) -> Dict[str, Any]:
        """
        Получает текущий URL страницы.
        
        Returns:
            Dict: Результат операции с текущим URL
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        try:
            # Если указан браузер, используем его
            if self.browser:
                from gopiai.app.utils.browsermcp_injector import execute_browsermcp_command
                
                # Выполняем команду get_url через BrowserMCP
                result = await execute_browsermcp_command(
                    self.browser,
                    "get_url",
                    {}
                )
                
                if result.get("success"):
                    return self._create_result(
                        True,
                        "Успешно получен текущий URL",
                        {"url": result.get("data", {}).get("url", "")}
                    )
                else:
                    return self._create_result(
                        False,
                        result.get("message", "Ошибка при получении текущего URL"),
                        {}
                    )
            else:
                # Используем MCP API напрямую
                import aiohttp
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.mcp_server_url}/api/get_url",
                        json={}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return self._create_result(
                                True,
                                "Успешно получен текущий URL",
                                {"url": data.get("url", "")}
                            )
                        else:
                            error = await response.text()
                            return self._create_result(
                                False,
                                f"Ошибка при получении текущего URL: {error}",
                                {"status": response.status}
                            )
        except Exception as e:
            logger.error(f"Ошибка при получении текущего URL через BrowserMCP: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при получении текущего URL: {str(e)}",
                {}
            )
            
    async def get_page_title(self) -> Dict[str, Any]:
        """
        Получает заголовок текущей страницы.
        
        Returns:
            Dict: Результат операции с заголовком страницы
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        try:
            # Если указан браузер, используем его
            if self.browser:
                from gopiai.app.utils.browsermcp_injector import execute_browsermcp_command
                
                # Выполняем команду get_title через BrowserMCP
                result = await execute_browsermcp_command(
                    self.browser,
                    "get_title",
                    {}
                )
                
                if result.get("success"):
                    return self._create_result(
                        True,
                        "Успешно получен заголовок страницы",
                        {"title": result.get("data", {}).get("title", "")}
                    )
                else:
                    return self._create_result(
                        False,
                        result.get("message", "Ошибка при получении заголовка страницы"),
                        {}
                    )
            else:
                # Используем MCP API напрямую
                import aiohttp
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.mcp_server_url}/api/get_title",
                        json={}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return self._create_result(
                                True,
                                "Успешно получен заголовок страницы",
                                {"title": data.get("title", "")}
                            )
                        else:
                            error = await response.text()
                            return self._create_result(
                                False,
                                f"Ошибка при получении заголовка страницы: {error}",
                                {"status": response.status}
                            )
        except Exception as e:
            logger.error(f"Ошибка при получении заголовка страницы через BrowserMCP: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при получении заголовка страницы: {str(e)}",
                {}
            )
            
    async def close(self) -> Dict[str, Any]:
        """
        Закрывает соединение с MCP сервером.
        
        Returns:
            Dict: Результат операции
        """
        try:
            # Останавливаем MCP сервер, если он был запущен нами
            if self.mcp_server_process:
                self.mcp_server_process.terminate()
                self.mcp_server_process = None
                self.mcp_server_running = False
                
            self.initialized = False
            
            return self._create_result(
                True,
                "Соединение с MCP сервером закрыто"
            )
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения с MCP сервером: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при закрытии соединения: {str(e)}"
            )


class BrowserUseAdapter(BrowserAdapter):
    """
    Адаптер для работы с Browser-use.
    
    Предоставляет интерфейс для работы с Browser-use через
    его Python API.
    """
    
    def __init__(self):
        """Инициализирует адаптер для Browser-use."""
        super().__init__(name="browser_use")
        self.agent = None
        
    async def initialize(self) -> bool:
        """
        Инициализирует адаптер для Browser-use.
        
        Проверяет наличие установленного Browser-use и создает
        экземпляр агента.
        
        Returns:
            bool: True, если инициализация прошла успешно
        """
        if self.initialized:
            return True
            
        try:
            # Проверяем, установлен ли Browser-use
            try:
                import browser_use
            except ImportError:
                logger.warning("Browser-use не установлен")
                return False
                
            # Импортируем необходимые модули
            from browser_use import Agent
            from langchain_openai import ChatOpenAI
            
            # Создаем агента
            self.agent = Agent(
                task="Выполнение браузерных операций",
                llm=ChatOpenAI(model="gpt-4o"),
                headless=False
            )
            
            self.initialized = True
            logger.info("Адаптер Browser-use инициализирован")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации адаптера Browser-use: {str(e)}")
            return False
            
    async def navigate(self, url: str) -> Dict[str, Any]:
        """
        Переходит по указанному URL.
        
        Args:
            url: URL для перехода
            
        Returns:
            Dict: Результат операции
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        try:
            # Выполняем навигацию через Browser-use
            result = await self.agent.run(f"Перейти по URL: {url}")
            
            return self._create_result(
                True,
                f"Успешно выполнен переход по URL: {url}",
                {"result": result}
            )
        except Exception as e:
            logger.error(f"Ошибка при навигации через Browser-use: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при навигации: {str(e)}",
                {"url": url}
            )
            
    async def click(self, selector: str) -> Dict[str, Any]:
        """
        Кликает по элементу с указанным селектором.
        
        Args:
            selector: CSS-селектор элемента
            
        Returns:
            Dict: Результат операции
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        try:
            # Выполняем клик через Browser-use
            result = await self.agent.run(f"Кликнуть по элементу с селектором: {selector}")
            
            return self._create_result(
                True,
                f"Успешно выполнен клик по элементу: {selector}",
                {"result": result}
            )
        except Exception as e:
            logger.error(f"Ошибка при клике через Browser-use: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при клике: {str(e)}",
                {"selector": selector}
            )
            
    async def type(self, selector: str, text: str) -> Dict[str, Any]:
        """
        Вводит текст в элемент с указанным селектором.
        
        Args:
            selector: CSS-селектор элемента
            text: Текст для ввода
            
        Returns:
            Dict: Результат операции
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        try:
            # Выполняем ввод текста через Browser-use
            result = await self.agent.run(f"Ввести текст '{text}' в элемент с селектором: {selector}")
            
            return self._create_result(
                True,
                f"Успешно введен текст в элемент: {selector}",
                {"result": result}
            )
        except Exception as e:
            logger.error(f"Ошибка при вводе текста через Browser-use: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при вводе текста: {str(e)}",
                {"selector": selector, "text": text}
            )
            
    async def extract_content(self, selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Извлекает содержимое страницы или элемента.
        
        Args:
            selector: CSS-селектор элемента (опционально)
            
        Returns:
            Dict: Результат операции с извлеченным содержимым
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        try:
            # Выполняем извлечение содержимого через Browser-use
            if selector:
                result = await self.agent.run(f"Извлечь содержимое элемента с селектором: {selector}")
            else:
                result = await self.agent.run("Извлечь содержимое текущей страницы")
            
            return self._create_result(
                True,
                f"Успешно извлечено содержимое" + (f" элемента: {selector}" if selector else ""),
                {"result": result}
            )
        except Exception as e:
            logger.error(f"Ошибка при извлечении содержимого через Browser-use: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при извлечении содержимого: {str(e)}",
                {"selector": selector}
            )
            
    async def get_current_url(self) -> Dict[str, Any]:
        """
        Получает текущий URL страницы.
        
        Returns:
            Dict: Результат операции с текущим URL
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        try:
            # Выполняем получение URL через Browser-use
            result = await self.agent.run("Получить текущий URL страницы")
            
            return self._create_result(
                True,
                "Успешно получен текущий URL",
                {"url": result}
            )
        except Exception as e:
            logger.error(f"Ошибка при получении текущего URL через Browser-use: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при получении текущего URL: {str(e)}",
                {}
            )
            
    async def get_page_title(self) -> Dict[str, Any]:
        """
        Получает заголовок текущей страницы.
        
        Returns:
            Dict: Результат операции с заголовком страницы
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        try:
            # Выполняем получение заголовка через Browser-use
            result = await self.agent.run("Получить заголовок текущей страницы")
            
            return self._create_result(
                True,
                "Успешно получен заголовок страницы",
                {"title": result}
            )
        except Exception as e:
            logger.error(f"Ошибка при получении заголовка страницы через Browser-use: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при получении заголовка страницы: {str(e)}",
                {}
            )
            
    async def close(self) -> Dict[str, Any]:
        """
        Закрывает браузер.
        
        Returns:
            Dict: Результат операции
        """
        try:
            # Закрываем браузер
            if self.agent:
                # У Browser-use нет явного метода для закрытия браузера,
                # но можно попробовать выполнить команду
                try:
                    await self.agent.run("Закрыть браузер")
                except:
                    pass
                    
                self.agent = None
                
            self.initialized = False
            
            return self._create_result(
                True,
                "Браузер закрыт"
            )
        except Exception as e:
            logger.error(f"Ошибка при закрытии браузера: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при закрытии браузера: {str(e)}"
            )


class HybridBrowserAdapter(BrowserAdapter):
    """
    Гибридный адаптер для работы с различными браузерными инструментами.
    
    Автоматически выбирает наиболее подходящий инструмент в зависимости
    от доступности и предпочтений.
    """
    
    def __init__(self, preferred_tool: str = "auto", browser=None):
        """
        Инициализирует гибридный адаптер.
        
        Args:
            preferred_tool: Предпочтительный инструмент ("mcp", "browser_use" или "auto")
            browser: Экземпляр встроенного браузера (опционально)
        """
        super().__init__(name="hybrid")
        self.preferred_tool = preferred_tool
        self.browser = browser
        self.mcp_adapter = BrowserMCPAdapter(browser=browser)
        self.browser_use_adapter = BrowserUseAdapter()
        self.active_adapter = None
        
    async def initialize(self) -> bool:
        """
        Инициализирует гибридный адаптер.
        
        Выбирает наиболее подходящий инструмент в зависимости от
        доступности и предпочтений.
        
        Returns:
            bool: True, если инициализация прошла успешно
        """
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
            
    async def navigate(self, url: str) -> Dict[str, Any]:
        """
        Переходит по указанному URL.
        
        Args:
            url: URL для перехода
            
        Returns:
            Dict: Результат операции
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        if not self.active_adapter:
            return self._create_result(False, "Нет активного адаптера")
            
        return await self.active_adapter.navigate(url)
        
    async def click(self, selector: str) -> Dict[str, Any]:
        """
        Кликает по элементу с указанным селектором.
        
        Args:
            selector: CSS-селектор элемента
            
        Returns:
            Dict: Результат операции
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        if not self.active_adapter:
            return self._create_result(False, "Нет активного адаптера")
            
        result = await self.active_adapter.click(selector)
        
        # Если операция не удалась и у нас есть запасной адаптер, пробуем его
        if not result["success"] and self.active_adapter != self.mcp_adapter and await self.mcp_adapter.initialize():
            logger.info(f"Пробуем выполнить клик через запасной адаптер BrowserMCP")
            result = await self.mcp_adapter.click(selector)
        elif not result["success"] and self.active_adapter != self.browser_use_adapter and await self.browser_use_adapter.initialize():
            logger.info(f"Пробуем выполнить клик через запасной адаптер Browser-use")
            result = await self.browser_use_adapter.click(selector)
            
        return result
        
    async def type(self, selector: str, text: str) -> Dict[str, Any]:
        """
        Вводит текст в элемент с указанным селектором.
        
        Args:
            selector: CSS-селектор элемента
            text: Текст для ввода
            
        Returns:
            Dict: Результат операции
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        if not self.active_adapter:
            return self._create_result(False, "Нет активного адаптера")
            
        result = await self.active_adapter.type(selector, text)
        
        # Если операция не удалась и у нас есть запасной адаптер, пробуем его
        if not result["success"] and self.active_adapter != self.mcp_adapter and await self.mcp_adapter.initialize():
            logger.info(f"Пробуем выполнить ввод текста через запасной адаптер BrowserMCP")
            result = await self.mcp_adapter.type(selector, text)
        elif not result["success"] and self.active_adapter != self.browser_use_adapter and await self.browser_use_adapter.initialize():
            logger.info(f"Пробуем выполнить ввод текста через запасной адаптер Browser-use")
            result = await self.browser_use_adapter.type(selector, text)
            
        return result
        
    async def extract_content(self, selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Извлекает содержимое страницы или элемента.
        
        Args:
            selector: CSS-селектор элемента (опционально)
            
        Returns:
            Dict: Результат операции с извлеченным содержимым
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        if not self.active_adapter:
            return self._create_result(False, "Нет активного адаптера")
            
        result = await self.active_adapter.extract_content(selector)
        
        # Если операция не удалась и у нас есть запасной адаптер, пробуем его
        if not result["success"] and self.active_adapter != self.mcp_adapter and await self.mcp_adapter.initialize():
            logger.info(f"Пробуем извлечь содержимое через запасной адаптер BrowserMCP")
            result = await self.mcp_adapter.extract_content(selector)
        elif not result["success"] and self.active_adapter != self.browser_use_adapter and await self.browser_use_adapter.initialize():
            logger.info(f"Пробуем извлечь содержимое через запасной адаптер Browser-use")
            result = await self.browser_use_adapter.extract_content(selector)
            
        return result
        
    async def execute_javascript(self, code: str) -> Dict[str, Any]:
        """
        Выполняет JavaScript-код на странице.
        
        Args:
            code: JavaScript-код для выполнения
            
        Returns:
            Dict: Результат операции с результатом выполнения кода
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        if not self.active_adapter:
            return self._create_result(False, "Нет активного адаптера")
            
        # Предпочитаем BrowserMCP для выполнения JavaScript
        if self.active_adapter != self.mcp_adapter and await self.mcp_adapter.initialize():
            logger.info(f"Используем BrowserMCP для выполнения JavaScript")
            return await self.mcp_adapter.execute_javascript(code)
            
        # Если BrowserMCP недоступен, пробуем активный адаптер
        if hasattr(self.active_adapter, "execute_javascript"):
            return await self.active_adapter.execute_javascript(code)
            
        return self._create_result(
            False,
            "Выполнение JavaScript не поддерживается активным адаптером",
            {"code": code}
        )
        
    async def get_current_url(self) -> Dict[str, Any]:
        """
        Получает текущий URL страницы.
        
        Returns:
            Dict: Результат операции с текущим URL
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        if not self.active_adapter:
            return self._create_result(False, "Нет активного адаптера")
            
        return await self.active_adapter.get_current_url()
        
    async def get_page_title(self) -> Dict[str, Any]:
        """
        Получает заголовок текущей страницы.
        
        Returns:
            Dict: Результат операции с заголовком страницы
        """
        if not self.initialized and not await self.initialize():
            return self._create_result(False, "Адаптер не инициализирован")
            
        if not self.active_adapter:
            return self._create_result(False, "Нет активного адаптера")
            
        return await self.active_adapter.get_page_title()
        
    async def close(self) -> Dict[str, Any]:
        """
        Закрывает браузер или соединение.
        
        Returns:
            Dict: Результат операции
        """
        try:
            # Закрываем активный адаптер
            if self.active_adapter and self.active_adapter.initialized:
                await self.active_adapter.close()
                
            # Закрываем все адаптеры
            if self.mcp_adapter and self.mcp_adapter.initialized:
                await self.mcp_adapter.close()
                
            if self.browser_use_adapter and self.browser_use_adapter.initialized:
                await self.browser_use_adapter.close()
                
            self.initialized = False
            self.active_adapter = None
            
            return self._create_result(
                True,
                "Все адаптеры закрыты"
            )
        except Exception as e:
            logger.error(f"Ошибка при закрытии адаптеров: {str(e)}")
            return self._create_result(
                False,
                f"Ошибка при закрытии адаптеров: {str(e)}"
            )


def get_browser_adapter(preferred_tool="auto", browser=None):
    """
    Возвращает экземпляр браузерного адаптера.
    
    Args:
        preferred_tool: Предпочтительный инструмент ("mcp", "browser_use" или "auto")
        browser: Экземпляр встроенного браузера (опционально)
        
    Returns:
        BrowserAdapter: Экземпляр браузерного адаптера
    """
    if preferred_tool == "mcp":
        return BrowserMCPAdapter(browser=browser)
    elif preferred_tool == "browser_use":
        return BrowserUseAdapter()
    else:  # auto
        return HybridBrowserAdapter(preferred_tool=preferred_tool, browser=browser)
