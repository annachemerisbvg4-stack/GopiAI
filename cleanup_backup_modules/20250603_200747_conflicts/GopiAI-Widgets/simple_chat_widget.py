"""
Упрощенный виджет чата для минимальной версии GopiAI.
"""

from PySide6.QtCore import Qt, Signal, Slot, QSize, QTimer
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QScrollArea, QLabel,
    QSizePolicy, QFileDialog, QFrame
)

try:
    from gopiai.widgets.core.icon_adapter import get_icon, IconAdapter
except ImportError:
    # Fallback function if icon_adapter is not available
    def get_icon(icon_name, color=None, size=24):
        from PySide6.QtGui import QIcon
        return QIcon()

import datetime
from gopiai.core.logging import get_logger
logger = get_logger().logger

logger = get_logger().logger

class MessageBubble(QWidget):
    """Виджет-пузырь для сообщения в чате."""

    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.setObjectName("userMessageBubble" if is_user else "assistantMessageBubble")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)  # Уменьшенные отступы

        # Создаем текстовую метку
        self.message = QTextEdit()
        self.message.setReadOnly(True)
        self.message.setHtml(text)

        # Убираем рамку и фон
        self.message.setFrameShape(QFrame.Shape.NoFrame)

        # Настраиваем шрифт
        font = self.message.font()
        font.setPointSize(10)
        self.message.setFont(font)

        # Адаптивный размер
        self.message.document().setDocumentMargin(0)

        # Рассчитываем высоту на основе контента
        doc_height = self.message.document().size().height()
        self.message.setFixedHeight(int(doc_height + 10))

        # Стилизуем в зависимости от отправителя
        if is_user:
            self.setStyleSheet("""
                #userMessageBubble {
                    background-color: #dcf8c6;
                    border-radius: 10px;
                    margin: 2px 40px 2px 80px;
                }
                #userMessageBubble QTextEdit {
                    color: #303030;
                    background-color: transparent;
                }
            """)
            layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            self.setStyleSheet("""
                #assistantMessageBubble {
                    background-color: #ececec;
                    border-radius: 10px;
                    margin: 2px 80px 2px 10px;
                }
                #assistantMessageBubble QTextEdit {
                    color: #363636;
                    background-color: transparent;
                }
            """)
            layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(self.message)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)


