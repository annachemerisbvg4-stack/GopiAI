"""
🔧 GopiAI Base Tool
Базовый класс для всех инструментов GopiAI-CrewAI с улучшенным логированием и обработкой ошибок
"""

import os
import sys
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel

class GopiAIBaseTool:
    """
    Базовый класс для всех GopiAI инструментов CrewAI
    
    Особенности:
    - Единая система логирования
    - Стандартизированная обработка ошибок
    - Метрики производительности
    - Базовый интерфейс для всех инструментов
    """
    
    name: str = "gopiai_base_tool"
    description: str = "Базовый класс для всех GopiAI инструментов"
    
    def __init__(self, verbose: bool = False, log_level: int = logging.INFO):
        """
        Инициализация базового инструмента
        
        Args:
            verbose: Подробный вывод сообщений
            log_level: Уровень логирования
        """
        self.verbose = verbose
        self.logger = self._setup_logger(log_level)
        self.metrics = {
            "calls": 0,
            "errors": 0,
            "total_time": 0,
            "last_call": None
        }
        self.logger.info(f"Инструмент {self.__class__.__name__} инициализирован")
    
    def _setup_logger(self, log_level: int) -> logging.Logger:
        """
        Настройка логгера для инструмента
        
        Args:
            log_level: Уровень логирования
            
        Returns:
            Настроенный логгер
        """
        logger_name = f"gopiai.tools.{self.__class__.__name__}"
        logger = logging.getLogger(logger_name)
        
        # Проверяем, не настроен ли уже логгер
        if not logger.handlers:
            logger.setLevel(log_level)
            
            # Создаем директорию для логов, если её нет
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            # Файловый обработчик
            log_file = os.path.join(log_dir, f"{self.__class__.__name__.lower()}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            
            # Консольный обработчик
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.ERROR)  # В консоль только ошибки
            
            # Форматтер
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Добавляем обработчики
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def run(self, *args, **kwargs) -> str:
        """
        Основной метод запуска инструмента с метриками и обработкой ошибок
        
        Returns:
            Результат работы инструмента
        """
        start_time = time.time()
        self.metrics["calls"] += 1
        self.metrics["last_call"] = datetime.now()
        
        try:
            self.logger.info(f"Запуск {self.__class__.__name__} с аргументами: {args}, {kwargs}")
            
            if self.verbose:
                print(f"🔧 Запуск {self.__class__.__name__}...")
                
            result = self._run(*args, **kwargs)
            
            execution_time = time.time() - start_time
            self.metrics["total_time"] += execution_time
            
            self.logger.info(f"Успешное выполнение за {execution_time:.2f}с: {result[:100]}...")
            return result
            
        except Exception as e:
            self.metrics["errors"] += 1
            execution_time = time.time() - start_time
            
            error_msg = f"Ошибка в {self.__class__.__name__}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            # Пытаемся выполнить fallback, если он есть
            try:
                if hasattr(self, '_fallback'):
                    self.logger.info("Попытка выполнить fallback...")
                    fallback_result = self._fallback(*args, **kwargs, error=e)
                    self.logger.info(f"Fallback успешен: {fallback_result[:100]}...")
                    return fallback_result
            except Exception as fallback_error:
                self.logger.error(f"Ошибка в fallback: {str(fallback_error)}")
            
            # Если fallback не сработал или его нет, возвращаем сообщение об ошибке
            return f"❌ {error_msg}"
    
    def _run(self, *args, **kwargs) -> str:
        """
        Метод для переопределения в дочерних классах
        
        Returns:
            Результат работы инструмента
        """
        raise NotImplementedError("Метод _run должен быть переопределен в дочернем классе")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Получение метрик использования инструмента
        
        Returns:
            Словарь с метриками
        """
        if self.metrics["calls"] > 0:
            avg_time = self.metrics["total_time"] / self.metrics["calls"]
        else:
            avg_time = 0
            
        return {
            "name": self.__class__.__name__,
            "calls": self.metrics["calls"],
            "errors": self.metrics["errors"],
            "error_rate": self.metrics["errors"] / self.metrics["calls"] if self.metrics["calls"] > 0 else 0,
            "avg_time": avg_time,
            "total_time": self.metrics["total_time"],
            "last_call": self.metrics["last_call"].isoformat() if self.metrics["last_call"] else None
        }
    
    def reset_metrics(self) -> None:
        """Сброс метрик инструмента"""
        self.metrics = {
            "calls": 0,
            "errors": 0,
            "total_time": 0,
            "last_call": None
        }
        self.logger.info(f"Метрики {self.__class__.__name__} сброшены")


# Пример использования
if __name__ == "__main__":
    # Настройка корневого логгера для тестов
    logging.basicConfig(level=logging.INFO)
    
    # Тестовый класс
    class TestTool(GopiAIBaseTool):
        name = "test_tool"
        description = "Тестовый инструмент"
        
        def _run(self, action, value=""):
            if action == "echo":
                return f"Echo: {value}"
            elif action == "error":
                raise ValueError("Тестовая ошибка")
            else:
                return f"Неизвестное действие: {action}"
        
        def _fallback(self, action, value="", error=None):
            return f"Fallback для {action}: {error}"
    
    # Создаем и тестируем
    tool = TestTool(verbose=True)
    
    print("=== Тест успешного выполнения ===")
    result = tool.run("echo", "Hello World")
    print(f"Результат: {result}")
    
    print("\n=== Тест обработки ошибки ===")
    result = tool.run("error")
    print(f"Результат: {result}")
    
    print("\n=== Метрики ===")
    print(tool.get_metrics())