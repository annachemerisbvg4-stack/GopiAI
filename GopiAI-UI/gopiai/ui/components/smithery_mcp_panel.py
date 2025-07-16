"""
Панель инструментов Smithery MCP для UI

Модуль предоставляет компоненты для отображения и управления
инструментами Smithery MCP в пользовательском интерфейсе.
"""

import os
import json
import sys
import asyncio
from typing import Dict, List, Any, Optional, Callable

from PySide6.QtCore import Qt, Signal, Slot, QObject, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QSizePolicy, QToolButton, QLineEdit,
    QComboBox, QCheckBox, QSpacerItem
)
from PySide6.QtGui import QIcon, QFont

# Добавляем путь к GopiAI-CrewAI для импорта модулей
crewai_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'GopiAI-CrewAI'))
if os.path.exists(crewai_path):
    sys.path.append(crewai_path)

try:
    # Импортируем MCPToolsManager для работы с MCP серверами
    from tools.gopiai_integration.mcp_integration import MCPToolsManager
except ImportError as e:
    print(f"[ERROR] Ошибка импорта модулей MCP: {e}")
    MCPToolsManager = None  # Заглушка для предотвращения ошибок

# Константы для UI
BUTTON_HEIGHT = 30
TOOL_BUTTON_SIZE = 24
MIN_PANEL_WIDTH = 200
MAX_PANEL_WIDTH = 350  # Увеличено для соответствия с шириной side_panel

