from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog, QLabel, QSizePolicy, QMessageBox
from PySide6.QtCore import Qt, QMimeData, Slot, QMetaObject, QTimer, Signal
from PySide6.QtGui import QIcon, QDropEvent, QDragEnterEvent, QPixmap, QTextCursor
import threading
import sys
import os
import time
import traceback
import logging
import requests

# Настройка логирования
logger = logging.getLogger(__name__)

# Импортируем UniversalIconManager для Lucide-иконок
from gopiai.ui.components.icon_file_system_model import UniversalIconManager

# Клиент для обращения к CrewAI API
from .crewai_client import CrewAIClient
# Модуль управления контекстом чата
from .chat_context import ChatContext

# Импортируем функцию для получения RAG контекста
# Прямая реализация функции вместо импорта для избежания проблем с зависимостями
import requests

def get_embedded_memory_context(query: str, max_results: int = 3) -> str:
    """Retrieve context from embedded memory system (SimpleMemoryManager).
    
    Args:
        query: The search query string
        max_results: Maximum number of context items to retrieve (default: 3)
        
    Returns:
        A string containing the retrieved context items, separated by newlines.
        Returns an empty string if memory system is unavailable or an error occurs.
    """
    try:
        from rag_memory_system import get_memory_manager
        
        # Get memory manager
        manager = get_memory_manager()
        
        # Search for relevant messages
        results = manager.search_memory(query, limit=max_results)
        
        if results:
            # Format results into context string
            context_items = []
            for result in results:
                content = result.get('content', '')
                # Include role information for better context
                role = result.get('role', 'unknown')
                if role == 'user':
                    context_items.append(f"Пользователь ранее спрашивал: {content}")
                elif role == 'assistant':
                    context_items.append(f"Ассистент ранее отвечал: {content}")
                else:
                    context_items.append(content)
            
            return "\n\n".join(context_items)
        else:
            logger.debug(f"No memory results found for query: {query}")
            return ""
            
    except ImportError as e:
        logger.warning(f"Embedded memory system not available: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error in get_embedded_memory_context: {e}")
        return ""

RAG_AVAILABLE = True  # Функция всегда доступна, но может возвращать пустой результат
logger.info("✅ RAG context function defined directly")




# DEBUG LOGGING PATCH - Added for hang diagnosis
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
print("🔧 DEBUG logging enabled for chat_widget.py")


