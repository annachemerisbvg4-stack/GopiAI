"""
Terminal Widget Component для GopiAI Standalone Interface
======================================================

Интерактивный виджет терминала с вкладками и поддержкой выполнения команд.
"""

import subprocess
import threading
import os
import sys
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QTextEdit, QLineEdit
from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtGui import QTextCursor, QFont


class InteractiveTerminal(QTextEdit):
    """Интерактивный терминал с поддержкой ввода команд"""
    
    command_executed = Signal(str)  # Сигнал для выполненной команды
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("interactiveTerminal")
        
        # Настройка шрифта и стиля
        font = QFont("Consolas", 10)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Настройка стиля
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
            }
        """)
        
        # Инициализация переменных
        self.current_directory = os.getcwd()
        self.command_history = []
        self.history_index = -1
        self.prompt = f"PS {self.current_directory}> "
        
        # Показываем приветствие
        self._show_welcome()
        self._show_prompt()
        
    def _show_welcome(self):
        """Показывает приветственное сообщение"""
        welcome_text = f"""
GopiAI Interactive Terminal
Copyright (C) 2025 GopiAI. Все права защищены.

Текущая директория: {self.current_directory}
Введите 'help' для получения справки.

"""
        self.append(welcome_text)
        
    def _show_prompt(self):
        """Показывает приглашение командной строки"""
        self.insertPlainText(self.prompt)
        self.moveCursor(QTextCursor.End)
        
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self._execute_current_command()
            return  # Add this to prevent default behavior
        elif event.key() == Qt.Key_Up:
            self._navigate_history(-1)
        elif event.key() == Qt.Key_Down:
            self._navigate_history(1)
        elif event.key() == Qt.Key_Backspace:
            # Предотвращаем удаление приглашения
            cursor = self.textCursor()
            if cursor.position() > self._get_prompt_end_position():
                super().keyPressEvent(event)
        else:
            # Проверяем, что курсор находится в области ввода
            cursor = self.textCursor()
            if cursor.position() >= self._get_prompt_end_position():
                super().keyPressEvent(event)
            else:
                # Перемещаем курсор в конец
                self.moveCursor(QTextCursor.End)
                super().keyPressEvent(event)
                
    def _get_prompt_end_position(self):
        """Получает позицию конца приглашения"""
        text = self.toPlainText()
        last_prompt_pos = text.rfind(self.prompt)
        if last_prompt_pos != -1:
            return last_prompt_pos + len(self.prompt)
        return len(text)
        
    def _get_current_command(self):
        """Получает текущую команду"""
        text = self.toPlainText()
        prompt_end = self._get_prompt_end_position()
        return text[prompt_end:].strip()
        
    def _execute_current_command(self):
        """Выполняет текущую команду"""
        command = self._get_current_command()
        if command:
            self.command_history.append(command)
            self.history_index = len(self.command_history)
            
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText('\n')  # Insert newline
        self.setTextCursor(cursor)
        
        if command:
            self._execute_command(command)
        else:
            self._show_prompt()
            
    def _navigate_history(self, direction):
        """Навигация по истории команд"""
        if not self.command_history:
            return
            
        new_index = self.history_index + direction
        if 0 <= new_index < len(self.command_history):
            self.history_index = new_index
            command = self.command_history[self.history_index]
            
            # Заменяем текущую команду
            cursor = self.textCursor()
            cursor.setPosition(self._get_prompt_end_position())
            cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertText(command)
            
    def _execute_command(self, command, timeout=None):
        """Выполняет команду"""
        # Обработка встроенных команд
        if command.lower() in ['clear', 'cls']:
            self.clear()
            self._show_welcome()
            self._show_prompt()
            return
        elif command.lower() == 'help':
            self._show_help()
            self._show_prompt()
            return
        elif command.lower().startswith('cd '):
            self._change_directory(command[3:].strip())
            self._show_prompt()
            return
            
        # Выполняем команду в отдельном потоке
        def run_command():
            try:
                # Определяем операционную систему
                if sys.platform == "win32":
                    # Windows: используем PowerShell
                    result = subprocess.run(
                        ["powershell", "-Command", command],
                        capture_output=True,
                        text=True,
                        cwd=self.current_directory,
                        timeout=timeout
                    )
                else:
                    # Unix/Linux: используем bash
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        cwd=self.current_directory,
                        timeout=timeout
                    )
                
                output = result.stdout if result.stdout else ""
                error = result.stderr if result.stderr else ""
                
                # Обновляем терминал в главном потоке
                def update_terminal():
                    if output:
                        self.append(output.rstrip())
                    if error:
                        self.append(f"[ERROR] {error.rstrip()}")
                        if 'input' in error.lower():
                            self.append("[WARNING] Command requires interactive input, which is not supported.")
                    self._show_prompt()
                    
                QTimer.singleShot(0, update_terminal)
                
            except subprocess.TimeoutExpired:
                def show_timeout():
                    self.append("[ERROR] Команда превысила время ожидания (30 сек)")
                    self._show_prompt()
                QTimer.singleShot(0, show_timeout)
                
            except Exception as e:
                def show_error():
                    self.append(f"[ERROR] {str(e)}")
                    self._show_prompt()
                QTimer.singleShot(0, show_error)
        
        # Запускаем команду в отдельном потоке
        thread = threading.Thread(target=run_command, daemon=True)
        thread.start()
        
        # Отправляем сигнал о выполнении команды
        self.command_executed.emit(command)
        
    def _change_directory(self, path):
        """Смена директории"""
        try:
            if path == '..':
                new_path = os.path.dirname(self.current_directory)
            elif os.path.isabs(path):
                new_path = path
            else:
                new_path = os.path.join(self.current_directory, path)
                
            if os.path.exists(new_path) and os.path.isdir(new_path):
                self.current_directory = os.path.abspath(new_path)
                self.prompt = f"PS {self.current_directory}> "
            else:
                self.append(f"[ERROR] Папка не найдена: {path}")
        except Exception as e:
            self.append(f"[ERROR] Ошибка смены директории: {str(e)}")
            
    def _show_help(self):
        """Показывает справку"""
        help_text = """
