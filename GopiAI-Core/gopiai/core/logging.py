#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🎯 Единый логгер для всех модулей GopiAI

Заменяет разрозненные логгеры из:
- gopiai.app.logger  
- Самодельные logging импорты по всему проекту

Теперь ВСЕ модули используют ОДИН логгер отсюда!
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

class GopiAILogger:
    """Централизованный логгер для всего проекта GopiAI 🎯"""
    
    _instance: Optional['GopiAILogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Настройка централизованного логгера"""
        import sys  # Ensure sys is imported at the function level
        import io
        
        self._logger = logging.getLogger('GopiAI')
        self._logger.setLevel(logging.DEBUG)
        
        # Убираем старые handlers если есть
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)
        
        # Консольный handler с поддержкой UTF-8
        if sys.platform.startswith('win'):
            
            # Создаем обертку для stdout с поддержкой UTF-8
            if sys.stdout.encoding != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            
            # Создаем консольный handler с поддержкой UTF-8
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Форматтер для консоли (без эмодзи)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self._logger.addHandler(console_handler)
        else:
            # Для не-Windows систем используем стандартный обработчик
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self._logger.addHandler(console_handler)
        
        # Файловый handler с UTF-8
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Форматтер для файла (с эмодзи)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)
        
        # Используем текстовое представление вместо эмодзи для Windows
        if sys.platform.startswith('win'):
            self._logger.info("[GOPIAI] GopiAI Unified Logger initialized")
        else:
            self._logger.info("🎯 GopiAI Unified Logger initialized")
    
    @property
    def logger(self) -> logging.Logger:
        """Получить экземпляр логгера"""
        if self._logger is None:
            self._setup_logger()
        assert self._logger is not None
        return self._logger
    
    def debug(self, message: str, *args, **kwargs):
        """Debug уровень логирования"""
        if self._logger is None:
            self._setup_logger()
        assert self._logger is not None
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Info уровень логирования"""
        if self._logger is None:
            self._setup_logger()
        assert self._logger is not None
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Warning уровень логирования"""
        if self._logger is None:
            self._setup_logger()
        assert self._logger is not None
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Error уровень логирования"""
        if self._logger is None:
            self._setup_logger()
        assert self._logger is not None
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Critical уровень логирования"""
        if self._logger is None:
            self._setup_logger()
        assert self._logger is not None
        self._logger.critical(message, *args, **kwargs)

# Глобальный экземпляр логгера
_global_logger = GopiAILogger()

# Удобные функции для импорта
def get_gopiai_logger() -> GopiAILogger:
    """Получить глобальный логгер GopiAI"""
    return _global_logger

def get_logger() -> GopiAILogger:
    """Получить глобальный логгер GopiAI (алиас)"""
    return _global_logger

def debug(message: str, *args, **kwargs):
    """Глобальная функция debug логирования"""
    _global_logger.debug(message, *args, **kwargs)

def info(message: str, *args, **kwargs):
    """Глобальная функция info логирования"""
    _global_logger.info(message, *args, **kwargs)

def warning(message: str, *args, **kwargs):
    """Глобальная функция warning логирования"""
    _global_logger.warning(message, *args, **kwargs)

def error(message: str, *args, **kwargs):
    """Глобальная функция error логирования"""
    _global_logger.error(message, *args, **kwargs)

def critical(message: str, *args, **kwargs):
    """Глобальная функция critical логирования"""
    _global_logger.critical(message, *args, **kwargs)

# Для обратной совместимости с gopiai.app.logger
logger = _global_logger.logger
