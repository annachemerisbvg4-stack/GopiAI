#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль для инъекции функциональности BrowserMCP в встроенный браузер.

Предоставляет функции для внедрения JavaScript-кода BrowserMCP
в встроенный браузер и для взаимодействия с MCP сервером.
"""

import asyncio
import json
from typing import Optional, Dict, Any

from PySide6.QtCore import QUrl, QByteArray
from PySide6.QtWebEngineCore import QWebEngineScript
from PySide6.QtWebEngineWidgets import QWebEngineView

from gopiai.core.logging import get_logger
logger = get_logger().logger
from gopiai.app.utils.browsermcp_setup import get_browsermcp_setup


class BrowserMCPInjector:
    """Класс для инъекции функциональности BrowserMCP в встроенный браузер."""
    
    def __init__(self, browser: QWebEngineView):
        """
        Инициализирует инжектор BrowserMCP.
        
        Args:
            browser: Экземпляр встроенного браузера
        """
        self.browser = browser
        self.mcp_server_url = "http://localhost:9009"
        self.connected = False
        self.injected = False
        
    async def inject(self) -> bool:
        """
        Внедряет JavaScript-код BrowserMCP в встроенный браузер.
        
        Returns:
            bool: True, если внедрение прошло успешно
        """
        try:
            # Проверяем, настроен ли BrowserMCP
            setup = get_browsermcp_setup()
            if not setup.mcp_server_running:
                logger.warning("MCP сервер не запущен. Внедрение BrowserMCP невозможно.")
                return False
                
            # Внедряем JavaScript-код BrowserMCP
            logger.info("Внедрение JavaScript-кода BrowserMCP...")
            
            # Получаем JavaScript-код для внедрения
            js_code = self._get_injection_code()
            
            # Внедряем код в браузер
            self._inject_script(js_code)
            
            # Устанавливаем флаг внедрения
            self.injected = True
            
            # Подключаемся к MCP серверу
            if await self.connect():
                logger.info("BrowserMCP успешно внедрен и подключен.")
                return True
                
            logger.warning("BrowserMCP внедрен, но не подключен к MCP серверу.")
            return False
        except Exception as e:
            logger.error(f"Ошибка при внедрении BrowserMCP: {str(e)}")
            return False
            
    async def connect(self) -> bool:
        """
        Подключается к MCP серверу.
        
        Returns:
            bool: True, если подключение прошло успешно
        """
        try:
            # Проверяем, внедрен ли BrowserMCP
            if not self.injected:
                logger.warning("BrowserMCP не внедрен. Подключение невозможно.")
                return False
                
            # Выполняем JavaScript-код для подключения к MCP серверу
            logger.info("Подключение к MCP серверу...")
            
            # Выполняем JavaScript-код для подключения
            js_code = f"""
            if (window.browsermcp) {{
                window.browsermcp.connect('{self.mcp_server_url}');
                true;
            }} else {{
                false;
            }}
            """
            
            # Выполняем код и получаем результат
            result = await self._execute_js(js_code)
            
            # Проверяем результат
            if result:
                self.connected = True
                logger.info("Подключение к MCP серверу успешно установлено.")
                return True
                
            logger.warning("Не удалось подключиться к MCP серверу.")
            return False
        except Exception as e:
            logger.error(f"Ошибка при подключении к MCP серверу: {str(e)}")
            return False
            
    async def execute_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Выполняет команду BrowserMCP.
        
        Args:
            command: Команда для выполнения
            args: Аргументы команды
            
        Returns:
            Dict: Результат выполнения команды
        """
        try:
            # Проверяем, подключен ли BrowserMCP
            if not self.connected:
                logger.warning("BrowserMCP не подключен. Выполнение команды невозможно.")
                return {
                    "success": False,
                    "message": "BrowserMCP не подключен",
                    "data": {}
                }
                
            # Формируем JavaScript-код для выполнения команды
            args_json = json.dumps(args or {})
            js_code = f"""
            (async function() {{
                try {{
                    if (!window.browsermcp) {{
                        return {{
                            success: false,
                            message: "BrowserMCP не найден",
                            data: {{}}
                        }};
                    }}
                    
                    const result = await window.browsermcp.execute('{command}', {args_json});
                    return {{
                        success: true,
                        message: "Команда успешно выполнена",
                        data: result
                    }};
                }} catch (error) {{
                    return {{
                        success: false,
                        message: error.message,
                        data: {{}}
                    }};
                }}
            }})();
            """
            
            # Выполняем код и получаем результат
            result = await self._execute_js(js_code)
            
            # Проверяем результат
            if isinstance(result, dict):
                return result
                
            logger.warning(f"Неожиданный результат выполнения команды: {result}")
            return {
                "success": False,
                "message": f"Неожиданный результат: {result}",
                "data": {}
            }
        except Exception as e:
            logger.error(f"Ошибка при выполнении команды BrowserMCP: {str(e)}")
            return {
                "success": False,
                "message": f"Ошибка: {str(e)}",
                "data": {}
            }
            
    def _get_injection_code(self) -> str:
        """
        Возвращает JavaScript-код для внедрения BrowserMCP.
        
        Returns:
            str: JavaScript-код для внедрения
        """
        # Базовый код для внедрения BrowserMCP
        return """
        (function() {
            // Проверяем, что BrowserMCP еще не внедрен
            if (window.browsermcp) {
                return;
            }
            
            // Создаем объект BrowserMCP
            window.browsermcp = {
                connected: false,
                serverUrl: null,
                
                // Подключение к MCP серверу
                connect: async function(serverUrl) {
                    this.serverUrl = serverUrl;
                    
                    try {
                        // Проверяем доступность сервера
                        const response = await fetch(`${serverUrl}/health`);
                        if (response.ok) {
                            this.connected = true;
                            console.log(`Connected to MCP server at ${serverUrl}`);
                            return true;
                        } else {
                            console.error(`Failed to connect to MCP server at ${serverUrl}`);
                            return false;
                        }
                    } catch (error) {
                        console.error(`Error connecting to MCP server: ${error.message}`);
                        return false;
                    }
                },
                
                // Выполнение команды
                execute: async function(command, args) {
                    if (!this.connected) {
                        throw new Error('Not connected to MCP server');
                    }
                    
                    try {
                        // Формируем URL для команды
                        const url = `${this.serverUrl}/api/${command}`;
                        
                        // Выполняем запрос
                        const response = await fetch(url, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(args || {})
                        });
                        
                        // Проверяем ответ
                        if (response.ok) {
                            const result = await response.json();
                            return result;
                        } else {
                            const error = await response.text();
                            throw new Error(`MCP server error: ${error}`);
                        }
                    } catch (error) {
                        console.error(`Error executing command ${command}: ${error.message}`);
                        throw error;
                    }
                }
            };
            
            console.log('BrowserMCP injected');
        })();
        """
        
    def _inject_script(self, js_code: str):
        """
        Внедряет JavaScript-код в браузер.
        
        Args:
            js_code: JavaScript-код для внедрения
        """
        # Получаем страницу браузера
        page = self.browser.page()
        
        # Создаем скрипт
        script = QWebEngineScript()
        script.setSourceCode(js_code)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setRunsOnSubFrames(True)
        
        # Добавляем скрипт на страницу
        page.scripts().insert(script)
        
    async def _execute_js(self, js_code: str) -> Any:
        """
        Выполняет JavaScript-код в браузере и возвращает результат.
        
        Args:
            js_code: JavaScript-код для выполнения
            
        Returns:
            Any: Результат выполнения JavaScript-кода
        """
        # Получаем страницу браузера
        page = self.browser.page()
        
        # Создаем future для получения результата
        future = asyncio.Future()
        
        # Выполняем JavaScript-код
        page.runJavaScript(js_code, 0, lambda result: future.set_result(result))
        
        # Ждем результат
        return await future

