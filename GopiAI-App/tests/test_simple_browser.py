#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Простой тест встроенного браузера.

Простой скрипт для тестирования встроенного браузера.
"""

import sys
import os
import asyncio
from gopiai.core.logging import get_logger
logger = get_logger().logger
from typing import Optional, Dict, Any

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = get_logger().logger

# Импортируем необходимые модули
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

class TestWindow(QMainWindow):
    """Тестовое окно для проверки встроенного браузера."""
    
    def __init__(self):
        """Инициализирует тестовое окно."""
        super().__init__()
        
        # Настраиваем окно
        self.setWindowTitle("Тестирование встроенного браузера")
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
        self.navigate_button = QPushButton("Перейти на Google")
        self.navigate_button.clicked.connect(self.navigate_to_google)
        
        self.execute_js_button = QPushButton("Выполнить JavaScript")
        self.execute_js_button.clicked.connect(self.execute_js)
        
        # Создаем метку для вывода результатов
        self.result_label = QLabel("Результаты:")
        
        # Добавляем виджеты в лейаут
        self.layout.addWidget(self.navigate_button)
        self.layout.addWidget(self.execute_js_button)
        self.layout.addWidget(self.result_label)
        self.layout.addWidget(self.browser)
        
        logger.info("Тестовое окно инициализировано")
        
    def navigate_to_google(self):
        """Переходит на Google."""
        logger.info("Переход на Google...")
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.result_label.setText("Переход на Google...")
            
    def execute_js(self):
        """Выполняет JavaScript-код."""
        logger.info("Выполнение JavaScript-кода...")
        
        # JavaScript-код для выполнения
        js_code = """
        (function() {
            // Получаем заголовок страницы
            var title = document.title;
            
            // Возвращаем результат
            return "Заголовок страницы: " + title;
        })();
        """
        
        # Выполняем JavaScript-код
        self.browser.page().runJavaScript(js_code, 0, self.handle_js_result)
        
    def handle_js_result(self, result):
        """Обрабатывает результат выполнения JavaScript-кода."""
        logger.info(f"Результат выполнения JavaScript-кода: {result}")
        self.result_label.setText(result)

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
