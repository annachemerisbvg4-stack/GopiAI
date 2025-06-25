
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog, QLabel, QSizePolicy
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QIcon, QDropEvent, QDragEnterEvent, QPixmap, QTextCursor

# Импортируем UniversalIconManager для Lucide-иконок
from gopiai.ui.components.icon_file_system_model import UniversalIconManager



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

        # История сообщений
        self.history = QTextEdit(self)
        self.history.setReadOnly(True)
        self.history.setObjectName("ChatHistory")
        self.history.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.history.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.main_layout.addWidget(self.history)

        # Нижняя панель
        self.bottom_panel = QHBoxLayout()

        # Многострочное поле ввода
        self.input = QTextEdit(self)
        self.input.setPlaceholderText("Введите сообщение...")
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

        self.multiagent_btn = QPushButton(icon_mgr.get_icon("users"), "", self)
        self.multiagent_btn.setToolTip("Multiagent режим")
        self.multiagent_btn.clicked.connect(self.multiagent_action)
        self.bottom_panel.addWidget(self.multiagent_btn)

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
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.send_message()
        else:
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


    def send_message(self):
        text = self.input.toPlainText().strip()
        if text:
            self.append_message("Вы", text)
            self.input.clear()
            # TODO: интеграция с backend/AI


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


    def multiagent_action(self):
        self.append_message("Multiagent", "Режим multiagent активирован!")
        # TODO: интеграция multiagent
