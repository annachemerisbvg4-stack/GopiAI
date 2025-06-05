"""
Terminal Widget Component для GopiAI Standalone Interface
======================================================

Виджет терминала с вкладками.
"""

from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QTextEdit


class TerminalWidget(QWidget):
    """Виджет терминала с вкладками"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("terminalWidget")
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса терминала"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Заголовок с кнопками
        header_layout = QHBoxLayout()
        header_label = QLabel("💻 Терминал")
        header_label.setObjectName("panelHeader")
        
        new_tab_btn = QPushButton("+ Новая вкладка")
        new_tab_btn.setFixedHeight(25)
        new_tab_btn.clicked.connect(self._add_terminal_tab)
        
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
                background-color: #1a1a1a;
                color: #00ff00;
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
        self.terminal_tabs.setTabText(current_index, name)

    def execute_command(self, command: str):
        """Выполнение команды в текущем терминале (заглушка)"""
        terminal = self.get_current_terminal()
        if terminal and isinstance(terminal, QTextEdit):
            current_text = terminal.toPlainText()
            new_text = f"{current_text}\nPS C:\\Users\\crazy\\GOPI_AI_MODULES> {command}\n# Команда выполнена (заглушка)\nPS C:\\Users\\crazy\\GOPI_AI_MODULES> "
            terminal.setPlainText(new_text)
            
            # Прокручиваем вниз
            cursor = terminal.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            terminal.setTextCursor(cursor)