# Словарь инжекторов для браузеров
_injectors = {}

def get_injector(browser: QWebEngineView) -> BrowserMCPInjector:
    """
    Возвращает инжектор BrowserMCP для указанного браузера.
    
    Args:
        browser: Экземпляр встроенного браузера
        
    Returns:
        BrowserMCPInjector: Инжектор BrowserMCP
    """
    global _injectors
    browser_id = id(browser)
    if browser_id not in _injectors:
        _injectors[browser_id] = BrowserMCPInjector(browser)
    return _injectors[browser_id]

async def inject_browsermcp(browser: QWebEngineView) -> bool:
    """
    Внедряет функциональность BrowserMCP в указанный браузер.
    
    Args:
        browser: Экземпляр встроенного браузера
        
    Returns:
        bool: True, если внедрение прошло успешно
    """
    injector = get_injector(browser)
    return await injector.inject()

async def execute_browsermcp_command(browser: QWebEngineView, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Выполняет команду BrowserMCP в указанном браузере.
    
    Args:
        browser: Экземпляр встроенного браузера
        command: Команда для выполнения
        args: Аргументы команды
        
    Returns:
        Dict: Результат выполнения команды
    """
    injector = get_injector(browser)
    if not injector.connected:
        await injector.inject()
    return await injector.execute_command(command, args)
