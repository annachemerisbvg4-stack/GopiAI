"""
Модуль для создания боковых панелей (dock-виджетов) приложения GopiAI-UI
"""

import logging
from PySide6.QtWidgets import QDockWidget, QMainWindow, QWidget
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)


def create_docks(main_window: QMainWindow):
    """Создает боковые панели (dock-виджеты) приложения."""
    try:
        # Проводник проекта
        main_window.project_explorer_dock = QDockWidget(
            "Проводник проекта", main_window
        )
        main_window.project_explorer_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        main_window.project_explorer_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        main_window.project_explorer_dock.setMinimumWidth(100)
        main_window.project_explorer_dock.setObjectName("ProjectExplorerDock")
        
        # Создаем простой виджет проводника (пока заглушка)
        project_explorer_widget = QWidget()
        main_window.project_explorer_dock.setWidget(project_explorer_widget)
        main_window.addDockWidget(Qt.LeftDockWidgetArea, main_window.project_explorer_dock)

        # Чат
        main_window.chat_dock = QDockWidget("ИИ-чат", main_window)
        main_window.chat_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        main_window.chat_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        main_window.chat_dock.setMinimumWidth(200)
        main_window.chat_dock.setObjectName("ChatDock")
        
        # Создаем простой виджет чата (пока заглушка)
        chat_widget = QWidget()
        main_window.chat_dock.setWidget(chat_widget)
        main_window.addDockWidget(Qt.RightDockWidgetArea, main_window.chat_dock)

        # Терминал
        main_window.terminal_dock = QDockWidget("Терминал", main_window)
        main_window.terminal_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        main_window.terminal_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        main_window.terminal_dock.setMinimumHeight(100)
        main_window.terminal_dock.setObjectName("TerminalDock")
        
        # Создаем простой виджет терминала (пока заглушка)
        terminal_widget = QWidget()
        main_window.terminal_dock.setWidget(terminal_widget)
        main_window.addDockWidget(Qt.BottomDockWidgetArea, main_window.terminal_dock)
        main_window.terminal_dock.hide()

        # Браузер
        logger.info("Creating browser dock")
        main_window.browser_dock = QDockWidget("Браузер", main_window)
        main_window.browser_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        main_window.browser_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        main_window.browser_dock.setMinimumWidth(250)
        main_window.browser_dock.setMinimumHeight(200)
        main_window.browser_dock.setObjectName("BrowserDock")

        # Создаем простой виджет браузера (пока заглушка)
        browser_widget = QWidget()
        main_window.browser_dock.setWidget(browser_widget)

        # Добавляем док в правую область, но не показываем его сразу
        main_window.addDockWidget(Qt.RightDockWidgetArea, main_window.browser_dock)
        main_window.browser_dock.hide()
        logger.info("Browser dock created successfully")

        logger.info("All docks created successfully")

    except Exception as e:
        logger.error(f"Error creating docks: {e}")
