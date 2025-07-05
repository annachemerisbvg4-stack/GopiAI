#!/usr/bin/env python3
"""
Прямой тест Enhanced браузера
"""

import sys
import os
from pathlib import Path

# Устанавливаем UTF-8 для Windows
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
    from PySide6.QtCore import QUrl, Slot, Signal
    from pathlib import Path
    import logging
    
    # Настраиваем простое логирование
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    
    class DirectEnhancedBrowserWidget(QWidget):
        """Прямая копия Enhanced браузера без внешних зависимостей"""
        
        page_loaded = Signal(str, str)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.current_url = ""
            self.current_title = ""
            self._setup_ui()
            
        def _setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Создаем браузер с персистентным профилем
            try:
                # Папка профиля
                profile_dir = Path.home() / ".gopiai" / "browser_profile"
                profile_dir.mkdir(parents=True, exist_ok=True)
                
                # Персистентный профиль
                self.profile = QWebEngineProfile("GopiAI_Direct_Test", self)
                self.profile.setPersistentStoragePath(str(profile_dir))
                self.profile.setCachePath(str(profile_dir / "cache"))
                self.profile.setPersistentCookiesPolicy(
                    QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
                )
                self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
                
                # Настройки
                settings = self.profile.settings()
                settings.setAttribute(settings.WebAttribute.LocalStorageEnabled, True)
                settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)
                
                # Создаем браузер
                self.browser = QWebEngineView(self)
                page = QWebEnginePage(self.profile, self.browser)
                self.browser.setPage(page)
                
                layout.addWidget(self.browser)
                
                # Подключаем сигналы
                self.browser.loadFinished.connect(self._on_load_finished)
                
                logger.info(f"Браузер создан с профилем: {profile_dir}")
                
            except Exception as e:
                logger.error(f"Ошибка создания браузера: {e}")
                import traceback
                traceback.print_exc()
        
        def load_url(self, url):
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            logger.info(f"Загружаем: {url}")
            self.browser.load(QUrl(url))
        
        @Slot(bool)
        def _on_load_finished(self, success):
            if success:
                self.current_url = self.browser.url().toString()
                self.current_title = self.browser.page().title()
                logger.info(f"Загружено: {self.current_title} ({self.current_url})")
                self.page_loaded.emit(self.current_url, self.current_title)
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Прямой тест Enhanced браузера")
            self.setMinimumSize(1000, 700)
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Кнопка
            btn = QPushButton("Создать браузер")
            btn.clicked.connect(self.create_browser)
            layout.addWidget(btn)
            
            # Статус
            self.status = QLabel("Нажмите кнопку для создания браузера")
            layout.addWidget(self.status)
            
            # Контейнер для браузера
            self.container = QWidget()
            self.container_layout = QVBoxLayout(self.container)
            layout.addWidget(self.container)
            
        def create_browser(self):
            try:
                self.status.setText("Создаем браузер...")
                
                self.browser = DirectEnhancedBrowserWidget()
                self.container_layout.addWidget(self.browser)
                
                self.browser.page_loaded.connect(self.on_page_loaded)
                self.browser.load_url("google.com")
                
                self.status.setText("Браузер создан! Загружаем Google...")
                
            except Exception as e:
                self.status.setText(f"Ошибка: {e}")
                logger.error(f"Ошибка: {e}")
                import traceback
                traceback.print_exc()
        
        def on_page_loaded(self, url, title):
            self.status.setText(f"Загружено: {title}")
    
    def main():
        print("Запуск прямого теста Enhanced браузера...")
        
        app = QApplication(sys.argv)
        app.setApplicationName("DirectBrowserTest")
        
        window = TestWindow()
        window.show()
        
        print("Окно открыто. Нажмите кнопку для тестирования.")
        
        sys.exit(app.exec())
        
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("pip install PySide6[webengine]")
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    main()
