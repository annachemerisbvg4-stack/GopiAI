#!/usr/bin/env python3
"""
🔍 Диагностика UI чата GopiAI
===========================

Проверяет работу чата в UI компоненте после исправлений puter.js
"""

import sys
from pathlib import Path

# Добавляем путь к GopiAI-UI
ui_path = Path(__file__).parent / "GopiAI-UI"
sys.path.insert(0, str(ui_path))

# Проверяем импорт 
try:
        print("✅ импортирован успешно")
except ImportError as e:
    print(f"❌ Ошибка импорта : {e}")
    sys.exit(1)

def test_ui_chat():
    """Тестирует UI чат"""
    print("\n🚀 Тестирование UI чата...")
    
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    
    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Создаем чат виджет
    chat_widget = ()
    
    # Показываем виджет
    chat_widget.show()
    chat_widget.resize(800, 600)
    
    print("✅ UI чат создан и отображен")
    print("📝 Попробуйте отправить сообщение для тестирования puter.js")
    print("🔍 Откройте DevTools (F12) для просмотра диагностических сообщений")
    
    # Запускаем приложение
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\n👋 Тестирование завершено")

if __name__ == "__main__":
    test_ui_chat()