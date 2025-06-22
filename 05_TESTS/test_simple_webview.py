#!/usr/bin/env python3
"""
Простой тест WebView без системы логирования
===========================================

Создаём минимальный WebView без перехвата консоли для проверки стабильности.
"""

import sys
from pathlib import Path

# Добавляем пути для импорта
sys.path.insert(0, str(Path(__file__).parent / "GopiAI-UI"))

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

class SimpleWebViewTest(QWidget):
    """Простой тест WebView без системы логирования"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GopiAI WebView Stability Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Основной layout
        layout = QVBoxLayout(self)
        
        # Информационная панель
        info_label = QLabel("🧪 Тестирование стабильности WebView (без логирования)")
        info_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(info_label)
        
        # WebView
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # Настройка WebEngine (минимальная)
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        
        # Кнопки для тестирования
        test_btn = QPushButton("🌐 Загрузить простую страницу")
        test_btn.clicked.connect(self.load_simple_page)
        layout.addWidget(test_btn)
        
        puter_btn = QPushButton("🚀 Загрузить puter.js (CDN)")
        puter_btn.clicked.connect(self.load_puter_test)
        layout.addWidget(puter_btn)
        
        close_btn = QPushButton("❌ Закрыть")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def load_simple_page(self):
        """Загрузка простой HTML страницы"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Simple Test</title>
            <style>
                body { font-family: Arial; padding: 20px; background: #f0f0f0; }
                .test { padding: 10px; margin: 10px; background: white; border: 1px solid #ccc; }
            </style>
        </head>
        <body>
            <h1>✅ WebView Test Page</h1>
            <div class="test">
                <h3>JavaScript Test:</h3>
                <button onclick="testFunction()">Run Test</button>
                <div id="result"></div>
            </div>
            
            <script>
                function testFunction() {
                    const result = document.getElementById('result');
                    result.innerHTML = '<p style="color: green;">✅ JavaScript работает!</p>';
                    
                    // Простое логирование без перехвата
                    console.log('Test function executed successfully');
                }
                
                // Проверяем загрузку
                document.addEventListener('DOMContentLoaded', function() {
                    console.log('✅ Simple page loaded successfully');
                });
            </script>
        </body>
        </html>
        """
        
        self.web_view.setHtml(html)
        print("🔄 Простая страница загружена")
    
    def load_puter_test(self):
        """Загрузка страницы с puter.js"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Puter.js Test</title>
            <script src="https://js.puter.com/v2/"></script>
            <style>
                body { font-family: Arial; padding: 20px; background: #f0f0f0; }
                .status { padding: 10px; margin: 10px; background: white; border: 1px solid #ccc; }
                .success { border-color: green; background: #f0fff0; }
                .error { border-color: red; background: #fff0f0; }
            </style>
        </head>
        <body>
            <h1>🚀 Puter.js Test Page</h1>
            <div id="status" class="status">Загрузка puter.js...</div>
            
            <script>
                function updateStatus(message, isSuccess = true) {
                    const status = document.getElementById('status');
                    status.textContent = message;
                    status.className = isSuccess ? 'status success' : 'status error';
                }
                
                // Ожидание загрузки puter.js
                function waitForPuter() {
                    if (typeof puter !== 'undefined') {
                        updateStatus('✅ Puter.js загружен успешно!');
                        console.log('✅ Puter.js ready');
                        
                        // Проверяем базовые функции
                        if (puter.ai && puter.ai.chat) {
                            updateStatus('✅ Puter.js и puter.ai готовы к работе!');
                        }
                    } else {
                        setTimeout(waitForPuter, 100);
                    }
                }
                
                // Запускаем проверку после загрузки DOM
                document.addEventListener('DOMContentLoaded', function() {
                    console.log('DOM loaded, waiting for puter.js...');
                    waitForPuter();
                });
                
                // Обработка ошибок загрузки
                window.addEventListener('error', function(event) {
                    updateStatus('❌ Ошибка: ' + event.message, false);
                    console.error('Page error:', event);
                });
            </script>
        </body>
        </html>
        """
        
        self.web_view.setHtml(html)
        print("🔄 Страница с puter.js загружена")

def main():
    """Главная функция"""
    app = QApplication(sys.argv)
    
    # Применяем тёмную тему
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
        QLabel {
            color: #ffffff;
        }
    """)
    
    # Создаём и показываем окно тестирования
    test_window = SimpleWebViewTest()
    test_window.show()
    
    print("🧪 Простой тест WebView запущен")
    print("📋 Инструкции:")
    print("   1. Нажмите 'Загрузить простую страницу' для базового теста")
    print("   2. Нажмите 'Загрузить puter.js' для теста с внешней библиотекой")
    print("   3. Проверьте, что нет падений приложения")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())