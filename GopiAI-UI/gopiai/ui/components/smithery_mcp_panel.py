"""
Заглушка для панели MCP - заменяет устаревшую Smithery MCP панель

Этот модуль предоставляет простую заглушку вместо удаленной Smithery MCP панели.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QSizePolicy
)

class SmitheryMcpPanel(QWidget):
    """
    Заглушка для MCP панели.
    """
    
    # Сигналы
    tool_selected = Signal(dict)  # Сигнализирует о выборе инструмента
    
    def __init__(self, parent=None):
        print("[Создание] MCP Panel: Создание заглушки...")
        super().__init__(parent)
        
        # Настраиваем UI
        self.setup_ui()
    
    def setup_ui(self):
        """Настраивает пользовательский интерфейс панели."""
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Информационная метка
        info_label = QLabel("MCP Tools панель отключена")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(info_label)
        
        # Описание
        description = QLabel(
            "Smithery MCP был удален из проекта. "
            "Эта панель является заглушкой для совместимости."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: #888;")
        layout.addWidget(description)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Кнопка для установки новых инструментов в будущем
        install_btn = QPushButton("Установить новые инструменты")
        install_btn.setEnabled(False)  # Отключена
        install_btn.setToolTip("Функция будет доступна в будущих версиях")
        layout.addWidget(install_btn)
        
        # Добавляем растягивающийся элемент
        layout.addStretch(1)
        
        # Информация о версии
        version_label = QLabel("GopiAI Tools v1.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(version_label)
    
    def reload_tools(self):
        """Заглушка для метода перезагрузки инструментов."""
        print("Метод reload_tools вызван, но не реализован в заглушке")
    
    def load_tools(self):
        """Заглушка для метода загрузки инструментов."""
        print("Метод load_tools вызван, но не реализован в заглушке")
    
    def select_tool(self, tool_data):
        """Заглушка для метода выбора инструмента."""
        print(f"Метод select_tool вызван с {tool_data}, но не реализован в заглушке")

# Для тестирования
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    window = SmitheryMcpPanel()
    window.resize(300, 500)
    window.show()
    
    sys.exit(app.exec())