class SmitheryMcpPanel(QWidget):
    """
    Панель для отображения и управления инструментами Smithery MCP.
    """
    
    # Сигналы
    tool_selected = Signal(dict)  # Сигнализирует о выборе инструмента
    
    def __init__(self, parent=None):
        print("[Создание] SmitheryMcpPanel: Создание объекта панели...")
        super().__init__(parent)
        self.api_key = None
        self.available_tools = []
        self.tools_loading = False
        self.tools_manager = None  # Менеджер инструментов MCP
        self.load_tools_timer = None
        self.setup_ui()
        
        # Вызываем метод инициализации после создания UI
        print("[Инициализация] SmitheryMcpPanel: Вызываем метод initialize()...")
        self.initialize()
        
        self.current_tool = None
        self.tools_loading = False  # Флаг загрузки инструментов
        self.api_key_warning = None  # Предупреждение о ключе API
        self.loading_label = None    # Метка загрузки
        self.spinner_movie = None    # Анимация загрузки
        
        self.setup_ui()
        # self.load_tools()  # Загрузка будет вызвана из setup_ui
    
    def setup_ui(self):
        """Настраивает пользовательский интерфейс панели."""
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Создаем заголовок панели
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Заголовок панели
        title_label = QLabel("MCP Tools")
        title_label.setStyleSheet("font-weight: bold; color: #f8f8f2;")
        header_layout.addWidget(title_label)
        
        # Кнопка обновления списка инструментов
        refresh_btn = QPushButton()
        refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_btn.setToolTip("Обновить список инструментов")
        refresh_btn.setMaximumWidth(30)
        refresh_btn.clicked.connect(self.reload_tools)
        header_layout.addWidget(refresh_btn)
        
        layout.addWidget(header_frame)
        
        # Создаем область поиска
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 0, 10, 0)
        search_layout.setSpacing(5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск инструментов...")
        self.search_input.textChanged.connect(self.filter_tools)
        search_layout.addWidget(self.search_input)
        
        layout.addWidget(search_frame)
        
        # Создаем анимацию загрузки и метку
        loading_frame = QFrame()
        loading_layout = QHBoxLayout(loading_frame)
        loading_layout.setContentsMargins(10, 5, 10, 5)
        loading_layout.setSpacing(5)
        
        # Анимация загрузки (просто текст для простоты)
        self.loading_label = QLabel("Загрузка инструментов...")
        self.loading_label.setStyleSheet("color: #cfcfd1;")
        self.loading_label.hide()  # Изначально скрыта
        loading_layout.addWidget(self.loading_label)
        
        # Предупреждение о ключе API (если нужно)
        self.api_key_warning = QLabel("API ключ не настроен")
        self.api_key_warning.setStyleSheet("color: #ff6e6e; font-size: 10px;")
        self.api_key_warning.setVisible(False)  # Изначально скрыто
        loading_layout.addWidget(self.api_key_warning)
        
        layout.addWidget(loading_frame)
        
        # Создаем область для списка инструментов
        tools_scroll_area = QScrollArea()
        tools_scroll_area.setWidgetResizable(True)
        tools_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tools_content = QWidget()
        self.tools_layout = QVBoxLayout(tools_content)
        self.tools_layout.setContentsMargins(5, 5, 5, 5)
        self.tools_layout.setSpacing(5)
        tools_scroll_area.setWidget(tools_content)
        
        layout.addWidget(tools_scroll_area, 1)
        
        # Создаем область для информации об инструменте
        tool_info_frame = QFrame()
        tool_info_layout = QVBoxLayout(tool_info_frame)
        tool_info_layout.setContentsMargins(10, 5, 10, 5)
        
        # Название инструмента
        self.tool_name_label = QLabel("Выберите инструмент")
        self.tool_name_label.setStyleSheet("font-weight: bold; color: #f8f8f2;")
        tool_info_layout.addWidget(self.tool_name_label)
        
        # Описание инструмента
        self.tool_description_label = QLabel("")
        self.tool_description_label.setStyleSheet("color: #cfcfd1; font-size: 10px;")
        self.tool_description_label.setWordWrap(True)
        tool_info_layout.addWidget(self.tool_description_label)
        
        layout.addWidget(tool_info_frame)
        
        # Создаем футер с информацией
        footer_frame = QFrame()
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(10, 5, 10, 5)
        
        # Информация о Smithery
        info_label = QLabel("Powered by Smithery MCP")
        info_label.setStyleSheet("color: #cfcfd1; font-size: 10px;")
        footer_layout.addWidget(info_label)
        
        layout.addWidget(footer_frame)
        
        # Запускаем загрузку инструментов после настройки UI
        # Используем QTimer для запуска загрузки в следующем цикле событий
        QTimer.singleShot(100, self.load_tools)
    
    def initialize(self):
        """Инициализирует панель и подключает сервисы MCP."""
        try:
            print("[MCP] Начало инициализации MCP панели...")
            
            # Пытаемся создать менеджер инструментов MCP, если модуль доступен
            self.tools_manager = MCPToolsManager() if MCPToolsManager else None
            
            # Определяем список серверов для работы с MCP
            # Эти URL используются для создания инструментов в UI (ленивая загрузка)
            servers = [
                "https://server.smithery.ai/@luminati-io/brightdata-mcp/mcp",
                "https://server.smithery.ai/@bytedance/mcp-server-browser/mcp",
                "https://server.smithery.ai/@flight505/mcp-think-tank/mcp",
                "https://server.smithery.ai/@FutureAtoms/agentic-control-framework/mcp",
                "https://server.smithery.ai/@mem0ai/mem0-memory-mcp/mcp",
                "https://server.smithery.ai/@wonderwhy-er/desktop-commander/mcp",
                "https://server.smithery.ai/@JigsawStack/vocr/mcp"
            ]
            
            # Создаем объект интеграции с серверами
            self.integration = {
                "servers": servers
            }
            
            print("[MCP] Объект интеграции MCP успешно создан")
            
            # Загружаем инструменты MCP при отображении панели
            self.tools_loading = False
            
            # Заполняем доступные инструменты на основе серверов (ленивая загрузка)
            self.available_tools = [
                {
                    "id": f"mcp_tool_{i}",
                    "name": f"MCP: {server.split('@')[1].split('/')[0] if '@' in server else server.split('/')[-2]}",
                    "description": f"Инструменты MCP с сервера {server.split('@')[1].split('/')[0] if '@' in server else server.split('/')[-2]}",
                    "server_url": server
                }
                for i, server in enumerate(servers, 1)
            ]
            
            # Обновляем UI с полученными инструментами
            print(f"[MCP] Загружено {len(self.available_tools)} инструментов MCP")
            self.update_tools_ui()
            
            print("[MCP] Инициализация MCP панели завершена")
            
        except Exception as e:
            print(f"Ошибка инициализации Smithery MCP панели: {e}")
            import traceback
            traceback.print_exc()
    
    def load_tools(self):
        """Загружает доступные инструменты Smithery MCP по принципу ленивой загрузки."""
        try:
            # Проверяем уже идет загрузка или виджет невидим
            if self.tools_loading or not self.isVisible():
                return
                
            self.tools_loading = True
            if self.loading_label:
                self.loading_label.setText("Загрузка инструментов...")
                self.loading_label.show()
            
            print("Загружаем список инструментов Smithery MCP (ленивая загрузка)...")
            
            # В режиме ленивой загрузки создаем инструменты только на основе списка серверов
            # Этот метод работает без API-ключа и не пытается подключаться к серверам
            if hasattr(self, 'integration') and self.integration and "servers" in self.integration:
                servers = self.integration["servers"]
                
                # Создаем инструменты по серверам (предоставляем базовую информацию)
                self.available_tools = []
                for i, server_url in enumerate(servers, 1):
                    # Извлекаем имя сервера из URL
                    server_name = server_url.split('@')[1].split('/')[0] if '@' in server_url else server_url.split('/')[-2]
                    
                    # Извлекаем тип сервера для группировки инструментов
                    server_type = server_name.split('-')[0] if '-' in server_name else server_name
                    
                    # Добавляем основной инструмент сервера
                    self.available_tools.append({
                        "id": f"mcp_tool_{i}",
                        "name": f"{server_name}",
                        "description": f"Инструменты MCP с сервера {server_name}",
                        "server_url": server_url,
                        "type": server_type
                    })
                    
                    # Добавляем дополнительные инструменты для крупных серверов
                    if "browser" in server_name.lower():
                        self.available_tools.append({
                            "id": f"mcp_browser_{i}",
                            "name": f"Браузер MCP",
                            "description": f"Управление браузером через MCP",
                            "server_url": server_url,
                            "type": "browser"
                        })
                    
                    if "mem" in server_name.lower():
                        self.available_tools.append({
                            "id": f"mcp_memory_{i}",
                            "name": f"Память MCP",
                            "description": f"Работа с долгосрочной памятью через MCP",
                            "server_url": server_url,
                            "type": "memory"
                        })
                
                print(f"Загружено {len(self.available_tools)} инструментов MCP (ленивая загрузка)")
                
                # Обновляем UI с полученными инструментами
                self.update_tools_ui()
            else:
                print("Нет доступных серверов MCP для загрузки инструментов")
                
        except Exception as e:
            print(f"Ошибка при загрузке инструментов Smithery MCP: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.tools_loading = False
            if hasattr(self, 'loading_label') and self.loading_label:
                self.loading_label.hide()
        
    def reload_tools(self):
        """Перезагружает список инструментов (ленивая загрузка)."""
        try:
            # Проверяем наличие интеграции
            if not hasattr(self, 'integration') or not self.integration:
                print("Выполняется повторная инициализация интеграции MCP...")
                # Создаем базовый объект интеграции для ленивой загрузки
                self.integration = {
                    "servers": [
                        "https://server.smithery.ai/@luminati-io/brightdata-mcp/mcp",
                        "https://server.smithery.ai/@bytedance/mcp-server-browser/mcp",
                        "https://server.smithery.ai/@flight505/mcp-think-tank/mcp",
                        "https://server.smithery.ai/@FutureAtoms/agentic-control-framework/mcp",
                        "https://server.smithery.ai/@mem0ai/mem0-memory-mcp/mcp",
                        "https://server.smithery.ai/@wonderwhy-er/desktop-commander/mcp",
                        "https://server.smithery.ai/@JigsawStack/vocr/mcp"
                    ],
                    "get_available_tools_for_ui": lambda: []
                }
                
                # Обязательно устанавливаем также атрибут smithery_integration для совместимости
                self.smithery_integration = self.integration
                
            # Загружаем инструменты с использованием ленивой загрузки
            print("Перезагружаем список инструментов MCP (ленивая загрузка)...")
            self.load_tools()  # Переиспользуем логику load_tools для ленивой загрузки
            
        except Exception as e:
            print(f"Ошибка при обновлении инструментов Smithery MCP: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Не удалось обновить инструменты: {str(e)}")
            # Скрываем предупреждение об API ключе, так как оно не требуется для ленивой загрузки
            if hasattr(self, 'api_key_warning') and self.api_key_warning:
                self.api_key_warning.setVisible(False)
    
    def update_tools_ui(self):
        """Обновляет UI с загруженными инструментами."""
        # Очищаем текущие элементы
        for i in reversed(range(self.tools_layout.count())):
            widget = self.tools_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Добавляем карточки для каждого инструмента
        for tool in self.available_tools:
            try:
                # Создаем карточку инструмента
                tool_card = QFrame()
                tool_card.setStyleSheet("""
                    QFrame {
                        background-color: rgba(60, 63, 80, 0.5);
                        border-radius: 8px;
                        padding: 4px;
                    }
                    QFrame:hover {
                        background-color: rgba(80, 83, 100, 0.7);
                    }
                """)
                
                card_layout = QVBoxLayout(tool_card)
                card_layout.setContentsMargins(10, 5, 10, 5)
                card_layout.setSpacing(2)
                
                # Заголовок инструмента
                title = QLabel(tool["name"])
                title.setStyleSheet("font-weight: bold; color: #f8f8f2;")
                card_layout.addWidget(title)
                
                # Описание инструмента
                description = QLabel(tool["description"][:100] + "..." if len(tool["description"]) > 100 else tool["description"])
                description.setStyleSheet("color: #cfcfd1; font-size: 10px;")
                description.setWordWrap(True)
                card_layout.addWidget(description)
                
                # Делаем карточку кликабельной
                tool_card.mousePressEvent = lambda event, t=tool: self.select_tool(t)
                
                self.tools_layout.addWidget(tool_card)
            except Exception as e:
                print(f"Ошибка при создании карточки инструмента {tool.get('name', 'unknown')}: {e}")
        
        # Добавляем растягивающийся элемент в конце
        self.tools_layout.addStretch()
    
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
        # Запоминаем выбранный инструмент
        self.current_tool = tool_data
        
        # Эмитим сигнал о выборе инструмента
        # Информация об инструменте уже в нужном формате
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
