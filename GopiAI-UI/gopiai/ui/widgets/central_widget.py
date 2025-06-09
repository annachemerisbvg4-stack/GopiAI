"""
Модуль для настройки центрального виджета главного окна GopiAI
"""

import logging
from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout

logger = logging.getLogger(__name__)


def setup_central_widget(main_window):
    """
    Создает и настраивает центральный виджет с вкладками для главного окна.

    Args:
        main_window: Экземпляр главного окна приложения
    """
    try:
        # Создаем виджет с вкладками
        main_window.central_tabs = QTabWidget()
        main_window.central_tabs.setTabsClosable(True)
        main_window.central_tabs.setMovable(True)
        main_window.central_tabs.setDocumentMode(True)

        # Создаем центральный виджет, если его еще нет
        if not hasattr(main_window, "centralWidget") or not main_window.centralWidget():
            central_widget = QWidget()
            layout = QVBoxLayout(central_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(main_window.central_tabs)
            central_widget.setLayout(layout)
            main_window.setCentralWidget(central_widget)
        else:
            # Если центральный виджет уже существует, добавляем вкладки в его layout
            layout = main_window.centralWidget().layout()
            if layout is None:
                layout = QVBoxLayout(main_window.centralWidget())
                layout.setContentsMargins(0, 0, 0, 0)
                main_window.centralWidget().setLayout(layout)
            layout.addWidget(main_window.central_tabs)

        logger.info("Центральный виджет с вкладками успешно создан")

        # Подключаем сигнал закрытия вкладок
        main_window.central_tabs.tabCloseRequested.connect(
            lambda index: main_window.central_tabs.removeTab(index)
        )

    except Exception as e:
        logger.error(f"Ошибка при создании центрального виджета: {e}")