class ChatWidget(QWidget):
    # Qt signals for thread-safe communication
    response_ready = Signal(str, bool)  # response_text, error_occurred
    def set_theme_manager(self, theme_manager):
        """Интеграция с глобальной темой (API совместим с WebViewChatWidget)"""
        self.theme_manager = theme_manager
        self.apply_theme()

    def apply_theme(self):
        """Применяет глобальную тему к чату (ничего не делает, всё подтянется из глобального стиля)"""
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
        
        # Инициализация контекста чата для краткосрочной памяти
        self.chat_context = ChatContext(max_messages=20, max_tokens=4000)

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
        
        # Кнопка статистики контекста
        self.context_stats_btn = QPushButton(icon_mgr.get_icon("info"), "", self)
        self.context_stats_btn.setToolTip("Показать статистику контекста")
        self.context_stats_btn.clicked.connect(self.show_context_stats)
        self.bottom_panel.addWidget(self.context_stats_btn)
        
        # Кнопка отправки
        self.send_btn = QPushButton(icon_mgr.get_icon("send"), "", self)
        self.send_btn.setToolTip("Отправить сообщение")
        self.send_btn.clicked.connect(self.send_message)
        self.bottom_panel.addWidget(self.send_btn)

        self.main_layout.addLayout(self.bottom_panel)

        # Обработка Enter (Ctrl+Enter для отправки)
        self.input.keyPressEvent = self._input_key_press_event

        # Автопрокрутка истории
        self.history.textChanged.connect(self._scroll_history_to_end)

        # Connect Qt signal for thread-safe communication
        self.response_ready.connect(self._handle_response_from_thread)

        # Применить тему при инициализации
        self.theme_manager = None
        self.apply_theme()
        
        # Check service availability after UI is fully initialized
        self._check_crewai_availability()

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
    def _handle_response_from_thread(self, response_text, error_occurred):
        """Handles responses from background thread via Qt signal"""
        try:
            logger.info(f"Signal received: response_len={len(response_text)}, error={error_occurred}")
            
            # Get current HTML and try to replace waiting span
            current_html = self.history.toHtml()
            
            # Try to find and replace waiting span
            waiting_patterns = [
                "⏳ Обрабатываю запрос...",
                "<span id="
            ]
            
            replaced = False
            for pattern in waiting_patterns:
                if pattern in current_html:
                    # Style error message in red if it's an error
                    if error_occurred:
                        styled_response = f"<span style='color: red;'>{response_text}</span>"
                    else:
                        styled_response = response_text
                    
                    # For waiting text pattern
                    if pattern == "⏳ Обрабатываю запрос...":
                        updated_html = current_html.replace(pattern, styled_response)
                        self.history.setHtml(updated_html)
                        replaced = True
                        break
                    # For span pattern, use regex to replace the whole span
                    elif "<span id=" in pattern:
                        import re
                        span_pattern = r"<span[^>]*id=['\"][^'\"]*['\"][^>]*>⏳ Обрабатываю запрос...</span>"
                        updated_html = re.sub(span_pattern, styled_response, current_html, flags=re.DOTALL)
                        if updated_html != current_html:
                            self.history.setHtml(updated_html)
                            replaced = True
                            break
            
            # If waiting span not found, append as new message
            if not replaced:
                if error_occurred:
                    self.append_message("Ассистент", f"<span style='color: red;'>{response_text}</span>")
                else:
                    self.append_message("Ассистент", response_text)
            
            logger.info("✅ Response handled successfully via Qt signal")
            
        except Exception as e:
            logger.error(f"❌ Error in signal handler: {e}", exc_info=True)
            # Fallback: append error message in red
            if error_occurred:
                self.append_message("Ассистент", f"<span style='color: red;'>{response_text}</span>")
            else:
                self.append_message("Ассистент", response_text)
        finally:
            # Always re-enable Send button and scroll to end
            self.send_btn.setEnabled(True)
            self._scroll_history_to_end()

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
        if text:
            # Добавляем сообщение пользователя в контекст
            self.chat_context.add_user_message(text)
            # Отображаем сообщение пользователя
            self.append_message("Вы", text)
            self.input.clear()
            
            # Показываем индикатор ожидания
            self.send_btn.setEnabled(False)
            
            # Создаем уникальный ID для сообщения ожидания
            waiting_id = f"waiting_{int(time.time())}"
            self.append_message("Ассистент", f"<span id='{waiting_id}'>⏳ Обрабатываю запрос...</span>")
            
            # Функция обработки в фоновом потоке
            def process_in_background():
                response = "Извините, я не смог обработать запрос из-за технической проблемы."
                error_occurred = False
                
                # ИСПРАВЛЕНИЕ: Обернуть весь body функции в try/except
                try:
                    # Получаем контекст из embedded памяти
                    rag_context = ""
                    if RAG_AVAILABLE:
                        try:
                            rag_context = get_embedded_memory_context(text, max_results=5)
                            if rag_context:
                                logger.info(f"📚 Получен контекст из embedded памяти ({len(rag_context)} символов)")
                            else:
                                logger.info("📚 Контекст из embedded памяти пуст")
                        except Exception as rag_e:
                            logger.warning(f"⚠️ Ошибка получения контекста из embedded памяти: {rag_e}")
                            rag_context = ""
                    
                    # Получаем контекст чата для передачи в API
                    chat_context_string = self.chat_context.get_context_string()
                    
                    # Формируем базовый системный промпт
                    system_preamble = "Вы - интеллектуальный ассистент GopiAI. Отвечайте на вопросы пользователей максимально полно и точно."
                    
                    # Строим финальный промпт ТОЧНО по схеме из требования:
                    # system_preamble + "\n\n" + ("Relevant context:\n" + context + "\n\n" if context else "") + "User:\n" + user_message
                    request_with_context = system_preamble
                    
                    # Добавляем RAG контекст, если есть (согласно точной схеме)
                    if rag_context:
                        request_with_context += "\n\n" + "Relevant context:\n" + rag_context + "\n\n"
                    else:
                        request_with_context += "\n\n"
                    
                    # Добавляем текущий запрос пользователя (User: format из требования)
                    request_with_context += "User:\n" + text
                    
                    # Добавляем контекст чата как дополнительную информацию, если есть
                    if chat_context_string:
                        request_with_context += f"\n\nПредыдущие сообщения:\n{chat_context_string}"
                    
                    # Используем CrewAI API клиент с timeout параметром
                    process_result = self.crew_ai_client.process_request(request_with_context, timeout=120)
                    logger.info(f"Получен результат от CrewAI API: {process_result}")
                    
                    # Проверяем, является ли это браузерной командой
                    if isinstance(process_result, dict) and process_result.get("impl") == "browser-use":
                        # Обрабатываем браузерную команду через вызов метода из главного потока
                        # Поскольку мы в фоновом потоке, используем QTimer для безопасного вызова
                        from PySide6.QtCore import QTimer
                        import time
                        
                        # Создаем переменную для результата
                        browser_result = [None]  # Используем список для передачи по ссылке
                        
                        def handle_browser_in_main_thread():
                            try:
                                result = self._handle_browser_command(process_result["command"])
                                browser_result[0] = result
                            except Exception as e:
                                browser_result[0] = f"Ошибка выполнения браузерной команды: {str(e)}"
                        
                        # Запускаем обработку в главном потоке
                        QTimer.singleShot(0, handle_browser_in_main_thread)
                        
                        # Ждем завершения (простая реализация)
                        timeout = 0
                        while browser_result[0] is None and timeout < 20:  # 2 секунды максимум
                            time.sleep(0.1)
                            timeout += 1
                        
                        if browser_result[0] is not None:
                            browser_response = browser_result[0]
                        else:
                            browser_response = "Таймаут при выполнении браузерной команды"
                        
                        process_result = {
                            "response": browser_response,
                            "processed_with_crewai": False
                        }
                    
                    # Handle structured error responses from CrewAI client
                    if isinstance(process_result, dict):
                        # Check for error_message field (new structured error format)
                        if "error_message" in process_result:
                            response = process_result["error_message"]
                            error_occurred = True
                            logger.warning(f"Получена структурированная ошибка от API: {response}")
                        # Check for response field (normal response)
                        elif "response" in process_result:
                            response = process_result["response"]
                            # Check if there was an error flag
                            if "error" in process_result:
                                logger.warning(f"Получена ошибка от API: {process_result['error']}")
                                error_occurred = True
                        else:
                            response = "Неизвестный формат ответа от CrewAI API."
                            error_occurred = True
                            logger.error(f"Неожиданный формат ответа: {process_result}")
                    elif isinstance(process_result, str):
                        # Обратная совместимость на случай, если клиент вернул строку
                        response = process_result
                        logger.info("Получен ответ в виде строки (обратная совместимость)")
                    else:
                        response = "Неизвестный тип ответа от CrewAI API."
                        error_occurred = True
                        logger.error(f"Неожиданный тип ответа: {type(process_result)}")
                    
                    # Добавляем ответ ассистента в контекст (только если нет ошибки)
                    if not error_occurred:
                        self.chat_context.add_assistant_message(response)
                        
                        # Сохраняем диалог в embedded памяти
                        try:
                            from rag_memory_system import get_memory_manager
                            manager = get_memory_manager()
                            manager.save_chat_exchange(text, response)
                            logger.info("💾 Диалог сохранен в embedded память")
                        except Exception as memory_e:
                            logger.warning(f"⚠️ Ошибка сохранения в embedded память: {memory_e}")
                        
                except Exception as e:
                    logger.error(f"❌ Полная ошибка в background thread: {e}", exc_info=True)
                    response = f"Произошла ошибка при обработке запроса: {str(e)}"
                    error_occurred = True
                
                # ИСПРАВЛЕНИЕ: Используем Qt signal вместо QTimer.singleShot
                try:
                    logger.info("🔄 Отправляем ответ через Qt signal")
                    self.response_ready.emit(response, error_occurred)
                except Exception as e:
                    logger.error(f"❌ Ошибка при отправке сигнала: {e}", exc_info=True)
                    # Fallback: используем QTimer как последний вариант
                    def emergency_update():
                        try:
                            # Get current HTML and try to replace waiting span
                            current_html = self.history.toHtml()
                            waiting_patterns = [
                                f"<span id='{waiting_id}'>⏳ Обрабатываю запрос...</span>",
                                "⏳ Обрабатываю запрос..."
                            ]
                            
                            # Try to replace waiting span with response
                            replaced = False
                            for pattern in waiting_patterns:
                                if pattern in current_html:
                                    # Style error message in red
                                    styled_response = f"<span style='color: red;'>{response}</span>" if error_occurred else response
                                    updated_html = current_html.replace(pattern, styled_response)
                                    self.history.setHtml(updated_html)
                                    replaced = True
                                    break
                            
                            # If waiting span not found, append as new message
                            if not replaced:
                                styled_response = f"<span style='color: red;'>{response}</span>" if error_occurred else response
                                self.append_message("Ассистент", styled_response)
                                
                        except Exception as fallback_e:
                            logger.error(f"❌ Критическая ошибка fallback: {fallback_e}", exc_info=True)
                        finally:
                            # Always re-enable Send button
                            self.send_btn.setEnabled(True)
                    QTimer.singleShot(0, emergency_update)
            
            # Запускаем обработку в отдельном потоке
            thread = threading.Thread(target=process_in_background)
            thread.daemon = True
            thread.start()
    
    @Slot(str, str, bool)
    def _update_assistant_response(self, waiting_id, response, error_occurred=False):
        """
        Обновляет ответ ассистента в истории чата (ИСПРАВЛЕННАЯ ВЕРСИЯ)
        
        Args:
            waiting_id: ID сообщения ожидания для замены
            response: Текст ответа
            error_occurred: Флаг ошибки для стилизации
        """
        logger.info(f"_update_assistant_response: waiting_id={waiting_id}, response_len={len(response)}, error={error_occurred}")
        
        # ИСПРАВЛЕНИЕ: Заменяем сообщение ожидания вместо добавления нового
        try:
            # Получаем текущий HTML
            current_html = self.history.toHtml()
            logger.info(f"Текущий HTML содержит {len(current_html)} символов")
            
            # Пробуем разные варианты поиска сообщения ожидания
            waiting_patterns = [
                f"<span id='{waiting_id}'>⏳ Обрабатываю запрос...</span>",
                f"<span id=\"'{waiting_id}'\">⏳ Обрабатываю запрос...</span>",
                f"id='{waiting_id}'",
                f"id=\"{waiting_id}\"",
                waiting_id,
                "⏳ Обрабатываю запрос..."
            ]
            
            replaced = False
            for pattern in waiting_patterns:
                if pattern in current_html:
                    logger.info(f"✅ Найден паттерн: {pattern}")
                    
                    # Стилизируем ответ в зависимости от наличия ошибки
                    if error_occurred:
                        new_response = f"<span style='color: #d73027;'>{response}</span>"
                    else:
                        new_response = response
                    
                    # Если это полный span, заменяем его
                    if "<span" in pattern and "</span>" in pattern:
                        updated_html = current_html.replace(pattern, new_response)
                    # Если это просто текст ожидания, заменяем его
                    elif pattern == "⏳ Обрабатываю запрос...":
                        updated_html = current_html.replace(pattern, new_response)
                    else:
                        # Для других случаев ищем весь span
                        import re
                        span_pattern = f"<span[^>]*id=['\"]{waiting_id}['\"][^>]*>.*?</span>"
                        updated_html = re.sub(span_pattern, new_response, current_html, flags=re.DOTALL)
                    
                    if updated_html != current_html:
                        self.history.setHtml(updated_html)
                        logger.info("✅ Сообщение ожидания успешно заменено на ответ")
                        replaced = True
                        break
                    else:
                        logger.warning(f"⚠️ Паттерн найден, но замена не произошла: {pattern}")
                        
            if not replaced:
                # Fallback: если не удалось найти сообщение ожидания, добавляем новое
                logger.warning("⚠️ Не удалось найти сообщение ожидания, добавляем новое сообщение")
                logger.debug(f"HTML для отладки (первые 500 символов): {current_html[:500]}")
                self.append_message("Ассистент", response)
        
        except Exception as e:
            logger.error(f"❌ Ошибка при обновлении ответа: {e}", exc_info=True)
            # Fallback: просто добавляем новое сообщение
            self.append_message("Ассистент", response)
        
        # Включаем кнопки и прокручиваем вниз
        self.send_btn.setEnabled(True)
        self._scroll_history_to_end()


    def append_message(self, author, text):
        logger.info(f"append_message: author={author}, text_len={len(text)}")
        self.history.append(f"<b>{author}:</b> {text}")
        self.history.repaint()


    def attach_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if file_path:
            self.append_message("Система", f"Файл прикреплен: {os.path.basename(file_path)}. (Дальнейшая обработка не реализована)")
            logger.info(f"Файл прикреплен: {file_path}")


    def attach_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", filter="Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if image_path:
            self.append_message("Система", f"Изображение прикреплено: {os.path.basename(image_path)}. (Дальнейшая обработка не реализована)")
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
            self.append_message("Система", "❌ CrewAI клиент не инициализирован")
            return False
            
        if not self.crew_ai_client.is_available():
            self.append_message("Система", "❌ CrewAI API сервер недоступен")
            return False
            
        # Отправляем тестовый запрос
        try:
            test_result = self.crew_ai_client.process_request("Тест соединения")
            if isinstance(test_result, dict):
                # Check for structured error response
                if "error_message" in test_result:
                    self.append_message("Система", f"❌ Ошибка API: {test_result['error_message']}")
                    return False
                elif "response" in test_result:
                    self.append_message("Система", "✅ CrewAI API работает корректно")
                    return True
                else:
                    self.append_message("Система", f"⚠️ Неожиданный ответ от API: {test_result}")
                    return False
            else:
                self.append_message("Система", f"⚠️ Неожиданный тип ответа от API: {type(test_result)}")
                return False
        except Exception as e:
            self.append_message("Система", f"❌ Ошибка тестирования API: {str(e)}")
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
        stats_before = self.chat_context.get_stats()
        self.chat_context.clear()
        
        self.append_message("Система", 
            f"🧹 Контекст чата очищен. Было: {stats_before['message_count']} сообщений, "
            f"~{stats_before['estimated_tokens']} токенов.")
        
        logger.info(f"Chat context cleared. Previous stats: {stats_before}")
    
    def show_context_stats(self):
        """Показывает статистику текущего контекста чата"""
        stats = self.chat_context.get_stats()
        context_preview = ""
        
        # Показываем превью последних 2 сообщений
        if stats['message_count'] > 0:
            last_messages = self.chat_context.get_last_messages(2)
            preview_parts = []
            for msg in last_messages:
                content_preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                preview_parts.append(f"- {msg.role}: {content_preview}")
            context_preview = "\n\nПоследние сообщения:\n" + "\n".join(preview_parts)
        
        self.append_message("Система", 
            f"📊 Статистика контекста:\n"
            f"• Сообщений: {stats['message_count']}/{stats['max_messages']}\n"
            f"• Символов: {stats['total_characters']}\n"
            f"• Примерно токенов: {stats['estimated_tokens']}/{stats['max_tokens']}"
            + context_preview)
        
        logger.info(f"Context stats displayed: {stats}")
    
    def _handle_browser_command(self, command: str) -> str:
        """Обрабатывает браузерную команду через встроенный браузер."""
        try:
            self.append_message("Система", f"🌐 Выполняю команду в встроенном браузере: {command}")
            
            # Получаем ссылку на встроенный браузер из главного окна
            browser_widget = self._get_embedded_browser()
            
            if not browser_widget:
                return "❌ Встроенный браузер не найден. Откройте вкладку браузера."
            
            # Парсим команду и выполняем соответствующее действие
            result = self._execute_browser_action(browser_widget, command)
            
            self.append_message("Система", f"✅ Результат: {result}")
            return result
            
        except Exception as e:
            error_msg = f"❌ Ошибка при выполнении команды браузера: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _get_embedded_browser(self):
        """Получает ссылку на встроенный браузер из главного окна."""
        try:
            # Ищем родительское окно
            parent = self.parent()
            while parent and not hasattr(parent, 'tab_document_widget'):
                parent = parent.parent()
            
            if not parent:
                return None
            
            # Получаем TabDocumentWidget
            tab_widget = getattr(parent, 'tab_document_widget', None)
            if not tab_widget:
                return None
            
            # Ищем активную вкладку браузера
            current_widget = tab_widget.tab_widget.currentWidget()
            
            # Проверяем, является ли это браузерной вкладкой
            if hasattr(current_widget, 'property'):
                web_view = current_widget.property('_web_view')
                if web_view:
                    return {
                        'web_view': web_view,
                        'address_bar': current_widget.property('_address_bar'),
                        'widget': current_widget
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения браузера: {str(e)}")
            return None
    
    def _execute_browser_action(self, browser_widget, command: str) -> str:
        """Выполняет действие в браузере на основе команды."""
        try:
            web_view = browser_widget['web_view']
            address_bar = browser_widget['address_bar']
            
            command_lower = command.lower()
            
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
