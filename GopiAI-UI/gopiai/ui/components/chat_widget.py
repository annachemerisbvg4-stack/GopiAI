"""
Chat Widget Component для GopiAI Standalone Interface
=================================================

Чат с ИИ ассистентом.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt, QThread, Signal
import importlib.util
import sys

# Попытка импорта AutoGen с обработкой ошибок
try:
    # Используем importlib для импорта модуля с дефисом в названии
    spec = importlib.util.spec_from_file_location(
        "autogen_core", 
        "GopiAI-Extensions/autogen/autogen_core.py"
    )
    if spec and spec.loader:
        autogen_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(autogen_module)
        AutoGenAgent = autogen_module.AutoGenAgent
        AutoGenManager = autogen_module.AutoGenManager
        AUTOGEN_AVAILABLE = True
    else:
        raise ImportError("Не удалось загрузить модуль autogen_core")
except (ImportError, FileNotFoundError, AttributeError):
    AUTOGEN_AVAILABLE = False
    AutoGenAgent = None
    AutoGenManager = None

# Заглушка для обработки сообщений, если ИИ недоступен
class MockAIProcessor:
    def process_message(self, message: str) -> str:
        return f"Заглушка ответа на: '{message}'. ИИ пока не подключен."

class AIResponseThread(QThread):
    response_ready = Signal(str)
    
    def __init__(self, message: str):
        super().__init__()
        self.message = message
    
    def run(self):
        try:
            if AUTOGEN_AVAILABLE and AutoGenManager is not None:
                # Инициализация AutoGen
                autogen_manager = AutoGenManager()
                user_agent = autogen_manager.create_agent("User", "user_proxy")
                assistant_agent = autogen_manager.create_agent("Assistant", "assistant")
                
                # Отправка сообщения
                response = user_agent.chat(self.message, assistant_agent)
                if response and hasattr(response, 'chat_history') and response.chat_history:
                    self.response_ready.emit(response.chat_history[-1]['content'])
                else:
                    self.response_ready.emit("Получен пустой ответ от ИИ.")
            else:
                # Используем заглушку
                mock_processor = MockAIProcessor()
                response = mock_processor.process_message(self.message)
                self.response_ready.emit(response)
        except Exception as e:
            self.response_ready.emit(f"Ошибка обработки: {str(e)}")


class ChatWidget(QWidget):
    """Чат с ИИ ассистентом"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatWidget")
        
        # Флаг доступности ИИ
        self.ai_available = AUTOGEN_AVAILABLE
        
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
        
        welcome_text = """🤖 GopiAI: Привет! Я ваш ИИ ассистент.

Я могу помочь с:
• Анализом кода
• Написанием документации  
• Решением задач программирования
• Объяснением сложных концепций
• Оптимизацией алгоритмов

Напишите ваш вопрос ниже и нажмите Enter!"""
        
        if not self.ai_available:
            welcome_text += "\n\n⚠️ Внимание: AutoGen недоступен. Используется режим заглушки."
            
        self.chat_area.setPlainText(welcome_text)
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
            
            # Отправляем запрос к ИИ в отдельном потоке
            self.ai_thread = AIResponseThread(message)
            self.ai_thread.response_ready.connect(self._on_ai_response)
            self.ai_thread.start()

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
            welcome_msg += "\n\n⚠️ Внимание: AutoGen недоступен. Используется режим заглушки."
        self.chat_area.setPlainText(welcome_msg)

    def get_input_text(self) -> str:
        """Получение текста из поля ввода"""
        return self.input_field.toPlainText().strip()

    def clear_input(self):
        """Очистка поля ввода"""
        self.input_field.clear()