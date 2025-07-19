"""
MCP Tools Integration для GopiAI

Этот модуль обеспечивает интеграцию с инструментами MCP (Model Context Protocol)
через модуль mcp.client.streamable_http.

Модуль предоставляет функциональность для подключения к MCP серверам
и использования их инструментов в CrewAI без зависимостей от crewai-tools.
"""

import os
import logging
import asyncio
import json
import httpx
import subprocess
import time
import signal
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Union, Callable, Awaitable

# Используем streamable_http для подключения к MCP серверам
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import JSONRPCRequest, JSONRPCResponse, JSONRPCNotification

# Инициализируем логгер
logger = logging.getLogger(__name__)

class MCPToolsManager:
    """
    Менеджер инструментов MCP для интеграции с CrewAI.
    
    Позволяет получать инструменты с нескольких MCP серверов
    и использовать их в CrewAI через streamable_http_client.
    """
    
    # Локальные MCP серверы (прямая интеграция без Smithery)
    LOCAL_MCP_SERVERS = [
        {
            "name": "mcp-think-tank",
            "type": "local",
            "path": "mcp-think-tank",
            "port": 3399,
            "url": "http://localhost:3399",
            "description": "Structured thinking and knowledge management tool"
        },
        {
            "name": "agentic-control-framework", 
            "type": "local",
            "path": "agentic-control-framework",
            "port": 8002,
            "url": "http://localhost:8002/mcp",
            "description": "Production-ready agentic control framework with 79+ verified tools"
        }
    ]
    
    # Устаревшие Smithery серверы (отключены)
    MCP_SERVERS = []
    
    def __init__(self):
        """Инициализация менеджера MCP инструментов."""
        # Путь к директории с локальными MCP серверами
        self.base_path = Path(__file__).parent
        
        # Основные структуры данных
        self.server_clients = {}  # Словарь клиентов HTTP для серверов
        self.server_tools = {}    # Словарь инструментов, доступных на каждом сервере
        self.initialized_servers = set()  # Множество инициализированных серверов
        self.all_tools = []  # Список всех инструментов со всех серверов
        self.tools_by_server = {}  # Словарь инструментов по серверам
        self.connected_servers = set()  # Множество подключенных серверов
        
        # Процессы локальных MCP серверов
        self.local_server_processes = {}  # Словарь процессов серверов
        
        logger.info("Менеджер MCP инструментов инициализирован для локальных серверов")
        
    def initialize(self):
        """
        Инициализирует менеджер MCP инструментов и подключается к доступным серверам.
        
        Returns:
            bool: True если инициализация прошла успешно, иначе False.
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.initialize_async())
    
    async def start_local_server(self, server_config: Dict) -> bool:
        """
        Запускает локальный MCP сервер.
        
        Args:
            server_config: Конфигурация сервера.
            
        Returns:
            True если сервер запущен успешно, иначе False.
        """
        server_name = server_config["name"]
        server_path = self.base_path / server_config["path"]
        port = server_config["port"]
        
        if server_name in self.local_server_processes:
            logger.info(f"Сервер {server_name} уже запущен")
            return True
            
        if not server_path.exists():
            logger.error(f"Путь к серверу {server_name} не найден: {server_path}")
            return False
            
        try:
            # Определяем команду запуска в зависимости от сервера
            if server_name == "mcp-think-tank":
                # Для mcp-think-tank используем npx с явным указанием HTTP режима
                cmd = ["npx", "-y", "mcp-think-tank@2.0.7", "--transport", "http", "--port", str(port)]
                env = os.environ.copy()
                # Добавляем переменные окружения для mcp-think-tank
                env["MEMORY_PATH"] = str(self.base_path / "mcp-think-tank" / "memory.jsonl")
                env["MCP_DEBUG"] = "true"  # Включаем отладку
                env["LOG_LEVEL"] = "debug"  # Максимальная отладка
            elif server_name == "agentic-control-framework":
                # Для ACF сначала устанавливаем зависимости, затем запускаем
                # Проверяем наличие node_modules и sharp
                node_modules_path = server_path / "node_modules"
                sharp_path = node_modules_path / "sharp"
                
                # Если sharp не работает, полностью переустанавливаем
                if not node_modules_path.exists() or sharp_path.exists():
                    logger.info(f"Полная переустановка зависимостей для {server_name}...")
                    
                    # Удаляем node_modules если существует
                    if node_modules_path.exists():
                        import shutil
                        logger.info(f"Удаляем старые node_modules...")
                        shutil.rmtree(str(node_modules_path), ignore_errors=True)
                    
                    # Чистая установка
                    logger.info(f"Чистая установка зависимостей...")
                    install_process = subprocess.run(
                        ["npm", "install", "--force"],
                        cwd=str(server_path),
                        capture_output=True,
                        text=True,
                        shell=True
                    )
                    if install_process.returncode != 0:
                        logger.error(f"Ошибка установки зависимостей: {install_process.stderr}")
                        return False
                    
                    # Отдельно устанавливаем sharp с правильными параметрами
                    logger.info(f"Устанавливаем sharp для Windows x64...")
                    sharp_process = subprocess.run(
                        ["npm", "install", "--force", "--platform=win32", "--arch=x64", "sharp"],
                        cwd=str(server_path),
                        capture_output=True,
                        text=True,
                        shell=True
                    )
                    if sharp_process.returncode != 0:
                        logger.warning(f"Предупреждение при установке sharp: {sharp_process.stderr}")
                        
                        # Попытка альтернативного способа
                        logger.info(f"Попытка альтернативной установки sharp...")
                        alt_process = subprocess.run(
                            ["npm", "install", "--include=optional", "sharp"],
                            cwd=str(server_path),
                            capture_output=True,
                            text=True,
                            shell=True
                        )
                        if alt_process.returncode != 0:
                            logger.error(f"Не удалось установить sharp: {alt_process.stderr}")
                        
                cmd = ["node", "bin/agentic-control-framework-mcp"]
                env = os.environ.copy()
                env["MCP_PORT"] = str(port)
                env["WORKSPACE_ROOT"] = str(self.base_path.parent.parent)
            else:
                logger.error(f"Неизвестный сервер: {server_name}")
                return False
                
            logger.info(f"Запускаем сервер {server_name} на порту {port}...")
            
            # Запускаем процесс (shell=True важен для npx на Windows)
            process = subprocess.Popen(
                cmd,
                cwd=str(server_path) if server_name != "mcp-think-tank" else None,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True  # Важно для Windows и npx
            )
            
            # Сохраняем процесс
            self.local_server_processes[server_name] = process
            
            # Ждем немного, чтобы сервер запустился
            await asyncio.sleep(3)
            
            # Проверяем, что процесс еще работает
            if process.poll() is None:
                logger.info(f"Сервер {server_name} успешно запущен на порту {port}")
                return True
            else:
                # Процесс завершился, получаем ошибку
                stdout, stderr = process.communicate()
                logger.error(f"Ошибка запуска сервера {server_name}: {stderr}")
                del self.local_server_processes[server_name]
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при запуске сервера {server_name}: {e}")
            return False
    
    def stop_local_server(self, server_name: str) -> bool:
        """
        Останавливает локальный MCP сервер.
        
        Args:
            server_name: Имя сервера.
            
        Returns:
            True если сервер остановлен успешно, иначе False.
        """
        if server_name not in self.local_server_processes:
            logger.warning(f"Сервер {server_name} не запущен")
            return True
            
        try:
            process = self.local_server_processes[server_name]
            process.terminate()
            
            # Ждем немного для корректного завершения
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Если процесс не завершился, принудительно убиваем
                process.kill()
                process.wait()
                
            del self.local_server_processes[server_name]
            logger.info(f"Сервер {server_name} остановлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при остановке сервера {server_name}: {e}")
            return False
    
    async def initialize_async(self) -> bool:
        """
        Асинхронная версия метода initialize.
        
        Returns:
            bool: True если инициализация прошла успешно, иначе False.
        """
        try:
            # Запускаем и подключаемся к локальным MCP серверам
            servers_info = await self.connect_to_local_servers()
            return len(servers_info) > 0
        except Exception as e:
            logger.error(f"Ошибка при инициализации MCP инструментов: {e}")
            return False
    
    async def connect_to_server(self, server_url: str) -> bool:
        """
        Подключается к локальному MCP серверу.
        
        Args:
            server_url: URL MCP сервера.
            
        Returns:
            True если подключение успешно, False в противном случае.
        """
        if server_url in self.server_clients:
            return True
            
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "GopiAI-MCP-Client/1.0",
            "Accept": "application/json"
        }
        
        try:
            # Для локальных MCP серверов используем обычный HTTP клиент
            client = httpx.AsyncClient(
                headers=headers,
                timeout=30.0
            )
            
            # Проверяем доступность сервера
            try:
                test_response = await client.get(server_url.replace('/mcp', '/health'), timeout=5.0)
                logger.info(f"Проверка доступности {server_url}: {test_response.status_code}")
            except:
                # Если health endpoint недоступен, продолжаем
                logger.info(f"Проверка доступности {server_url}: health endpoint недоступен, продолжаем")
            
            self.server_clients[server_url] = client
            self.connected_servers.add(server_url)
            logger.info(f"Успешное подключение к MCP серверу {server_url}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при подключении к MCP серверу {server_url}: {e}")
            return False
    
    async def initialize_server(self, server_url: str) -> bool:
        """
        Инициализирует подключение к серверу и получает список его инструментов.
        
        Args:
            server_url: URL MCP сервера.
            
        Returns:
            True если инициализация прошла успешно, False в противном случае.
        """
        if server_url in self.initialized_servers:
            return True
            
        try:
            if not await self.connect_to_server(server_url):
                return False
                
            # Получаем список инструментов
            tools = await self.get_server_tools_by_url(server_url)
            if tools:
                self.initialized_servers.add(server_url)
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при инициализации сервера {server_url}: {e}")
            return False
    
    async def connect_to_local_servers(self) -> Dict[str, List[Dict]]:
        """
        Запускает и подключается ко всем локальным MCP серверам.
        
        Returns:
            Словарь с названиями серверов и списками их инструментов.
        """
        result = {}
        
        for server_config in self.LOCAL_MCP_SERVERS:
            server_name = server_config["name"]
            
            try:
                # Запускаем локальный сервер
                if await self.start_local_server(server_config):
                    # Подключаемся к серверу
                    server_url = server_config["url"]
                    if await self.connect_to_server(server_url):
                        # Получаем инструменты
                        tools = await self.get_server_tools_by_url(server_url)
                        if tools:
                            result[server_name] = tools
                            self.server_tools[server_url] = tools
                            logger.info(f"Успешно подключен к {server_name}: {len(tools)} инструментов")
                        else:
                            logger.warning(f"Не удалось получить инструменты с {server_name}")
                    else:
                        logger.error(f"Не удалось подключиться к {server_name}")
                else:
                    logger.error(f"Не удалось запустить {server_name}")
                    
            except Exception as e:
                logger.error(f"Ошибка при работе с сервером {server_name}: {e}")
        
        return result
        
    async def get_server_tools_by_url(self, server_url: str) -> List[Dict]:
        """
        Получает список инструментов с указанного MCP сервера через Streamable HTTP.
        
        Args:
            server_url: URL сервера.
            
        Returns:
            Список инструментов сервера или пустой список, если сервер недоступен.
        """
        if server_url not in self.server_clients:
            if not await self.connect_to_server(server_url):
                return []
                
        try:
            # Создаем JSON-RPC запрос для получения списка инструментов
            request_data = {
                "jsonrpc": "2.0",
                "id": "list_tools_request",
                "method": "tools/list",
                "params": {}
            }
            
            # Отправляем POST запрос к Smithery API
            client = self.server_clients[server_url]
            
            # Отладочная информация
            logger.info(f"Отправляем запрос к {server_url}")
            logger.info(f"Заголовки: {dict(client.headers)}")
            
            response = await client.post(server_url, json=request_data)
            
            # Логируем полный ответ
            logger.info(f"Ответ от сервера: {response.status_code}")
            if response.status_code != 200:
                logger.info(f"Тело ответа: {response.text[:500]}")
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "result" in response_data and "tools" in response_data["result"]:
                    # Преобразуем информацию об инструментах в более удобный формат
                    tools = []
                    for tool in response_data["result"]["tools"]:
                        tools.append({
                            "id": tool.get("name", ""),
                            "name": tool.get("name", ""),
                            "description": tool.get("description", ""),
                            "server_url": server_url,
                            "schema": tool.get("inputSchema", {})
                        })
                    
                    # Сохраняем список инструментов для сервера
                    self.server_tools[server_url] = tools
                    logger.info(f"Получено {len(tools)} инструментов с сервера {server_url}")
                    return tools
                
                return []
            else:
                logger.warning(f"Получен статус {response.status_code} от сервера {server_url}")
                return []
                
        except Exception as e:
            logger.error(f"Ошибка при получении инструментов с сервера {server_url}: {e}")
            return []
    
    async def get_all_tools(self) -> List[Dict]:
        """
        Получает все инструменты со всех доступных MCP серверов.
        
        Returns:
            Список всех инструментов со всех серверов.
        """
        all_tools = []
        
        # Если еще нет подключенных серверов, подключаемся
        if not self.server_tools:
            await self.connect_to_all_servers()
            
        # Собираем инструменты со всех серверов
        for server_url, tools in self.server_tools.items():
            all_tools.extend(tools)
            
        return all_tools
        
    def get_tool_by_name(self, tool_name: str) -> Optional[Dict]:
        """
        Находит инструмент по его имени среди всех серверов.
        
        Args:
            tool_name: Имя инструмента для поиска.
            
        Returns:
            Инструмент с указанным именем или None, если не найден.
        """
        try:
            # Метод поиска через асинхронные операции
            async def search_tool() -> Optional[Dict]:
                tools = await self.get_all_tools()
                for tool in tools:
                    if tool["name"].lower() == tool_name.lower():
                        return tool
                return None
            
            # Запускаем поиск в асинхронном режиме
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(search_tool())
        except Exception as e:
            logger.error(f"Ошибка при поиске инструмента {tool_name}: {e}")
            return None
        
    async def execute_tool_async(self, tool: Dict, **kwargs) -> Dict:
        """
        Выполняет вызов инструмента MCP с заданными параметрами через Streamable HTTP.
        
        Args:
            tool: Информация об инструменте MCP для выполнения.
            **kwargs: Параметры для вызова инструмента.
            
        Returns:
            Результат выполнения инструмента.
        """
        server_url = tool.get("server_url")
        tool_name = tool.get("name")
        
        if not server_url or not tool_name:
            logger.error("Неверная информация об инструменте")
            return {"error": "Неверная информация об инструменте"}
            
        if server_url not in self.server_clients:
            if not await self.connect_to_server(server_url):
                return {"error": f"Не удалось подключиться к серверу {server_url}"}
                
        try:
            # Подготавливаем параметры для вызова инструмента
            params = {
                "name": tool_name,
                "arguments": kwargs
            }
            
            # Создаем JSON-RPC запрос для выполнения инструмента
            request = JSONRPCRequest(
                id=f"execute_{tool_name}",
                method="tools/call",
                params=params
            )
            
            # Отправляем POST запрос к Smithery API
            client = self.server_clients[server_url]
            request_data = {
                "jsonrpc": "2.0",
                "id": f"execute_{tool_name}",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": kwargs
                }
            }
            response = await client.post(server_url, json=request_data)
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "result" in response_data:
                    return response_data["result"]
                elif "error" in response_data:
                    return {"error": response_data["error"]}
                else:
                    return {"error": "Неожиданный формат ответа"}
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            logger.error(f"Ошибка при выполнении инструмента {tool.get('name', '')}: {e}")
            return {"error": str(e)}
            
    def execute_tool(self, tool: Dict, **kwargs) -> Dict:
        """
        Выполняет вызов инструмента MCP с заданными параметрами.
        
        Args:
            tool: Информация об инструменте MCP для выполнения.
            **kwargs: Параметры для вызова инструмента.
            
        Returns:
            Результат выполнения инструмента.
        """
        try:
            # Запускаем выполнение в асинхронном режиме
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(self.execute_tool_async(tool, **kwargs))
        except Exception as e:
            logger.error(f"Ошибка при выполнении инструмента {tool.get('name', '')}: {e}")
            return {"error": str(e)}
    
    def disconnect_from_all_servers(self) -> bool:
        """
        Отключается от всех серверов MCP.
        
        Returns:
            True, если все отключения успешны, иначе False.
        """
        all_success = True
        
        # Создаем копию множества, чтобы избежать ошибки при изменении во время итерации
        servers_to_disconnect = set(self.connected_servers)
        
        for server_url in servers_to_disconnect:
            success = self.disconnect_from_server(server_url)
            all_success = all_success and success
        
        if all_success:
            logger.info("Отключение от всех серверов MCP выполнено успешно")
        else:
            logger.warning("Не удалось корректно отключиться от некоторых серверов MCP")
        
        return all_success
        
    async def disconnect_from_server_async(self, server_url: str) -> bool:
        """
        Асинхронно отключается от указанного MCP сервера.
        
        Args:
            server_url: URL сервера для отключения.
            
        Returns:
            True если отключение успешно, False в противном случае.
        """
        try:
            if server_url in self.server_clients:
                client = self.server_clients[server_url]
                await client.close()
                del self.server_clients[server_url]
                self.connected_servers.discard(server_url)
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при отключении от сервера {server_url}: {e}")
            return False
    
    def disconnect_from_server(self, server_url: str) -> bool:
        """
        Отключается от указанного MCP сервера.
        
        Args:
            server_url: URL сервера для отключения.
            
        Returns:
            True если отключение успешно, False в противном случае.
        """
        try:
            # Запускаем отключение в асинхронном режиме
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(self.disconnect_from_server_async(server_url))
        except Exception as e:
            logger.error(f"Ошибка при отключении от сервера {server_url}: {e}")
            return False
    
    def __del__(self):
        """Деструктор для корректного закрытия всех соединений и остановки локальных серверов."""
        try:
            # Останавливаем все локальные серверы
            for server_name in list(self.local_server_processes.keys()):
                self.stop_local_server(server_name)
            
            # Закрываем соединения
            self.disconnect_from_all_servers()
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединений в деструкторе: {e}")

# Синглтон для повторного использования менеджера
_mcp_tools_manager_instance = None

def get_mcp_tools_manager() -> Optional[MCPToolsManager]:
    """
    Возвращает экземпляр менеджера MCP инструментов.
    
    Returns:
        Экземпляр менеджера MCP инструментов или None, если менеджер не может быть создан.
    """
    global _mcp_tools_manager_instance
    try:
        if _mcp_tools_manager_instance is None:
            _mcp_tools_manager_instance = MCPToolsManager()
        return _mcp_tools_manager_instance
    except Exception as e:
        logger.error(f"Ошибка при создании менеджера MCP инструментов: {e}")
        return None

def get_mcp_tools_info() -> str:
    """
    Получает информацию о доступных инструментах MCP для использования в промптах.
    
    Returns:
        Строка с информацией о доступных инструментах MCP.
    """
    manager = get_mcp_tools_manager()
    if not manager:
        return "Менеджер MCP недоступен"
    
    try:
        # Получаем информацию о локальных серверах
        local_servers_info = []
        for server_config in manager.LOCAL_MCP_SERVERS:
            server_name = server_config["name"]
            description = server_config["description"]
            status = "запущен" if server_name in manager.local_server_processes else "остановлен"
            local_servers_info.append(f"- {server_name}: {description} ({status})")
        
        if not local_servers_info:
            return "Локальные MCP серверы не настроены"
        
        servers_info = "\n".join(local_servers_info)
        return f"""Локальные MCP серверы:
{servers_info}

Для получения списка инструментов необходимо запустить серверы."""
        
    except Exception as e:
        logger.error(f"Ошибка при получении информации об инструментах MCP: {e}")
        return f"Ошибка при получении информации об инструментах MCP: {e}"
