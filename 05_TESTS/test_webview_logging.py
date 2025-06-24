#!/usr/bin/env python3
"""
Тестирование системы логирования WebView консоли
===============================================

Этот скрипт тестирует новую систему перехвата логов JavaScript консоли
и их передачу в Python для отладки WebView.
"""

import sys
from pathlib import Path
import time

# Добавляем пути для импорта
sys.path.insert(0, str(Path(__file__).parent / "GopiAI-UI"))
sys.path.insert(0, str(Path(__file__).parent / "GopiAI-WebView"))

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QTextEdit, QLabel
from PySide6.QtCore import Qt, QTimer


class WebViewLoggingTest(QWidget):
    """Тестовое окно для демонстрации логирования WebView"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GopiAI WebView Logging Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Основной layout
        layout = QVBoxLayout(self)
        
        # Информационная панель
        info_label = QLabel("🔍 Тестирование системы логирования WebView консоли")
        info_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(info_label)
        
        # WebView чат
        self.chat_widget = ()
        layout.addWidget(self.chat_widget, stretch=3)
        
        # Панель для отображения логов
        logs_label = QLabel("📋 JavaScript Console Logs:")
        logs_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(logs_label)
        
        self.logs_display = QTextEdit()
        self.logs_display.setMaximumHeight(200)
        self.logs_display.setStyleSheet("""
            background-color: #1e1e1e; 
            color: #ffffff; 
            font-family: 'Courier New', monospace; 
            font-size: 11px;
        """)
        layout.addWidget(self.logs_display, stretch=1)
        
        # Кнопки для тестирования
        test_buttons_layout = QVBoxLayout()
        
        test_log_btn = QPushButton("🧪 Тест console.log")
        test_log_btn.clicked.connect(self.test_console_log)
        test_buttons_layout.addWidget(test_log_btn)
        
        test_error_btn = QPushButton("🚨 Тест console.error")
        test_error_btn.clicked.connect(self.test_console_error)
        test_buttons_layout.addWidget(test_error_btn)
        
        test_puter_btn = QPushButton("🌐 Тест puter.js загрузки")
        test_puter_btn.clicked.connect(self.test_puter_loading)
        test_buttons_layout.addWidget(test_puter_btn)
        
        clear_logs_btn = QPushButton("🧹 Очистить логи")
        clear_logs_btn.clicked.connect(self.clear_logs)
        test_buttons_layout.addWidget(clear_logs_btn)
        
        layout.addLayout(test_buttons_layout)
        
        # Подключаемся к системе логирования
        self.setup_logging_connections()
        
        # Добавляем стартовое сообщение
        self.add_log("info", "🚀 Система логирования WebView инициализирована", "test")
    
    def setup_logging_connections(self):
        """Настройка подключений к системе логирования"""
        try:
            # Подключаемся к signal логирования JavaScript консоли
            if hasattr(self.chat_widget.bridge, 'js_console_log'):
                self.chat_widget.bridge.js_console_log.connect(self.on_js_log_received)
                print("✅ Подключен к js_console_log signal")
            else:
                print("⚠️ js_console_log signal не найден")
            
            # Подключаемся к остальным signals
            if hasattr(self.chat_widget.bridge, 'error_occurred'):
                self.chat_widget.bridge.error_occurred.connect(
                    lambda msg: self.add_log("error", msg, "bridge")
                )
                print("✅ Подключен к error_occurred signal")
                
        except Exception as e:
            print(f"❌ Ошибка при настройке logging connections: {e}")
            self.add_log("error", f"Ошибка настройки логирования: {e}", "test")
    
    def on_js_log_received(self, level: str, message: str, source: str):
        """Обработчик получения логов от JavaScript"""
        self.add_log(level, message, source)
    
    def add_log(self, level: str, message: str, source: str = ""):
        """Добавление лога в панель отображения"""
        # Цветовая кодировка по уровню
        color_map = {
            "error": "#ff4444",
            "warn": "#ffaa00", 
            "info": "#00aaff",
            "debug": "#888888",
            "log": "#ffffff"
        }
        
        # Иконки по уровню
        icon_map = {
            "error": "❌",
            "warn": "⚠️",
            "info": "ℹ️",
            "debug": "🐛",
            "log": "📝"
        }
        
        color = color_map.get(level, "#ffffff")
        icon = icon_map.get(level, "📝")
        
        # Формируем сообщение
        timestamp = time.strftime("%H:%M:%S")
        source_part = f" [{source}]" if source else ""
        
        formatted_message = f'<span style="color: {color};">[{timestamp}] {icon} {message.replace("<", "&lt;").replace(">", "&gt;")}{source_part}</span>'
        
        # Добавляем в виджет
        self.logs_display.append(formatted_message)
        
        # Прокручиваем вниз
        cursor = self.logs_display.textCursor()
        cursor.movePosition(cursor.End)
        self.logs_display.setTextCursor(cursor)
    
    def test_console_log(self):
        """Тестирование console.log"""
        self.add_log("info", "Выполняется тест console.log...", "test")
        
        script = """
        console.log('🧪 Test console.log message from WebView');
        console.log('Это тестовое сообщение для проверки системы логирования');
        """
        
        self.chat_widget.web_view.page().runJavaScript(script)
    
    def test_console_error(self):
        """Тестирование console.error"""
        self.add_log("info", "Выполняется тест console.error...", "test")
        
        script = """
        console.error('🚨 Test console.error message from WebView');
        console.warn('⚠️ Test console.warn message');
        """
        
        self.chat_widget.web_view.page().runJavaScript(script)
    
    def test_puter_loading(self):
        """Тестирование загрузки puter.js"""
        self.add_log("info", "Проверка состояния puter.js...", "test")
        
        script = """
        if (typeof puter !== 'undefined') {
            console.log('✅ puter.js загружен успешно');
            console.log('Версия puter:', puter.version || 'неизвестно');
        } else {
            console.warn('⚠️ puter.js не загружен');
        }
        
        // Проверяем наличие chat объекта
        if (typeof window.chat !== 'undefined') {
            console.log('✅ Chat объект инициализирован');
        } else {
            console.warn('⚠️ Chat объект не найден');
        }
        
        // Проверяем bridge
        if (typeof bridge !== 'undefined') {
            console.log('✅ Bridge подключен');
        } else {
            console.warn('⚠️ Bridge не подключен');
        }
        """
        
        self.chat_widget.web_view.page().runJavaScript(script)
    
    def clear_logs(self):
        """Очистка панели логов"""
        self.logs_display.clear()
        self.add_log("info", "Логи очищены", "test")

def main():
    """Главная функция"""
    app = QApplication(sys.argv)
    
    # Применяем темную тему
    app.setStyleSheet("""
        QWidget {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        QPushButton {
            background-color: #0078d4;
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        QLabel {
            color: #ffffff;
        }
    """)
    
    # Создаем и показываем окно тестирования
    test_window = WebViewLoggingTest()
    test_window.show()
    
    print("🧪 Тестовое окно WebView логирования запущено")
    print("📋 Инструкции:")
    print("   1. Нажмите кнопки для тестирования разных типов логов")
    print("   2. Наблюдайте за выводом логов в нижней панели")
    print("   3. Проверьте, что логи JavaScript передаются в Python")
    print("   4. Логи также выводятся в консоль Python")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())