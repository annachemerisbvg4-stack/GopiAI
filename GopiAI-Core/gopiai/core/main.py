#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Основной модуль запуска приложения GopiAI.

Этот модуль содержит функцию main(), которая создает и запускает
основное приложение GopiAI с полной инициализацией и обработкой ошибок.
"""

import argparse
from gopiai.core.logging import get_logger
logger = get_logger().logger
import warnings
import os
import sys
from pathlib import Path

# WebEngine flags (если нужен браузер)
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --no-sandbox"

# --- Глобальные константы ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VERSION_STRING = "GopiAI Core 1.0"

warnings.filterwarnings("ignore", category=UserWarning)

# Qt imports
try:
    from PySide6.QtCore import Qt, QCoreApplication
    from PySide6.QtGui import QIcon, QFont
    from PySide6.QtWidgets import QApplication
except ImportError:
    QIcon = QFont = QApplication = None

def setup_logging(debug=False):
    """Настраивает систему логирования."""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = get_logger().logger
    return logger

def setup_application():
    """Настраивает базовое приложение Qt."""
    if QApplication is None:
        logger.error("Ошибка: Не удалось импортировать PySide6. Пожалуйста, установите PySide6 с помощью pip:")
        logger.error("pip install PySide6")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("GopiAI")
    app.setOrganizationName("GopiAI")
    app.setOrganizationDomain("gopiai.org")

    # Настройка шрифтов
    if QFont is not None:
        default_font = QFont("Segoe UI", 10)
        app.setFont(default_font)

    return app

def apply_theme_safely(app):
    """Безопасно применяет тему к приложению."""
    try:
        # Путь к теме в настройках Core модуля
        theme_path = os.path.join(PROJECT_ROOT, "..", "..", "settings", "simple_theme.json")
        if os.path.exists(theme_path):
            # Попытка импорта функции применения темы
            try:
                from gopiai.app.utils.theme_loader import apply_theme_from_json
                apply_theme_from_json(app, theme_path)
                logger.info(f"Тема применена из: {theme_path}")
            except ImportError:
                logger.warning("Модуль theme_loader не найден, используется тема по умолчанию")
        else:
            logger.warning(f"Файл темы не найден: {theme_path}")
    except Exception as e:
        logger.warning(f"Не удалось применить тему: {e}")

def setup_icons(app):
    """Настраивает иконки приложения."""
    try:
        # Попытка установить иконку приложения
        from gopiai.widgets.core.icon_adapter import IconAdapter
        if QIcon is not None:
            icon_adapter = IconAdapter()
            app.setWindowIcon(QIcon(icon_adapter.get_icon_path("app")))
            logger.info("Иконка приложения установлена")
        else:
            logger.warning("Qt не загружен, иконка приложения не установлена")
    except ImportError:
        logger.warning("IconAdapter не найден, иконка приложения не установлена")
    except Exception as e:
        logger.warning(f"Не удалось установить иконку приложения: {e}")

def main():
    """
    Основная функция для запуска GopiAI.

    Создаёт и настраивает приложение Qt, инициализирует главное окно
    и запускает цикл обработки событий с полной обработкой ошибок.
    """
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(description="GopiAI Core Application")
    parser.add_argument("--debug", action="store_true", help="Запустить в режиме отладки")
    parser.add_argument("--no-browser", action="store_true", help="Отключить встроенный браузер")
    parser.add_argument("--no-extensions", action="store_true", help="Отключить расширения")
    args = parser.parse_args()

    # Настройка логирования
    logger = setup_logging(args.debug)

    # Логируем версии и окружение
    logger.info(f"Запуск {VERSION_STRING}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Operating System: {sys.platform}")
    logger.info(f"Рабочий каталог: {PROJECT_ROOT}")

    try:
        from PySide6.QtCore import QCoreApplication
        logger.info(f"Qt version: {QCoreApplication.applicationVersion()}")
    except Exception:
        pass

    logger.info("Инициализация приложения GopiAI...")

    # Создание и настройка приложения
    app = setup_application()

    # Применение темы
    apply_theme_safely(app)

    # Настройка иконок
    setup_icons(app)

    try:
        # Импорт основных компонентов
        from gopiai.core.minimal_app import FramelessMainWindow

        # Создание главного окна
        logger.info("Создание главного окна приложения...")
        main_window = FramelessMainWindow()
        main_window.show()

        # Инициализация расширений (если не отключено)
        if not args.no_extensions:
            try:
                from gopiai.extensions import init_all_extensions
                init_all_extensions(main_window)
                logger.info("Расширения инициализированы")
            except ImportError:
                logger.warning("Модуль расширений не найден")
            except Exception as e:
                logger.warning(f"Ошибка инициализации расширений: {e}")

        # Запуск цикла обработки событий
        logger.info("Запуск приложения...")
        sys.exit(app.exec())

    except ImportError as e:
        logger.error(f"Ошибка импорта компонентов GopiAI: {e}")
        logger.error("Возможно, модули не найдены или в неправильном месте.")
        logger.error("Пожалуйста, проверьте структуру проекта и наличие всех необходимых модулей.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске приложения: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
