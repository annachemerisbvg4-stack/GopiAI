#!/usr/bin/env python3
"""
Пример использования виджета чата с Gemini.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from gopiai.ui.widgets.gemini_chat_widget import GeminiChatWidget

def main():
    app = QApplication(sys.argv)
    
    # Создаем и настраиваем виджет чата
    chat_widget = GeminiChatWidget()
    chat_widget.setWindowTitle("Gemini Chat - Тест")
    chat_widget.resize(800, 600)
    chat_widget.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
