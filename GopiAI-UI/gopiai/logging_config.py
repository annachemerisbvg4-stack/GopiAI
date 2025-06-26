import logging
import logging.handlers # Импортируем модуль для обработчиков ротации
import os

def setup_logging(
    log_file_path: str = 'application.log',
    level: int = logging.INFO,
    console_output: bool = True
):
    """
    Настраивает базовое логирование для всего приложения.

    Сообщения из всех модулей будут записываться в указанный файл
    и, опционально, выводиться в консоль.

    Args:
        log_file_path (str): Путь к файлу логов.
        level (int): Минимальный уровень логирования (например, logging.INFO, logging.DEBUG).
        console_output (bool): Если True, логи также будут выводиться в консоль.
    """
    # Получаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Удаляем все существующие обработчики, чтобы избежать дублирования
    # Это важно, если функция вызывается несколько раз или если уже есть дефолтные обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - P:%(process)d T:%(threadName)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Обработчик для записи в файл
    # Используем RotatingFileHandler для ротации логов по размеру
    # maxBytes=10*1024*1024 (10 МБ), backupCount=5 (хранить 5 старых файлов)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Обработчик для вывода в консоль (опционально)
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)