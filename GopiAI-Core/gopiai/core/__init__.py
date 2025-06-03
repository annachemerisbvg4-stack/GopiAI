"""
Базовый модуль GopiAI.

Содержит основные компоненты для запуска минимальной версии приложения.
Включает унифицированные системы логирования и конфигурации.
"""

__version__ = "0.1.0"

# Экспорт унифицированных систем
from .logging import get_logger, info, debug, warning, error, critical, logger
from .config import get_config, get_config_manager, get_setting, set_setting, config

__all__ = [
    # Logging
    'get_logger', 'info', 'debug', 'warning', 'error', 'critical', 'logger',
    # Config
    'get_config', 'get_config_manager', 'get_setting', 'set_setting', 'config'
]
