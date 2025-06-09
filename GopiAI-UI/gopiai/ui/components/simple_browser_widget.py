"""
Простой тестовый браузер виджет для диагностики
"""

import logging
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

logger = logging.getLogger(__name__)

class SimpleBrowserWidget(QWidget):
    """Простой браузер виджет для тестирования"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Добавляем метку для диагностики
        self.label = QLabel("🌐 Простой браузер GopiAI")
        self.label.setStyleSheet("color: white; background: #4a9eff; padding: 5px; border-radius: 3px;")
        layout.addWidget(self.label)
        
        # Создаем браузер
        self.browser = QWebEngineView()
        self.browser.setMinimumSize(400, 300)
        
        # Устанавливаем простой фон
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 2px solid #4a9eff;
                border-radius: 5px;
            }
        """)
        
        layout.addWidget(self.browser)
        
        print("🌐 SimpleBrowserWidget created successfully")
    
    def load_url(self, url):
        """Загружает URL"""
        try:
            print(f"🌐 Loading URL: {url}")
            self.browser.load(QUrl(url))
            self.browser.show()
            print("🌐 URL loaded, browser shown")
        except Exception as e:
            print(f"❌ Error loading URL: {e}")
