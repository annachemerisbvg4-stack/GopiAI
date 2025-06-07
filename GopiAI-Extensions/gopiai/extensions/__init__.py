"""
Модуль расширений для минимальной версии GopiAI.

Этот модуль содержит различные интеграции и расширения для
базового приложения, такие как файловый проводник, терминал, браузер и др.
"""

from gopiai.core.logging import get_logger
logger = get_logger().logger
import importlib
import sys
from pathlib import Path

# Инициализация логгера
logger = get_logger().logger

def init_all_extensions(main_window):
    """
    Инициализирует все доступные расширения.

    Эта функция последовательно пытается загрузить и инициализировать
    все доступные расширения. Если какое-то расширение не удается загрузить,
    оно пропускается, и приложение продолжает работу.

    Args:
        main_window: Главное окно приложения
    """
    # В первую очередь инициализируем менеджер док-виджетов (чтобы управлять размещением виджетов)
    try:
        module = _safely_import("gopiai.extensions.dock_manager_extension")
        if module and hasattr(module, "init_extension"):
            logger.info("Инициализация dock_manager_extension...")
            module.init_extension(main_window)
        else:
            logger.warning("Модуль dock_manager_extension не найден или не содержит функцию init_extension")
    except Exception as e:
        logger.error(f"Ошибка при инициализации dock_manager: {e}")

    # Инициализируем проводник проектов
    try:
        logger.info("Инициализация project_explorer...")
        init_project_explorer_dock_extension(main_window)
    except Exception as e:
        logger.error(f"Ошибка при инициализации проводника проектов: {e}")

    # Инициализируем чат
    try:
        logger.info("Инициализация чата...")
        init_chat_extension(main_window)
    except Exception as e:
        logger.error(f"Ошибка при инициализации чата: {e}")

    # Инициализируем терминал
    try:
        logger.info("Инициализация терминала...")
        init_terminal_extension(main_window)
    except Exception as e:
        logger.error(f"Ошибка при инициализации терминала: {e}")

    # Подключаем меню браузера
    try:
        logger.info("Подключение браузера...")
        connect_browser_menu(main_window)
    except Exception as e:
        logger.error(f"Ошибка при подключении браузера: {e}")
        
    # Инициализируем статусную строку
    try:
        logger.info("Инициализация статусной строки...")
        init_status_bar_extension(main_window)
    except Exception as e:
        logger.error(f"Ошибка при инициализации статусной строки: {e}")
          # Инициализируем центр уведомлений
    try:
        logger.info("Инициализация центра уведомлений...")
        init_notification_center_extension(main_window)
    except Exception as e:
        logger.error(f"Ошибка при инициализации центра уведомлений: {e}")

    # Инициализируем AutoGen расширение
    try:
        logger.info("Инициализация AutoGen расширения...")
        init_autogen_extension(main_window)
    except Exception as e:
        logger.error(f"Ошибка при инициализации AutoGen: {e}")

    logger.info("Инициализация расширений завершена")

def _safely_import(module_name, attr_name=None):
    """Безопасно импортирует модуль или его атрибут."""
    try:
        module = importlib.import_module(module_name)
        if attr_name:
            return getattr(module, attr_name)
        return module
    except (ImportError, AttributeError) as e:
        logger.warning(f"Не удалось импортировать {module_name}.{attr_name or ''}: {e}")
        return None

# Для обратной совместимости экспортируем функции из других модулей
def init_project_explorer_dock_extension(main_window):
    """Инициализирует проводник проектов."""
    try:
        # Пробуем динамически импортировать модуль и функцию
        module = _safely_import("gopiai.extensions.project_explorer_integration")
        if module and hasattr(module, "add_project_explorer_dock"):
            module.add_project_explorer_dock(main_window)
        else:
            logger.warning("Функция add_project_explorer_dock не найдена")
    except Exception as e:
        logger.error(f"Ошибка при инициализации проводника проектов: {e}")

def init_chat_extension(main_window):
    """Инициализирует чат с ИИ."""
    try:
        # Пробуем динамически импортировать модуль и функцию
        module = _safely_import("gopiai.extensions.orchestrator_agent_integration")
        if module and hasattr(module, "show_orchestrator_chat_dock"):
            module.show_orchestrator_chat_dock(main_window)
        else:
            # Попробуем альтернативный модуль
            module = _safely_import("gopiai.extensions.simple_chat_integration")
            if module and hasattr(module, "show_chat"):
                module.show_chat(main_window)
            else:
                logger.warning("Модуль чата не найден")
    except Exception as e:
        logger.error(f"Ошибка при инициализации чата: {e}")

def connect_browser_menu(main_window):
    """Подключает меню браузера."""
    try:
        module = _safely_import("gopiai.extensions.browser_integration")
        if module:
            # Проверяем наличие различных возможных функций
            if hasattr(module, "connect_browser_menu"):
                module.connect_browser_menu(main_window)
            elif hasattr(module, "add_browser_dock"):
                module.add_browser_dock(main_window)
            else:
                logger.warning("Функции browser_integration не найдены")
    except Exception as e:
        logger.error(f"Ошибка при подключении браузера: {e}")

def init_terminal_extension(main_window):
    """Инициализирует терминал."""
    try:
        module = _safely_import("gopiai.extensions.terminal_integration")
        if module and hasattr(module, "add_terminal_dock"):
            module.add_terminal_dock(main_window)
        else:
            logger.warning("Функция add_terminal_dock не найдена")
    except Exception as e:
        logger.error(f"Ошибка при инициализации терминала: {e}")

def init_status_bar_extension(main_window):
    """Инициализирует статусную строку."""
    try:
        module = _safely_import("gopiai.extensions.status_bar_extension")
        if module and hasattr(module, "init_extension"):
            return module.init_extension(main_window)
        else:
            logger.warning("Функция init_extension в status_bar_extension не найдена")
    except Exception as e:
        logger.error(f"Ошибка при инициализации статусной строки: {e}")
    return None

def init_notification_center_extension(main_window):
    """Инициализирует центр уведомлений."""
    try:
        module = _safely_import("gopiai.extensions.notification_center_extension")
        if module and hasattr(module, "init_extension"):
            return module.init_extension(main_window)
        else:
            logger.warning("Функция init_extension в notification_center_extension не найдена")
    except Exception as e:
        logger.error(f"Ошибка при инициализации центра уведомлений: {e}")
    return None

def init_autogen_extension(main_window):
    """Инициализирует AutoGen расширение."""
    try:
        # Ищем AutoGen extension в разных возможных местах
        autogen_module = None
        
        # Пробуем импортировать из autogen пакета
        try:
            import sys
            import os
            autogen_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'autogen')
            if autogen_path not in sys.path:
                sys.path.insert(0, autogen_path)
            
            from autogen.autogen_extension import add_autogen_dock
            autogen_module = True
        except ImportError:
            # Пробуем альтернативный импорт
            try:
                from autogen_extension import add_autogen_dock
                autogen_module = True
            except ImportError:
                logger.warning("AutoGen extension модуль не найден")
                return None
        
        if autogen_module:
            logger.info("✅ AutoGen extension найден, добавляем dock...")
            add_autogen_dock(main_window)
            logger.info("✅ AutoGen extension успешно инициализирован")
        else:
            logger.warning("AutoGen extension не найден или недоступен")
    except Exception as e:
        logger.error(f"Ошибка при инициализации AutoGen extension: {e}")
    return None

__version__ = "0.1.0"
