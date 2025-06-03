#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестирование специализированного браузерного агента.

Простой скрипт для тестирования специализированного браузерного агента.
"""

import sys
import os
import asyncio
from gopiai.core.logging import get_logger
logger = get_logger().logger
from typing import Optional, Dict, Any

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = get_logger().logger

# Импортируем необходимые модули
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

from gopiai.app.agent.browser_specialized_agent import BrowserSpecializedAgent
from gopiai.app.utils.browsermcp_setup import setup_browsermcp, get_browsermcp_setup

class TestWindow(QMainWindow):
    """Тестовое окно для проверки специализированного браузерного агента."""
    
    def __init__(self):
        """Инициализирует тестовое окно."""
        super().__init__()
        
        # Настраиваем окно
        self.setWindowTitle("Тестирование специализированного браузерного агента")
        self.setGeometry(100, 100, 1000, 800)
        
        # Создаем центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Создаем лейаут
        self.layout = QVBoxLayout(self.central_widget)
        
        # Создаем браузер
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.example.com"))
        
        # Создаем поле для ввода запроса
        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("Введите запрос для агента...")
        self.query_input.setMaximumHeight(100)
        
        # Создаем кнопки
        self.setup_button = QPushButton("Настроить BrowserMCP")
        self.setup_button.clicked.connect(self.setup_browsermcp)
        
        self.init_agent_button = QPushButton("Инициализировать агента")
        self.init_agent_button.clicked.connect(self.init_agent)
        
        self.process_button = QPushButton("Обработать запрос")
        self.process_button.clicked.connect(self.process_query)
        
        self.get_state_button = QPushButton("Получить состояние")
        self.get_state_button.clicked.connect(self.get_state)
        
        # Создаем метку для вывода результатов
        self.result_label = QLabel("Результаты:")
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        
        # Добавляем виджеты в лейаут
        self.layout.addWidget(self.setup_button)
        self.layout.addWidget(self.init_agent_button)
        self.layout.addWidget(self.query_input)
        self.layout.addWidget(self.process_button)
        self.layout.addWidget(self.get_state_button)
        self.layout.addWidget(self.result_label)
        self.layout.addWidget(self.result_output)
        self.layout.addWidget(self.browser)
        
        # Создаем агента
        self.agent = None
        
        logger.info("Тестовое окно инициализировано")
        
    def setup_browsermcp(self):
        """Настраивает BrowserMCP."""
        logger.info("Настройка BrowserMCP...")
        
        # Запускаем настройку BrowserMCP
        asyncio.ensure_future(self._setup_browsermcp())
        
    async def _setup_browsermcp(self):
        """Асинхронно настраивает BrowserMCP."""
        try:
            # Настраиваем BrowserMCP
            result = await setup_browsermcp()
            
            # Выводим результат
            if result:
                self.result_output.setText("BrowserMCP успешно настроен")
            else:
                self.result_output.setText("Не удалось настроить BrowserMCP")
        except Exception as e:
            logger.error(f"Ошибка при настройке BrowserMCP: {str(e)}")
            self.result_output.setText(f"Ошибка: {str(e)}")
            
    def init_agent(self):
        """Инициализирует агента."""
        logger.info("Инициализация агента...")
        
        # Запускаем инициализацию агента
        asyncio.ensure_future(self._init_agent())
        
    async def _init_agent(self):
        """Асинхронно инициализирует агента."""
        try:
            # Создаем агента
            self.agent = BrowserSpecializedAgent(
                preferred_tool="mcp",
                browser=self.browser
            )
            
            # Устанавливаем контекст
            await self.agent.set_context({
                "task": "Работа с браузером",
                "relevant_files": {
                    "browser_specialized_agent.py": {
                        "summary": "Специализированный агент для работы с браузером"
                    }
                }
            })
            
            # Выводим результат
            self.result_output.setText("Агент успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации агента: {str(e)}")
            self.result_output.setText(f"Ошибка: {str(e)}")
            
    def process_query(self):
        """Обрабатывает запрос."""
        logger.info("Обработка запроса...")
        
        # Получаем запрос
        query = self.query_input.toPlainText()
        
        # Проверяем, что запрос не пустой
        if not query:
            self.result_output.setText("Запрос не может быть пустым")
            return
            
        # Запускаем обработку запроса
        asyncio.ensure_future(self._process_query(query))
        
    async def _process_query(self, query):
        """Асинхронно обрабатывает запрос."""
        try:
            # Проверяем, что агент инициализирован
            if not self.agent:
                self.result_output.setText("Сначала инициализируйте агента")
                return
                
            # Обрабатываем запрос
            result = await self.agent.process(query)
            
            # Выводим результат
            self.result_output.setText(result)
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {str(e)}")
            self.result_output.setText(f"Ошибка: {str(e)}")
            
    def get_state(self):
        """Получает состояние агента."""
        logger.info("Получение состояния агента...")
        
        # Запускаем получение состояния
        asyncio.ensure_future(self._get_state())
        
    async def _get_state(self):
        """Асинхронно получает состояние агента."""
        try:
            # Проверяем, что агент инициализирован
            if not self.agent:
                self.result_output.setText("Сначала инициализируйте агента")
                return
                
            # Получаем состояние
            state = self.agent.get_current_state()
            
            # Выводим состояние
            import json
            self.result_output.setText(json.dumps(state, indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Ошибка при получении состояния: {str(e)}")
            self.result_output.setText(f"Ошибка: {str(e)}")

def main():
    """Основная функция."""
    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Создаем и показываем окно
    window = TestWindow()
    window.show()
    
    # Запускаем цикл событий
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
