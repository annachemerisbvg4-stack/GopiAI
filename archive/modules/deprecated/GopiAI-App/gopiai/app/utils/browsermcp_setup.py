#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль для автоматической установки и запуска BrowserMCP.

Предоставляет функции для установки и запуска MCP сервера,
а также для инъекции функциональности BrowserMCP в встроенный браузер.
"""

import asyncio
import os
import shutil
import subprocess
import sys
import tempfile

from gopiai.core.logging import get_logger
logger = get_logger().logger


class BrowserMCPSetup:
    """Класс для настройки BrowserMCP."""
    
    def __init__(self):
        """Инициализирует настройку BrowserMCP."""
        self.mcp_server_process = None
        self.mcp_server_url = "http://localhost:9009"
        self.mcp_server_running = False
        self.mcp_installed = False
        self.temp_dir = None
        
    async def setup(self) -> bool:
        """
        Настраивает BrowserMCP.
        
        Returns:
            bool: True, если настройка прошла успешно
        """
        try:
            # Проверяем, установлен ли npm
            if not self._check_npm():
                # Если npm не установлен, пытаемся установить его
                if not await self._install_npm():
                    logger.warning("Не удалось установить npm. BrowserMCP не будет доступен.")
                    return False
            
            # Проверяем, установлен ли BrowserMCP
            if not self._is_mcp_installed():
                # Если BrowserMCP не установлен, пытаемся установить его
                if not await self._install_mcp():
                    logger.warning("Не удалось установить BrowserMCP. BrowserMCP не будет доступен.")
                    return False
                    
            self.mcp_installed = True
            
            # Проверяем, запущен ли MCP сервер
            if not await self._is_mcp_server_running():
                # Если MCP сервер не запущен, пытаемся запустить его
                if not await self._start_mcp_server():
                    logger.warning("Не удалось запустить MCP сервер. BrowserMCP не будет доступен.")
                    return False
                    
            self.mcp_server_running = True
            
            logger.info("BrowserMCP успешно настроен.")
            return True
        except Exception as e:
            logger.error(f"Ошибка при настройке BrowserMCP: {str(e)}")
            return False
            
    def _check_npm(self) -> bool:
        """
        Проверяет, установлен ли npm.
        
        Returns:
            bool: True, если npm установлен
        """
        try:
            subprocess.run(
                ["npm", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info("npm установлен.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("npm не установлен.")
            return False
            
    async def _install_npm(self) -> bool:
        """
        Устанавливает npm.
        
        Returns:
            bool: True, если установка прошла успешно
        """
        logger.info("Установка npm...")
        
        # В тестовом режиме просто возвращаем False
        logger.warning("Пропускаем установку npm в тестовом режиме")
        return False
        
        # Создаем временную директорию
        self.temp_dir = tempfile.mkdtemp()
        
        try:
            # Скачиваем Node.js
            node_url = "https://nodejs.org/dist/v18.16.0/node-v18.16.0-win-x64.zip"
            node_zip = os.path.join(self.temp_dir, "node.zip")
            
            # Скачиваем Node.js с помощью curl
            subprocess.run(
                ["curl", "-L", node_url, "-o", node_zip],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Распаковываем Node.js
            import zipfile
            with zipfile.ZipFile(node_zip, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
                
            # Добавляем Node.js в PATH
            node_bin = os.path.join(self.temp_dir, "node-v18.16.0-win-x64")
            os.environ["PATH"] = node_bin + os.pathsep + os.environ["PATH"]
            
            # Проверяем, установлен ли npm
            if self._check_npm():
                logger.info("npm успешно установлен.")
                return True
                
            logger.warning("Не удалось установить npm.")
            return False
        except Exception as e:
            logger.error(f"Ошибка при установке npm: {str(e)}")
            return False
            
    def _is_mcp_installed(self) -> bool:
        """
        Проверяет, установлен ли BrowserMCP.
        
        Returns:
            bool: True, если BrowserMCP установлен
        """
        try:
            # Проверяем наличие пакета @browsermcp/mcp
            result = subprocess.run(
                ["npm", "list", "-g", "@browsermcp/mcp"],
                capture_output=True,
                text=True
            )
            
            if "@browsermcp/mcp" in result.stdout:
                logger.info("BrowserMCP установлен глобально.")
                return True
                
            # Проверяем наличие локального пакета
            result = subprocess.run(
                ["npm", "list", "@browsermcp/mcp"],
                capture_output=True,
                text=True
            )
            
            if "@browsermcp/mcp" in result.stdout:
                logger.info("BrowserMCP установлен локально.")
                return True
                
            logger.warning("BrowserMCP не найден.")
            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке установки BrowserMCP: {str(e)}")
            return False
            
    async def _install_mcp(self) -> bool:
        """
        Устанавливает BrowserMCP.
        
        Returns:
            bool: True, если установка прошла успешно
        """
        logger.info("Установка BrowserMCP...")
        
        try:
            # Устанавливаем BrowserMCP
            subprocess.run(
                ["npm", "install", "-g", "@browsermcp/mcp"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Проверяем, установлен ли BrowserMCP
            if self._is_mcp_installed():
                logger.info("BrowserMCP успешно установлен.")
                return True
                
            logger.warning("Не удалось установить BrowserMCP.")
            return False
        except Exception as e:
            logger.error(f"Ошибка при установке BrowserMCP: {str(e)}")
            return False
            
    async def _is_mcp_server_running(self) -> bool:
        """
        Проверяет, запущен ли MCP сервер.
        
        Returns:
            bool: True, если MCP сервер запущен
        """
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"{self.mcp_server_url}/health", timeout=2) as response:
                        if response.status == 200:
                            logger.info("MCP сервер запущен.")
                            return True
                except:
                    pass
                    
            logger.info("MCP сервер не запущен.")
            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке статуса MCP сервера: {str(e)}")
            return False
            
    async def _start_mcp_server(self) -> bool:
        """
        Запускает MCP сервер.
        
        Returns:
            bool: True, если MCP сервер успешно запущен
        """
        try:
            # Запускаем MCP сервер
            logger.info("Запуск MCP сервера...")
            
            # Определяем команду для запуска сервера
            if sys.platform == "win32":
                # На Windows используем start /b
                cmd = ["npx", "@browsermcp/mcp"]
                self.mcp_server_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                # На Unix-подобных системах используем nohup
                cmd = ["npx", "@browsermcp/mcp"]
                self.mcp_server_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            # Ждем запуска сервера
            for _ in range(10):
                if await self._is_mcp_server_running():
                    logger.info("MCP сервер успешно запущен.")
                    return True
                await asyncio.sleep(1)
                
            logger.warning("Таймаут при запуске MCP сервера.")
            return False
        except Exception as e:
            logger.error(f"Ошибка при запуске MCP сервера: {str(e)}")
            return False
            
    def cleanup(self):
        """Очищает ресурсы."""
        try:
            # Останавливаем MCP сервер
            if self.mcp_server_process:
                self.mcp_server_process.terminate()
                self.mcp_server_process = None
                self.mcp_server_running = False
                
            # Удаляем временную директорию
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
                
            logger.info("Ресурсы BrowserMCP очищены.")
        except Exception as e:
            logger.error(f"Ошибка при очистке ресурсов BrowserMCP: {str(e)}")

# Глобальный экземпляр настройки BrowserMCP
_browsermcp_setup = None

def get_browsermcp_setup() -> BrowserMCPSetup:
    """
    Возвращает глобальный экземпляр настройки BrowserMCP.
    
    Returns:
        BrowserMCPSetup: Экземпляр настройки BrowserMCP
    """
    global _browsermcp_setup
    if _browsermcp_setup is None:
        _browsermcp_setup = BrowserMCPSetup()
    return _browsermcp_setup

async def setup_browsermcp() -> bool:
    """
    Настраивает BrowserMCP.
    
    Returns:
        bool: True, если настройка прошла успешно
    """
    setup = get_browsermcp_setup()
    return await setup.setup()

def cleanup_browsermcp():
    """Очищает ресурсы BrowserMCP."""
    setup = get_browsermcp_setup()
    setup.cleanup()
