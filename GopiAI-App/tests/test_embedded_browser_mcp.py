#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестирование интеграции BrowserMCP с встроенным браузером.

Простой скрипт для тестирования интеграции BrowserMCP с встроенным браузером.
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
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

from gopiai.app.utils.browser_adapters import HybridBrowserAdapter
from gopiai.app.utils.browsermcp_setup import setup_browsermcp
from gopiai.app.utils.browsermcp_injector import inject_browsermcp, execute_browsermcp_command

class TestWindow(QMainWindow):
    """Тестовое окно для проверки интеграции BrowserMCP с встроенным браузером."""
    
    def __init__(self):
        """Инициализирует тестовое окно."""
        super().__init__()
        
        # Настраиваем окно
        self.setWindowTitle("Тестирование интеграции BrowserMCP с встроенным браузером")
        self.setGeometry(100, 100, 800, 600)
        
        # Создаем центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Создаем лейаут
        self.layout = QVBoxLayout(self.central_widget)
        
        # Создаем браузер
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.example.com"))
        
        # Создаем кнопки
        self.setup_button = QPushButton("Настроить BrowserMCP")
        self.setup_button.clicked.connect(self.setup_browsermcp)
        
        self.inject_button = QPushButton("Внедрить BrowserMCP")
        self.inject_button.clicked.connect(self.inject_browsermcp)
        
        self.navigate_button = QPushButton("Перейти на Google")
        self.navigate_button.clicked.connect(self.navigate_to_google)
        
        self.extract_button = QPushButton("Извлечь содержимое")
        self.extract_button.clicked.connect(self.extract_content)
        
        # Создаем метку для вывода результатов
        self.result_label = QLabel("Результаты:")
        
        # Добавляем виджеты в лейаут
        self.layout.addWidget(self.setup_button)
        self.layout.addWidget(self.inject_button)
        self.layout.addWidget(self.navigate_button)
        self.layout.addWidget(self.extract_button)
        self.layout.addWidget(self.result_label)
        self.layout.addWidget(self.browser)
        
        # Создаем адаптер
        self.adapter = None
        
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
                self.result_label.setText("BrowserMCP успешно настроен")
            else:
                self.result_label.setText("Не удалось настроить BrowserMCP")
        except Exception as e:
            logger.error(f"Ошибка при настройке BrowserMCP: {str(e)}")
            self.result_label.setText(f"Ошибка: {str(e)}")
            
    def inject_browsermcp(self):
        """Внедряет BrowserMCP в браузер."""
        logger.info("Внедрение BrowserMCP...")
        
        # Запускаем внедрение BrowserMCP
        asyncio.ensure_future(self._inject_browsermcp())
        
    async def _inject_browsermcp(self):
        """Асинхронно внедряет BrowserMCP в браузер."""
        try:
            # Внедряем BrowserMCP
            result = await inject_browsermcp(self.browser)
            
            # Выводим результат
            if result:
                self.result_label.setText("BrowserMCP успешно внедрен")
                
                # Создаем адаптер
                self.adapter = HybridBrowserAdapter(preferred_tool="mcp", browser=self.browser)
                await self.adapter.initialize()
            else:
                self.result_label.setText("Не удалось внедрить BrowserMCP")
        except Exception as e:
            logger.error(f"Ошибка при внедрении BrowserMCP: {str(e)}")
            self.result_label.setText(f"Ошибка: {str(e)}")
            
    def navigate_to_google(self):
        """Переходит на Google."""
        logger.info("Переход на Google...")
        
        # Запускаем переход на Google
        asyncio.ensure_future(self._navigate_to_google())
        
    async def _navigate_to_google(self):
        """Асинхронно переходит на Google."""
        try:
            # Проверяем, создан ли адаптер
            if not self.adapter:
                self.result_label.setText("Сначала внедрите BrowserMCP")
                return
                
            # Переходим на Google
            result = await self.adapter.navigate("https://www.google.com")
            
            # Выводим результат
            if result.get("success"):
                self.result_label.setText("Успешно выполнен переход на Google")
            else:
                self.result_label.setText(f"Ошибка: {result.get('message')}")
        except Exception as e:
            logger.error(f"Ошибка при переходе на Google: {str(e)}")
            self.result_label.setText(f"Ошибка: {str(e)}")
            
    def extract_content(self):
        """Извлекает содержимое страницы."""
        logger.info("Извлечение содержимого...")
        
        # Запускаем извлечение содержимого
        asyncio.ensure_future(self._extract_content())
        
    async def _extract_content(self):
        """Асинхронно извлекает содержимое страницы."""
        try:
            # Проверяем, создан ли адаптер
            if not self.adapter:
                self.result_label.setText("Сначала внедрите BrowserMCP")
                return
                
            # Извлекаем содержимое
            result = await self.adapter.extract_content()
            
            # Выводим результат
            if result.get("success"):
                content = result.get("data", {}).get("content", "Содержимое не найдено")
                self.result_label.setText(f"Успешно извлечено содержимое: {content[:100]}...")
            else:
                self.result_label.setText(f"Ошибка: {result.get('message')}")
        except Exception as e:
            logger.error(f"Ошибка при извлечении содержимого: {str(e)}")
            self.result_label.setText(f"Ошибка: {str(e)}")

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
