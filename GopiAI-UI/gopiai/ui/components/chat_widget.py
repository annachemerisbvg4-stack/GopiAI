from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QFileDialog, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class ChatWidget(QWidget):
    def set_theme_manager(self, theme_manager):
        """Интеграция с глобальной темой (API совместим с WebViewChatWidget)"""
        self.theme_manager = theme_manager
        # TODO: применить стили/цвета из theme_manager, если нужно

    """
    Современный чат-виджет для GopiAI на Qt с поддержкой глобальной темы, истории сообщений,
    полем ввода и кнопками: "прикрепить файл", "прикрепить изображение", "multiagent".
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChatWidget")
        self.setMinimumHeight(320)
        self.setStyleSheet("""
            QWidget#ChatWidget {
                background: palette(base);
                border-radius: 8px;
            }
        """)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(6)

        # История сообщений
        self.history = QTextEdit(self)
        self.history.setReadOnly(True)
        self.history.setObjectName("ChatHistory")
        self.main_layout.addWidget(self.history)

        # Нижняя панель
        self.bottom_panel = QHBoxLayout()
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Введите сообщение...")
        self.input.setObjectName("ChatInput")
        self.bottom_panel.addWidget(self.input, 1)

        # Кнопка "прикрепить файл"
        self.attach_file_btn = QPushButton(QIcon(), "📎", self)
        self.attach_file_btn.setToolTip("Прикрепить файл")
        self.attach_file_btn.clicked.connect(self.attach_file)
        self.bottom_panel.addWidget(self.attach_file_btn)

        # Кнопка "прикрепить изображение"
        self.attach_image_btn = QPushButton(QIcon(), "🖼️", self)
        self.attach_image_btn.setToolTip("Прикрепить изображение")
        self.attach_image_btn.clicked.connect(self.attach_image)
        self.bottom_panel.addWidget(self.attach_image_btn)

        # Кнопка "multiagent"
        self.multiagent_btn = QPushButton(QIcon(), "🤖", self)
        self.multiagent_btn.setToolTip("Multiagent режим")
        self.multiagent_btn.clicked.connect(self.multiagent_action)
        self.bottom_panel.addWidget(self.multiagent_btn)

        self.main_layout.addLayout(self.bottom_panel)

        # Обработка Enter
        self.input.returnPressed.connect(self.send_message)

    def send_message(self):
        text = self.input.text().strip()
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
