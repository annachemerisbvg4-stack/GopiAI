#!/usr/bin/env python3
"""
Простой тест браузера без Unicode символов
"""

import sys
import os
from pathlib import Path

# Устанавливаем UTF-8 для Windows
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
    from PySide6.QtCore import QUrl
    from pathlib import Path
    
    class SimpleBrowserTest(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Тест браузера GopiAI")
            self.setMinimumSize(800, 600)
            
            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Кнопка для создания браузера
            btn = QPushButton("Создать браузер с персистентным профилем")
            btn.clicked.connect(self.create_browser)
            layout.addWidget(btn)
            
            self.browser_container = QWidget()
            self.browser_layout = QVBoxLayout(self.browser_container)
            layout.addWidget(self.browser_container)
            
            print("Тестовое окно создано")
        
        def create_browser(self):
            try:
                print("Создаем браузер с персистентным профилем...")
                
                # Создаем папку для профиля
                profile_dir = Path.home() / ".gopiai" / "browser_profile"
                profile_dir.mkdir(parents=True, exist_ok=True)
                print(f"Папка профиля: {profile_dir}")
                
                # Создаем персистентный профиль
                profile = QWebEngineProfile("GopiAI_Test_Browser", self)
                
                # Настраиваем сохранение данных
                profile.setPersistentStoragePath(str(profile_dir))
                profile.setCachePath(str(profile_dir / "cache"))
                profile.setPersistentCookiesPolicy(
                    QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
                )
                profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
                
                # Настройки браузера
                settings = profile.settings()
                settings.setAttribute(settings.WebAttribute.LocalStorageEnabled, True)
                settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)
                
                # Создаем браузер
                browser = QWebEngineView()
                page = QWebEnginePage(profile, browser)
                browser.setPage(page)
                
                # Добавляем в лейаут
                self.browser_layout.addWidget(browser)
                
                # Загружаем тестовую страницу
                browser.load(QUrl("https://google.com"))
                
                print("Браузер создан успешно!")
                print("Профиль сохраняет данные в:", profile_dir)
                
            except Exception as e:
                print(f"Ошибка: {e}")
                import traceback
                traceback.print_exc()
    
    def main():
        print("Запуск теста браузера...")
        
        app = QApplication(sys.argv)
        app.setApplicationName("GopiAI_BrowserTest")
        
        window = SimpleBrowserTest()
        window.show()
        
        print("Нажмите кнопку для создания браузера")
        print("Проверьте, что страницы загружаются")
        
        sys.exit(app.exec())

except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Установите зависимости: pip install PySide6[webengine]")
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    main()
