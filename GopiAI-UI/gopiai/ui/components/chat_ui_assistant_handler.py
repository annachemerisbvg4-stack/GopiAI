# --- START OF FILE chat_ui_assistant_handler.py ---

import logging
from PySide6.QtCore import QObject, QTimer, QRect, Slot, QPoint, Qt 
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel 
from gopiai.ui_core.ai_tools import get_ui_assistant_tool

logger = logging.getLogger(__name__)

class ChatUIAssistantHandler(QObject):
    """
    Handles all interactions with the UI Assistant tool.
    Manages visual feedback like status messages and element highlighting.
    """
    def __init__(self, parent_widget: QWidget):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.ui_assistant = None
        
        # Визуальные элементы для обратной связи
        self.overlay_widget = None
        self.status_label = None
        self.highlight_widget = None
        
        self._setup_visual_feedback()
        self._initialize_assistant()

    def _setup_visual_feedback(self):
        """Creates the overlay and widgets for visual feedback."""
        try:
            # Создаем прозрачный виджет-оверлей поверх родительского виджета
            self.overlay_widget = QWidget(self.parent_widget)
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
            
            self.status_label = QLabel()
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(0, 0, 0, 180); color: white;
                    padding: 8px 16px; border-radius: 4px; font-weight: bold;
                    font-size: 12px; margin: 10px;
                }
            """)
            self.status_label.hide()
            
            self.highlight_widget = QLabel()
            self.highlight_widget.setStyleSheet("""
                QLabel {
                    background-color: rgba(65, 131, 196, 40);
                    border: 2px solid #4183c4; border-radius: 4px;
                }
            """)
            self.highlight_widget.hide()
            
            layout.addWidget(self.status_label, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            layout.addStretch()
            
            self.overlay_widget.setLayout(layout)
            self.overlay_widget.hide()
            logger.info("✅ UI Assistant visual feedback elements created.")
        except Exception as e:
            logger.error(f"❌ Failed to set up visual feedback: {e}", exc_info=True)

    def _initialize_assistant(self):
        """Gets the UI Assistant instance and connects its signals."""
        try:
            self.ui_assistant = get_ui_assistant_tool()
            if not self.ui_assistant:
                logger.warning("⚠️ UI Assistant tool not available.")
                return

            # Подключаем сигналы
            self.ui_assistant.action_started.connect(self.on_assistant_action_started)
            self.ui_assistant.action_completed.connect(self.on_assistant_action_completed)
            self.ui_assistant.visual_feedback.connect(self.on_visual_feedback)
            
            # Устанавливаем ссылку на главное окно
            main_window = self.parent_widget.window()
            if main_window:
                self.ui_assistant.set_main_window(main_window)
                
            logger.info("✅ UI Assistant initialized and signals connected.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize UI Assistant: {e}", exc_info=True)

    @Slot(str)
    def on_assistant_action_started(self, message: str):
        """Handles the action_started signal from the UI Assistant."""
        # Этот метод должен быть подключен к сигналу append_message в ChatWidget
        # Пока просто логируем
        logger.info(f"[ASSISTANT ACTION STARTED] {message}")
        if hasattr(self.parent_widget, 'append_message'):
            self.parent_widget.append_message("UI Ассистент", message)

    @Slot(str, bool)
    def on_assistant_action_completed(self, message: str, success: bool):
        """Handles the action_completed signal."""
        status = "успешно" if success else "с ошибкой"
        full_message = f"{message} - {status}"
        logger.info(f"[ASSISTANT ACTION COMPLETED] {full_message}")
        if hasattr(self.parent_widget, 'append_message'):
            self.parent_widget.append_message("UI Ассистент", full_message)

    @Slot(str, dict)
    def on_visual_feedback(self, feedback_type: str, data: dict):
        """Handles visual feedback signals."""
        if feedback_type == "status_message":
            self._show_status_message(data["message"], data.get("duration", 3000))
        elif feedback_type == "highlight_element":
            rect = QRect(data["x"], data["y"], data["width"], data["height"])
            self._highlight_element(rect, data.get("duration", 1000))

    def _show_status_message(self, message: str, duration: int = 3000):
        """Shows a status message to the user."""
        if not self.status_label: return
        self.status_label.setText(message)
        self.status_label.show()
        self.overlay_widget.show() # Показываем оверлей
        self.overlay_widget.raise_()
        QTimer.singleShot(duration, self.status_label.hide)

    def _highlight_element(self, rect: QRect, duration: int = 1000):
        """Highlights a UI element at the specified position."""
        if not self.highlight_widget or not self.parent_widget.window(): return
        
        # Пересчитываем координаты относительно главного окна
        global_pos = self.parent_widget.window().mapFromGlobal(QPoint(0,0))
        widget_pos = self.parent_widget.mapTo(self.parent_widget.window(), rect.topLeft())
        final_rect = QRect(widget_pos - global_pos, rect.size())
        
        self.highlight_widget.setGeometry(final_rect)
        self.highlight_widget.show()
        self.overlay_widget.show() # Показываем оверлей
        self.overlay_widget.raise_()
        QTimer.singleShot(duration, self.highlight_widget.hide)
        
    def resize_overlay(self):
        """Resizes the overlay to match the parent widget's size."""
        if self.overlay_widget:
            self.overlay_widget.setGeometry(self.parent_widget.rect())

# --- КОНЕЦ ФАЙЛА chat_ui_assistant_handler.py ---