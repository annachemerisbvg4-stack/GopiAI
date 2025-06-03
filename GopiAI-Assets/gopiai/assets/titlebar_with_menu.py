from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QWidget, QHBoxLayout

# Если есть кастомный MenuBar — импортируй и его, иначе удали эту строку
from gopiai.widgets.components.menubar import MenuBar
# Важно! Импортируй свой кастомный Titlebar (тот, что выше мы делали)
from gopiai.widgets.components.titlebar import Titlebar


class TitlebarWithMenu(QWidget):
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self._main_window = None
        self._drag_active = False
        self._drag_pos = QPoint()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Добавляем кастомный MenuBar, если он у тебя есть
        self.menubar = MenuBar(self)  # Если нет — закомментируй эту строку и ниже
        layout.addWidget(self.menubar)

        # Добавляем кастомный Titlebar — теперь он принимает тему!
        self.titlebar = Titlebar(parent=self, theme=theme)
        layout.addWidget(self.titlebar, 1)

    def set_window(self, main_window):
        self._main_window = main_window
        self.titlebar.minimizeClicked.connect(main_window.showMinimized)
        self.titlebar.maximizeClicked.connect(main_window.showMaximized)
        self.titlebar.restoreClicked.connect(main_window.showNormal)
        self.titlebar.closeClicked.connect(main_window.close)

    def update_title(self, text):
        self.titlebar.set_title(text)

    def maximize_window(self):
        self.titlebar.show_restore(True)

    def restore_window(self):
        self.titlebar.show_restore(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            self._drag_pos = (
                    event.globalPosition().toPoint()
                    - self.window().frameGeometry().topLeft()
            )
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.MouseButton.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = False
        super().mouseReleaseEvent(event)
