# --- START OF FILE chat_widget.py ---

import logging
import time
import os
import html
import re
from typing import Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
                               QFileDialog, QSizePolicy, QMessageBox)
from PySide6.QtCore import Qt, Slot, QPoint, QTimer
from PySide6.QtGui import QResizeEvent, QTextCursor, QDropEvent, QDragEnterEvent, QTextCursor, QTextCharFormat, QColor, QTextOption
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# --- Импорты наших новых модулей-обработчиков ---
from .crewai_client import CrewAIClient
from ..memory import get_memory_manager
from .chat_async_handler import ChatAsyncHandler
from .side_panel import SidePanelContainer
from .icon_file_system_model import UniversalIconManager

class ChatWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChatWidget")
        self.setAcceptDrops(True)
        
        # Инициализируем базовые переменные
        self.session_id = None  # Будет установлен после загрузки
        self._waiting_message_id = None
        self.theme_manager = None
        self.current_tool = None  # Текущий выбранный инструмент
        self._animation_timer = None  # Таймер для анимации
        self._pending_updates = []  # Очередь обновлений
        self._is_updating = False  # Флаг обновления
        self.attached_files = []
        
        logger.info("[CHAT] Инициализация ChatWidget начата")
        
        # Сначала настраиваем UI, чтобы все элементы были готовы
        self._setup_ui()
        
        # Инициализируем таймер для анимации
        self._setup_animation_timer()
        
        # Затем инициализируем менеджер памяти
        logger.info("[CHAT] Инициализация менеджера памяти")
        self.memory_manager = get_memory_manager()
        
        # Загружаем или создаем сессию и историю
        self._initialize_session_and_history()
        
        # Инициализируем клиент CrewAI
        logger.info("[CHAT] Инициализация CrewAI клиента")
        self.crew_ai_client = CrewAIClient()
        
        # Создаем обработчики в правильном порядке
        logger.info("[CHAT] Инициализация обработчиков сообщений")
        self.async_handler = ChatAsyncHandler(self.crew_ai_client, self)
        
        # Подключаем сигналы в конце, когда все компоненты уже созданы
        logger.info("[CHAT] Подключение сигналов обработчиков")
        self.async_handler.response_ready.connect(self._handle_response)
        self.async_handler.status_update.connect(self._update_status_message)
        
        logger.info("[CHAT] Инициализация ChatWidget завершена")

    def _setup_animation_timer(self):
        """Настраивает таймер для анимации точек загрузки"""
        self._animation_timer = QTimer(self)
        self._animation_timer.setInterval(500)  # 500ms между обновлениями
        self._animation_timer.timeout.connect(self._update_animation)
        self._animation_dots = 0

    def _update_animation(self):
        """Обновляет анимацию точек в статусном сообщении"""
        if hasattr(self, '_current_status_text'):
            self._animation_dots = (self._animation_dots + 1) % 4
            dots = "." * self._animation_dots
            self._update_status_display(f"{self._current_status_text}{dots}")

    def _setup_ui(self):
        """Создает и настраивает все элементы интерфейса"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(6)

        # 1. Создаем контейнер для области чата
        self.chat_area_widget = QWidget()
        self.chat_area_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        chat_area_layout = QVBoxLayout(self.chat_area_widget)
        chat_area_layout.setContentsMargins(0, 0, 0, 0)

        # 2. Создаем историю чата
        self.history = QTextEdit(self)
        self.history.setReadOnly(True)
        self.history.setObjectName("ChatHistory")
        self.history.setAcceptRichText(True)
        self.history.document().setDefaultStyleSheet(self._get_markdown_styles())
        self.history.setWordWrapMode(QTextOption.WordWrap)
        
        chat_area_layout.addWidget(self.history)
        self.main_layout.addWidget(self.chat_area_widget, 1)

        # 3. Нижняя панель
        self._setup_bottom_panel()

    def _setup_bottom_panel(self):
        """Настраивает нижнюю панель с полем ввода и кнопками"""
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 5, 0, 0)
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

        # Кнопки действий
        self._setup_action_buttons(bottom_layout)
        
        self.main_layout.addWidget(bottom_container)

    def _setup_action_buttons(self, parent_layout):
        """Настраивает кнопки действий"""
        icon_mgr = UniversalIconManager.instance()
        action_buttons_layout = QVBoxLayout()
        
        # Кнопка прикрепления файла
        self.attach_file_btn = QPushButton(icon_mgr.get_icon("paperclip"), "", self)
        self.attach_file_btn.setToolTip("Прикрепить файл")
        self.attach_file_btn.clicked.connect(self.attach_file)
        action_buttons_layout.addWidget(self.attach_file_btn)
        
        # Кнопка прикрепления изображения
        self.attach_image_btn = QPushButton(icon_mgr.get_icon("image"), "", self)
        self.attach_image_btn.setToolTip("Прикрепить изображение")
        self.attach_image_btn.clicked.connect(self.attach_image)
        action_buttons_layout.addWidget(self.attach_image_btn)
        
        parent_layout.addLayout(action_buttons_layout)

        # Кнопка отправки
        self.send_btn = QPushButton(icon_mgr.get_icon("send"), "", self)
        self.send_btn.setToolTip("Отправить сообщение")
        self.send_btn.setFixedSize(40, 80)
        self.send_btn.clicked.connect(self.send_message)
        parent_layout.addWidget(self.send_btn)

    def _get_markdown_styles(self) -> str:
        """Возвращает адаптивные CSS стили для элегантного чата"""
        return """
        :root {
            --user-bg: rgba(0, 120, 255, 0.15); /* Лёгкий синий, адаптивный */
            --assistant-bg: rgba(128, 128, 128, 0.1); /* Лёгкий серый */
            --text-color: inherit; /* Адаптируется к глобальной теме */
            --shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            margin: 0;
            padding: 8px;
            color: var(--text-color);
            background: transparent;
            white-space: pre-wrap;
            word-wrap: break-word;
            word-break: break-all;
        }
        
        .message {
            max-width: 75%;
            margin: 6px 0;
            padding: 8px 12px;
            border-radius: 20px;
            box-shadow: var(--shadow);
            animation: fadeIn 0.3s ease-out;
            transition: all 0.2s ease;
            display: inline-block;
            position: relative;
            white-space: pre-wrap;
            word-wrap: break-word;
            word-break: break-all;
        }
        
        .message:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        }
        
        .user-message {
            background: linear-gradient(135deg, var(--user-bg), transparent);
            margin-left: auto;
            text-align: right;
        }
        
        .assistant-message {
            background: linear-gradient(135deg, var(--assistant-bg), transparent);
            margin-right: auto;
            text-align: left;
        }
        
        .system-message {
            background: rgba(255, 193, 7, 0.05);
            font-style: italic;
            text-align: center;
            margin: 0 auto;
            opacity: 0.8;
            border-radius: 10px;
        }
        
        .error-message {
            background: rgba(220, 53, 69, 0.1);
            color: #dc3545;
            text-align: center;
        }
        
        .status-message {
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            font-style: italic;
            margin: 10px auto;
        }
        
        .spinner {
            border: 3px solid rgba(0,0,0,0.1);
            border-top: 3px solid var(--user-bg);
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
        }
        
        .avatar {
            display: inline-block;
            width: 24px;
            height: 24px;
            margin: 0 4px;
            vertical-align: middle;
            border-radius: 50%;
        }
        
        .user-avatar {
            background-color: var(--user-bg);
            position: relative;
        }
        
        .user-avatar:after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 12px;
            height: 12px;
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 50%;
        }
        
        .assistant-avatar {
            background-color: var(--assistant-bg);
            position: relative;
        }
        
        .assistant-avatar:after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 14px;
            height: 8px;
            border: 2px solid rgba(0, 0, 0, 0.2);
            border-top: none;
            border-radius: 0 0 8px 8px;
        }
        
        .timestamp {
            font-size: 0.7em;
            opacity: 0.6;
            margin-top: 2px;
            text-align: right;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Markdown стили */
        h1, h2, h3 { margin: 8px 0; }
        code { background: rgba(0,0,0,0.05); padding: 2px 4px; border-radius: 4px; }
        pre { background: rgba(0,0,0,0.05); padding: 8px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; max-height: 300px; }
        a { color: inherit; text-decoration: underline; }
        blockquote { border-left: 2px solid rgba(0,0,0,0.2); padding-left: 8px; opacity: 0.9; }
        """

    def _render_markdown(self, text: str) -> str:
        """Улучшенная функция рендеринга markdown в HTML"""
        if not text:
            return ""
            
        # Экранируем HTML символы, сохраняя уже существующие HTML теги
        text = self._safe_html_escape(text)
        
        # Обработка блоков кода
        text = re.sub(r'```([^`]*?)```', lambda m: f'<pre><code>{m.group(1)}</code></pre>', text)
        
        # Обработка инлайн-кода
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # Заголовки
        for i in range(6, 0, -1):
            pattern = r'^{} (.+)$'.format('#' * i)
            text = re.sub(pattern, r'<h{0}>\1</h{0}>'.format(i), text, flags=re.MULTILINE)
        
        # Жирный текст
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        
        # Курсив
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        
        # Списки
        text = re.sub(r'^\* (.+)$', r'<ul><li>\1</li></ul>', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\. (.+)$', r'<ol><li>\1</li></ol>', text, flags=re.MULTILINE)
        
        # Ссылки
        text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
        
        # Горизонтальная линия
        text = re.sub(r'^---$', r'<hr>', text, flags=re.MULTILINE)
        
        # Параграфы (только для строк, которые не являются HTML)
        lines = []
        for line in text.split('\n'):
            if line.strip() and not line.strip().startswith(('<', '>')):
                lines.append(f'<p>{line}</p>')
            else:
                lines.append(line)
        
        return '\n'.join(lines)

    def _safe_html_escape(self, text: str) -> str:
        """Безопасное экранирование HTML с сохранением существующих тегов"""
        chunks = []
        last_pos = 0
        
        for match in re.finditer(r'<[^>]+>', text):
            start, end = match.span()
            # Экранируем текст до тега
            if start > last_pos:
                chunks.append(html.escape(text[last_pos:start]))
            # Сохраняем тег как есть
            chunks.append(text[start:end])
            last_pos = end
            
        # Добавляем оставшийся текст
        if last_pos < len(text):
            chunks.append(html.escape(text[last_pos:]))
            
        return ''.join(chunks)

    def send_message(self):
        """Отправляет сообщение"""
        logger.debug("[CHAT] Вызван метод send_message")
        
        text = self.input.toPlainText().strip()
        if not text:
            return
            
        # Очищаем поле ввода и блокируем кнопку
        self.input.clear()
        self.send_btn.setEnabled(False)
        
        # Добавляем сообщение пользователя
        self._append_message_with_style("user", text)
        
        # Добавляем индикатор загрузки
        self._show_loading_indicator()
        
        # Сохраняем в память, если сессия инициализирована
        if self.session_id:
            self.memory_manager.add_message(self.session_id, "user", text)
        else:
            logger.warning("[CHAT] Session not initialized, message not saved")

        # Запускаем асинхронную обработку
        message_data = {
            "message": text,
            "metadata": {
                "session_id": self.session_id,
                "current_tool": self.current_tool,
                "attachments": self.attached_files
            }
        }
        self.async_handler.process_message(message_data)
        self.attached_files = []

    def _show_loading_indicator(self):
        """Показывает индикатор загрузки с анимацией"""
        self._current_status_text = "Обрабатываю запрос"
        status_html = f"""
        <div id="status_msg" class="status-message">
            <div class="spinner"></div>
            {self._current_status_text}
        </div>
        """
        cursor = self.history.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(status_html)
        self._scroll_history_to_end()
        if self._animation_timer is not None:
            self._animation_timer.start()

    def _append_message_with_style(self, role: str, text: str):
        """Добавляет сообщение с соответствующим стилем"""
        msg_id = 'status_msg' if role == 'status' else f'msg_{uuid.uuid4().hex[:8]}'
        
        style_class = {
            "user": "user-message",
            "assistant": "assistant-message",
            "system": "system-message",
            "error": "error-message",
            "status": "status-message"
        }.get(role, "message")
        
        formatted_text = self._render_markdown(text) if role in ["assistant", "system"] else html.escape(text)
        
        author = {
            "user": "Вы",
            "assistant": "Ассистент",
            "system": "Система",
            "error": "Ошибка",
            "status": "Статус"
        }.get(role, "")
        
        # Используем CSS классы вместо эмодзи для аватаров
        avatar = ''
        if role == 'user':
            avatar = '<span class="avatar user-avatar"></span>'
        elif role == 'assistant':
            avatar = '<span class="avatar assistant-avatar"></span>'
        
        timestamp = datetime.now().strftime('%H:%M')
        
        message_html = f"""
        <div id="{msg_id}" class="message {style_class}">
            {avatar}
            <b>{author}:</b> {formatted_text}
            <div class="timestamp">{timestamp}</div>
        </div>
        """
        
        cursor = self.history.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(message_html)
        self.history.setTextCursor(cursor)
        self.history.ensureCursorVisible()
        self._scroll_history_to_end()

    def _update_status_display(self, text: str):
        """Обновляет текст статусного сообщения без повторного добавления"""
        doc = self.history.document()
        cursor = doc.find('id="status_msg"')
        if cursor:
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            updated_html = f"""
            <div id="status_msg" class="status-message">
                <div class="spinner"></div>
                {text}
            </div>
            """
            cursor.insertHtml(updated_html)
            self.history.ensureCursorVisible()
            self._scroll_history_to_end()

    @Slot(str)
    def _update_status_message(self, status_text: str):
        """Обновляет статусное сообщение с анимацией"""
        self._current_status_text = status_text
        self._update_status_display(f"{status_text}...")

    def _handle_response(self, response, is_error=False):
        """Обрабатывает ответ от асинхронного обработчика"""
        if self._animation_timer is not None:
            self._animation_timer.stop()
        
        # Удаляем статусное сообщение
        doc = self.history.document()
        cursor = doc.find('id="status_msg"')
        if cursor:
         cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
         cursor.removeSelectedText()
        
        if is_error:
            self._append_message_with_style("error", f"Ошибка: {response}")
        else:
            message = self._clean_response_message(str(response))
            message = "\n".join(line for line in message.splitlines() if line.strip())
            self._append_message_with_style("assistant", message)
            if self.session_id:
                self.memory_manager.add_message(self.session_id, "assistant", message)
        
        self.send_btn.setEnabled(True)

    def _clean_response_message(self, message: str) -> str:
        """Расширенная очистка от лишних символов и меток"""
        import re
        # Удаляем JSON артефакты
        match = re.search(r"'response':\s*['\"](.*?)['\"]", message, re.DOTALL)
        if match:
            message = match.group(1).strip()
        
        # Удаляем системные префиксы/суффиксы
        message = re.sub(r"^\{.*'response':", '', message, flags=re.DOTALL)
        message = re.sub(r"\}.*$", '', message, flags=re.DOTALL)
        message = re.sub(r"analysis\.time: [\d.]+, 'complexity': \d+, 'requires\.crewai': (True|False), 'type': '[^']+', 'processed\.with_crewai': (True|False),", '', message)
        
        # Удаляем лишние символы: кавычки, скобки, даты, тесты
        message = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+", '', message)  # Даты
        message = re.sub(r"Тестовая запись от.*", '', message)  # Тестовые метки
        message = message.strip("'\"{}[]() \n")
        
        message = message.replace('\\n', '\n')
        
        return message

    def _scroll_history_to_end(self):
        scrollbar = self.history.verticalScrollBar()
        QTimer.singleShot(0, lambda: scrollbar.setValue(scrollbar.maximum()))

    def _input_key_press_event(self, event):
        """Обрабатывает нажатия клавиш в поле ввода"""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.send_message()
            event.accept()
        else:
            QTextEdit.keyPressEvent(self.input, event)
            
    def attach_file(self):
        """Обработчик прикрепления файла"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if file_path:
            logger.info(f"📎 Файл прикреплен: {os.path.basename(file_path)}")
            self._append_message_with_style("system", f"Файл прикреплен: {os.path.basename(file_path)}")
            self.attached_files.append({"path": file_path, "type": "file"})

    def attach_image(self):
        """Обработчик прикрепления изображения"""
        image_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение",
            filter="Images (*.png *.jpg *.jpeg)"
        )
        if image_path:
            logger.info(f"🖼️ Изображение прикреплено: {os.path.basename(image_path)}")
            self._append_message_with_style("system", f"Изображение прикреплено: {os.path.basename(image_path)}")
            self.attached_files.append({"path": image_path, "type": "image"})

    def show_context_stats(self):
        """Показывает статистику контекста"""
        QMessageBox.information(self, "Статистика", "Логика статистики будет добавлена позже.")
        
    def set_theme_manager(self, theme_manager):
        """Устанавливает менеджер тем"""
        self.theme_manager = theme_manager
        self.apply_theme()

    def apply_theme(self):
        """Применяет текущую тему"""
        if self.theme_manager:
            # TODO: Реализовать применение темы
            pass
        logger.info("Theme applied to ChatWidget")
        
    def on_tool_selected(self, tool_id: str, tool_data: dict):
        """Обрабатывает выбор инструмента"""
        self.current_tool = tool_data
        tool_name = tool_data.get("name", tool_id)
        self.input.setPlaceholderText(f"Используется инструмент: {tool_name}. Введите запрос...")
        self._append_message_with_style(
            "system",
            f"Выбран инструмент: {tool_name}. Следующий запрос будет обработан с использованием этого инструмента."
        )

    def resizeEvent(self, event: QResizeEvent):
        """Обрабатывает изменение размера виджета"""
        super().resizeEvent(event)
        if hasattr(self, 'side_panel_container'):
            self.side_panel_container.update_trigger_position()

    def _initialize_session_and_history(self):
        """Инициализирует сессию: загружает последнюю или создает новую, затем загружает историю"""
        sessions = self.memory_manager.list_sessions()
        if sessions:
            # Сортируем сессии по дате создания (самая новая последняя)
            sessions.sort(key=lambda s: s.get('created_at', '0'), reverse=True)
            latest_session = sessions[0]
            self.session_id = latest_session['id']
            logger.info(f"[CHAT] Загружена последняя сессия: {self.session_id}")
        else:
            # Создаем новую сессию
            self.session_id = f"session_{int(time.time())}"
            logger.info(f"[CHAT] Создана новая сессия: {self.session_id}")
        
        # Теперь загружаем историю для этой сессии
        self._load_history()

    def _load_history(self):
        """Загружает и отображает историю сообщений из памяти для текущей сессии"""
        if not self.session_id:
            logger.warning("[CHAT] Сессия не инициализирована, история не загружена")
            return
        
        try:
            messages = self.memory_manager.get_chat_history(self.session_id)
        except AttributeError:
            logger.warning("[CHAT] Метод get_chat_history не найден в MemoryManager")
            messages = []
        
        if not messages:
            logger.info("[CHAT] Нет сохраненных сообщений для сессии")
            return
        
        logger.info(f"[CHAT] Загрузка {len(messages)} сообщений из истории")
        for msg in messages:
            role = msg.get('role', 'system')
            content = msg.get('content', '')
            if role == 'user':
                self._append_message_with_style('user', content)
            elif role == 'assistant':
                self._append_message_with_style('assistant', content)
            else:
                self._append_message_with_style('system', content)
        
        # Прокручиваем к концу после загрузки
        self._scroll_history_to_end()