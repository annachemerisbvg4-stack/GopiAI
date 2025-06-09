"""
Ультра-простой браузер, только WebEngine без лишних наворотов
"""

import os
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

# Отключаем аппаратное ускорение, которое может вызывать проблемы
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"
os.environ["QT_OPENGL"] = "software"

class UltraSimpleBrowser(QWidget):
    """Максимально упрощенный браузерный виджет для тестирования"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем веб-движок
        self.browser = QWebEngineView(self)
        self.browser.setUrl(QUrl("https://google.com"))
        
        # Добавляем в лейаут
        self.main_layout.addWidget(self.browser)
        

# Для тестирования как отдельного приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    browser = UltraSimpleBrowser()
    window.setCentralWidget(browser)
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
