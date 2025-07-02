"""
Terminal Widget Component для GopiAI Standalone Interface
======================================================

Виджет терминала с вкладками.
"""

import subprocess
import threading
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QTextEdit
from PySide6.QtCore import QTimer


class TerminalWidget(QWidget):
    """Виджет терминала с вкладками"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("terminalWidget")
        self._setup_icon_system()
        self._setup_ui()

    def _setup_icon_system(self):
        """Настройка системы иконок"""
        try:
            from .icon_file_system_model import UniversalIconManager
            self.icon_manager = UniversalIconManager()
            print("[OK] Terminal: Загружена система иконок UniversalIconManager")
        except ImportError:
            self.icon_manager = None
            print("[WARNING] Terminal: Не удалось загрузить UniversalIconManager")

    def _setup_ui(self):
        """Настройка интерфейса терминала"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Заголовок с кнопками
        header_layout = QHBoxLayout()
        header_label = QLabel("Терминал")
        header_label.setObjectName("panelHeader")
        
        # Добавляем иконку терминала
        if self.icon_manager:
            try:
                terminal_icon = self.icon_manager.get_icon("terminal")
                if terminal_icon and not terminal_icon.isNull():
                    header_label.setPixmap(terminal_icon.pixmap(16, 16))
            except Exception as e:
                print(f"[WARNING] Ошибка загрузки иконки терминала: {e}")

        new_tab_btn = QPushButton("Новая вкладка")
        new_tab_btn.setFixedHeight(25)
        new_tab_btn.clicked.connect(self._add_terminal_tab)
        
        # Добавляем иконку плюса к кнопке
        if self.icon_manager:
            try:
                plus_icon = self.icon_manager.get_icon("plus")
                if plus_icon and not plus_icon.isNull():
                    new_tab_btn.setIcon(plus_icon)
            except Exception as e:
                print(f"[WARNING] Ошибка загрузки иконки плюса: {e}")
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(new_tab_btn)
        layout.addLayout(header_layout)
        
        # Вкладки терминала
        self.terminal_tabs = QTabWidget()
        self.terminal_tabs.setTabsClosable(True)
        self.terminal_tabs.tabCloseRequested.connect(self._close_terminal_tab)
        
        # Добавляем первую вкладку
        self._add_terminal_tab()
        layout.addWidget(self.terminal_tabs)

    def _add_terminal_tab(self):
        """Добавление новой вкладки терминала"""
        terminal = QTextEdit()
        terminal.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border: none;
            }
        """)
        
        terminal.setPlainText("""
Microsoft Windows PowerShell
Copyright (C) Microsoft Corporation. Все права защищены.

PS C:\\Users\\crazy\\GOPI_AI_MODULES> # Готов к работе!
PS C:\\Users\\crazy\\GOPI_AI_MODULES> 
        """)
        
        tab_index = self.terminal_tabs.addTab(terminal, f"Терминал {self.terminal_tabs.count() + 1}")
        self.terminal_tabs.setCurrentIndex(tab_index)

    def _close_terminal_tab(self, index):
        """Закрытие вкладки терминала"""
        if self.terminal_tabs.count() > 1:
            self.terminal_tabs.removeTab(index)

    def get_current_terminal(self):
        """Получение текущего терминала"""
        return self.terminal_tabs.currentWidget()

    def add_new_terminal(self, name: Optional[str] = None):
        """Добавление нового терминала"""
        if name is None:
            name = f"Терминал {self.terminal_tabs.count() + 1}"
        self._add_terminal_tab()
        current_index = self.terminal_tabs.currentIndex()
        self.terminal_tabs.setTabText(current_index, name)

    def execute_command(self, command: str):
        """Выполнение команды в текущем терминале"""
        terminal = self.get_current_terminal()
        if terminal and isinstance(terminal, QTextEdit):
            current_text = terminal.toPlainText()
            
            # Добавляем команду в терминал
            terminal.setPlainText(f"{current_text}\nPS C:\\Users\\crazy\\GOPI_AI_MODULES> {command}")
            
            # Выполняем команду в отдельном потоке
            def run_command():
                try:
                    # Выполняем команду через PowerShell
                    result = subprocess.run(
                        ["powershell", "-Command", command],
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd="C:\\Users\\crazy\\GOPI_AI_MODULES"
                    )
                    
                    output = result.stdout if result.stdout else ""
                    error = result.stderr if result.stderr else ""
                    
                    # Обновляем терминал в главном потоке
                    def update_terminal():
                        current_text = terminal.toPlainText()
                        if output:
                            terminal.setPlainText(f"{current_text}\n{output}")
                        if error:
                            terminal.setPlainText(f"{terminal.toPlainText()}\n{error}")
                        
                        # Добавляем новую строку приглашения
                        terminal.setPlainText(f"{terminal.toPlainText()}\nPS C:\\Users\\crazy\\GOPI_AI_MODULES> ")
                        
                        # Прокручиваем вниз
                        cursor = terminal.textCursor()
                        cursor.movePosition(cursor.MoveOperation.End)
                        terminal.setTextCursor(cursor)
                    
                    # Используем QTimer для обновления UI в главном потоке
                    QTimer.singleShot(0, update_terminal)
                    
                except subprocess.TimeoutExpired:
                    def show_timeout():
                        current_text = terminal.toPlainText()
                        terminal.setPlainText(f"{current_text}\nОшибка: Команда превысила время ожидания (30 сек)\nPS C:\\Users\\crazy\\GOPI_AI_MODULES> ")
                    QTimer.singleShot(0, show_timeout)
                    
                except Exception as e:
                    def show_error():
                        current_text = terminal.toPlainText()
                        terminal.setPlainText(f"{current_text}\nОшибка: {str(e)}\nPS C:\\Users\\crazy\\GOPI_AI_MODULES> ")
                    QTimer.singleShot(0, show_error)
            
            # Запускаем команду в отдельном потоке
            thread = threading.Thread(target=run_command, daemon=True)
            thread.start()
