from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
                              QFileDialog, QLabel, QSizePolicy, QMessageBox, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, QMimeData, Slot, QMetaObject, QTimer, QThread, Signal, QRect, QPoint
from PySide6.QtGui import QIcon, QDropEvent, QDragEnterEvent, QPixmap, QTextCursor, QPainter, QColor, QPen

# Import UI Assistant
from gopiai.ui_core.ai_tools import get_ui_assistant_tool
from typing import Optional, List, Dict, Any, Tuple, Union
import re
import threading
import time
import json
import time
import logging
import html
import uuid
from datetime import datetime

# Настройка логирования
logger = logging.getLogger(__name__)

# Импортируем UniversalIconManager
from gopiai.ui.components.icon_file_system_model import UniversalIconManager

# Импортируем ChatContext из компонентов
from .chat_context import ChatContext

# Импортируем CrewAIClient
from .crewai_client import CrewAIClient

# Импортируем SidePanelContainer
from .side_panel import SidePanelContainer

# Импортируем MemoryManager
from ..memory import get_memory_manager, MemoryManager

# Импортируем системный промпт из personality
# Пытаемся импортировать из gopiai.app.prompt.personality, если не получится - используем стандартный
PERSONALITY_SYSTEM_PROMPT = None
try:
    from gopiai.app.prompt.personality import PERSONALITY_SYSTEM_PROMPT
except ImportError:
    # Fallback на стандартный промпт если файл не найден
    PERSONALITY_SYSTEM_PROMPT = "Вы - интеллектуальный ассистент GopiAI. Отвечайте на вопросы пользователей максимально полно и точно."

# Глобальный экземпляр менеджера памяти
memory_manager = get_memory_manager()
RAG_AVAILABLE = True  # Флаг доступности RAG
logger.info("✅ Memory manager initialized")

# DEBUG LOGGING PATCH - Enhanced for browser command debugging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create file handler for persistent logging
file_handler = logging.FileHandler('chat_debug.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

print("🔧 Enhanced DEBUG logging enabled for chat_widget.py (console + file)")
logger.info("=== Chat Widget Debug Session Started ===")


class ChatWidget(QWidget):
    # Qt signals for thread-safe communication
    response_ready = Signal(object, bool)  # response_data (str or dict), error_occurred
    browser_command_ready = Signal(str)  # browser_command
    def set_theme_manager(self, theme_manager):
        """Интеграция с глобальной темой (API совместим с WebViewChatWidget)"""
        self.theme_manager = theme_manager
        self.apply_theme()

    def _init_ui_assistant(self):
        """Initialize the UI Assistant integration."""
        # Create visual feedback elements
        self._setup_visual_feedback()
        
        # Get the UI Assistant instance
        self.ui_assistant = get_ui_assistant_tool()
        
        # Connect UI Assistant signals
        self.ui_assistant.action_started.connect(self._on_assistant_action_started)
        self.ui_assistant.action_completed.connect(self._on_assistant_action_completed)
        self.ui_assistant.visual_feedback.connect(self._on_visual_feedback)
        
        # Set the main window reference
        main_window = self.window()
        if main_window:
            self.ui_assistant.set_main_window(main_window)
    
    def _setup_visual_feedback(self):
        """Set up visual feedback elements for the UI Assistant."""
        # Create a transparent overlay window for visual feedback
        self.overlay_widget = QWidget(self)
        self.overlay_widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.overlay_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.overlay_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Status label for showing current action
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                margin: 10px;
            }
        """)
        self.status_label.hide()
        
        # Highlight widget for showing where actions are being performed
        self.highlight_widget = QLabel()
        self.highlight_widget.setStyleSheet("""
            QLabel {
                background-color: rgba(65, 131, 196, 40);
                border: 2px solid #4183c4;
                border-radius: 4px;
            }
        """)
        self.highlight_widget.hide()
        
        layout.addWidget(self.status_label, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        
        self.overlay_widget.setLayout(layout)
        self.overlay_widget.hide()
    
    def _on_assistant_action_started(self, message: str):
        """Handle action started signal from UI Assistant."""
        self.append_message("assistant", message)
    
    def _on_assistant_action_completed(self, message: str, success: bool):
        """Handle action completed signal from UI Assistant."""
        status = "успешно" if success else "с ошибкой"
        self.append_message("assistant", f"{message} - {status}")
    
    def _on_visual_feedback(self, feedback_type: str, data: dict):
        """Handle visual feedback from UI Assistant."""
        if feedback_type == "status_message":
            self._show_status_message(data["message"], data.get("duration", 3000))
        elif feedback_type == "highlight_element":
            rect = QRect(
                data["x"], data["y"],
                data["width"], data["height"]
            )
            self._highlight_element(rect, data.get("duration", 1000))
    
    def _show_status_message(self, message: str, duration: int = 3000):
        """Show a status message to the user."""
        if not hasattr(self, 'status_label') or not self.status_label:
            return
            
        self.status_label.setText(message)
        self.status_label.show()
        self.overlay_widget.raise_()
        
        # Hide the message after the duration
        QTimer.singleShot(duration, self.status_label.hide)
    
    def _highlight_element(self, rect: QRect, duration: int = 1000):
        """Highlight a UI element at the specified position."""
        if not hasattr(self, 'highlight_widget') or not self.highlight_widget:
            return
            
        # Convert to global coordinates if needed
        main_window = self.window()
        if main_window:
            pos = main_window.mapToGlobal(rect.topLeft())
            pos = self.overlay_widget.mapFromGlobal(pos)
            rect = QRect(pos, rect.size())
        
        self.highlight_widget.setGeometry(rect)
        self.highlight_widget.show()
        self.highlight_widget.raise_()
        
        # Hide the highlight after the duration
        QTimer.singleShot(duration, self.highlight_widget.hide)

    def apply_theme(self):
        """Apply the current theme to the chat widget."""
        # Theme is applied through global stylesheet
        pass


    """
    Современный чат-виджет для GopiAI на Qt с поддержкой глобальной темы, истории сообщений,
    полем ввода и кнопками: "прикрепить файл", "прикрепить изображение", "multiagent".
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChatWidget")
        self.setMinimumHeight(320)
        self.setAcceptDrops(True)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(6)
        
        # Инициализация CrewAIClient
        self.crew_ai_client = CrewAIClient()
        
        # Инициализация менеджера памяти
        self.memory_manager = get_memory_manager()
        self.session_id = f"session_{int(time.time())}"  # Уникальный ID сессии
        
        # Флаг использования долгосрочной памяти (RAG)
        self.use_long_term_memory = True
        
        # Загружаем историю чата из памяти
        self._load_chat_history()
        
        # Инициализируем переменные для отслеживания состояния чата
        self._waiting_message_id = None

        # История сообщений
        self.history = QTextEdit(self)
        self.history.setReadOnly(True)
        self.history.setObjectName("ChatHistory")
        self.history.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.history.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.main_layout.addWidget(self.history)
        
        # Информационное сообщение о горячих клавишах
        self.history.append("<b>Система:</b> Добро пожаловать в чат! Используйте <b>Enter</b> для отправки сообщения и <b>Shift+Enter</b> для переноса строки. Ассистент автоматически определит, когда нужно использовать команду агентов для сложных запросов.")

        # Нижняя панель
        self.bottom_panel = QHBoxLayout()

        # Многострочное поле ввода
        self.input = QTextEdit(self)
        self.input.setPlaceholderText("Введите сообщение... (Enter - отправить, Shift+Enter - новая строка)")
        self.input.setObjectName("ChatInput")
        self.input.setFixedHeight(80)  # ~в 10 раз выше обычного QLineEdit
        self.input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.bottom_panel.addWidget(self.input, 1)

        # Lucide-иконки через UniversalIconManager
        icon_mgr = UniversalIconManager.instance()
        self.attach_file_btn = QPushButton(icon_mgr.get_icon("paperclip"), "", self)
        self.attach_file_btn.setToolTip("Прикрепить файл")
        self.attach_file_btn.clicked.connect(self.attach_file)
        self.bottom_panel.addWidget(self.attach_file_btn)

        self.attach_image_btn = QPushButton(icon_mgr.get_icon("image"), "", self)
        self.attach_image_btn.setToolTip("Прикрепить изображение")
        self.attach_image_btn.clicked.connect(self.attach_image)
        self.bottom_panel.addWidget(self.attach_image_btn)

        # Кнопка очистки контекста
        self.clear_context_btn = QPushButton(icon_mgr.get_icon("trash-2"), "", self)
        self.clear_context_btn.setToolTip("Очистить контекст чата")
        self.clear_context_btn.clicked.connect(self.clear_chat_context)
        self.bottom_panel.addWidget(self.clear_context_btn)
        
        # Кнопка статистики контекста (будет добавлена в боковую панель)
        self.context_stats_btn = QPushButton(icon_mgr.get_icon("info"), "", self)
        self.context_stats_btn.setToolTip("Показать статистику контекста")
        self.context_stats_btn.clicked.connect(self.show_context_stats)
        
        # Создание боковой панели с триггером
        self.side_panel_container = SidePanelContainer(parent=self)
        
        # Кнопка статистики контекста будет добавлена в боковую панель
        # Перемещаем кнопку статистики в боковую панель
        self.context_stats_btn.setText(" Статистика контекста")
        self.side_panel_container.add_button_to_panel(self.context_stats_btn)
        
        # Кнопка отправки
        self.send_btn = QPushButton(icon_mgr.get_icon("send"), "", self)
        self.send_btn.setToolTip("Отправить сообщение")
        self.send_btn.clicked.connect(self.send_message)
        self.bottom_panel.addWidget(self.send_btn)

        # Добавляем контейнер боковой панели перед нижней панелью
        self.main_layout.addWidget(self.side_panel_container)
        
        self.main_layout.addLayout(self.bottom_panel)

        # Обработка Enter (Ctrl+Enter для отправки)
        self.input.keyPressEvent = self._input_key_press_event

        # Автопрокрутка истории
        self.history.textChanged.connect(self._scroll_history_to_end)

        # Connect Qt signal for thread-safe communication
        self.response_ready.connect(self._handle_response_from_thread)
        self.browser_command_ready.connect(self._handle_browser_command_from_signal)

        # Применить тему при инициализации
        self.theme_manager = None
        self.apply_theme()
        
        # Initialize UI Assistant integration
        self._init_ui_assistant()
        
        # Check service availability after UI is fully initialized
        self._check_crewai_availability()

    @Slot(object, bool)
    def _handle_response_from_thread(self, response_data, error_occurred=False):
        """
        Обрабатывает ответы от фонового потока через Qt signal
        
        Args:
            response_data: Ответ от CrewAI (может быть строкой или словарем)
            error_occurred: Флаг ошибки
        """
        try:
            logger.info(f"[RESPONSE] Получен ответ. Тип: {type(response_data)}, Ошибка: {error_occurred}")
            logger.debug(f"[RESPONSE] Полные данные ответа: {response_data}")
            
            # Если это словарь с командой браузера
            if isinstance(response_data, dict) and 'browser_command' in response_data:
                logger.info(f"[BROWSER] Обнаружена браузерная команда")
                command = response_data['browser_command']
                # Выполняем команду браузера в основном потоке
                QTimer.singleShot(0, lambda: self._handle_browser_command(command))
                return
            
            # Обработка ответа от CrewAI
            response_text = ""
            if isinstance(response_data, dict):
                # Если это словарь, извлекаем текст ответа
                response_text = response_data.get('response', str(response_data))
                # Если response - это словарь с ключом 'response', проверим его тип
                if isinstance(response_text, dict):
                    response_text = str(response_text)
            else:
                # Иначе используем как есть (строка)
                response_text = str(response_data)
            
            # Если ответ пустой, используем заглушку
            if not response_text.strip():
                response_text = "Пустой ответ от сервера"
            
            logger.info(f"[RESPONSE] Текст ответа: {response_text[:200]}...")
            
            # Получаем ID сообщения ожидания или создаем новый
            waiting_id = getattr(self, '_waiting_message_id', f"msg_{int(time.time() * 1000)}")
            logger.info(f"[RESPONSE] Обновление сообщения с ID: {waiting_id}")
            
            # Обновляем сообщение с ответом
            self._update_assistant_response(
                waiting_id,
                response_text,
                error_occurred
            )
            
            # Очищаем ID сообщения ожидания
            if hasattr(self, '_waiting_message_id'):
                del self._waiting_message_id
            
        except Exception as e:
            logger.error(f"[ERROR] Ошибка при обработке ответа: {e}", exc_info=True)
            try:
                # Пытаемся показать ошибку пользователю
                error_msg = f"Произошла ошибка: {str(e)}"
                if hasattr(self, '_waiting_message_id'):
                    self._update_assistant_response(self._waiting_message_id, error_msg, True)
                else:
                    self.append_message("Ошибка", error_msg)
            except Exception as inner_e:
                logger.error(f"[CRITICAL] Не удалось показать сообщение об ошибке: {inner_e}")
        finally:
            # Всегда включаем кнопку отправки
            self.send_btn.setEnabled(True)
            self._scroll_history_to_end()

    def _input_key_press_event(self, event):
        # Если нажат Enter без Shift, отправляем сообщение
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Shift+Enter для переноса строки
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                QTextEdit.keyPressEvent(self.input, event)
            else:
                # Простой Enter отправляет сообщение
                self.send_message()
        else:
            # Обрабатываем остальные клавиши стандартным образом
            QTextEdit.keyPressEvent(self.input, event)

    @Slot(str, bool)
    def _update_assistant_response(self, message_id, response, error_occurred=False):
        """
        Обновляет ответ ассистента в истории чата с улучшенной обработкой контекста
        
        Args:
            message_id: ID сообщения для обновления
            response: Текст ответа или данные ответа
            error_occurred: Флаг ошибки
        """
        try:
            # Получаем текст ответа, если response - словарь
            response_text = response
            if isinstance(response, dict):
                response_text = response.get('response', str(response))
                
                # Если есть дополнительные данные в ответе, обрабатываем их
                if 'action' in response:
                    # Обработка специальных действий (например, навигация, поиск и т.д.)
                    action = response.get('action')
                    if action == 'search' and 'query' in response:
                        response_text = f"🔍 Ищу информацию по запросу: {response['query']}"
                    elif action == 'navigate' and 'url' in response:
                        response_text = f"🌐 Перехожу по ссылке: {response['url']}"
            
            # Обработка ошибок
            if error_occurred:
                error_msg = ""
                if isinstance(response, dict) and 'error' in response:
                    error_msg = response['error']
                elif isinstance(response, str):
                    error_msg = response
                
                if "connection" in str(error_msg).lower():
                    response_text = "⚠️ Не удалось подключиться к серверу. Пожалуйста, проверьте подключение к интернету и повторите попытку."
                else:
                    response_text = f"⚠️ Произошла ошибка: {error_msg if error_msg else 'Неизвестная ошибка'}"
            
            # Добавляем сообщение ассистента в чат
            self.append_message("assistant", response_text)
            
            # Прокручиваем чат вниз
            self._scroll_history_to_end()
            
            # Очищаем ID сообщения ожидания
            if hasattr(self, '_waiting_message_id'):
                del self._waiting_message_id
                
            # Сохраняем контекст разговора
            if hasattr(self, 'memory_manager') and self.memory_manager:
                try:
                    self.memory_manager.add_message(
                        role="assistant",
                        content=response_text,
                        session_id=self.session_id
                    )
                except Exception as e:
                    logger.error(f"Ошибка при сохранении сообщения в память: {e}")
                
        except Exception as e:
            logger.error(f"Ошибка при обновлении ответа ассистента: {e}", exc_info=True)
            
            # Показываем пользователю понятное сообщение об ошибке
            try:
                self.append_message("Система", "Извините, произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз.")
            except:
                pass
            
    def _handle_response_from_thread(self, response_data, error_occurred=False):
        """
        Обрабатывает ответы от фонового потока через Qt signal
        
        Args:
            response_data: Ответ от CrewAI или команда браузера
            error_occurred: Флаг ошибки
        """
        try:
            logger.info(f"🔄 [SIGNAL_HANDLER] Получен ответ в основном потоке: {response_data}")
            
            # Если это словарь с командой браузера
            if isinstance(response_data, dict) and "impl" in response_data and response_data["impl"] == "browser-use":
                command = response_data.get("command", "")
                logger.info(f"🌐 [BROWSER-USE] Получена команда браузера: {command}")
                
                # Отправляем команду в браузер
                self.browser_command_ready.emit(command)
                
                # Показываем ответ пользователю
                response_message = response_data.get("response", f"Выполняю команду: {command}")
                self._update_assistant_response(self._waiting_message_id, response_message, False)
            
            # Если это обычный текстовый ответ
            elif isinstance(response_data, str):
                self._update_assistant_response(self._waiting_message_id, response_data, error_occurred)
            
            # Если это словарь с ответом от CrewAI
            elif isinstance(response_data, dict):
                response_text = response_data.get("response", "")
                if not response_text and "error" in response_data:
                    response_text = f"Произошла ошибка: {response_data['error']}"
                    error_occurred = True
                self._update_assistant_response(self._waiting_message_id, response_text, error_occurred)
            
            # Неизвестный формат ответа
            else:
                logger.error(f"❌ [SIGNAL_HANDLER] Неизвестный формат ответа: {response_data}")
                self._update_assistant_response(
                    self._waiting_message_id,
                    "Получен ответ в неизвестном формате. Пожалуйста, попробуйте еще раз.",
                    True
                )
                
        except Exception as e:
            logger.error(f"❌ [SIGNAL_HANDLER] Ошибка при обработке ответа: {e}", exc_info=True)
            self._update_assistant_response(
                self._waiting_message_id,
                f"Произошла ошибка при обработке ответа: {str(e)}",
                True
            )

    @Slot(str)
    def _handle_browser_command_from_signal(self, command):
        """Handles browser command from signal in main thread"""
        logger.info(f"🔄 [SIGNAL_HANDLER] Получена браузерная команда через сигнал: '{command}'")
        
        try:
            # Store the result in a shared location that background thread can access
            if not hasattr(self, '_browser_command_result'):
                self._browser_command_result = {}
            
            # Execute browser command
            result = self._handle_browser_command(command)
            
            # Store result with timestamp as key
            import time
            timestamp = str(int(time.time() * 1000))  # milliseconds for uniqueness
            self._browser_command_result[timestamp] = result
            
            logger.info(f"🔄 [SIGNAL_HANDLER] Результат браузерной команды сохранен под ключом {timestamp}: '{result}'")
            
        except Exception as e:
            logger.error(f"🔄 [SIGNAL_HANDLER] Ошибка обработки браузерной команды: {str(e)}", exc_info=True)
            # Store error result
            import time
            timestamp = str(int(time.time() * 1000))
            self._browser_command_result[timestamp] = f"Ошибка: {str(e)}"

    def _scroll_history_to_end(self):
        """Прокручивает историю чата в конец"""
        scrollbar = self.history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _check_crewai_availability(self):
        """Checks availability of CrewAI and RAG services, showing warnings if necessary."""
        try:
            crewai_available = self.crew_ai_client.is_available()
            if crewai_available:
                logger.info("✅ CrewAI API server is available.")
            else:
                logger.warning("⚠️ CrewAI API server is unavailable.")
                QTimer.singleShot(3000, lambda: QMessageBox.warning(
                    self,
                    "CrewAI Unavailable",
                    "CrewAI API server is unavailable.\n\n"
                    "To fully utilize multi-agent mode, run:\n"
                    "GopiAI-CrewAI/run_crewai_api_server.bat"
                ))
        except Exception as e:
            logger.error(f"❌ Error checking CrewAI availability: {e}", exc_info=True)
            QTimer.singleShot(3000, lambda: QMessageBox.warning(
                self,
                "CrewAI Unavailable",
                f"Error connecting to CrewAI API server: {e}\n\n"
                "To fully utilize multi-agent mode, run:\n"
                "GopiAI-CrewAI/run_crewai_api_server.bat"
            ))

        # Check embedded memory system (SimpleMemoryManager)
        try:
            from rag_memory_system import get_memory_manager
            manager = get_memory_manager()
            stats = manager.get_stats()
            self.rag_available = stats.get('txtai_available', False)
            
            if self.rag_available:
                logger.info(f"✅ Embedded memory system available. Stats: {stats}")
            else:
                logger.warning("⚠️ Embedded memory system initialized but txtai not available.")
                
        except Exception as e:
            logger.error(f"❌ Error initializing embedded memory system: {e}")
            self.rag_available = False
            
        # No warning message for embedded system - it should always work

    # Drag & Drop
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path:
                    if self._is_image_file(file_path):
                        self.append_message("Изображение", file_path)
                    else:
                        self.append_message("Файл", file_path)
            event.acceptProposedAction()
        else:
            event.ignore()

    def _is_image_file(self, path):
        return any(path.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".bmp", ".gif"])


    

    def send_message(self):
        """Отправляет сообщение и обрабатывает его через CrewAI API"""
        text = self.input.toPlainText().strip()
        if not text:
            return
            
        # Добавляем сообщение в историю и контекст
        self.append_message("Вы", text)
        self.input.clear()
        
        # Показываем индикатор ожидания
        self.send_btn.setEnabled(False)
        
        # Создаем уникальный ID для сообщения ожидания
        self._waiting_message_id = f"msg_{int(time.time() * 1000)}"
        self.append_message("Ассистент", "⏳ Обрабатываю запрос...")
        
        # Запускаем обработку в фоновом потоке
        processing_thread = threading.Thread(
            target=self._process_message_in_background,
            args=(text,),
            daemon=True
        )
        processing_thread.start()
        
    def _process_message_in_background(self, message):
        """
        Обрабатывает сообщение в фоновом потоке
        
        Args:
            message: Текст сообщения от пользователя
        """
        try:
            # Получаем контекст из памяти, если включена долгосрочная память
            context = ""
            if self.use_long_term_memory and hasattr(self, 'memory_manager'):
                context = self._get_rag_context(message)
                if context:
                    logger.info(f"[MEMORY] Найден контекст из памяти: {context[:200]}...")
            
            # Формируем промпт с учетом контекста
            prompt = message
            if context:
                prompt = f"Контекст из предыдущих обсуждений:\n{context}\n\nТекущий вопрос: {message}"
            
            # Отправляем запрос в CrewAI API
            try:
                # Получаем историю сообщений для контекста
                history = []
                if hasattr(self, 'memory_manager') and self.memory_manager:
                    history = self.memory_manager.get_chat_history(
                        session_id=self.session_id,
                        limit=5  # Берем последние 5 сообщений для контекста
                    )
                
                # Формируем историю сообщений в формате для API
                messages = [
                    {"role": "system", "content": "Ты - полезный ассистент, который помогает пользователю. Будь дружелюбным и отзывчивым."}
                ]
                
                # Добавляем историю сообщений
                for msg in history:
                    role = "user" if msg.get("role") == "user" else "assistant"
                    messages.append({"role": role, "content": msg.get("content", "")})
                
                # Добавляем текущее сообщение пользователя
                messages.append({"role": "user", "content": message})
                
                # Отправляем запрос в CrewAI API
                # Формируем сообщение в формате, ожидаемом process_request
                user_message = messages[-1]["content"] if messages else message
                
                # Создаем объект сообщения с историей и контекстом
                message_data = {
                    "message": user_message,
                    "metadata": {
                        "session_id": self.session_id,
                        "chat_history": messages
                    }
                }
                
                # Добавляем контекст из RAG, если он есть
                if context:
                    if isinstance(context, dict):
                        message_data["metadata"].update(context)
                    else:  # Если context - строка
                        message_data["metadata"]["rag_context"] = context
                
                # Отправляем запрос в CrewAI API
                response = self.crew_ai_client.process_request(message_data)
                
                # Если ответ пустой, возвращаем стандартное сообщение
                if not response:
                    response = "Извините, не удалось обработать ваш запрос. Пожалуйста, попробуйте еще раз."
                
            except Exception as e:
                logger.error(f"Ошибка при обработке сообщения через CrewAI: {e}", exc_info=True)
                response = f"Произошла ошибка при обработке вашего запроса: {str(e)}"
            
            # Добавляем задержку для имитации обработки
            import time
            time.sleep(0.5)
                
            self.response_ready.emit(response, False)
            
        except Exception as e:
            error_msg = f"Ошибка при обработке сообщения: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.response_ready.emit(error_msg, True)

    def append_message(self, author, text, **kwargs):
        """
        Добавляет сообщение в историю чата и сохраняет в памяти
        
        Args:
            author: Отправитель сообщения (user/assistant)
            text: Текст сообщения
            **kwargs: Дополнительные метаданные (timestamp, emotion и т.д.)
        """
        # Сохраняем сообщение в памяти
        role = 'user' if author.lower() == 'user' else 'assistant'
        self.memory_manager.add_message(
            session_id=self.session_id,
            role=role,
            content=text,
            **kwargs
        )
        
        # Отображаем сообщение в чате
        self.history.append(f"<b>{author}:</b> {text}")
        self._scroll_history_to_end()

    def attach_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if file_path:
            # НЕ выводим системное сообщение в чат - только в логи
            logger.info(f"📎 Файл прикреплен: {os.path.basename(file_path)} (полный путь: {file_path})")
            logger.info(f"Файл прикреплен: {file_path}")

    def attach_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", filter="Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if image_path:
            # НЕ выводим системное сообщение в чат - только в логи
            logger.info(f"🖼️ Изображение прикреплено: {os.path.basename(image_path)} (полный путь: {image_path})")
            logger.info(f"Изображение прикреплено: {image_path}")
    
    # ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ДЛЯ ОТЛАДКИ (согласно советам от Minimax и GenSpark)
    
    def get_debug_info(self):
        """Возвращает отладочную информацию о состоянии чата"""
        return {
            "crewai_client_available": self.crew_ai_client is not None,
            "crewai_server_available": self.crew_ai_client.is_available() if self.crew_ai_client else False,
            "send_button_enabled": self.send_btn.isEnabled(),
            "input_text_length": len(self.input.toPlainText()),
            "history_length": len(self.history.toPlainText())
        }
    
    def test_crewai_connection(self):
        """Тестирует соединение с CrewAI API"""
        if not self.crew_ai_client:
            logger.error("❌ CrewAI клиент не инициализирован")  # НЕ выводим в чат
            return False
            
        if not self.crew_ai_client.is_available():
            logger.warning("❌ CrewAI API сервер недоступен")  # НЕ выводим в чат
            return False
            
        # Отправляем тестовый запрос
        try:
            test_result = self.crew_ai_client.process_request("Тест соединения")
            if isinstance(test_result, dict):
                # Check for structured error response
                if "error_message" in test_result:
                    logger.error(f"❌ Ошибка API: {test_result['error_message']}")  # НЕ выводим в чат
                    return False
                elif "response" in test_result:
                    logger.info("✅ CrewAI API работает корректно")  # НЕ выводим в чат
                    return True
                else:
                    logger.warning(f"⚠️ Неожиданный ответ от API: {test_result}")  # НЕ выводим в чат
                    return False
            else:
                logger.warning(f"⚠️ Неожиданный тип ответа от API: {type(test_result)}")  # НЕ выводим в чат
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования API: {str(e)}")  # НЕ выводим в чат
            return False
    
    def test_timer_from_thread(self):
        """ТЕСТ: Проверяет работу QTimer.singleShot из фонового потока"""
        logger.info("🧪 Запуск теста QTimer из фонового потока")
        
        def background_test():
            logger.info("🧪 Фоновый поток запущен")
            time.sleep(1)  # Имитируем работу
            
            def ui_update():
                logger.info("🎯 UI update вызван из QTimer!")
                self.append_message("Тест", "✅ QTimer.singleShot работает из фонового потока!")
            
            logger.info("🧪 Вызываем QTimer.singleShot")
            QTimer.singleShot(0, ui_update)
            logger.info("🧪 QTimer.singleShot вызван")
        
        thread = threading.Thread(target=background_test)
        thread.daemon = True
        thread.start()
        
        self.append_message("Тест", "🧪 Тест QTimer запущен, ожидайте результат...")
    
    def clear_chat_context(self):
        """Очищает контекст чата (краткосрочную память)"""
        # Создаем новую сессию
        self.session_id = f"session_{int(time.time())}"
        
        # Очищаем историю отображения
        self.history.clear()
        self.history.append("<b>Система:</b> Контекст чата очищен. Начата новая сессия.")
        self.history.append("<b>Система:</b> Добро пожаловать в чат! Используйте <b>Enter</b> для отправки сообщения и <b>Shift+Enter</b> для переноса строки.")
        
        # Очищаем историю в памяти для текущей сессии
        if hasattr(self, 'memory_manager') and self.memory_manager:
            try:
                # Очищаем только текущую сессию в памяти
                # Проверяем, есть ли метод clear_session, иначе используем clear_memory
                if hasattr(self.memory_manager, 'clear_session'):
                    self.memory_manager.clear_session(self.session_id)
                else:
                    self.memory_manager.clear_memory()
                logger.info("Контекст чата и сессия очищены")
            except Exception as e:
                logger.error(f"Ошибка при очистке сессии в памяти: {e}")
    
    def _load_chat_history(self):
        """Загружает историю чата из памяти"""
        if not hasattr(self, 'memory_manager') or not self.memory_manager:
            return
            
        try:
            messages = self.memory_manager.get_chat_history(self.session_id)
            for msg in messages:
                role = msg.get('role', 'assistant')
                content = msg.get('content', '')
                if role == 'user':
                    self.append_message("User", content)
                else:
                    self.append_message("Assistant", content)
        except Exception as e:
            logger.error(f"Ошибка при загрузке истории чата: {e}")

    def show_context_stats(self):
        """Показывает статистику текущего контекста чата"""
        try:
            # Получаем статистику из ChatContext
            stats = self.chat_context.get_stats()
            
            # Получаем статистику из MemoryManager
            memory_stats = {}
            if RAG_AVAILABLE:
                try:
                    memory_stats = memory_manager.get_stats()
                except Exception as e:
                    memory_stats = {"error": str(e)}
            
            # Формируем сообщение
            message = "<b>Статистика контекста:</b>\n"
            message += f"• Сообщений в текущем контексте: {stats['total_messages']}\n"
            # Добавляем информацию о токенах, если доступна
            if 'total_tokens' in stats and 'max_tokens' in stats:
                message += f"• Всего токенов: {stats['total_tokens']}/{stats['max_tokens']}\n"
            
            # Добавляем информацию о долгосрочной памяти
            message += f"\n<b>Долгосрочная память (txtai):</b>\n"
            
            if 'error' in memory_stats:
                message += f"Ошибка: {memory_stats['error']}\n"
            else:
                message += f"• Всего сообщений: {memory_stats.get('total_messages', 0)}\n"
                # Добавляем информацию о сессиях, если доступно
                if 'total_sessions' in memory_stats:
                    message += f"• Всего сессий: {memory_stats['total_sessions']}\n"
                # Добавляем информацию о доступности эмбеддингов
                if 'embeddings_available' in memory_stats:
                    status = "доступны" if memory_stats['embeddings_available'] else "недоступны"
                    message += f"• Семантический поиск: {status}\n"
                # Добавляем информацию о доступности анализа эмоций
                if 'emotion_analyzer_available' in memory_stats:
                    status = "доступен" if memory_stats['emotion_analyzer_available'] else "недоступен"
                    message += f"• Анализ эмоций: {status}\n"
                # Добавляем информацию о каталоге данных
                if 'data_dir' in memory_stats:
                    message += f"\n<b>Каталог данных:</b>\n{memory_stats['data_dir']}\n"

            # Показываем диалоговое окно с информацией
            QMessageBox.information(
                self,
                "Статистика контекста",
                message,
                QMessageBox.StandardButton.Ok
            )
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики контекста: {e}")
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось получить статистику контекста: {e}",
                QMessageBox.StandardButton.Ok
            )
            logger.info(f"Context stats displayed: {stats}")
    
    def _get_rag_context(self, query: str) -> str:
        """
        Получает релевантный контекст из долгосрочной памяти (RAG)
        
        Args:
            query: Поисковый запрос
            
        Returns:
            str: Релевантный контекст или пустая строка, если RAG недоступен
        """
        if not self.use_long_term_memory or not hasattr(self, 'memory_manager'):
            return ""
            
        try:
            # Ищем релевантные сообщения в памяти
            results = self.memory_manager.search_memory(query, limit=3)
            
            if not results:
                return ""
                
            # Формируем контекст из найденных сообщений
            context_parts = []
            for i, result in enumerate(results, 1):
                role = result.get('role', 'user')
                content = result.get('content', '')
                score = result.get('score', 0)
                
                # Обрезаем слишком длинные сообщения
                if len(content) > 200:
                    content = content[:200] + "..."
                    
                context_parts.append(f"{i}. [{role.upper()}] {content} (релевантность: {score:.2f})")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"[RAG] Ошибка при поиске в памяти: {e}", exc_info=True)
            return ""

    def _handle_browser_command(self, command: str) -> str:
        """Обрабатывает браузерную команду через встроенный браузер."""
        logger.info(f"🌐 [BROWSER] Начало обработки команды: '{command}'")
        
        try:
            logger.info(f"🌐 [BROWSER] Начинаем выполнение команды (без вывода в чат): '{command}'")
            # НЕ выводим системные сообщения в чат - они отвлекают пользователя
            
            # Получаем ссылку на встроенный браузер из главного окна
            logger.info(f"🌐 [BROWSER] Поиск встроенного браузера...")
            browser_widget = self._get_embedded_browser()
            logger.info(f"🌐 [BROWSER] Результат поиска браузера: {browser_widget is not None}")
            
            if not browser_widget:
                logger.info(f"🌐 [BROWSER] Встроенный браузер не найден. Создаем новую вкладку...")
                try:
                    # Автоматически создаем новую вкладку браузера
                    browser_widget = self._create_browser_tab()
                    if not browser_widget:
                        error_msg = "❌ Не удалось создать вкладку браузера."
                        logger.error(f"🌐 [BROWSER] {error_msg}")
                        return error_msg
                    logger.info(f"🌐 [BROWSER] ✅ Вкладка браузера создана автоматически")
                except Exception as e:
                    error_msg = f"❌ Ошибка создания вкладки браузера: {str(e)}"
                    logger.error(f"🌐 [BROWSER] {error_msg}", exc_info=True)
                    return error_msg
            
            logger.info(f"🌐 [BROWSER] Найден браузер, детали: {type(browser_widget)}")
            
            # Парсим команду и выполняем соответствующее действие
            logger.info(f"🌐 [BROWSER] Выполнение действия в браузере...")
            result = self._execute_browser_action(browser_widget, command)
            logger.info(f"🌐 [BROWSER] Результат выполнения: '{result}'")
            
            logger.info(f"🌐 [BROWSER] Команда выполнена успешно (результат в логах): '{result}'")
            # НЕ выводим результат в чат - пользователь видит изменения в браузере
            
            logger.info(f"🌐 [BROWSER] Команда успешно обработана")
            return result
            
        except Exception as e:
            error_msg = f"❌ Ошибка при выполнении команды браузера: {str(e)}"
            logger.error(f"🌐 [BROWSER] {error_msg}", exc_info=True)
            return error_msg
    
    def _create_browser_tab(self):
        """Создает новую вкладку браузера, если её нет."""
        logger.info(f"🆕 [CREATE_BROWSER] Создание новой вкладки браузера...")
        
        try:
            # Ищем tab_document через иерархию родителей
            parent = self.parent()
            level = 0
            while parent and not hasattr(parent, 'tab_document'):
                level += 1
                logger.debug(f"🆕 [CREATE_BROWSER] Уровень {level}: {type(parent).__name__}")
                parent = parent.parent()
                if level > 10:  # защита от бесконечного цикла
                    break
            
            if not parent or not hasattr(parent, 'tab_document'):
                logger.warning(f"🆕 [CREATE_BROWSER] Не найден родительский объект с tab_document")
                return None
            
            tab_document = parent.tab_document
            logger.info(f"🆕 [CREATE_BROWSER] Найден tab_document: {type(tab_document)}")
            
            if not hasattr(tab_document, 'add_browser_tab'):
                logger.warning(f"🆕 [CREATE_BROWSER] tab_document не поддерживает add_browser_tab")
                return None
            
            # Создаем новую вкладку браузера
            logger.info(f"🆕 [CREATE_BROWSER] Вызываем add_browser_tab...")
            browser_widget = tab_document.add_browser_tab()
            
            if browser_widget:
                logger.info(f"🆕 [CREATE_BROWSER] ✅ Вкладка браузера создана успешно")
                
                # Возвращаем в том же формате, что ожидает _execute_browser_action
                if hasattr(browser_widget, 'property'):
                    web_view = browser_widget.property('_web_view')
                    address_bar = browser_widget.property('_address_bar')
                    
                    if web_view:
                        result = {
                            'web_view': web_view,
                            'address_bar': address_bar,
                            'widget': browser_widget
                        }
                        logger.info(f"🆕 [CREATE_BROWSER] ✅ Браузер готов к использованию")
                        return result
                    else:
                        logger.warning(f"🆕 [CREATE_BROWSER] _web_view не найден в созданной вкладке")
                        return None
                else:
                    logger.warning(f"🆕 [CREATE_BROWSER] Созданная вкладка не поддерживает свойства")
                    return None
            else:
                logger.warning(f"🆕 [CREATE_BROWSER] add_browser_tab вернул None")
                return None
                
        except Exception as e:
            logger.error(f"🆕 [CREATE_BROWSER] Ошибка создания вкладки: {e}", exc_info=True)
            return None
    
    def _get_embedded_browser(self):
        """Получает ссылку на встроенный браузер из главного окна."""
        logger.info(f"🔍 [GET_BROWSER] Начинаем поиск встроенного браузера")
        
        try:
            # Ищем tab_document через иерархию родителей (так же как в _create_browser_tab)
            logger.info(f"🔍 [GET_BROWSER] Поиск tab_document...")
            parent = self.parent()
            level = 0
            while parent and not hasattr(parent, 'tab_document'):
                level += 1
                logger.debug(f"🔍 [GET_BROWSER] Уровень {level}: {type(parent).__name__}")
                parent = parent.parent()
                if level > 10:  # защита от бесконечного цикла
                    break
            
            if not parent or not hasattr(parent, 'tab_document'):
                logger.warning(f"🔍 [GET_BROWSER] Родительское окно с tab_document не найдено")
                return None
            
            logger.info(f"🔍 [GET_BROWSER] Найдено родительское окно: {type(parent).__name__}")
            
            # Получаем TabDocumentWidget
            tab_document = getattr(parent, 'tab_document', None)
            if not tab_document:
                logger.warning(f"🔍 [GET_BROWSER] tab_document отсутствует в родителе")
                return None
            
            logger.info(f"🔍 [GET_BROWSER] Найден TabDocument: {type(tab_document).__name__}")
            
            # Ищем активную вкладку браузера
            if not hasattr(tab_document, 'tab_widget'):
                logger.warning(f"🔍 [GET_BROWSER] tab_widget отсутствует в TabDocument")
                return None
                
            current_widget = tab_document.tab_widget.currentWidget()
            logger.info(f"🔍 [GET_BROWSER] Текущая вкладка: {type(current_widget).__name__ if current_widget else 'None'}")
            
            if not current_widget:
                logger.warning(f"🔍 [GET_BROWSER] Активная вкладка не найдена")
                return None
            
            # Проверяем, является ли это браузерной вкладкой
            if hasattr(current_widget, 'property'):
                logger.info(f"🔍 [GET_BROWSER] Вкладка поддерживает свойства, проверяем _web_view")
                web_view = current_widget.property('_web_view')
                address_bar = current_widget.property('_address_bar')
                
                logger.info(f"🔍 [GET_BROWSER] web_view найден: {web_view is not None}")
                logger.info(f"🔍 [GET_BROWSER] address_bar найден: {address_bar is not None}")
                
                if web_view:
                    result = {
                        'web_view': web_view,
                        'address_bar': address_bar,
                        'widget': current_widget
                    }
                    logger.info(f"🔍 [GET_BROWSER] ✅ Браузер успешно найден!")
                    return result
                else:
                    logger.warning(f"🔍 [GET_BROWSER] _web_view отсутствует в свойствах вкладки")
            else:
                logger.warning(f"🔍 [GET_BROWSER] Вкладка не поддерживает свойства (method 'property' not found)")
            
            logger.warning(f"🔍 [GET_BROWSER] Браузерная вкладка не найдена")
            return None
            
        except Exception as e:
            logger.error(f"🔍 [GET_BROWSER] ❌ Ошибка получения браузера: {str(e)}", exc_info=True)
            return None
    
    def _execute_browser_action(self, browser_widget, command: str) -> str:
        """Выполняет действие в браузере на основе команды."""
        logger.info(f"⚡ [EXECUTE_ACTION] Начало выполнения действия: '{command}'")
        
        try:
            logger.info(f"⚡ [EXECUTE_ACTION] Извлечение компонентов браузера...")
            web_view = browser_widget['web_view']
            address_bar = browser_widget['address_bar']
            
            logger.info(f"⚡ [EXECUTE_ACTION] web_view: {type(web_view).__name__ if web_view else 'None'}")
            logger.info(f"⚡ [EXECUTE_ACTION] address_bar: {type(address_bar).__name__ if address_bar else 'None'}")
            
            command_lower = command.lower()
            logger.info(f"⚡ [EXECUTE_ACTION] Команда в нижнем регистре: '{command_lower}'")
            
            # Навигация
            if any(word in command_lower for word in ['открой', 'открыть', 'перейди', 'перейти', 'зайди', 'зайти']):
                url = self._extract_url_from_command(command)
                if url:
                    if address_bar:
                        address_bar.setText(url)
                    from PySide6.QtCore import QUrl
                    web_view.load(QUrl(url))
                    return f"Переход к {url}"
                else:
                    return "❌ Не удалось определить URL из команды"
            
            # Обновление страницы
            elif any(word in command_lower for word in ['обнови', 'обновить', 'перезагрузи', 'перезагрузить']):
                web_view.reload()
                return "Страница обновлена"
            
            # Назад
            elif any(word in command_lower for word in ['назад', 'back']):
                if web_view.history().canGoBack():
                    web_view.back()
                    return "Переход назад"
                else:
                    return "Нельзя перейти назад"
            
            # Вперед
            elif any(word in command_lower for word in ['вперед', 'forward']):
                if web_view.history().canGoForward():
                    web_view.forward()
                    return "Переход вперед"
                else:
                    return "Нельзя перейти вперед"
            
            # Получение информации о странице
            elif any(word in command_lower for word in ['заголовок', 'title', 'url', 'адрес']):
                current_url = web_view.url().toString()
                return f"Текущий URL: {current_url}"
            
            # Поиск Google
            elif 'google' in command_lower or 'поиск' in command_lower:
                search_query = self._extract_search_from_command(command)
                if search_query:
                    google_url = f"https://google.com/search?q={search_query}"
                    if address_bar:
                        address_bar.setText(google_url)
                    web_view.load(QUrl(google_url))
                    return f"Поиск в Google: {search_query}"
                else:
                    google_url = "https://google.com"
                    if address_bar:
                        address_bar.setText(google_url)
                    web_view.load(QUrl(google_url))
                    return "Переход на Google"
            
            else:
                # Для более сложных команд можно использовать browser-use
                return self._try_browser_use_command(command, web_view)
            
        except Exception as e:
            return f"❌ Ошибка выполнения: {str(e)}"
    
    def _extract_url_from_command(self, command: str) -> str:
        """Извлекает URL из команды."""
        import re
        
        # Поиск URL в команде
        url_patterns = [
            r'https?://[^\s]+',  # Полный URL
            r'www\.[^\s]+',      # www.example.com
            r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # example.com
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, command)
            if match:
                url = match.group(0)
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                return url
        
        # Популярные сайты
        sites_map = {
            'google': 'https://google.com',
            'гугл': 'https://google.com',
            'github': 'https://github.com',
            'гитхаб': 'https://github.com',
            'youtube': 'https://youtube.com',
            'ютуб': 'https://youtube.com',
        }
        
        command_lower = command.lower()
        for keyword, url in sites_map.items():
            if keyword in command_lower:
                return url
        
        return None
    
    def _extract_search_from_command(self, command: str) -> str:
        """Извлекает поисковый запрос из команды."""
        # Убираем служебные слова
        stop_words = ['найди', 'найти', 'поиск', 'поищи', 'google', 'гугл', 'в', 'на']
        words = command.split()
        
        filtered_words = []
        for word in words:
            if word.lower() not in stop_words:
                filtered_words.append(word)
        
        return ' '.join(filtered_words)
    
    def _try_browser_use_command(self, command: str, web_view) -> str:
        """Пытается выполнить команду через browser-use для сложных действий."""
        try:
            # Здесь можно интегрировать browser-use для более сложных команд
            # Пока возвращаем информационное сообщение
            return f"Команда '{command}' передана для обработки. Сложные браузерные действия будут добавлены в следующих версиях."
            
        except Exception as e:
            return f"❌ Не удалось выполнить сложную команду: {str(e)}"
