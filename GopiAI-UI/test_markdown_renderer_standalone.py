#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы markdown рендерера без запуска сервера CrewAI.
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

# Добавляем путь к модулям GopiAI
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем наш рендерер markdown
from gopiai.ui.utils.markdown_renderer import render_markdown

class MarkdownTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест Markdown Рендерера")
        self.setGeometry(100, 100, 800, 600)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем layout
        layout = QVBoxLayout(central_widget)
        
        # Создаем поле ввода markdown
        self.markdown_input = QTextEdit()
        self.markdown_input.setPlaceholderText("Введите markdown текст...")
        layout.addWidget(self.markdown_input)
        
        # Создаем кнопки
        button_layout = QHBoxLayout()
        
        self.render_button = QPushButton("Рендерить")
        self.render_button.clicked.connect(self.render_markdown)
        button_layout.addWidget(self.render_button)
        
        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # Создаем поле вывода HTML
        self.html_output = QTextEdit()
        self.html_output.setReadOnly(True)
        layout.addWidget(self.html_output)
        
        # Создаем поле предпросмотра
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        layout.addWidget(self.preview)
        
        # Добавляем CSS стили для markdown
        self.setup_markdown_styles()
        
        # Добавляем пример markdown
        self.add_example_markdown()
    
    def setup_markdown_styles(self):
        """Настраивает CSS стили для красивого отображения markdown."""
        markdown_css = """
        QTextEdit {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.6;
        }
        
        /* Стили для HTML элементов в QTextEdit */
        h1, h2, h3, h4, h5, h6 {
            font-weight: bold;
            margin-top: 16px;
            margin-bottom: 8px;
            line-height: 1.2;
        }
        
        h1 { font-size: 1.8em; }
        h2 { font-size: 1.5em; }
        h3 { font-size: 1.3em; }
        h4 { font-size: 1.1em; }
        h5 { font-size: 1.0em; }
        h6 { font-size: 0.9em; }
        
        p {
            margin: 8px 0;
            line-height: 1.4;
        }
        
        strong {
            font-weight: bold;
        }
        
        em {
            font-style: italic;
        }
        
        code {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            padding: 2px 4px;
            border-radius: 3px;
            background-color: rgba(128, 128, 128, 0.1);
        }
        
        pre {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            background-color: rgba(128, 128, 128, 0.1);
            padding: 12px;
            border-radius: 6px;
            margin: 12px 0;
            overflow-x: auto;
        }
        
        ul, ol {
            margin: 8px 0;
            padding-left: 24px;
        }
        
        li {
            margin: 4px 0;
            line-height: 1.4;
        }
        
        a {
            color: #0066cc;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        """
        
        # Применяем стили к предпросмотру
        self.preview.setStyleSheet(markdown_css)
    
    def add_example_markdown(self):
        """Добавляет пример markdown в поле ввода."""
        example = """# Пример Markdown

## Форматирование текста

Это **жирный текст** и *курсивный текст*.
Также можно использовать __жирный__ и _курсивный_ текст.

## Код

Вот `inline код` в тексте.

```python
def hello():
    print('Hello, World!')
```

## Списки

### Маркированный список
- Первый элемент
- Второй элемент
- Третий элемент

### Нумерованный список
1. Первый пункт
2. Второй пункт
3. Третий пункт

## Ссылки

Посетите [Google](https://google.com) для поиска.
"""
        self.markdown_input.setPlainText(example)
    
    def render_markdown(self):
        """Рендерит markdown в HTML и отображает результат."""
        markdown_text = self.markdown_input.toPlainText()
        html_text = render_markdown(markdown_text)
        
        # Отображаем HTML
        self.html_output.setPlainText(html_text)
        
        # Отображаем предпросмотр
        self.preview.setHtml(html_text)
    
    def clear_fields(self):
        """Очищает все поля."""
        self.markdown_input.clear()
        self.html_output.clear()
        self.preview.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarkdownTestWindow()
    window.show()
    sys.exit(app.exec())