#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы браузера с персистентным профилем
"""

import sys
import os
from pathlib import Path

# Добавляем пути к модулям проекта
project_root = Path(__file__).parent
ui_module_path = project_root / "GopiAI-UI"
sys.path.insert(0, str(ui_module_path))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
    from PySide6.QtCore import Qt
    
    # Импортируем наши виджеты
    from gopiai.ui.components.tab_widget import TabDocumentWidget
    from gopiai.ui.components.enhanced_browser_widget import EnhancedBrowserWidget
    
    class TestBrowserWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("🔥 Тест браузера GopiAI с персистентным профилем")
            self.setMinimumSize(1000, 700)
            
            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Кнопки для тестирования
            btn_layout = QVBoxLayout()
            
            btn_tab_browser = QPushButton("🌐 Создать вкладку браузера в TabWidget")
            btn_tab_browser.clicked.connect(self.create_tab_browser)
            
            btn_enhanced_browser = QPushButton("⚡ Создать EnhancedBrowserWidget")
            btn_enhanced_browser.clicked.connect(self.create_enhanced_browser)
            
            btn_layout.addWidget(btn_tab_browser)
            btn_layout.addWidget(btn_enhanced_browser)
            
            layout.addLayout(btn_layout)
            
            # TabWidget для тестирования
            self.tab_widget = TabDocumentWidget()
            layout.addWidget(self.tab_widget)
            
            print("✅ Тестовое окно создано успешно")
        
        def create_tab_browser(self):
            """Создает вкладку браузера в TabWidget"""
            try:
                print("🔄 Создаем вкладку браузера...")
                browser_widget = self.tab_widget.add_browser_tab(
                    url="https://google.com", 
                    title="Google Test"
                )
                print("✅ Вкладка браузера создана!")
                return browser_widget
            except Exception as e:
                print(f"❌ Ошибка создания вкладки браузера: {e}")
                import traceback
                traceback.print_exc()
        
        def create_enhanced_browser(self):
            """Создает EnhancedBrowserWidget"""
            try:
                print("🔄 Создаем Enhanced браузер...")
                enhanced_browser = EnhancedBrowserWidget()
                enhanced_browser.load_url("https://google.com")
                
                # Добавляем как новую вкладку
                index = self.tab_widget.tab_widget.addTab(enhanced_browser, "Enhanced Browser")
                self.tab_widget.tab_widget.setCurrentIndex(index)
                print("✅ Enhanced браузер создан!")
                return enhanced_browser
            except Exception as e:
                print(f"❌ Ошибка создания Enhanced браузера: {e}")
                import traceback
                traceback.print_exc()
    
    def main():
        print("🚀 Запуск теста браузера...")
        
        app = QApplication(sys.argv)
        
        # Устанавливаем имя приложения для профилей
        app.setApplicationName("GopiAI_BrowserTest")
        app.setApplicationVersion("1.0")
        
        window = TestBrowserWindow()
        window.show()
        
        print("\n📋 Инструкции:")
        print("1. Нажмите 'Создать вкладку браузера' для тестирования TabWidget")
        print("2. Нажмите 'Создать EnhancedBrowserWidget' для тестирования Enhanced виджета")
        print("3. Проверьте, что браузер открывается и загружает страницы")
        print("4. Закройте и перезапустите тест - данные должны сохраниться\n")
        
        sys.exit(app.exec())

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что установлены все зависимости:")
    print("pip install PySide6[webengine]")
    sys.exit(1)
except Exception as e:
    print(f"❌ Общая ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    main()
