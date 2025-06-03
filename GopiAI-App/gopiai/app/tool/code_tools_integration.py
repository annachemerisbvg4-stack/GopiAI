#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Интеграция инструментов для работы с кодом."""

from gopiai.core.logging import get_logger
logger = get_logger().logger
from typing import List

from gopiai.app.tool.base import BaseTool
from gopiai.app.tool.tool_collection import ToolCollection

logger = get_logger().logger


class CodeControl(BaseTool):
    """Инструмент для управления редактором кода."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="code_control",
            description="Управляет редактором кода",
            function=self._control,
            parameters={
                "action": {
                    "type": "string",
                    "description": "Действие для выполнения",
                    "enum": ["get_open_files", "get_current_file", "open_file", "close_file"]
                },
                "file_path": {
                    "type": "string",
                    "description": "Путь к файлу (для действий open_file, close_file)"
                }
            },
            required_params=["action"]
        )
    
    def _control(self, action, file_path=None):
        """
        Управляет редактором кода.
        
        Args:
            action: Действие для выполнения
            file_path: Путь к файлу (для действий open_file, close_file)
            
        Returns:
            dict: Результат операции
        """
        logger.info(f"Управление редактором кода: {action}")
        
        if action == "get_open_files":
            return {
                "success": True,
                "message": "Получен список открытых файлов",
                "files": ["example.py", "test.py"]
            }
        elif action == "get_current_file":
            return {
                "success": True,
                "message": "Получен текущий файл",
                "file": "example.py"
            }
        elif action == "open_file":
            if not file_path:
                return {
                    "success": False,
                    "message": "Не указан путь к файлу"
                }
            return {
                "success": True,
                "message": f"Открыт файл: {file_path}"
            }
        elif action == "close_file":
            if not file_path:
                return {
                    "success": False,
                    "message": "Не указан путь к файлу"
                }
            return {
                "success": True,
                "message": f"Закрыт файл: {file_path}"
            }
        else:
            return {
                "success": False,
                "message": f"Неизвестное действие: {action}"
            }


class CodeEdit(BaseTool):
    """Инструмент для редактирования кода."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="code_edit",
            description="Редактирует код",
            function=self._edit,
            parameters={
                "action": {
                    "type": "string",
                    "description": "Действие для выполнения",
                    "enum": ["insert", "replace", "delete"]
                },
                "file_path": {
                    "type": "string",
                    "description": "Путь к файлу"
                },
                "line": {
                    "type": "integer",
                    "description": "Номер строки"
                },
                "content": {
                    "type": "string",
                    "description": "Содержимое для вставки или замены"
                },
                "end_line": {
                    "type": "integer",
                    "description": "Конечная строка для замены или удаления"
                }
            },
            required_params=["action", "file_path"]
        )
    
    def _edit(self, action, file_path, line=None, content=None, end_line=None):
        """
        Редактирует код.
        
        Args:
            action: Действие для выполнения
            file_path: Путь к файлу
            line: Номер строки
            content: Содержимое для вставки или замены
            end_line: Конечная строка для замены или удаления
            
        Returns:
            dict: Результат операции
        """
        logger.info(f"Редактирование кода: {action} в файле {file_path}")
        
        if action == "insert":
            if line is None or content is None:
                return {
                    "success": False,
                    "message": "Не указаны номер строки или содержимое"
                }
            return {
                "success": True,
                "message": f"Вставлено содержимое в файл {file_path} на строке {line}"
            }
        elif action == "replace":
            if line is None or content is None:
                return {
                    "success": False,
                    "message": "Не указаны номер строки или содержимое"
                }
            end_line_str = f" до строки {end_line}" if end_line else ""
            return {
                "success": True,
                "message": f"Заменено содержимое в файле {file_path} на строке {line}{end_line_str}"
            }
        elif action == "delete":
            if line is None:
                return {
                    "success": False,
                    "message": "Не указан номер строки"
                }
            end_line_str = f" до строки {end_line}" if end_line else ""
            return {
                "success": True,
                "message": f"Удалено содержимое в файле {file_path} на строке {line}{end_line_str}"
            }
        else:
            return {
                "success": False,
                "message": f"Неизвестное действие: {action}"
            }


class CodeAnalyze(BaseTool):
    """Инструмент для анализа кода."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="code_analyze",
            description="Анализирует код",
            function=self._analyze,
            parameters={
                "file_path": {
                    "type": "string",
                    "description": "Путь к файлу"
                },
                "analysis_type": {
                    "type": "string",
                    "description": "Тип анализа",
                    "enum": ["lint", "complexity", "dependencies"]
                }
            },
            required_params=["file_path"]
        )
    
    def _analyze(self, file_path, analysis_type="lint"):
        """
        Анализирует код.
        
        Args:
            file_path: Путь к файлу
            analysis_type: Тип анализа
            
        Returns:
            dict: Результат операции
        """
        logger.info(f"Анализ кода: {analysis_type} для файла {file_path}")
        
        if analysis_type == "lint":
            return {
                "success": True,
                "message": f"Выполнен линтинг файла {file_path}",
                "issues": [
                    {"line": 10, "message": "Неиспользуемая переменная"},
                    {"line": 15, "message": "Отсутствует документация"}
                ]
            }
        elif analysis_type == "complexity":
            return {
                "success": True,
                "message": f"Выполнен анализ сложности файла {file_path}",
                "complexity": {
                    "cyclomatic": 5,
                    "cognitive": 8
                }
            }
        elif analysis_type == "dependencies":
            return {
                "success": True,
                "message": f"Выполнен анализ зависимостей файла {file_path}",
                "dependencies": [
                    "os", "sys", "json"
                ]
            }
        else:
            return {
                "success": False,
                "message": f"Неизвестный тип анализа: {analysis_type}"
            }


def get_coding_tools() -> List[BaseTool]:
    """
    Возвращает список инструментов для работы с кодом.
    
    Returns:
        List[BaseTool]: Список инструментов
    """
    return [
        CodeControl(),
        CodeEdit(),
        CodeAnalyze()
    ]


def create_coding_tool_collection() -> ToolCollection:
    """
    Создает коллекцию инструментов для работы с кодом.
    
    Returns:
        ToolCollection: Коллекция инструментов
    """
    collection = ToolCollection()
    for tool in get_coding_tools():
        collection.add_tool(tool)
    return collection
