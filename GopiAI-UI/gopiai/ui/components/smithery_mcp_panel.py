"""
Панель инструментов Smithery MCP для UI

Модуль предоставляет компоненты для отображения и управления
инструментами Smithery MCP в пользовательском интерфейсе.
"""

import os
import json
import sys
from typing import Dict, List, Any, Optional, Callable

from PySide6.QtCore import Qt, Signal, Slot, QObject
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QSizePolicy, QToolButton, QLineEdit,
    QComboBox, QCheckBox, QSpacerItem
)
from PySide6.QtGui import QIcon, QFont

# Добавляем путь к пакетам GopiAI-CrewAI
crewai_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'GopiAI-CrewAI'))
sys.path.append(crewai_path)

try:
    # Корректные импорты из директории GopiAI-CrewAI
    from tools.gopiai_integration.smithery_client import get_smithery_client
    from tools.gopiai_integration.smithery_tools import get_smithery_tools_adapter
    from tools.gopiai_integration.smithery_integration import get_smithery_integration
except ImportError as e:
    print(f"Ошибка импорта модулей Smithery: {e}")
    # Фиктивные функции для предотвращения падения при инициализации класса
    def get_smithery_client():
        return None
        
    def get_smithery_tools_adapter():
        return None
        
    def get_smithery_integration():
        return None

# Константы для UI
BUTTON_HEIGHT = 30
TOOL_BUTTON_SIZE = 24
MIN_PANEL_WIDTH = 200
MAX_PANEL_WIDTH = 350

