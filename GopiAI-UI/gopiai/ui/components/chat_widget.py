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
        
        # Инициализируем базовые переменные
        self.session_id = f"session_{int(time.time())}"
        self._waiting_message_id = None
        self.theme_manager = None
        self.current_tool = None  # Текущий выбранный инструмент
        
        logger.info("[CHAT] Инициализация ChatWidget начата")
        
        # Сначала настраиваем UI, чтобы все элементы были готовы
        self._setup_ui()
        
        # Затем инициализируем менеджер памяти
        logger.info("[CHAT] Инициализация менеджера памяти")
        self.memory_manager = get_memory_manager()
        
        # Инициализируем клиент CrewAI
        logger.info("[CHAT] Инициализация CrewAI клиента")
        self.crew_ai_client = CrewAIClient()
        
        # Создаем обработчики в правильном порядке
        logger.info("[CHAT] Инициализация обработчиков сообщений")
        self.async_handler = ChatAsyncHandler(self.crew_ai_client, self)
        self.ui_assistant_handler = ChatUIAssistantHandler(self)
        self.browser_handler = ChatBrowserHandler(self)
        
        # Подключаем сигналы в конце, когда все компоненты уже созданы
        logger.info("[CHAT] Подключение сигналов обработчиков")
        self.async_handler.response_ready.connect(self._handle_response)
        self.async_handler.status_update.connect(self._update_status_message)
        
        logger.info("[CHAT] Инициализация ChatWidget завершена")

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
        
        # Добавляем CSS стили для markdown
        self._setup_markdown_styles()
        
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
        
        # Подключаем сигнал выбора инструмента
        self.side_panel_container.tool_selected.connect(self.on_tool_selected)
        
        # Добавляем кнопку статистики внутрь панели
        stats_button = QPushButton(icon_mgr.get_icon("info"), " Статистика", self)
        stats_button.setToolTip("Показать статистику контекста")
        stats_button.clicked.connect(self.show_context_stats)
        self.side_panel_container.add_button_to_panel(stats_button)

        # Подключаем прокрутку истории
        self.history.textChanged.connect(self._scroll_history_to_end)

    def _setup_markdown_styles(self):
        """Настраивает CSS стили для красивого отображения markdown в чате."""
        # CSS стили для markdown элементов, адаптированные к теме
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
        
        # Применяем стили к истории чата
        self.history.setStyleSheet(markdown_css)

    def send_message(self):
        print("[DEBUG] Вызван метод send_message в ChatWidget")
        logger.info("[CHAT] Вызван метод send_message в ChatWidget")
        
        text = self.input.toPlainText().strip()
        if not text: return
        
        print(f"[DEBUG] Текст сообщения: {text}")
        logger.info(f"[CHAT] Текст сообщения: {text}")
        
        self.append_message("Вы", text)
        self.input.clear()
        self.send_btn.setEnabled(False)
        self._waiting_message_id = self.append_message("Ассистент", "⏳ Обрабатываю запрос...")
        
        # Формируем метаданные с информацией о сессии и выбранном инструменте
        metadata = {"session_id": self.session_id}
        
        # Добавляем информацию о выбранном инструменте, если он есть
        if self.current_tool:
            metadata["tool"] = self.current_tool
            # После использования инструмента сбрасываем его
            self.current_tool = None
            
        message_data = {"message": text, "metadata": metadata}
        print(f"[DEBUG] Подготовлены данные для отправки: {message_data}")
        logger.info(f"[CHAT] Подготовлены данные для отправки: {message_data}")
        
        print("[DEBUG] Вызываем async_handler.process_message...")
        logger.info("[CHAT] Вызываем async_handler.process_message...")
        
        try:
            self.async_handler.process_message(message_data)
            print("[DEBUG] async_handler.process_message вызван успешно")
            logger.info("[CHAT] async_handler.process_message вызван успешно")
        except Exception as e:
            print(f"[DEBUG-ERROR] Ошибка при вызове async_handler.process_message: {e}")
            logger.error(f"[CHAT-ERROR] Ошибка при вызове async_handler.process_message: {e}", exc_info=True)

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

    def _render_markdown(self, text: str) -> str:
        """
        Встроенная функция для рендеринга markdown в HTML.
        """
        if not text:
            return ""
        
        # Экранируем HTML символы
        text = html.escape(text)
        
        # Заменяем markdown на HTML
        # Жирный текст
        text = text.replace('**', '<strong>', 1)
        while '**' in text:
            text = text.replace('**', '</strong>', 1)
            if '**' in text:
                text = text.replace('**', '<strong>', 1)
        
        # Курсивный текст
        text = text.replace('*', '<em>', 1)
        while '*' in text:
            text = text.replace('*', '</em>', 1)
            if '*' in text:
                text = text.replace('*', '<em>', 1)
        
        # Код
        text = text.replace('`', '<code>', 1)
        while '`' in text:
            text = text.replace('`', '</code>', 1)
            if '`' in text:
                text = text.replace('`', '<code>', 1)
        
        # Разбиваем на параграфы
        paragraphs = []
        for line in text.split('\n'):
            if line.strip():
                paragraphs.append(f'<p>{line}</p>')
        
        return '\n'.join(paragraphs)
    
    def append_message(self, author: str, text: str) -> Optional[str]:
        # Для сообщений пользователя просто экранируем HTML
        if author.lower() == 'вы':
            formatted_text = html.escape(text)
        else:
            # Для сообщений ассистента и системы используем markdown рендеринг
            try:
                formatted_text = self._render_markdown(text)
            except Exception as e:
                print(f"[ERROR] Ошибка при рендеринге markdown: {e}")
                formatted_text = html.escape(text)
        
        self.history.append(f"<b>{author}:</b> {formatted_text}")
        role = 'user' if author.lower() == 'вы' else 'assistant'
        return self.memory_manager.add_message(self.session_id, role, text)

    def _update_assistant_response(self, message_id: str, new_text: str, is_status: bool = False):
        cursor = self.history.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        
        # Для статусных сообщений не используем markdown
        if is_status:
            formatted_text = html.escape(new_text)
        else:
            try:
                formatted_text = self._render_markdown(new_text)
            except Exception as e:
                print(f"[ERROR] Ошибка при рендеринге markdown: {e}")
                formatted_text = html.escape(new_text)
            
        self.history.append(f"<b>Ассистент:</b> {formatted_text}")
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
        
    def on_tool_selected(self, tool_id: str, tool_data: dict):
        """
        Обрабатывает сигнал выбора инструмента и добавляет его в метаданные следующего запроса.
        
        Args:
            tool_id: Идентификатор выбранного инструмента
            tool_data: Данные о выбранном инструменте
        """
        # Сохраняем выбранный инструмент для следующего запроса
        self.current_tool = tool_data
        
        # Добавляем подсказку в поле ввода
        tool_name = tool_data.get("name", tool_id)
        self.input.setPlaceholderText(f"Используется инструмент: {tool_name}. Введите запрос...")
        
        # Показываем уведомление пользователю
        self.append_message("Система", f"Выбран инструмент: {tool_name}. Следующий запрос будет обработан с использованием этого инструмента.")

# --- КОНЕЦ ФАЙЛА chat_widget.py ---