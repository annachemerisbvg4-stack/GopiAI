"""
Виджет для чата с Gemini.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QHBoxLayout, QLabel, QComboBox, QSplitter, QFrame
)
from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtGui import QTextCursor, QFont, QTextCharFormat, QColor
import json
import logging
import requests
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class GeminiWorker(QObject):
    """Воркер для асинхронных запросов к Gemini API."""
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url
    
    def send_message(self, messages: List[Dict[str, str]], model: str = "gemini-pro", **kwargs):
        """Отправляет сообщение в чат."""
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "messages": messages,
                    "model": model,
                    **kwargs
                },
                timeout=30
            )
            
            if response.status_code != 200:
                self.error.emit(f"Ошибка {response.status_code}: {response.text}")
                return
                
            result = response.json()
            if result.get("status") != "success":
                self.error.emit(f"Ошибка: {result.get('message', 'Неизвестная ошибка')}")
                return
                
            self.finished.emit(result)
            
        except requests.exceptions.Timeout:
            self.error.emit("Таймаут запроса. Проверьте соединение и повторите попытку.")
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Ошибка соединения: {str(e)}")
        except Exception as e:
            logger.exception("Неожиданная ошибка при отправке сообщения")
            self.error.emit(f"Внутренняя ошибка: {str(e)}")


class GeminiChatWidget(QWidget):
    """Виджет чата с Gemini."""
    
    def __init__(self, parent=None, api_url: str = "http://localhost:5000/api/gemini"):
        super().__init__(parent)
        self.api_url = api_url
        self.messages = []
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        self.setWindowTitle("Gemini Chat")
        
        # Основной макет
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Виджет для отображения чата
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Arial", 11))
        
        # Виджет для ввода сообщения
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.returnPressed.connect(self.send_message)
        
        # Кнопка отправки
        self.send_button = QPushButton("Отправить")
        self.send_button.setFixedWidth(100)
        
        # Панель для выбора модели
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Модель:"))
        
        self.model_selector = QComboBox()
        self.model_selector.addItem("gemini-pro", "gemini-pro")
        self.model_selector.addItem("gemini-1.5-pro", "gemini-1.5-pro")
        
        model_layout.addWidget(self.model_selector)
        model_layout.addStretch()
        
        # Кнопка очистки чата
        self.clear_button = QPushButton("Очистить чат")
        self.clear_button.clicked.connect(self.clear_chat)
        
        model_layout.addWidget(self.clear_button)
        
        # Панель управления
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.message_input)
        control_layout.addWidget(self.send_button)
        
        # Собираем всё вместе
        layout.addLayout(model_layout)
        layout.addWidget(self.chat_display)
        layout.addLayout(control_layout)
        
        # Настройка стилей
        self.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }
            QPushButton {
                padding: 8px 15px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
    
    def setup_connections(self):
        """Настраивает соединения сигналов и слотов."""
        self.send_button.clicked.connect(self.send_message)
        
        # Инициализируем воркер для асинхронных запросов
        self.worker_thread = QThread()
        self.worker = GeminiWorker(self.api_url)
        self.worker.moveToThread(self.worker_thread)
        
        # Подключаем сигналы воркера
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        
        # Запускаем поток
        self.worker_thread.start()
    
    def send_message(self):
        """Отправляет сообщение в чат."""
        message = self.message_input.text().strip()
        if not message:
            return
            
        # Добавляем сообщение пользователя в историю
        self.add_message("user", message)
        self.message_input.clear()
        
        # Получаем выбранную модель
        model = self.model_selector.currentData()
        
        # Отправляем запрос асинхронно
        self.set_ui_enabled(False)
        self.worker.send_message(
            messages=self.messages,
            model=model,
            temperature=0.7,
            max_output_tokens=2048
        )
    
    def handle_response(self, response: Dict[str, Any]):
        """Обрабатывает ответ от API."""
        try:
            response_text = response.get("data", {})
            if isinstance(response_text, dict):
                response_text = response_text.get("text", str(response_text))
            
            if response_text:
                self.add_message("assistant", response_text)
        except Exception as e:
            logger.exception("Ошибка при обработке ответа")
            self.add_message("system", f"Ошибка: {str(e)}")
        finally:
            self.set_ui_enabled(True)
    
    def handle_error(self, error_message: str):
        """Обрабатывает ошибки."""
        self.add_message("system", error_message)
        self.set_ui_enabled(True)
    
    def add_message(self, role: str, content: str):
        """Добавляет сообщение в чат."""
        # Сохраняем сообщение в историю
        self.messages.append({"role": role, "content": content})
        
        # Форматируем сообщение для отображения
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Устанавливаем форматирование в зависимости от роли
        format_ = QTextCharFormat()
        if role == "user":
            format_.setForeground(QColor("#0d6efd"))
            prefix = "Вы: "
        elif role == "assistant":
            format_.setForeground(QColor("#198754"))
            prefix = "Gemini: "
        else:
            format_.setForeground(QColor("#dc3545"))
            format_.setFontItalic(True)
            prefix = "Система: "
        
        # Добавляем сообщение в чат
        cursor.insertText(prefix, format_)
        cursor.insertText(content + "\n\n")
        
        # Прокручиваем к последнему сообщению
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def clear_chat(self):
        """Очищает историю чата."""
        self.messages = []
        self.chat_display.clear()
    
    def set_ui_enabled(self, enabled: bool):
        """Включает/отключает элементы управления."""
        self.send_button.setEnabled(enabled)
        self.message_input.setEnabled(enabled)
        self.model_selector.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)
    
    def closeEvent(self, event):
        """Обработчик события закрытия окна."""
        if hasattr(self, 'worker_thread') and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
        event.accept()
