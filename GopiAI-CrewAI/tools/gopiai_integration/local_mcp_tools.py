"""
Локальные MCP инструменты для GopiAI
Набор полезных инструментов, которые работают без внешних сервисов
"""

import os
import json
import time
import logging
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class LocalMCPTools:
    """Класс для локальных MCP инструментов"""
    
    def __init__(self):
        self.tools_registry = {
            "system_info": {
                "name": "system_info",
                "description": "Получение информации о системе",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "file_operations": {
                "name": "file_operations",
                "description": "Операции с файлами: создание, чтение, запись",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["read", "write", "create", "list", "delete"],
                            "description": "Тип операции"
                        },
                        "path": {
                            "type": "string",
                            "description": "Путь к файлу или директории"
                        },
                        "content": {
                            "type": "string",
                            "description": "Содержимое файла (для операций write/create)"
                        }
                    },
                    "required": ["operation", "path"]
                }
            },
            "process_manager": {
                "name": "process_manager",
                "description": "Управление процессами системы",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["list", "kill", "start"],
                            "description": "Действие с процессом"
                        },
                        "process_name": {
                            "type": "string",
                            "description": "Имя процесса"
                        },
                        "command": {
                            "type": "string",
                            "description": "Команда для запуска (для действия start)"
                        }
                    },
                    "required": ["action"]
                }
            },
            "time_helper": {
                "name": "time_helper",
                "description": "Помощник для работы со временем",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["current_time", "timestamp", "format_time"],
                            "description": "Операция со временем"
                        },
                        "format": {
                            "type": "string",
                            "description": "Формат времени (для format_time)"
                        }
                    },
                    "required": ["operation"]
                }
            },
            "project_helper": {
                "name": "project_helper",
                "description": "Помощник для управления проектом GopiAI",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["status", "restart_server", "check_logs", "health_check"],
                            "description": "Действие с проектом"
                        },
                        "component": {
                            "type": "string",
                            "enum": ["crewai", "ui", "txtai", "all"],
                            "description": "Компонент проекта"
                        }
                    },
                    "required": ["action"]
                }
            }
        }
    
    def get_available_tools(self) -> List[Dict]:
        """Получение списка доступных инструментов"""
        return list(self.tools_registry.values())
    
    def call_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Вызов инструмента"""
        try:
            if tool_name == "system_info":
                return self._system_info()
            elif tool_name == "file_operations":
                return self._file_operations(parameters)
            elif tool_name == "process_manager":
                return self._process_manager(parameters)
            elif tool_name == "time_helper":
                return self._time_helper(parameters)
            elif tool_name == "project_helper":
                return self._project_helper(parameters)
            else:
                return {"error": f"Неизвестный инструмент: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Ошибка при вызове инструмента {tool_name}: {e}")
            return {"error": f"Ошибка выполнения: {str(e)}"}
    
    def _system_info(self) -> Dict:
        """Получение информации о системе"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "current_directory": os.getcwd(),
            "user": os.environ.get("USERNAME", "unknown"),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _file_operations(self, params: Dict) -> Dict:
        """Операции с файлами"""
        operation = params.get("operation")
        path = params.get("path")
        
        if not path:
            return {"error": "Не указан путь к файлу"}
        
        try:
            if operation == "read":
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"success": True, "content": content}
            
            elif operation == "write" or operation == "create":
                content = params.get("content", "")
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {"success": True, "message": f"Файл {'создан' if operation == 'create' else 'изменен'}: {path}"}
            
            elif operation == "list":
                path_obj = Path(path)
                if path_obj.is_dir():
                    files = [str(p) for p in path_obj.iterdir()]
                    return {"success": True, "files": files}
                else:
                    return {"error": "Указанный путь не является директорией"}
            
            elif operation == "delete":
                os.remove(path)
                return {"success": True, "message": f"Файл удален: {path}"}
            
            else:
                return {"error": f"Неизвестная операция: {operation}"}
                
        except Exception as e:
            return {"error": f"Ошибка операции с файлом: {str(e)}"}
    
    def _process_manager(self, params: Dict) -> Dict:
        """Управление процессами"""
        action = params.get("action")
        
        try:
            if action == "list":
                # Получаем список процессов
                if platform.system() == "Windows":
                    result = subprocess.run(['tasklist'], capture_output=True, text=True)
                    return {"success": True, "processes": result.stdout[:1000]}  # Ограничиваем вывод
                else:
                    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                    return {"success": True, "processes": result.stdout[:1000]}
            
            elif action == "kill":
                process_name = params.get("process_name")
                if not process_name:
                    return {"error": "Не указано имя процесса"}
                
                if platform.system() == "Windows":
                    result = subprocess.run(['taskkill', '/f', '/im', process_name], 
                                          capture_output=True, text=True)
                else:
                    result = subprocess.run(['pkill', process_name], 
                                          capture_output=True, text=True)
                
                return {"success": True, "message": f"Процесс {process_name} завершен"}
            
            elif action == "start":
                command = params.get("command")
                if not command:
                    return {"error": "Не указана команда для запуска"}
                
                process = subprocess.Popen(command, shell=True)
                return {"success": True, "message": f"Процесс запущен с PID: {process.pid}"}
            
            else:
                return {"error": f"Неизвестное действие: {action}"}
                
        except Exception as e:
            return {"error": f"Ошибка управления процессом: {str(e)}"}
    
    def _time_helper(self, params: Dict) -> Dict:
        """Помощник для работы со временем"""
        operation = params.get("operation")
        
        try:
            if operation == "current_time":
                return {
                    "success": True,
                    "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp": int(time.time())
                }
            
            elif operation == "timestamp":
                return {
                    "success": True,
                    "timestamp": int(time.time()),
                    "iso_format": datetime.now().isoformat()
                }
            
            elif operation == "format_time":
                format_str = params.get("format", "%Y-%m-%d %H:%M:%S")
                return {
                    "success": True,
                    "formatted_time": datetime.now().strftime(format_str)
                }
            
            else:
                return {"error": f"Неизвестная операция: {operation}"}
                
        except Exception as e:
            return {"error": f"Ошибка работы со временем: {str(e)}"}
    
    def _project_helper(self, params: Dict) -> Dict:
        """Помощник для управления проектом"""
        action = params.get("action")
        component = params.get("component", "all")
        
        try:
            if action == "status":
                # Проверяем статус компонентов
                status = {}
                
                # Проверка CrewAI сервера
                try:
                    import requests
                    response = requests.get("http://127.0.0.1:5051/api/health", timeout=2)
                    status["crewai_server"] = "running" if response.status_code == 200 else "stopped"
                except:
                    status["crewai_server"] = "stopped"
                
                # Проверка процессов
                if platform.system() == "Windows":
                    result = subprocess.run(['tasklist'], capture_output=True, text=True)
                    processes = result.stdout
                    status["python_processes"] = processes.count("python.exe")
                
                return {"success": True, "status": status}
            
            elif action == "health_check":
                # Полная проверка здоровья системы
                health = {
                    "timestamp": datetime.now().isoformat(),
                    "system": platform.system(),
                    "python_version": platform.python_version(),
                    "working_directory": os.getcwd(),
                    "crewai_server": "unknown",
                    "memory_usage": "unknown"
                }
                
                # Проверка CrewAI сервера
                try:
                    import requests
                    response = requests.get("http://127.0.0.1:5051/api/health", timeout=2)
                    if response.status_code == 200:
                        health["crewai_server"] = "healthy"
                        health["crewai_data"] = response.json()
                    else:
                        health["crewai_server"] = "unhealthy"
                except:
                    health["crewai_server"] = "down"
                
                return {"success": True, "health": health}
            
            else:
                return {"error": f"Неизвестное действие: {action}"}
                
        except Exception as e:
            return {"error": f"Ошибка управления проектом: {str(e)}"}


# Глобальный экземпляр
_local_mcp_tools = None

def get_local_mcp_tools() -> LocalMCPTools:
    """Получение экземпляра локальных MCP инструментов"""
    global _local_mcp_tools
    if _local_mcp_tools is None:
        _local_mcp_tools = LocalMCPTools()
    return _local_mcp_tools
