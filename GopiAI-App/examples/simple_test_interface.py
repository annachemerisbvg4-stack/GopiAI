#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Минимальный пример интерфейса на основе PySide6 для тестирования GopiAI.

Этот пример демонстрирует базовый интерфейс без зависимостей от других модулей.
"""

import os
import sys
from gopiai.core.logging import get_logger
logger = get_logger().logger
from pathlib import Path

try:
    from PySide6.QtCore import Qt, QCoreApplication, QSize
    from PySide6.QtGui import QIcon, QAction, QFont
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout,
        QHBoxLayout, QWidget, QTextEdit, QMenu, QMenuBar,
        QStatusBar, QToolBar, QDockWidget, QTabWidget
    )
except ImportError:
    print("Ошибка: PySide6 не установлен. Установите с помощью: pip install PySide6")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = get_logger().logger

class SimpleMainWindow(QMainWindow):
    """Простое главное окно для тестирования."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GopiAI Test Interface")
        self.resize(1200, 800)

        # Основной виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Главный layout
        self.layout = QVBoxLayout(self.central_widget)
        
        # Верхняя панель с информацией
        self.info_layout = QHBoxLayout()
        self.info_label = QLabel("GopiAI Testing Environment")
        self.info_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.info_layout.addWidget(self.info_label)
        self.layout.addLayout(self.info_layout)
        
        # Создаем вкладки
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        # Вкладка с текстовой информацией
        self.text_widget = QTextEdit()
        self.text_widget.setReadOnly(True)
        self.text_widget.setText("""
        # GopiAI Testing Environment
        
        Это тестовое окружение для проверки интеграции модулей GopiAI.
        
        ## Проверка компонентов
        - Главное окно: ✅
        - Меню: ✅
        - Панели инструментов: ✅
        - Доки: ✅
        - Вкладки: ✅
        
        ## Инструкции
        1. Используйте меню для навигации между компонентами
        2. Проверьте доки слева и справа
        3. Протестируйте различные функции интерфейса
        """)
        self.tab_widget.addTab(self.text_widget, "Информация")
        
        # Вкладка для тестирования агентов
        self.agent_test_widget = QWidget()
        self.agent_layout = QVBoxLayout(self.agent_test_widget)
        
        self.agent_prompt = QTextEdit()
        self.agent_prompt.setPlaceholderText("Введите запрос для AI агента...")
        self.agent_layout.addWidget(self.agent_prompt)
        
        self.agent_button = QPushButton("Отправить запрос")
        self.agent_button.clicked.connect(self.on_agent_request)
        self.agent_layout.addWidget(self.agent_button)
        
        self.agent_response = QTextEdit()
        self.agent_response.setReadOnly(True)
        self.agent_response.setPlaceholderText("Здесь появится ответ агента...")
        self.agent_layout.addWidget(self.agent_response)
        
        self.tab_widget.addTab(self.agent_test_widget, "Тест агента")
        
        # Создаем меню
        self.create_menus()
        
        # Создаем панели инструментов
        self.create_toolbars()
        
        # Создаем доки
        self.create_docks()
        
        # Статусная строка
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Готово к тестированию")

    def create_menus(self):
        """Создает меню приложения."""
        # Меню "Файл"
        file_menu = self.menuBar().addMenu("Файл")
        
        # Действие "Новый"
        new_action = QAction("Новый", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_file_new)
        file_menu.addAction(new_action)
        
        # Действие "Открыть"
        open_action = QAction("Открыть...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_file_open)
        file_menu.addAction(open_action)
        
        # Действие "Сохранить"
        save_action = QAction("Сохранить", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_file_save)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Действие "Выход"
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Вид"
        view_menu = self.menuBar().addMenu("Вид")
        
        # Подменю "Панели инструментов"
        toolbar_menu = QMenu("Панели инструментов", self)
        view_menu.addMenu(toolbar_menu)
        
        # Действие для показа/скрытия основной панели инструментов
        main_toolbar_action = QAction("Основная панель", self)
        main_toolbar_action.setCheckable(True)
        main_toolbar_action.setChecked(True)
        main_toolbar_action.triggered.connect(lambda checked: self.main_toolbar.setVisible(checked))
        toolbar_menu.addAction(main_toolbar_action)
        
        # Подменю "Доки"
        dock_menu = QMenu("Доки", self)
        view_menu.addMenu(dock_menu)
        
        # Действие для показа/скрытия левого дока
        left_dock_action = QAction("Левый док", self)
        left_dock_action.setCheckable(True)
        left_dock_action.setChecked(True)
        left_dock_action.triggered.connect(lambda checked: self.left_dock.setVisible(checked))
        dock_menu.addAction(left_dock_action)
        
        # Действие для показа/скрытия правого дока
        right_dock_action = QAction("Правый док", self)
        right_dock_action.setCheckable(True)
        right_dock_action.setChecked(True)
        right_dock_action.triggered.connect(lambda checked: self.right_dock.setVisible(checked))
        dock_menu.addAction(right_dock_action)
        
        # Меню "Инструменты"
        tools_menu = self.menuBar().addMenu("Инструменты")
        
        # Действие "Настройки"
        settings_action = QAction("Настройки...", self)
        settings_action.triggered.connect(self.on_settings)
        tools_menu.addAction(settings_action)
        
        # Меню "Помощь"
        help_menu = self.menuBar().addMenu("Помощь")
        
        # Действие "О программе"
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def create_toolbars(self):
        """Создает панели инструментов."""
        # Основная панель инструментов
        self.main_toolbar = QToolBar("Основная панель")
        self.main_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.main_toolbar)
        
        # Добавляем действия на панель инструментов
        new_action = QAction("Новый", self)
        new_action.triggered.connect(self.on_file_new)
        self.main_toolbar.addAction(new_action)
        
        open_action = QAction("Открыть", self)
        open_action.triggered.connect(self.on_file_open)
        self.main_toolbar.addAction(open_action)
        
        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self.on_file_save)
        self.main_toolbar.addAction(save_action)
        
        self.main_toolbar.addSeparator()
        
        # Действие "Запустить"
        run_action = QAction("Запустить", self)
        run_action.triggered.connect(self.on_run)
        self.main_toolbar.addAction(run_action)
        
        # Действие "Остановить"
        stop_action = QAction("Остановить", self)
        stop_action.triggered.connect(self.on_stop)
        self.main_toolbar.addAction(stop_action)
        
        self.main_toolbar.addSeparator()
        
        # Действие "Настройки"
        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(self.on_settings)
        self.main_toolbar.addAction(settings_action)

    def create_docks(self):
        """Создает доки."""
        # Левый док (проводник)
        self.left_dock = QDockWidget("Проводник", self)
        self.left_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                     Qt.DockWidgetArea.RightDockWidgetArea)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        files_label = QLabel("Файлы проекта:")
        left_layout.addWidget(files_label)
        
        files_list = QTextEdit()
        files_list.setReadOnly(True)
        files_list.setText("main.py\nutils.py\nwidgets/\n  button.py\n  label.py")
        left_layout.addWidget(files_list)
        
        self.left_dock.setWidget(left_widget)
        
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.left_dock)
        
        # Правый док (свойства)
        self.right_dock = QDockWidget("Свойства", self)
        self.right_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                      Qt.DockWidgetArea.RightDockWidgetArea)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        properties_label = QLabel("Свойства объекта:")
        right_layout.addWidget(properties_label)
        
        properties_list = QTextEdit()
        properties_list.setReadOnly(True)
        properties_list.setText("Name: MainWindow\nSize: 1200x800\nVisible: True\nEnabled: True")
        right_layout.addWidget(properties_list)
        
        self.right_dock.setWidget(right_widget)
        
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_dock)

    # Обработчики событий
    def on_file_new(self):
        self.statusBar.showMessage("Создан новый файл")
        
    def on_file_open(self):
        self.statusBar.showMessage("Выберите файл для открытия...")
        
    def on_file_save(self):
        self.statusBar.showMessage("Файл сохранен")
        
    def on_run(self):
        self.statusBar.showMessage("Запуск...")
        
    def on_stop(self):
        self.statusBar.showMessage("Остановлено")
        
    def on_settings(self):
        self.statusBar.showMessage("Открыты настройки")
        
    def on_about(self):
        self.statusBar.showMessage("О программе GopiAI")
        
    def on_agent_request(self):
        """Обрабатывает запрос к AI агенту."""
        prompt = self.agent_prompt.toPlainText()
        if not prompt:
            return
            
        self.statusBar.showMessage("Обработка запроса к AI агенту...")
        self.agent_response.setText("Симуляция ответа AI агента:\n\n"
                                  f"Вы спросили: '{prompt}'\n\n"
                                  "В тестовом режиме агенты не подключены к AI сервисам.\n"
                                  "Это просто демонстрация интерфейса.")
        self.statusBar.showMessage("Ответ получен")

def main():
    """Основная функция для запуска приложения."""
    app = QApplication(sys.argv)
    app.setApplicationName("GopiAI Test Interface")
    
    # Устанавливаем тему
    app.setStyle("Fusion")
    
    # Создаем и показываем главное окно
    main_window = SimpleMainWindow()
    main_window.show()
    
    # Запускаем приложение
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}", exc_info=True)
        sys.exit(1)
