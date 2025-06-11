"""
Chat Widget Component для GopiAI Standalone Interface
=================================================

Чат с ИИ ассистентом.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt, QThread, Signal
# import sys # Удаляем ненужный импорт
# import os # Удаляем ненужный импорт

# Импортируем глобальный менеджер AutoGen
try:
    from gopiai.extensions.autogen.autogen_core import autogen_manager
    AUTOGEN_AVAILABLE = autogen_manager.is_available
    print("✅ autogen_manager импортирован успешно")
except ImportError as e:
    print(f"❌ autogen_manager недоступен: {e}")
    AUTOGEN_AVAILABLE = False
    # Создаем заглушку, если менеджер недоступен
    class MockAutoGenManager:
        def __init__(self):
            self.is_available = False
        def simple_chat(self, message: str, strategy: str = "best_first") -> str:
            return f"Извините, модуль AutoGen недоступен. Ваш запрос: '{message}'"
    autogen_manager = MockAutoGenManager()


class AIResponseThread(QThread):
    """Поток для асинхронной обработки ответов ИИ"""
    response_ready = Signal(str)
    
    def __init__(self, message): # Убираем autogen_core из параметров
        super().__init__()
        self.message = message
    
    def run(self):
        try:
            # Используем глобальный autogen_manager
            response = autogen_manager.simple_chat(self.message, strategy="best_first") # Используем simple_chat
            self.response_ready.emit(response)
        except Exception as e:
            self.response_ready.emit(f"Ошибка: {str(e)}")


class ChatWidget(QWidget):
    """Чат с ИИ ассистентом"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatWidget")
        
        # Инициализация AutoGen
        try:
            # Используем глобальный статус доступности
            self.ai_available = AUTOGEN_AVAILABLE
            if not self.ai_available:
                 print("⚠️ AutoGen недоступен для чат-виджета")
        except Exception as e:
            print(f"Ошибка проверки доступности AutoGen: {e}")
            self.ai_available = False
        
        self.ai_thread = None
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
            self.add_message("user", message)
            
            # Очищаем поле ввода
            self.input_field.clear()
            
            # Блокируем кнопку отправки
            self.send_button.setEnabled(False)
            self.send_button.setText("⏳ Обработка...")
            
            if self.ai_available: # Проверяем доступность через глобальный флаг
                # Отправляем запрос к ИИ в отдельном потоке
                self.ai_thread = AIResponseThread(message) # Передаем только сообщение
                self.ai_thread.response_ready.connect(self._on_ai_response)
                self.ai_thread.start()
            else:
                # Заглушка если ИИ недоступен
                self._on_ai_response("Спасибо за ваш вопрос! В данный момент ИИ недоступен. Проверьте настройки подключения.")

    def _on_ai_response(self, response: str):
        """Обработка ответа от ИИ"""
        # Добавляем ответ ИИ в чат
        self.add_message("ai", response)
        
        # Разблокируем кнопку отправки
        self.send_button.setEnabled(True)
        self.send_button.setText("➤ Отправить")
        
        # Очищаем поток
        if self.ai_thread:
            self.ai_thread.deleteLater()
            self.ai_thread = None

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
        welcome_msg = "🤖 GopiAI: Чат очищен. Как дела?"
        if not self.ai_available:
            welcome_msg += "\n\n⚠️ Внимание: ИИ недоступен. Проверьте настройки подключения."
        self.chat_area.setPlainText(welcome_msg)

    def get_input_text(self) -> str:
        """Получение текста из поля ввода"""
        return self.input_field.toPlainText().strip()

    def clear_input(self):
        """Очистка поля ввода"""
        self.input_field.clear()