class SmitheryMcpPanel(QWidget):
    """
    Панель для отображения и управления инструментами Smithery MCP.
    """
    
    # Сигналы
    tool_selected = Signal(dict)  # Сигнализирует о выборе инструмента
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.integration = get_smithery_integration()
        self.tools_adapter = get_smithery_tools_adapter()
        self.available_tools = []
        self.current_tool = None
        
        self.setup_ui()
        self.load_tools()
    
    def setup_ui(self):
        """Настраивает пользовательский интерфейс панели."""
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Заголовок
        header_layout = QHBoxLayout()
        title_label = QLabel("Smithery MCP")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        # Кнопка обновления
        refresh_button = QToolButton()
        refresh_button.setIcon(QIcon("ui/icons/refresh.png"))  # Предполагается, что иконка существует
        refresh_button.setToolTip("Обновить список инструментов")
        refresh_button.clicked.connect(self.reload_tools)
        header_layout.addWidget(refresh_button)
        
        # Кнопка настроек
        settings_button = QToolButton()
        settings_button.setIcon(QIcon("ui/icons/settings.png"))  # Предполагается, что иконка существует
        settings_button.setToolTip("Настройки MCP")
        settings_button.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_button)
        
        main_layout.addLayout(header_layout)
        
        # Поле поиска
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск инструментов...")
        self.search_input.textChanged.connect(self.filter_tools)
        search_layout.addWidget(self.search_input)
        
        main_layout.addLayout(search_layout)
        
        # Область инструментов
        self.tools_area = QScrollArea()
        self.tools_area.setWidgetResizable(True)
        self.tools_area.setFrameShape(QFrame.NoFrame)
        self.tools_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.tools_container = QWidget()
        self.tools_layout = QVBoxLayout(self.tools_container)
        self.tools_layout.setContentsMargins(0, 0, 0, 0)
        self.tools_layout.setSpacing(2)
        self.tools_layout.addStretch(1)  # Добавляем растягивающийся элемент в конец
        
        self.tools_area.setWidget(self.tools_container)
        main_layout.addWidget(self.tools_area)
        
        # Нижняя часть - информация о текущем инструменте
        self.tool_info_frame = QFrame()
        self.tool_info_frame.setFrameShape(QFrame.StyledPanel)
        self.tool_info_layout = QVBoxLayout(self.tool_info_frame)
        
        self.tool_name_label = QLabel("Выберите инструмент")
        self.tool_name_label.setStyleSheet("font-weight: bold;")
        self.tool_info_layout.addWidget(self.tool_name_label)
        
        self.tool_description_label = QLabel("")
        self.tool_description_label.setWordWrap(True)
        self.tool_info_layout.addWidget(self.tool_description_label)
        
        main_layout.addWidget(self.tool_info_frame)
        
        # Кнопка "API ключ не настроен"
        self.api_key_warning = QPushButton("Настроить API ключ Smithery")
        self.api_key_warning.clicked.connect(self.show_api_key_dialog)
        self.api_key_warning.setStyleSheet("background-color: #FFD700; color: black;")
        self.api_key_warning.setVisible(False)  # По умолчанию скрыта
        main_layout.addWidget(self.api_key_warning)
        
        # Проверяем наличие API ключа
        try:
            client = get_smithery_client()
            if not client.api_key:
                self.api_key_warning.setVisible(True)
        except Exception as e:
            print(f"Ошибка при инициализации клиента Smithery: {e}")
    
    def load_tools(self):
        """Загружает доступные инструменты Smithery MCP."""
        try:
            # Проверяем наличие объекта интеграции перед использованием
            if not self.integration:
                print("Объект интеграции Smithery MCP не инициализирован")
                self.show_error_message("Интеграция Smithery MCP недоступна. Проверьте API-ключ и перезапустите приложение.")
                self.api_key_warning.setVisible(True)
                self.available_tools = []
                self.update_tools_ui()
                return
                
            print("Загружаем список инструментов Smithery MCP...")
            self.available_tools = self.integration.get_available_tools_for_ui()
            print(f"Загружено инструментов: {len(self.available_tools)}")
            self.update_tools_ui()
        except Exception as e:
            print(f"Ошибка при загрузке инструментов Smithery MCP: {e}")
            self.show_error_message(f"Не удалось загрузить инструменты: {str(e)}")
    
    def reload_tools(self):
        """Перезагружает список инструментов."""
        try:
            # Проверяем наличие интеграции
            if not self.integration:
                print("Объект интеграции Smithery MCP не инициализирован")
                self.show_error_message("Интеграция Smithery MCP недоступна. Проверьте настройки и перезапустите приложение.")
                # Переинициализируем интеграцию
                self.integration = get_smithery_integration()
                if not self.integration:
                    self.api_key_warning.setVisible(True)
                    return
                    
            # Получаем клиент с обновлением кеша
            client = get_smithery_client()
            if not client:
                raise ValueError("Клиент Smithery MCP не инициализирован. Проверьте API-ключ в переменной среды SMITHERY_API_KEY.")
            
            # Обновляем список серверов
            print("Обновляем список серверов Smithery MCP...")
            servers = client.list_servers(refresh=True)
            print(f"Найдено серверов: {len(servers)}")
            
            # Обновляем инструменты в адаптере
            self.available_tools = self.integration.get_available_tools_for_ui()
            print(f"Загружено инструментов: {len(self.available_tools)}")
            self.update_tools_ui()
        except Exception as e:
            print(f"Ошибка при обновлении инструментов Smithery MCP: {e}")
            self.show_error_message(f"Не удалось обновить инструменты: {str(e)}")
            # Проверяем API ключ
            import os
            api_key = os.environ.get("SMITHERY_API_KEY")
            if not api_key:
                self.show_error_message("SMITHERY_API_KEY не установлен в переменных среды. Установите ключ и перезапустите приложение.")
                # Показываем предупреждение об API ключе
                self.api_key_warning.setVisible(True)
    
    def update_tools_ui(self):
        """Обновляет UI с загруженными инструментами."""
        # Очищаем текущие инструменты
        while self.tools_layout.count() > 1:  # Оставляем только растягивающийся элемент
            item = self.tools_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Добавляем инструменты
        for tool in self.available_tools:
            tool_btn = QPushButton(tool.get('name', 'Неизвестный инструмент'))
            tool_btn.setToolTip(tool.get('description', ''))
            tool_btn.setFixedHeight(BUTTON_HEIGHT)
            tool_btn.setStyleSheet("text-align: left; padding-left: 5px;")
            tool_btn.setProperty("tool_data", tool)
            tool_btn.clicked.connect(self.on_tool_clicked)
            
            self.tools_layout.insertWidget(self.tools_layout.count() - 1, tool_btn)
    
    def filter_tools(self, text):
        """Фильтрует инструменты по тексту."""
        search_text = text.lower()
        
        for i in range(self.tools_layout.count() - 1):  # Не учитываем растягивающийся элемент
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                tool_data = widget.property("tool_data")
                
                if tool_data:
                    name = tool_data.get('name', '').lower()
                    description = tool_data.get('description', '').lower()
                    
                    if search_text in name or search_text in description:
                        widget.setVisible(True)
                    else:
                        widget.setVisible(False)
    
    def on_tool_clicked(self):
        """Обрабатывает клик по инструменту."""
        sender = self.sender()
        if sender:
            tool_data = sender.property("tool_data")
            if tool_data:
                self.select_tool(tool_data)
    
    def select_tool(self, tool_data):
        """Выбирает инструмент и обновляет UI."""
        self.current_tool = tool_data
        
        # Обновляем информацию об инструменте
        self.tool_name_label.setText(tool_data.get('name', 'Неизвестный инструмент'))
        self.tool_description_label.setText(tool_data.get('description', ''))
        
        # Отправляем сигнал о выборе инструмента
        self.tool_selected.emit(tool_data)
    
    def show_settings(self):
        """Показывает диалог настроек MCP."""
        # Здесь будет код для диалога настроек
        print("Показ диалога настроек MCP")
    
    def show_api_key_dialog(self):
        """Показывает диалог настройки API ключа."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
        import os
        
        # Создаем диалог
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройка API ключа Smithery MCP")
        dialog.setMinimumWidth(400)
        
        # Компоновка диалога
        layout = QVBoxLayout(dialog)
        
        # Пояснение
        info_label = QLabel(
            "Введите ваш API ключ Smithery MCP. "
            "Ключ будет сохранен в файле smithery_env.bat "
            "и автоматически загружен при следующем запуске."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Текущий ключ
        current_key = os.environ.get("SMITHERY_API_KEY", "")
        
        # Поле ввода ключа
        key_label = QLabel("API ключ:")
        layout.addWidget(key_label)
        
        key_input = QLineEdit(current_key)
        key_input.setPlaceholderText("Введите ваш API ключ Smithery MCP")
        layout.addWidget(key_input)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        save_button = QPushButton("Сохранить")
        save_button.setDefault(True)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        layout.addLayout(buttons_layout)
        
        # Обработчики событий
        cancel_button.clicked.connect(dialog.reject)
        
        def save_api_key():
            new_key = key_input.text().strip()
            if not new_key:
                self.show_error_message("Введите действующий API ключ Smithery MCP")
                return
            
            try:
                # Сохраняем в файл smithery_env.bat
                smithery_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "smithery_env.bat")
                
                with open(smithery_env_path, 'w', encoding='utf-8') as f:
                    f.write("@echo off\n")
                    f.write("REM Настройки для Smithery MCP\n")
                    f.write(f"SET SMITHERY_API_KEY={new_key}\n\n")
                    f.write("echo API-ключ Smithery установлен\n")
                
                # Устанавливаем ключ в текущем сеансе
                os.environ["SMITHERY_API_KEY"] = new_key
                
                # Переинициализируем клиент и интеграцию
                from .smithery_client import get_smithery_client
                from .smithery_integration import get_smithery_integration
                from .smithery_tools import get_smithery_tools_adapter
                
                # Скрываем предупреждение о ключе
                self.api_key_warning.setVisible(False)
                
                # Перезагружаем инструменты
                self.reload_tools()
                
                dialog.accept()
                self.show_error_message(f"API ключ Smithery MCP успешно сохранен! Инструменты будут доступны при следующем запуске приложения.")
                
            except Exception as e:
                self.show_error_message(f"Ошибка при сохранении API ключа: {str(e)}")
        
        save_button.clicked.connect(save_api_key)
        
        # Показываем диалог
        dialog.exec_()
    
    def show_error_message(self, message):
        """Показывает сообщение об ошибке."""
        self.tool_name_label.setText("Ошибка")
        self.tool_description_label.setText(message)


# Для тестирования
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    window = SmitheryMcpPanel()
    window.resize(300, 500)
    window.show()
    
    sys.exit(app.exec())
