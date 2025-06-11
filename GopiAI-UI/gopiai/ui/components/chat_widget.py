"""
Chat Widget Component для GopiAI Standalone Interface
=================================================

Чат с ИИ ассистентом.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt


class ChatWidget(QWidget):
    """Чат с ИИ ассистентом"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatWidget")
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса чата"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Заголовок
        header = QLabel("🤖 ИИ Ассистент")
        header.setObjectName("panelHeader")
        header.setFixedHeight(30)
        layout.addWidget(header)
        
        # Область чата
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setPlainText("""
🤖 GopiAI: Привет! Я ваш ИИ ассистент.

Я могу помочь с:
• Анализом кода
• Написанием документации  
• Решением задач программирования
• Объяснением сложных концепций
• Оптимизацией алгоритмов

Напишите ваш вопрос ниже и нажмите Enter!
        """)
        layout.addWidget(self.chat_area, 1)
        
        # Поле ввода
        input_layout = QHBoxLayout()
        self.input_field = QTextEdit()
        self.input_field.setFixedHeight(60)
        self.input_field.setPlaceholderText("Введите ваш вопрос... (Enter - отправить, Shift+Enter - новая строка)")
        self.input_field.keyPressEvent = self._input_key_press
        
        self.send_button = QPushButton("➤ Отправить")
        self.send_button.setObjectName("sendButton")
        self.send_button.setFixedSize(100, 60)
        self.send_button.clicked.connect(self._send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

    def _input_key_press(self, event):
        """Обработка нажатий клавиш в поле ввода"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                # Shift+Enter - новая строка
                QTextEdit.keyPressEvent(self.input_field, event)
            else:
                # Enter - отправить сообщение
                self._send_message()
        else:
            # Остальные клавиши обрабатываются обычно
            QTextEdit.keyPressEvent(self.input_field, event)

    def _send_message(self):
        """Отправка сообщения в чат"""
        message = self.input_field.toPlainText().strip()
        if message:
            # Добавляем сообщение пользователя
            current_text = self.chat_area.toPlainText()
            new_text = f"{current_text}\n\n👤 Вы: {message}\n\n🤖 GopiAI: Спасибо за ваш вопрос! В данный момент я работаю в режиме заглушки. Полная интеграция с ИИ будет добавлена в следующих версиях."
            self.chat_area.setPlainText(new_text)
            
            # Прокручиваем вниз
            cursor = self.chat_area.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.chat_area.setTextCursor(cursor)
            
            # Очищаем поле ввода
            self.input_field.clear()

    def add_message(self, sender: str, message: str):
        """Добавление сообщения в чат"""
        current_text = self.chat_area.toPlainText()
        icon = "👤" if sender == "user" else "🤖"
        name = "Вы" if sender == "user" else "GopiAI"
        new_text = f"{current_text}\n\n{icon} {name}: {message}"
        self.chat_area.setPlainText(new_text)
        
        # Прокручиваем вниз
        cursor = self.chat_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.chat_area.setTextCursor(cursor)

    def clear_chat(self):
        """Очистка чата"""
        self.chat_area.setPlainText("🤖 GopiAI: Чат очищен. Как дела?")

    def get_input_text(self) -> str:
        """Получение текста из поля ввода"""
        return self.input_field.toPlainText().strip()

    def clear_input(self):
        """Очистка поля ввода"""
        self.input_field.clear()