Доступные команды:
  help          - Показать эту справку
  clear, cls    - Очистить экран
  cd <path>     - Сменить директорию
  ↑/↓           - Навигация по истории команд
  
Любые другие команды будут выполнены через системную оболочку.
"""
        self.append(help_text)

    def log_ai_command(self, command: str, output: str):
        self.append(f'[AI] Executed: {command}')
        self.append(output)
        self.append('')  # New line
        self._show_prompt()


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
        """Добавление новой вкладки интерактивного терминала"""
        # Создаем новый интерактивный терминал
        terminal = InteractiveTerminal()
        
        # Подключаем сигнал выполнения команд
        terminal.command_executed.connect(self._on_command_executed)
        
        # Добавляем вкладку
        tab_index = self.terminal_tabs.addTab(terminal, f"Терминал {self.terminal_tabs.count() + 1}")
        self.terminal_tabs.setCurrentIndex(tab_index)
        
        print(f"[TERMINAL] Добавлена новая вкладка интерактивного терминала")

    def _close_terminal_tab(self, index):
        """Закрытие вкладки терминала"""
        if self.terminal_tabs.count() > 1:
            self.terminal_tabs.removeTab(index)

    def _on_command_executed(self, command):
        """Обработчик выполненных команд"""
        print(f"[TERMINAL] Выполнена команда: {command}")
        # Здесь можно добавить логирование или другую обработку

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
        """Выполнение команды в текущем интерактивном терминале"""
        terminal = self.get_current_terminal()
        if terminal and isinstance(terminal, InteractiveTerminal):
            # Используем метод выполнения команды интерактивного терминала
            terminal._execute_command(command)
            print(f"[TERMINAL] Команда передана в интерактивный терминал: {command}")
        else:
            print(f"[TERMINAL] Ошибка: Не удалось получить интерактивный терминал")

    def log_ai_command(self, command: str, output: str):
        terminal = self.get_current_terminal()
        if terminal:
            terminal.log_ai_command(command, output)
