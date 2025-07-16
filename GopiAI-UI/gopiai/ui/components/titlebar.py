"""
Titlebar Component для GopiAI Standalone Interface
==============================================

Заголовок окна с кнопками управления и возможностью перетаскивания.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt, QPoint, QRect
from PySide6.QtGui import QMouseEvent, QIcon

# Импорт меню для комбинированного titlebar
try:
    from .menu_bar import StandaloneMenuBar
except ImportError:
    StandaloneMenuBar = None


class StandaloneTitlebar(QWidget):
    """Автономный titlebar с кнопками управления окном"""
    
    minimizeClicked = Signal()
    maximizeClicked = Signal()
    restoreClicked = Signal()
    closeClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titlebarWidget")
        self.setFixedHeight(40)
        self._drag_active = False
        self._drag_pos = QPoint()
        self.icon_manager = None
        self._setup_icon_system()
        self._setup_icon_system()
        self._setup_ui()

    def _setup_icon_system(self):
        """Настройка системы иконок"""
        try:
            from .icon_file_system_model import UniversalIconManager
            self.icon_manager = UniversalIconManager()
            print("[OK] Titlebar: Загружена система иконок UniversalIconManager")
        except ImportError:
            self.icon_manager = None
            print("[ERROR] Titlebar: Не удалось загрузить UniversalIconManager")

    def _setup_ui(self):
        """Настройка интерфейса titlebar"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        
        # Заголовок окна
        self.window_title = QLabel("GopiAI v0.2.0", self)
        self.window_title.setObjectName("windowTitle")
        self.window_title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.window_title, 1)
        
        # Кнопки управления окном
        self.minimize_button = self._create_titlebar_button("minimize", "—", self.minimizeClicked.emit)
        layout.addWidget(self.minimize_button)
        
        self.restore_button = self._create_titlebar_button("square", "❐", self.restoreClicked.emit)
        self.restore_button.setVisible(False)
        layout.addWidget(self.restore_button)
        
        self.maximize_button = self._create_titlebar_button("maximize", "□", self.maximizeClicked.emit)
        layout.addWidget(self.maximize_button)
        
        self.close_button = self._create_titlebar_button("x", "×", self.closeClicked.emit)
        layout.addWidget(self.close_button)

    def _create_titlebar_button(self, icon_name: str, fallback_text: str, callback) -> QPushButton:
        """Создает кнопку titlebar с иконкой"""
        btn = QPushButton()
        btn.setFixedSize(40, 40)
        btn.clicked.connect(callback)
        
        # Устанавливаем объект-нейм для стилизации
        if icon_name == "minimize":
            btn.setObjectName("minimizeButton")
        elif icon_name == "maximize":
            btn.setObjectName("maximizeButton")
        elif icon_name == "square":
            btn.setObjectName("restoreButton")
        elif icon_name == "x":
            btn.setObjectName("closeButton")
        
        if self.icon_manager:
            try:
                icon = self.icon_manager.get_icon(icon_name)
                if icon and not icon.isNull():
                    btn.setIcon(icon)
                else:
                    btn.setText(fallback_text)
            except Exception as e:
                print(f"⚠️ Ошибка загрузки иконки {icon_name}: {e}")
                btn.setText(fallback_text)
        else:
            btn.setText(fallback_text)
            
        return btn

    def set_title(self, text: str):
        """Установка заголовка окна"""
        self.window_title.setText(text)

    def mousePressEvent(self, event: QMouseEvent):
        """Обработка нажатия мыши для перетаскивания"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Обработка перемещения мыши для перетаскивания"""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_active:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Обработка отпускания мыши"""
        self._drag_active = False


class StandaloneTitlebarWithMenu(QWidget):
    """Комбинированный titlebar с меню"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titlebarWithMenu")
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Titlebar
        self.titlebar = StandaloneTitlebar(self)
        layout.addWidget(self.titlebar)
        
        # Меню
        if StandaloneMenuBar:
            self.menu_bar = StandaloneMenuBar(self)
            layout.addWidget(self.menu_bar)
        else:
            print("⚠️ StandaloneMenuBar не доступен для titlebar")

    def set_window(self, window):
        """Подключение к окну"""
        self.window_ref = window
        # Подключение сигналов titlebar к окну
        self.titlebar.minimizeClicked.connect(window.showMinimized)
        self.titlebar.maximizeClicked.connect(self._toggle_maximize)
        self.titlebar.restoreClicked.connect(self._toggle_maximize)
        self.titlebar.closeClicked.connect(window.close)

    def _toggle_maximize(self):
        """Переключение между развернутым и обычным состоянием"""
        if hasattr(self, 'window_ref'):
            if self.window_ref.isMaximized():
                self.window_ref.showNormal()
                self.titlebar.maximize_button.setVisible(True)
                self.titlebar.restore_button.setVisible(False)
            else:
                self.window_ref.showMaximized()
                self.titlebar.maximize_button.setVisible(False)
                self.titlebar.restore_button.setVisible(True)

    def menuBar(self):
        """Возвращает объект меню"""
        if hasattr(self, 'menu_bar'):
            return self.menu_bar
        return None


class CustomGrip(QWidget):
    """Элемент для изменения размера окна"""
    
    def __init__(self, parent, direction):
        super().__init__(parent)
        self.direction = direction
        self._setup_cursor()

    def _setup_cursor(self):
        """Настройка курсора для грипа"""
        if self.direction in ['top', 'bottom']:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif self.direction in ['left', 'right']:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif self.direction in ['top-left', 'bottom-right']:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif self.direction in ['top-right', 'bottom-left']:
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)

    def mousePressEvent(self, event):
        """Начало изменения размера"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()
            self.start_geometry = self.window().geometry()

    def mouseMoveEvent(self, event):
        """Изменение размера окна"""
        if hasattr(self, 'start_pos'):
            delta = event.globalPosition().toPoint() - self.start_pos
            self._resize_window(delta)

    def _resize_window(self, delta):
        """Изменение размера окна в зависимости от направления"""
        geo = self.start_geometry
        new_geo = QRect(geo)
        
        if 'top' in self.direction:
            new_geo.setTop(geo.top() + delta.y())
        if 'bottom' in self.direction:
            new_geo.setBottom(geo.bottom() + delta.y())
        if 'left' in self.direction:
            new_geo.setLeft(geo.left() + delta.x())
        if 'right' in self.direction:
            new_geo.setRight(geo.right() + delta.x())
        
        # Минимальные размеры
        if new_geo.width() < 600:
            new_geo.setWidth(600)
        if new_geo.height() < 400:
            new_geo.setHeight(400)
        
        self.window().setGeometry(new_geo)
