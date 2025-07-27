#!/usr/bin/env python3
"""
Тест для ModelSelectorWidget
"""

import sys
import os

# Добавляем пути к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "GopiAI-UI"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "GopiAI-CrewAI"))

from PySide6.QtWidgets import QApplication
from gopiai.ui.components.model_selector_widget import ModelSelectorWidget

def test_widget():
    """Тестируем виджет"""
    app = QApplication(sys.argv)
    
    try:
        widget = ModelSelectorWidget()
        widget.setWindowTitle("Test Model Selector Widget")
        widget.resize(400, 600)
        widget.show()
        
        print("✅ Виджет создан успешно!")
        print(f"✅ Текущий провайдер: {widget.get_current_provider()}")
        print(f"✅ Текущая модель: {widget.get_current_model()}")
        
        # Проверяем вкладки
        tab_count = widget.tab_widget.count()
        print(f"✅ Количество вкладок: {tab_count}")
        
        for i in range(tab_count):
            tab_text = widget.tab_widget.tabText(i)
            print(f"  - Вкладка {i}: {tab_text}")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_widget())