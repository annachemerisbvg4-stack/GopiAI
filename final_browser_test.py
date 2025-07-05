#!/usr/bin/env python3
"""
Финальный тест исправленного браузера
"""

import sys
import os
from pathlib import Path

# Устанавливаем UTF-8 для Windows
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Добавляем пути к модулям проекта
project_root = Path(__file__).parent
ui_module_path = project_root / "GopiAI-UI"
sys.path.insert(0, str(ui_module_path))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
    from PySide6.QtCore import Qt
    
    # Импортируем наши виджеты
    from gopiai.ui.components.enhanced_browser_widget import EnhancedBrowserWidget
    
    class BrowserTestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Тест исправленного браузера GopiAI")
            self.setMinimumSize(1000, 700)
            
            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Заголовок
            title = QLabel("Тест браузера с персистентным профилем")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
            layout.addWidget(title)
            
            # Кнопка для создания браузера
            btn = QPushButton("Создать Enhanced браузер")
            btn.clicked.connect(self.create_enhanced_browser)
            layout.addWidget(btn)
            
            # Контейнер для браузера
            self.browser_container = QWidget()
            self.browser_layout = QVBoxLayout(self.browser_container)
            layout.addWidget(self.browser_container)
            
            # Информационная панель
            info = QLabel("""Нажмите кнопку выше для создания браузера.
Браузер должен:
1. Открыться без ошибок
2. Загрузить Google
3. Сохранять данные между запусками
4. Поддерживать куки и историю""")
            info.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
            layout.addWidget(info)
            
            print("Тестовое окно создано успешно")
        
        def create_enhanced_browser(self):
            try:
                print("Создаем Enhanced браузер...")
                
                # Создаем браузер
                self.browser = EnhancedBrowserWidget()
                
                # Добавляем в контейнер
                self.browser_layout.addWidget(self.browser)
                
                # Загружаем Google
                self.browser.load_url("https://google.com")
                
                print("Enhanced браузер создан успешно!")
                print("Профиль сохраняется в: ~/.gopiai/browser_profile")
                
                # Подключаем сигналы для отслеживания загрузки
                self.browser.page_loaded.connect(self.on_page_loaded)
                
            except Exception as e:
                print(f"Ошибка создания Enhanced браузера: {e}")
                import traceback
                traceback.print_exc()
        
        def on_page_loaded(self, url, title):
            print(f"Страница загружена: {title} ({url})")
    
    def main():
        print("Запуск финального теста браузера...")
        
        app = QApplication(sys.argv)
        app.setApplicationName("GopiAI_FinalBrowserTest")
        app.setApplicationVersion("1.0")
        
        window = BrowserTestWindow()
        window.show()
        
        print("\nИнструкции по тестированию:")
        print("1. Нажмите 'Создать Enhanced браузер'")
        print("2. Проверьте, что Google загружается")
        print("3. Попробуйте перейти на другие сайты")
        print("4. Закройте приложение и запустите снова")
        print("5. Данные должны сохраниться\n")
        
        sys.exit(app.exec())

except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что установлены зависимости:")
    print("pip install PySide6[webengine]")
except Exception as e:
    print(f"Общая ошибка: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    main()
