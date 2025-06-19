"""
Claude Tools Handler для GopiAI
==============================

Профессиональная система инструментов для интеграции Claude AI с браузерной автоматизацией
через QWebEngineView, основанная на best practices.

Адаптировано из профессионального руководства по Claude Tools + puter.js + QWebEngineView
для архитектуры GopiAI.
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import os
import urllib.request
import urllib.parse
import urllib.error

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeToolsHandler(QObject):
    """
    Основной класс для обработки инструментов Claude AI.
    Предоставляет систему browser automation, file operations и script execution.
    """
    
    # Сигналы для асинхронной связи
    tool_executed = Signal(str, str, str)  # request_id, tool_name, result_json
    tool_error = Signal(str, str, str)     # request_id, tool_name, error_message
    
    # Безопасность: разрешенные домены для навигации
    ALLOWED_DOMAINS = [
        'localhost',
        '127.0.0.1',
        'puter.com',
        'github.com',
        'stackoverflow.com',
        'google.com',
        'bing.com',
        'duckduckgo.com',
        'weather.com',
        'accuweather.com',
        'weather.gov',
        'openweathermap.org'
    ]
    
    def __init__(self, web_view: QWebEngineView, parent=None):
        super().__init__(parent)
        self.web_view = web_view
        self._pending_requests: Dict[str, Dict[str, Any]] = {}
        
        logger.info("ClaudeToolsHandler initialized")
    
    def _generate_request_id(self) -> str:
        """Генерация уникального ID для отслеживания асинхронных запросов"""
        return str(uuid.uuid4())
    
    def _is_url_allowed(self, url: str) -> bool:
        """Проверка, разрешен ли URL для навигации"""
        if not url or not isinstance(url, str):
            return False
        
        # Разрешаем file:// URLs для локальных файлов
        if url.startswith('file://'):
            return True
        
        # Разрешаем about: URLs
        if url.startswith('about:'):
            return True
        
        # Проверяем домены
        for domain in self.ALLOWED_DOMAINS:
            if domain in url.lower():
                return True
        
        return False
    
    # ==============================================
    # BROWSER AUTOMATION TOOLS
    # ==============================================
    
    @Slot(str, str, result=str)
    def navigate_to_url(self, url: str, request_id: str = None) -> str:
        """Навигация по URL с проверкой безопасности"""
        if not request_id:
            request_id = self._generate_request_id()
        
        try:
            if not self._is_url_allowed(url):
                raise ValueError(f"URL not allowed: {url}")
            
            logger.info(f"Navigating to: {url}")
            self.web_view.setUrl(url)
            
            result = {
                "success": True,
                "action": "navigate",
                "url": url,
                "request_id": request_id
            }
            
            self.tool_executed.emit(request_id, "navigate_to_url", json.dumps(result))
            return json.dumps(result)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Navigation error: {error_msg}")
            
            error_result = {
                "success": False,
                "error": error_msg,
                "request_id": request_id
            }
            
            self.tool_error.emit(request_id, "navigate_to_url", error_msg)
            return json.dumps(error_result)
    
    @Slot(result=str)
    def get_current_url(self) -> str:
        """Получение текущего URL"""
        try:
            current_url = self.web_view.page().url().toString()
            result = {
                "success": True,
                "url": current_url,
                "action": "get_current_url"
            }
            return json.dumps(result)
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e)
            }
            return json.dumps(error_result)
    
    @Slot(result=str)
    def get_page_title(self) -> str:
        """Получение заголовка страницы"""
        try:
            title = self.web_view.page().title()
            result = {
                "success": True,
                "title": title,
                "action": "get_page_title"
            }
            return json.dumps(result)
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e)
            }
            return json.dumps(error_result)
    
    @Slot(str, str, result=str)
    def execute_javascript(self, script: str, request_id: str = None) -> str:
        """Выполнение JavaScript в браузере"""
        if not request_id:
            request_id = self._generate_request_id()
        
        try:
            logger.info(f"Executing JavaScript: {script[:100]}...")
            
            # Сохраняем информацию о запросе
            self._pending_requests[request_id] = {
                "tool": "execute_javascript",
                "script": script
            }
            
            # Создаем callback для обработки результата
            def script_callback(result):
                try:
                    # Безопасная обработка результата JavaScript
                    if result is None:
                        result_value = "null"
                    elif isinstance(result, (dict, list)):
                        result_value = json.dumps(result)
                    else:
                        result_value = str(result)
                    
                    result_data = {
                        "success": True,
                        "result": result_value,
                        "script": script[:100] + "..." if len(script) > 100 else script,
                        "request_id": request_id
                    }
                    
                    self.tool_executed.emit(request_id, "execute_javascript", json.dumps(result_data))
                    
                    # Удаляем из pending запросов
                    if request_id in self._pending_requests:
                        del self._pending_requests[request_id]
                        
                except Exception as e:
                    logger.error(f"JavaScript callback error: {e}")
                    self.tool_error.emit(request_id, "execute_javascript", str(e))
            
            # Оборачиваем script в функцию если он содержит return
            if 'return ' in script and not script.strip().startswith('(function'):
                wrapped_script = f"(function() {{ {script} }})()"
            else:
                wrapped_script = script
            
            # Выполняем JavaScript согласно Qt документации
            self.web_view.page().runJavaScript(wrapped_script, script_callback)
            
            # Возвращаем немедленный ответ о начале выполнения
            initial_result = {
                "success": True,
                "status": "executing",
                "request_id": request_id,
                "message": "JavaScript execution started asynchronously"
            }
            
            return json.dumps(initial_result)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"JavaScript execution error: {error_msg}")
            
            error_result = {
                "success": False,
                "error": error_msg,
                "request_id": request_id
            }
            
            self.tool_error.emit(request_id, "execute_javascript", error_msg)
            return json.dumps(error_result)
    
    @Slot(str, result=str)
    def get_page_source(self, request_id: str = None) -> str:
        """Получение HTML источника страницы"""
        if not request_id:
            request_id = self._generate_request_id()
        
        script = "document.documentElement.outerHTML;"
        return self.execute_javascript(script, request_id)
    
    @Slot(str, int, result=str)
    def wait_for_element(self, selector: str, timeout: int = 5000, request_id: str = None) -> str:
        """Ожидание появления элемента на странице"""
        if not request_id:
            request_id = self._generate_request_id()
        
        script = f"""
        new Promise((resolve, reject) => {{
            const timeout = {timeout};
            const startTime = Date.now();
            
            function checkElement() {{
                const element = document.querySelector('{selector}');
                if (element) {{
                    resolve({{
                        found: true,
                        selector: '{selector}',
                        tagName: element.tagName,
                        id: element.id,
                        className: element.className
                    }});
                }} else if (Date.now() - startTime > timeout) {{
                    resolve({{
                        found: false,
                        selector: '{selector}',
                        timeout: timeout
                    }});
                }} else {{
                    setTimeout(checkElement, 100);
                }}
            }}
            
            checkElement();
        }});
        """
        
        return self.execute_javascript(script, request_id)
    
    # ==============================================
    # SYSTEM TOOLS (по образцу из руководства)
    # ==============================================
    
    @Slot(str, result=str)
    def read_file(self, file_path: str) -> str:
        """Чтение файла с проверкой безопасности"""
        try:
            # Проверяем, что путь безопасен
            path = Path(file_path).resolve()
            
            # Ограничиваем доступ только к определенным директориям
            allowed_dirs = [
                Path.cwd(),  # Текущая директория
                Path.home() / "Documents",  # Документы пользователя
            ]
            
            if not any(str(path).startswith(str(allowed_dir)) for allowed_dir in allowed_dirs):
                raise PermissionError(f"Access denied to path: {path}")
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = {
                "success": True,
                "content": content,
                "file_path": str(path),
                "size": len(content)
            }
            
            logger.info(f"Read file: {path} ({len(content)} chars)")
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
            logger.error(f"Read file error: {e}")
            return json.dumps(error_result)
    
    @Slot(str, str, result=str)
    def write_file(self, file_path: str, content: str) -> str:
        """Запись файла с проверкой безопасности"""
        try:
            path = Path(file_path).resolve()
            
            # Проверяем безопасность пути (аналогично read_file)
            allowed_dirs = [
                Path.cwd(),
                Path.home() / "Documents",
            ]
            
            if not any(str(path).startswith(str(allowed_dir)) for allowed_dir in allowed_dirs):
                raise PermissionError(f"Access denied to path: {path}")
            
            # Создаем директорию если нужно
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result = {
                "success": True,
                "file_path": str(path),
                "size": len(content),
                "message": "File written successfully"
            }
            
            logger.info(f"Wrote file: {path} ({len(content)} chars)")
            return json.dumps(result)
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
            logger.error(f"Write file error: {e}")
            return json.dumps(error_result)
    
    @Slot(str, result=str)
    def run_script(self, command: str) -> str:
        """Выполнение системной команды (с ограничениями безопасности)"""
        try:
            # Белый список разрешенных команд
            allowed_commands = [
                'ls', 'dir', 'pwd', 'cd', 'echo', 'cat', 'head', 'tail',
                'python', 'node', 'npm', 'git'
            ]
            
            command_parts = command.split()
            if not command_parts or command_parts[0] not in allowed_commands:
                raise PermissionError(f"Command not allowed: {command_parts[0] if command_parts else 'empty'}")
            
            # Выполняем команду с timeout
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,  # 30 секунд timeout
                cwd=Path.cwd()
            )
            
            response = {
                "success": True,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
            logger.info(f"Executed command: {command} (return code: {result.returncode})")
            return json.dumps(response)
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "command": command
            }
            logger.error(f"Script execution error: {e}")
            return json.dumps(error_result)
    
    # ==============================================
    # RAG MEMORY INTEGRATION
    # ==============================================
    
    @Slot(str, int, result=str)
    def search_memory(self, query: str, limit: int = 5) -> str:
        """
        Поиск в RAG памяти через HTTP API.
        Интегрирует Claude Tools с системой памяти GopiAI.
        """
        try:
            # Валидация входных данных
            if not query or not query.strip():
                raise ValueError("Empty search query")
            
            if limit < 1 or limit > 20:
                limit = 5  # Безопасное значение по умолчанию
            
            # Подготовка URL для RAG API
            rag_api_url = "http://127.0.0.1:8080"
            search_endpoint = f"{rag_api_url}/search"
            
            # Кодирование параметров
            params = urllib.parse.urlencode({
                'q': query.strip(),
                'limit': limit
            })
            
            full_url = f"{search_endpoint}?{params}"
            
            logger.info(f"Searching RAG memory: {query} (limit: {limit})")
            
            # HTTP запрос к RAG API
            try:
                request = urllib.request.Request(full_url)
                request.add_header('Content-Type', 'application/json')
                request.add_header('User-Agent', 'GopiAI-ClaudeTools/1.0')
                
                with urllib.request.urlopen(request, timeout=10) as response:
                    if response.status == 200:
                        search_results = json.loads(response.read().decode('utf-8'))
                    else:
                        raise Exception(f"RAG API returned status {response.status}")
                        
            except urllib.error.URLError as e:
                if "Connection refused" in str(e) or "[Errno 10061]" in str(e):
# Теперь используется txtai - не требует отдельного сервера
                else:
                    raise Exception(f"RAG API connection error: {e}")
            
            # Обработка результатов поиска
            if not search_results:
                result = {
                    "success": True,
                    "query": query,
                    "results": [],
                    "total_found": 0,
                    "message": "No results found in memory"
                }
            else:
                # Форматирование результатов для Claude
                formatted_results = []
                for item in search_results:
                    formatted_item = {
                        "session_id": item.get("session_id", ""),
                        "title": item.get("title", "Untitled"),
                        "relevance_score": item.get("relevance_score", 0.0),
                        "matched_content": item.get("matched_content", ""),
                        "context_preview": item.get("context_preview", ""),
                        "timestamp": item.get("timestamp", ""),
                        "tags": item.get("tags", [])
                    }
                    formatted_results.append(formatted_item)
                
                result = {
                    "success": True,
                    "query": query,
                    "results": formatted_results,
                    "total_found": len(formatted_results),
                    "rag_api_url": rag_api_url
                }
            
            logger.info(f"RAG search completed: {len(search_results)} results for '{query}'")
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"RAG search error: {error_msg}")
            
            error_result = {
                "success": False,
                "error": error_msg,
                "query": query,
                "rag_status": "error"
            }
            
            return json.dumps(error_result, ensure_ascii=False)
    
    # ==============================================
    # INTEGRATION METHODS
    # ==============================================
    
    @Slot(result=str)
    def get_available_tools(self) -> str:
        """Получение списка доступных инструментов"""
        tools = {
            "browser_automation": [
                "navigate_to_url",
                "get_current_url", 
                "get_page_title",
                "execute_javascript",
                "get_page_source",
                "wait_for_element"
            ],
            "file_operations": [
                "read_file",
                "write_file"
            ],
            "system": [
                "run_script"
            ],
            "rag_memory": [
                "search_memory"
            ]
        }
        
        result = {
            "success": True,
            "tools": tools,
            "handler": "ClaudeToolsHandler",
            "version": "1.0"
        }
        
        return json.dumps(result, ensure_ascii=False)
    
    @Slot(result=str)
    def get_pending_requests(self) -> str:
        """Получение информации о ожидающих запросах"""
        result = {
            "success": True,
            "pending_count": len(self._pending_requests),
            "requests": list(self._pending_requests.keys())
        }
        
        return json.dumps(result)


class AdvancedClaudeToolsHandler(ClaudeToolsHandler):
    """
    Расширенная версия ClaudeToolsHandler с дополнительными возможностями.
    Планируется для будущих улучшений (Selenium, advanced automation, etc.)
    """
    
    def __init__(self, web_view: QWebEngineView, parent=None):
        super().__init__(web_view, parent)
        logger.info("AdvancedClaudeToolsHandler initialized")
    
    # Здесь будут дополнительные методы для Selenium и других инструментов
    # TODO: Selenium WebDriver integration
    # TODO: Advanced screenshot capabilities  
    # TODO: File upload/download automation
    # TODO: Form automation