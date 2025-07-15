"""
MCP Panel - компонент UI для работы с MCP инструментами

Этот модуль реализует панель для взаимодействия с инструментами MCP (Model Context Protocol)
в пользовательском интерфейсе GopiAI.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QDialog, QLineEdit, QMessageBox,
    QTabWidget, QComboBox, QTextEdit, QGroupBox, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize

from tools.gopiai_integration.mcp_integration import get_mcp_tools_manager, MCPToolsManager

logger = logging.getLogger(__name__)

class MCPPanel(QWidget):
    """
    Панель для работы с инструментами MCP в интерфейсе GopiAI.
    
    Позволяет:
    - Просматривать доступные MCP серверы и инструменты
    - Подключаться и отключаться от MCP серверов
    - Запускать инструменты MCP
    - Настраивать API ключи
    """
    
    tool_selected = pyqtSignal(dict)  # Сигнал о выборе инструмента
    
    def __init__(self, parent=None):
        """Инициализация панели MCP."""
        super().__init__(parent)
        self.mcp_manager = get_mcp_tools_manager()
        self.init_ui()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        # Главный layout
        layout = QVBoxLayout()
        
        # Заголовок и кнопки управления
        header_layout = QHBoxLayout()
        
        title_label = QLabel("<h2>MCP Инструменты</h2>")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.reload_tools)
        header_layout.addWidget(self.refresh_button)
        
        self.settings_button = QPushButton("API Ключ")
        self.settings_button.clicked.connect(self.show_api_key_dialog)
        header_layout.addWidget(self.settings_button)
        
        layout.addLayout(header_layout)
        
        # Разделитель на две панели
        splitter = QSplitter(Qt.Vertical)
        
        # Верхняя панель с серверами и инструментами
        servers_tools_widget = QWidget()
        servers_tools_layout = QVBoxLayout(servers_tools_widget)
        
        # Вкладки для разных серверов
        self.servers_tabs = QTabWidget()
        servers_tools_layout.addWidget(self.servers_tabs)
        
        # Нижняя панель для выполнения инструмента
        tool_execution_group = QGroupBox("Выполнение инструмента")
        tool_execution_layout = QVBoxLayout(tool_execution_group)
        
        # Выбранный инструмент
        tool_selection_layout = QHBoxLayout()
        tool_selection_layout.addWidget(QLabel("Инструмент:"))
        self.selected_tool_label = QLabel("Не выбран")
        tool_selection_layout.addWidget(self.selected_tool_label)
        tool_execution_layout.addLayout(tool_selection_layout)
        
        # Параметры инструмента
        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel("Параметры:"))
        self.params_editor = QTextEdit()
        self.params_editor.setPlaceholderText("Введите параметры в формате JSON")
        params_layout.addWidget(self.params_editor)
        tool_execution_layout.addLayout(params_layout)
        
        # Кнопка выполнения
        execute_layout = QHBoxLayout()
        execute_layout.addStretch()
        self.execute_button = QPushButton("Выполнить")
        self.execute_button.clicked.connect(self.execute_tool)
        self.execute_button.setEnabled(False)
        execute_layout.addWidget(self.execute_button)
        tool_execution_layout.addLayout(execute_layout)
        
        # Результат выполнения
        result_layout = QVBoxLayout()
        result_layout.addWidget(QLabel("Результат:"))
        self.result_editor = QTextEdit()
        self.result_editor.setReadOnly(True)
        result_layout.addWidget(self.result_editor)
        tool_execution_layout.addLayout(result_layout)
        
        splitter.addWidget(servers_tools_widget)
        splitter.addWidget(tool_execution_group)
        
        # Устанавливаем соотношение размеров панелей
        splitter.setSizes([300, 400])
        
        layout.addWidget(splitter)
        
        self.setLayout(layout)
        
        # Загружаем инструменты
        self.reload_tools()
    
    def reload_tools(self):
        """Загружает и отображает доступные MCP инструменты."""
        # Очищаем вкладки
        self.servers_tabs.clear()
        
        if not self.mcp_manager:
            QMessageBox.warning(
                self, 
                "Ошибка MCP", 
                "Не удалось инициализировать менеджер MCP инструментов. Проверьте API ключ."
            )
            return
        
        # Подключаемся ко всем серверам и получаем инструменты
        try:
            self.mcp_manager.connect_to_all_servers()
            
            # Для каждого сервера создаем вкладку с его инструментами
            for server_name in self.mcp_manager.connected_servers:
                # Создаем виджет для инструментов сервера
                server_tab = QWidget()
                server_layout = QVBoxLayout(server_tab)
                
                # Список инструментов
                tools_list = QListWidget()
                tools_list.itemClicked.connect(self.on_tool_clicked)
                server_layout.addWidget(tools_list)
                
                # Добавляем инструменты в список
                server_tools = self.mcp_manager.tools_by_server.get(server_name, [])
                for tool in server_tools:
                    item = QListWidgetItem(f"{tool.name}: {tool.description}")
                    # Сохраняем информацию об инструменте в пользовательских данных элемента списка
                    item.setData(Qt.UserRole, {
                        "server": server_name,
                        "name": tool.name,
                        "description": tool.description,
                        "tool": tool
                    })
                    tools_list.addItem(item)
                
                # Добавляем вкладку для сервера
                self.servers_tabs.addTab(server_tab, server_name)
            
            if not self.mcp_manager.connected_servers:
                QMessageBox.information(
                    self, 
                    "MCP Серверы", 
                    "Не удалось подключиться ни к одному MCP серверу. Проверьте API ключ и доступность серверов."
                )
        except Exception as e:
            logger.error(f"Ошибка при загрузке MCP инструментов: {e}")
            QMessageBox.critical(
                self, 
                "Ошибка MCP", 
                f"Произошла ошибка при загрузке MCP инструментов: {e}"
            )
    
    def on_tool_clicked(self, item):
        """Обрабатывает клик по инструменту в списке."""
        tool_data = item.data(Qt.UserRole)
        if not tool_data:
            return
        
        # Отображаем выбранный инструмент
        self.selected_tool_label.setText(f"{tool_data['name']} ({tool_data['server']})")
        
        # Включаем кнопку выполнения
        self.execute_button.setEnabled(True)
        
        # Подготавливаем шаблон параметров
        self.params_editor.setText("{}")
        
        # Очищаем результат предыдущего выполнения
        self.result_editor.clear()
        
        # Отправляем сигнал о выборе инструмента
        self.tool_selected.emit(tool_data)
    
    def execute_tool(self):
        """Выполняет выбранный инструмент с указанными параметрами."""
        # Получаем выбранную вкладку
        current_tab_index = self.servers_tabs.currentIndex()
        if current_tab_index < 0:
            return
        
        server_name = self.servers_tabs.tabText(current_tab_index)
        
        # Получаем выбранный инструмент
        tools_list = self.servers_tabs.currentWidget().findChild(QListWidget)
        if not tools_list or not tools_list.currentItem():
            return
        
        tool_data = tools_list.currentItem().data(Qt.UserRole)
        if not tool_data:
            return
        
        # Получаем параметры
        try:
            import json
            params_text = self.params_editor.toPlainText()
            params = json.loads(params_text) if params_text.strip() else {}
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self,
                "Ошибка параметров",
                f"Некорректный формат JSON: {e}"
            )
            return
        
        # Выполняем инструмент
        try:
            # Получаем инструмент и вызываем его
            tool = tool_data["tool"]
            result = tool(**params)
            
            # Отображаем результат
            self.result_editor.setText(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Ошибка при выполнении MCP инструмента: {e}")
            QMessageBox.critical(
                self,
                "Ошибка выполнения",
                f"Произошла ошибка при выполнении инструмента: {e}"
            )
            self.result_editor.setText(f"Ошибка: {e}")
    
    def show_api_key_dialog(self):
        """Показывает диалог для ввода API ключа Smithery."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Smithery API Ключ")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Введите ваш Smithery API ключ:"))
        
        api_key_input = QLineEdit()
        current_key = os.environ.get("SMITHERY_API_KEY", "")
        api_key_input.setText(current_key)
        layout.addWidget(api_key_input)
        
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        
        layout.addLayout(buttons_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            new_key = api_key_input.text().strip()
            if new_key != current_key:
                # Сохраняем ключ в переменной среды
                os.environ["SMITHERY_API_KEY"] = new_key
                
                # Сохраняем ключ в файле для будущих запусков
                try:
                    env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                               "config", "smithery_env.bat")
                    
                    # Создаем директорию, если она не существует
                    os.makedirs(os.path.dirname(env_file_path), exist_ok=True)
                    
                    with open(env_file_path, 'w') as f:
                        f.write(f"@echo off\nset SMITHERY_API_KEY={new_key}\n")
                    
                    logger.info(f"API ключ успешно сохранен в {env_file_path}")
                except Exception as e:
                    logger.error(f"Ошибка при сохранении API ключа: {e}")
                
                # Пересоздаем менеджер MCP и перезагружаем инструменты
                global _mcp_tools_manager_instance
                _mcp_tools_manager_instance = None
                self.mcp_manager = get_mcp_tools_manager()
                self.reload_tools()
                
                QMessageBox.information(
                    self,
                    "API Ключ",
                    "API ключ успешно обновлен."
                )
