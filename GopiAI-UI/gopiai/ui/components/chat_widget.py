from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog, QLabel, QSizePolicy, QMessageBox
from PySide6.QtCore import Qt, QMimeData, Slot, QMetaObject, QTimer
from PySide6.QtGui import QIcon, QDropEvent, QDragEnterEvent, QPixmap, QTextCursor
import threading
import sys
import os
import time
import traceback

# Импортируем UniversalIconManager для Lucide-иконок
from gopiai.ui.components.icon_file_system_model import UniversalIconManager

# Клиент для обращения к CrewAI API
from gopiai.ui.components.crewai_client import crewai_client



class ChatWidget(QWidget):
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
        
        # Инициализация Smart Delegator
        self.smart_delegator = None
        self._init_smart_delegator()

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

        # Применить тему при инициализации
        self.theme_manager = None
        self.apply_theme()

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

    def _scroll_history_to_end(self):
        self.history.moveCursor(QTextCursor.MoveOperation.End)

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


    def _init_smart_delegator(self):
        """Инициализирует подключение к CrewAI API"""
        try:
            # Проверяем доступность CrewAI API сервера
            if crewai_client.is_available():
                print("✅ CrewAI API сервер доступен")
                
                # Индексируем документацию в фоновом потоке
                def index_in_background():
                    result = crewai_client.index_documentation()
                    print(f"Результат индексации документации: {result}")
                
                threading.Thread(target=index_in_background, daemon=True).start()
            else:
                print("⚠️ CrewAI API сервер недоступен")
                
                # Показываем сообщение через 3 секунды (чтобы не блокировать загрузку UI)
                def show_warning():
                    QMessageBox.warning(
                        self,
                        "CrewAI недоступен",
                        "CrewAI API сервер недоступен.\n\n"
                        "Для полноценной работы многоагентного режима запустите:\n"
                        "GopiAI-CrewAI/run_crewai_api_server.bat"
                    )
                
                QTimer.singleShot(3000, show_warning)
                
        except Exception as e:
            print(f"❌ Ошибка при инициализации соединения с CrewAI: {e}")
            traceback.print_exc()

    def send_message(self):
        """Отправляет сообщение и обрабатывает его через CrewAI API"""
        text = self.input.toPlainText().strip()
        if text:
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
                
                try:
                    # Пусть система сама определяет нужность использования CrewAI
                    # на основе сложности запроса и типа задачи
                    force_crewai = False
                    
                    # Используем CrewAI API клиент
                    if crewai_client.is_available():
                        # Обработка запроса через CrewAI API
                        response = crewai_client.process_request(text, force_crewai)
                    else:
                        # Fallback если API недоступен
                        response = f"Я получил ваш запрос, но CrewAI API сервер недоступен.\n\n" \
                                   f"Для полноценной работы с агентами запустите:\n" \
                                   f"GopiAI-CrewAI/run_crewai_api_server.bat"
                        time.sleep(1)  # Имитация задержки
                        
                except Exception as e:
                    print(f"❌ Ошибка при обработке запроса: {e}")
                    traceback.print_exc()
                    response = "Произошла ошибка при обработке запроса. Подробности в консоли."
                
                # Обновляем UI в основном потоке
                def update_ui():
                    self._update_assistant_response(waiting_id, response)
                
                QTimer.singleShot(0, update_ui)
            
            # Запускаем обработку в отдельном потоке
            thread = threading.Thread(target=process_in_background)
            thread.daemon = True
            thread.start()
    
    @Slot(str, str)
    def _update_assistant_response(self, waiting_id, response):
        """Обновляет сообщение ассистента в истории (вызывается из другого потока)"""
        # Получаем HTML истории
        html = self.history.toHtml()
        
        # Заменяем временное сообщение на ответ
        html = html.replace(
            f"<span id='{waiting_id}'>⏳ Обрабатываю запрос...</span>",
            response
        )
        
        # Обновляем историю
        self.history.setHtml(html)
        
        # Включаем кнопки
        self.send_btn.setEnabled(True)


    def append_message(self, author, text):
        self.history.append(f"<b>{author}:</b> {text}")


    def attach_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if file_path:
            self.append_message("Файл", file_path)
            # TODO: обработка файла


    def attach_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", filter="Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if image_path:
            self.append_message("Изображение", image_path)
            # TODO: обработка изображения
