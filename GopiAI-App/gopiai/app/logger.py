"""
Модуль логирования для приложения GopiAI.
Предоставляет унифицированный доступ к логированию.
"""

import datetime
from gopiai.core.logging import get_logger
logger = get_logger().logger
import os
from pathlib import Path

# Настройка корневого логгера
logger = get_logger().logger

def setup_logging(level=logging.INFO, log_to_file=True):
    """
    Настраивает систему логирования для всего приложения.
    
    Args:
        level: Уровень логирования (по умолчанию INFO)
        log_to_file: Если True, также логировать в файл
    """
    # Очищаем существующие обработчики для переконфигурации
    logger.handlers.clear()
    
    # Настраиваем формат вывода логов
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Настраиваем вывод в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Если log_to_file=True, настраиваем вывод в файл
    if log_to_file:
        try:
            # Используем абсолютный путь к директории проекта
            project_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
            log_dir = project_dir / "logs"
            
            # Создаем директорию, если она не существует
            os.makedirs(log_dir, exist_ok=True)
            
            # Создаем файл лога с временной меткой
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            log_file = log_dir / f"{timestamp}.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # В случае ошибки просто выводим сообщение и продолжаем без логирования в файл
            print(f"Не удалось настроить логирование в файл: {e}")
            # Не добавляем file_handler в случае ошибки
    
    # Устанавливаем уровень логирования
    logger.setLevel(level)
    
    return logger

# Создаем или получаем логгеры для разных модулей
def get_logger(name):
    """
    Возвращает логгер с указанным именем.
    """
    return get_logger().logger

# Инициализируем логирование при импорте модуля
setup_logging()

# Публичные функции и константы для прямого использования
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical
