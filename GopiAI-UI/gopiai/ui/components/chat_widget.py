# --- START OF FILE chat_widget.py ---

import logging
import time
import os
import html
from typing import Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
                               QFileDialog, QSizePolicy, QMessageBox)
from PySide6.QtCore import Qt, Slot, QPoint
from PySide6.QtGui import QResizeEvent, QTextCursor, QDropEvent, QDragEnterEvent

logger = logging.getLogger(__name__)

# --- Импорты наших новых модулей-обработчиков ---
from .crewai_client import CrewAIClient
from ..memory import get_memory_manager
from .chat_async_handler import ChatAsyncHandler
from .chat_ui_assistant_handler import ChatUIAssistantHandler
from .chat_browser_handler import ChatBrowserHandler

# --- Другие необходимые импорты ---
from gopiai.ui.components.icon_file_system_model import UniversalIconManager
from .side_panel import SidePanelContainer # <-- Возвращаем импорт SidePanelContainer

class ChatWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChatWidget")
        self.setAcceptDrops(True)
        
        self.memory_manager = get_memory_manager()
        self.crew_ai_client = CrewAIClient()
        
        self.async_handler = ChatAsyncHandler(self.crew_ai_client, self)
        self.ui_assistant_handler = ChatUIAssistantHandler(self)
        self.browser_handler = ChatBrowserHandler(self)
        
        self.session_id = f"session_{int(time.time())}"
        self._waiting_message_id = None
        self.theme_manager = None

        self._setup_ui()
        
        self.async_handler.response_ready.connect(self._handle_response)
        self.async_handler.status_update.connect(self._update_status_message)

    def _setup_ui(self):
        """Создает и настраивает все элементы интерфейса, как в оригинальной версии."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(6)

        # 1. Создаем контейнер для области чата. Это нужно, чтобы
        #    боковая панель позиционировалась относительно него, а не всего окна.
        self.chat_area_widget = QWidget()
        self.chat_area_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        chat_area_layout = QVBoxLayout(self.chat_area_widget)
        chat_area_layout.setContentsMargins(0, 0, 0, 0)

        # 2. Создаем историю чата и добавляем ее ВНУТРЬ chat_area_layout
        self.history = QTextEdit(self)
        self.history.setReadOnly(True)
        self.history.setObjectName("ChatHistory")
        chat_area_layout.addWidget(self.history)

        # 3. Добавляем chat_area_widget в основной layout, чтобы он растягивался
        self.main_layout.addWidget(self.chat_area_widget, 1)

        # 4. Нижняя панель для поля ввода и кнопок
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 5, 0, 0) # Небольшой отступ сверху
        bottom_layout.setSpacing(6)
        
        self.side_panel_container = SidePanelContainer(self)
        bottom_layout.addWidget(self.side_panel_container.trigger_button)

        # Поле ввода
        self.input = QTextEdit(self)
        self.input.setPlaceholderText("Введите сообщение...")
        self.input.setObjectName("ChatInput")
        self.input.setFixedHeight(80)
        self.input.keyPressEvent = self._input_key_press_event
        bottom_layout.addWidget(self.input, 1)

        # Кнопки
        icon_mgr = UniversalIconManager.instance()
        action_buttons_layout = QVBoxLayout()
        
        self.attach_file_btn = QPushButton(icon_mgr.get_icon("paperclip"), "", self)
        self.attach_file_btn.setToolTip("Прикрепить файл")
        self.attach_file_btn.clicked.connect(self.attach_file)
        action_buttons_layout.addWidget(self.attach_file_btn)
        
        self.attach_image_btn = QPushButton(icon_mgr.get_icon("image"), "", self)
        self.attach_image_btn.setToolTip("Прикрепить изображение")
        self.attach_image_btn.clicked.connect(self.attach_image)
        action_buttons_layout.addWidget(self.attach_image_btn)
        
        bottom_layout.addLayout(action_buttons_layout)

        # Кнопка отправки
        self.send_btn = QPushButton(icon_mgr.get_icon("send"), "", self)
        self.send_btn.setToolTip("Отправить сообщение")
        self.send_btn.setFixedSize(40, 80)
        self.send_btn.clicked.connect(self.send_message)
        bottom_layout.addWidget(self.send_btn)
        
        self.main_layout.addWidget(bottom_container)

        # 5. Создаем боковую панель. Ее родителем будет chat_area_widget.
        #    Это заставит ее позиционироваться поверх истории чата.
        self.side_panel_container = SidePanelContainer(self.chat_area_widget)
        
        # Добавляем кнопку статистики внутрь панели
        stats_button = QPushButton(icon_mgr.get_icon("info"), " Статистика", self)
        stats_button.setToolTip("Показать статистику контекста")
        stats_button.clicked.connect(self.show_context_stats)
        self.side_panel_container.add_button_to_panel(stats_button)

        # Подключаем прокрутку истории
        self.history.textChanged.connect(self._scroll_history_to_end)
    # ... (все остальные методы остаются без изменений) ...
    # send_message, _handle_response, append_message, и т.д.

    def send_message(self):
        text = self.input.toPlainText().strip()
        if not text: return
        self.append_message("Вы", text)
        self.input.clear()
        self.send_btn.setEnabled(False)
        self._waiting_message_id = self.append_message("Ассистент", "⏳ Обрабатываю запрос...")
        message_data = {"message": text, "metadata": {"session_id": self.session_id}}
        self.async_handler.process_message(message_data)

    @Slot(str)
    def _update_status_message(self, status_text: str):
        self._update_assistant_response(self._waiting_message_id, status_text, is_status=True)

    @Slot(object, bool)
    def _handle_response(self, result: object, is_error: bool):
        if is_error:
            response_text = f"Произошла ошибка: {str(result)}"
        elif isinstance(result, dict) and result.get("impl") == "browser-use":
            response_text = self.browser_handler.handle_command(result.get("command", ""))
        else:
            response_text = str(result.get('response', result)) if isinstance(result, dict) else str(result)
        
        self._update_assistant_response(self._waiting_message_id, response_text)
        self.memory_manager.add_message(self.session_id, "assistant", response_text)
        self.send_btn.setEnabled(True)
        self._waiting_message_id = None

    def append_message(self, author: str, text: str) -> Optional[str]:
        self.history.append(f"<b>{author}:</b> {html.escape(text)}")
        role = 'user' if author.lower() == 'вы' else 'assistant'
        return self.memory_manager.add_message(self.session_id, role, text)

    def _update_assistant_response(self, message_id: str, new_text: str, is_status: bool = False):
        cursor = self.history.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        self.history.append(f"<b>Ассистент:</b> {html.escape(new_text)}")
        self._scroll_history_to_end()

    def resizeEvent(self, event: QResizeEvent):
        """Перемещает кнопку вызова боковой панели при изменении размера окна."""
        super().resizeEvent(event)
        # Вызываем новый, более понятный метод нашего контейнера
        if hasattr(self, 'side_panel_container'):
            self.side_panel_container.update_trigger_position()

    def _scroll_history_to_end(self):
        self.history.verticalScrollBar().setValue(self.history.verticalScrollBar().maximum())

    def _input_key_press_event(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.send_message()
            event.accept()
        else:
            QTextEdit.keyPressEvent(self.input, event)
            
    def attach_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if file_path:
            logger.info(f"📎 Файл прикреплен: {os.path.basename(file_path)}")

    def attach_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", filter="Images (*.png *.jpg *.jpeg)")
        if image_path:
            logger.info(f"🖼️ Изображение прикреплено: {os.path.basename(image_path)}")

    def show_context_stats(self):
        QMessageBox.information(self, "Статистика", "Логика статистики будет добавлена позже.")
        
    def set_theme_manager(self, theme_manager):
        self.theme_manager = theme_manager
        self.apply_theme()

    def apply_theme(self):
        logger.info("Theme applied to ChatWidget (placeholder method).")
        pass

# --- КОНЕЦ ФАЙЛА chat_widget.py ---