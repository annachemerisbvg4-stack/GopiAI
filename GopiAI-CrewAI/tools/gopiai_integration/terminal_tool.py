"""
Terminal Tool для GopiAI-CrewAI
==============================

Инструмент для выполнения команд в терминале через интерфейс GopiAI-UI.
Безопасная интеграция между LLM и терминальным виджетом.
"""

# Используем BaseTool из crewai_tools вместо langchain
from crewai.tools import BaseTool
from typing import Dict, Any, Optional
import subprocess
import logging
import re
import os

# Настраиваем логгер
logger = logging.getLogger(__name__)

# Список запрещенных команд и паттернов для безопасности
FORBIDDEN_COMMANDS = [
    "rm -rf", "deltree", "format", "shutdown", "reboot",
    "mkfs", "dd if=", ":(){ :|:& };:", "> /dev/sda",
    "chmod -R 777 /", "mv /* /dev/null", "wget -O- | bash"
]

# Глобальная переменная для хранения ссылки на терминальный виджет
_terminal_widget_instance = None

def set_terminal_widget(terminal_widget):
    """Устанавливает глобальную ссылку на терминальный виджет"""
    global _terminal_widget_instance
    _terminal_widget_instance = terminal_widget
    logger.info(f"Терминальный виджет установлен: {terminal_widget}")

def get_terminal_widget():
    """Возвращает глобальную ссылку на терминальный виджет"""
    global _terminal_widget_instance
    return _terminal_widget_instance

class TerminalTool(BaseTool):
    """Инструмент для выполнения команд в терминале GopiAI"""
    
    name: str = 'terminal'
    description: str = 'Execute shell commands in the UI terminal and get output. Use for running commands visible to user.'
    
    def _is_safe_command(self, command: str) -> bool:
        """Проверяет команду на безопасность"""
        # Проверка на запрещенные команды
        for forbidden in FORBIDDEN_COMMANDS:
            if forbidden in command.lower():
                return False
        
        # Проверка на подозрительные паттерны
        suspicious_patterns = [
            r"rm\s+-rf\s+[/~]",  # Удаление корневой директории
            r">\s+/dev/[hs]d[a-z]",  # Запись в устройство
            r"dd\s+.*\s+of=/dev/[hs]d[a-z]",  # Запись через dd
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, command):
                return False
                
        return True
    
    def _run(self, command: str) -> Dict[str, Any]:
        """Выполняет команду в терминале через MCP"""
        logger.debug(f"Executing command via MCP: {command}")
        
        # Проверка на безопасность
        if not self._is_safe_command(command):
            logger.warning(f"Команда заблокирована: {command}")
            return {"terminal_output": {
                "command": command, 
                "output": "", 
                "error": "Команда заблокирована по соображениям безопасности", 
                "success": False
            }}
        
        try:
            # Вызов через MCP
            mcp_result = self.mcp_client.query({"type": "execute_shell", "command": command})  # Предполагаем, что mcp_client доступен
            
            # Логируем и возвращаем
            output = mcp_result.get('output', '')
            error = mcp_result.get('error', '')
            success = mcp_result.get('success', False)
            
            terminal = get_terminal_widget()
            if terminal:
                terminal.log_ai_command(command, output + ("\n" + error if error else ""))
            
            return {"terminal_output": {"command": command, "output": output, "error": error, "success": success}}
        except Exception as e:
            error_msg = f"Ошибка MCP: {str(e)}"
            return {"terminal_output": {"command": command, "output": "", "error": error_msg, "success": False}}

    def _arun(self, command: str) -> Any:
        """Асинхронное выполнение не поддерживается"""
        raise NotImplementedError('Async operation not supported')