class ChatHistoryArea(QScrollArea):
    """Область для отображения истории чата."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # Контейнер для пузырей сообщений
        self.container = QWidget()
        self.message_layout = QVBoxLayout(self.container)
        self.message_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.message_layout.setSpacing(8)
        self.message_layout.setContentsMargins(12, 12, 12, 12)

        # Стиль фона чата будет применен в setThemeColors
        self.container.setObjectName("chatHistoryContainer")
        self.setWidget(self.container)

        # Включаем автоматическую прокрутку при добавлении сообщений
        self.verticalScrollBar().rangeChanged.connect(self.scroll_to_bottom)

    def add_message(self, text, is_user=True):
        """Добавляет сообщение в историю чата."""
        bubble = MessageBubble(text, is_user, self)
        self.message_layout.addWidget(bubble)

        # Добавляем небольшую задержку перед прокруткой, чтобы виджет успел обновиться
        QTimer.singleShot(50, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """Прокручивает историю чата вниз."""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class SimpleChatWidget(QWidget):
    """Простой виджет чата для минимальной версии GopiAI."""

    message_sent = Signal(str)  # Сигнал для отправки сообщений

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        # Основной лейаут
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # История чата
        self.chat_history = ChatHistoryArea()
        main_layout.addWidget(self.chat_history, 1)  # Растягивается

        # Панель ввода
        input_container = QWidget()
        input_container.setObjectName("inputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(10)

        # Поле ввода сообщений
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        # Кнопка отправки
        self.send_button = QPushButton()
        self.send_button.setIcon(get_icon("send"))
        self.send_button.setIconSize(QSize(22, 22))
        self.send_button.setFixedSize(40, 40)
        self.send_button.setObjectName("sendButton")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        # Добавляем панель ввода в основной лейаут
        main_layout.addWidget(input_container)

        # Стилизация
        input_container.setStyleSheet("""
            #inputContainer {
                background-color: #f0f0f0;
                border-top: 1px solid #cccccc;
            }
            QPushButton#sendButton {
                background-color: #00a884;
                border-radius: 20px;
                padding: 5px;
            }
            QPushButton#sendButton:hover {
                background-color: #008f72;
            }
            QPushButton#sendButton:pressed {
                background-color: #007d63;
            }
            QLineEdit {
                border-radius: 18px;
                padding: 8px 12px;
                border: 1px solid #d1d7db;
                background-color: white;
                color: #333333;
            }
        """)

        # Добавляем приветственное сообщение
        self.add_assistant_message("Привет! Я твой AI-ассистент. Чем я могу помочь?")

    def send_message(self):
        """Отправляет сообщение."""
        message = self.message_input.text().strip()
        if message:
            self.message_input.clear()
            self.add_user_message(message)

            # Отправка сигнала
            self.message_sent.emit(message)

            # Генерация ответа через ИИ (прямой вызов без задержки)
            self.generate_assistant_response(message)

            # Возвращаем фокус на поле ввода для удобного продолжения диалога
            self.message_input.setFocus()

    def add_user_message(self, text):
        """Добавляет сообщение пользователя в историю чата."""
        timestamp = datetime.datetime.now().strftime("%H:%M")
        formatted_text = f"{text}<br><span style='font-size: 0.8em; color: #888888;'>{timestamp}</span>"
        self.chat_history.add_message(formatted_text, is_user=True)

    def add_assistant_message(self, text):
        """Добавляет сообщение ассистента в историю чата."""
        timestamp = datetime.datetime.now().strftime("%H:%M")
        formatted_text = f"<b>AI Assistant</b><br>{text}<br><span style='font-size: 0.8em; color: #888888;'>{timestamp}</span>"
        self.chat_history.add_message(formatted_text, is_user=False)

    def show_typing_indicator(self):
        """Показывает индикатор печатания сообщения."""
        timestamp = datetime.datetime.now().strftime("%H:%M")
        formatted_text = f"<b>AI Assistant</b><br><i>печатает...</i><br><span style='font-size: 0.8em; color: #888888;'>{timestamp}</span>"

        # Используем обычный метод добавления сообщения для показа индикатора
        self.chat_history.add_message(formatted_text, is_user=False)
        self.typing_indicator_shown = True

    def hide_typing_indicator(self):
        """Скрывает индикатор печатания сообщения."""
        # Отмечаем, что индикатор был скрыт
        self.typing_indicator_shown = False
        # Не удаляем физически, просто позволяем новому сообщению
        # появиться под ним в истории чата

    def initialize_orchestrator_agent(self):
        """Инициализирует Orchestrator Agent если он еще не инициализирован."""
        try:
            # Импортируем нужные модули только при необходимости
            from extensions.orchestrator_agent_integration import init_extension

            # Инициализируем расширение для Orchestrator Agent
            if not hasattr(self.main_window, 'orchestrator_agent'):
                logger.info("Инициализация Orchestrator Agent...")
                init_extension(self.main_window)

                # Проверяем успешность инициализации
                if hasattr(self.main_window, 'orchestrator_agent'):
                    logger.info("Orchestrator Agent успешно инициализирован")

                    # Устанавливаем флаг готовности, если его нет
                    agent = self.main_window.orchestrator_agent
                    if not hasattr(agent, 'is_ready'):
                        setattr(agent, 'is_ready', True)
                else:
                    logger.warning("Orchestrator Agent не был инициализирован корректно")
        except ImportError as e:
            logger.warning(f"Не удалось импортировать модуль Orchestrator Agent: {e}")
        except Exception as e:
            logger.warning(f"Не удалось инициализировать Orchestrator Agent: {e}")

    def generate_assistant_response(self, user_message):
        """
        Генерирует ответ ассистента на сообщение пользователя.
        Использует Orchestrator Agent для обработки запроса.
        """
        try:
            # Попытка использовать Orchestrator Agent
            if hasattr(self.main_window, 'orchestrator_agent'):
                agent = self.main_window.orchestrator_agent

                # Проверяем, готов ли агент отвечать
                if not agent.is_ready:
                    self.add_assistant_message("Пожалуйста, подождите. ИИ агент инициализируется...")

                    # Повторяем попытку через 2 секунды
                    QTimer.singleShot(2000, lambda: self.generate_assistant_response(user_message))
                    return

                # Отображение индикатора ожидания
                self.show_typing_indicator()

                # Функция обратного вызова для получения инкрементального ответа
                def on_agent_response(response):
                    if response:
                        # Убираем индикатор и отображаем ответ
                        self.hide_typing_indicator()
                        self.add_assistant_message(response)
                        # Возвращаем фокус в поле ввода для удобства
                        self.message_input.setFocus()

                # Запуск обработки запроса
                # Проверяем доступные методы API агента
                if hasattr(agent, 'process_message'):
                    agent.process_message(user_message, callback=on_agent_response)
                elif hasattr(agent, 'process_request'):
                    # Альтернативный API для Orchestrator Agent
                    agent.process_request(user_message, callback=on_agent_response)
                return

            # Если агент недоступен, пытаемся инициализировать его
            self.initialize_orchestrator_agent()

            # Показываем временное сообщение
            self.add_assistant_message("Инициализирую ИИ модуль. Ваш запрос будет обработан через несколько секунд.")

            # Повторяем запрос через 3 секунды
            QTimer.singleShot(3000, lambda: self.generate_assistant_response(user_message))
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {e}")
            self.add_assistant_message(f"Произошла ошибка при обработке запроса: {str(e)}")
