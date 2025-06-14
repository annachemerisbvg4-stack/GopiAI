#!/usr/bin/env python3
"""
Простой пример использования GopiAI WebView модуля

Демонстрирует основные возможности модуля:
- Создание окна с веб-чатом
- Обработка сообщений и ответов ИИ
- Управление моделями
- Экспорт истории чата
"""

import sys
import os
from pathlib import Path

# Добавляем корневую папку проекта в PYTHONPATH
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLabel, QPushButton, QComboBox, QTextEdit,
    QStatusBar, QMenuBar, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

from gopiai.webview import WebViewWidget, PuterChatInterface


class GopiAIChatWindow(QMainWindow):
    """
    Главное окно приложения с чатом ИИ.
    
    Демонстрирует интеграцию WebView виджета в обычное Qt приложение.
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_chat_interface()
        self.setup_connections()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса."""
        self.setWindowTitle("GopiAI WebView Chat - Example")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout(central_widget)
        
        # Левая панель с информацией
        self.setup_info_panel(main_layout)
        
        # WebView виджет для чата
        self.webview_widget = WebViewWidget()
        main_layout.addWidget(self.webview_widget, stretch=2)
        
        # Статусная строка
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to chat with AI")
        
        # Меню
        self.setup_menu()
    
    def setup_info_panel(self, main_layout):
        """Настройка информационной панели."""
        info_panel = QWidget()
        info_panel.setMaximumWidth(300)
        info_layout = QVBoxLayout(info_panel)
        
        # Заголовок
        title = QLabel("Chat Information")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        info_layout.addWidget(title)
        
        # Выбор модели
        model_label = QLabel("AI Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["claude-sonnet-4", "claude-opus-4"])
        info_layout.addWidget(model_label)
        info_layout.addWidget(self.model_combo)
        
        # Кнопки управления
        self.clear_button = QPushButton("Clear Chat")
        self.export_button = QPushButton("Export Chat")
        self.stats_button = QPushButton("Show Statistics")
        
        info_layout.addWidget(self.clear_button)
        info_layout.addWidget(self.export_button)
        info_layout.addWidget(self.stats_button)
        
        # Статистика чата
        stats_label = QLabel("Statistics:")
        stats_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        info_layout.addWidget(stats_label)
        
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(200)
        self.stats_text.setReadOnly(True)
        info_layout.addWidget(self.stats_text)
        
        # Лог сообщений
        log_label = QLabel("Message Log:")
        log_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        info_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        info_layout.addWidget(self.log_text)
        
        info_layout.addStretch()
        main_layout.addWidget(info_panel)
    
    def setup_menu(self):
        """Настройка меню."""
        menubar = self.menuBar()
        
        # Меню Chat
        chat_menu = menubar.addMenu("Chat")
        
        clear_action = QAction("Clear Chat", self)
        clear_action.triggered.connect(self.clear_chat)
        chat_menu.addAction(clear_action)
        
        chat_menu.addSeparator()
        
        export_json_action = QAction("Export as JSON", self)
        export_json_action.triggered.connect(lambda: self.export_chat("json"))
        chat_menu.addAction(export_json_action)
        
        export_txt_action = QAction("Export as Text", self)
        export_txt_action.triggered.connect(lambda: self.export_chat("txt"))
        chat_menu.addAction(export_txt_action)
        
        export_md_action = QAction("Export as Markdown", self)
        export_md_action.triggered.connect(lambda: self.export_chat("md"))
        chat_menu.addAction(export_md_action)
        
        # Меню Help
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_chat_interface(self):
        """Настройка интерфейса чата."""
        self.chat_interface = PuterChatInterface(self.webview_widget)
        
        # Таймер для обновления статистики
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(2000)  # Обновление каждые 2 секунды
    
    def setup_connections(self):
        """Настройка подключений сигналов."""
        # Подключение сигналов WebView
        self.webview_widget.message_sent.connect(self.on_message_sent)
        self.webview_widget.message_received.connect(self.on_message_received)
        self.webview_widget.model_changed.connect(self.on_model_changed)
        self.webview_widget.chat_cleared.connect(self.on_chat_cleared)
        
        # Подключение сигналов интерфейса чата
        self.chat_interface.error_occurred.connect(self.on_error)
        
        # Подключение элементов управления
        self.model_combo.currentTextChanged.connect(self.change_model)
        self.clear_button.clicked.connect(self.clear_chat)
        self.export_button.clicked.connect(lambda: self.export_chat("json"))
        self.stats_button.clicked.connect(self.show_detailed_statistics)
    
    def on_message_sent(self, message):
        """Обработка отправленного сообщения."""
        self.log_text.append(f"[USER] {message[:50]}...")
        self.status_bar.showMessage("Message sent, waiting for AI response...")
    
    def on_message_received(self, model, message):
        """Обработка полученного ответа ИИ."""
        self.log_text.append(f"[{model.upper()}] {message[:50]}...")
        self.status_bar.showMessage(f"Response received from {model}")
    
    def on_model_changed(self, model):
        """Обработка изменения модели."""
        self.model_combo.setCurrentText(model)
        self.status_bar.showMessage(f"Model changed to {model}")
    
    def on_chat_cleared(self):
        """Обработка очистки чата."""
        self.log_text.clear()
        self.status_bar.showMessage("Chat cleared")
    
    def on_error(self, error_message):
        """Обработка ошибок."""
        self.log_text.append(f"[ERROR] {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")
    
    def change_model(self, model):
        """Изменение модели ИИ."""
        if self.chat_interface:
            self.chat_interface.set_model(model)
    
    def clear_chat(self):
        """Очистка чата."""
        if self.chat_interface:
            self.chat_interface.clear_chat()
    
    def export_chat(self, format_type="json"):
        """Экспорт истории чата."""
        if not self.chat_interface:
            return
        
        try:
            # Получение данных для экспорта
            export_data = self.chat_interface.export_chat(format_type)
            
            if export_data:
                # Сохранение в файл
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"gopiai_chat_export_{timestamp}.{format_type}"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(export_data)
                
                QMessageBox.information(
                    self, 
                    "Export Successful", 
                    f"Chat exported to {filename}"
                )
                self.status_bar.showMessage(f"Chat exported to {filename}")
            else:
                QMessageBox.warning(
                    self, 
                    "Export Failed", 
                    "No chat data to export"
                )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Export Error", 
                f"Failed to export chat: {str(e)}"
            )
    
    def update_statistics(self):
        """Обновление статистики чата."""
        if not self.chat_interface:
            return
        
        try:
            stats = self.chat_interface.get_statistics()
            
            stats_text = f"""Total Messages: {stats['total_messages']}
User Messages: {stats['user_messages']}
AI Messages: {stats['ai_messages']}
Models Used: {', '.join(stats['models_used'])}
Session Start: {stats['session_start'][:19]}
Last Activity: {stats['last_activity'][:19] if stats['last_activity'] else 'None'}"""
            
            self.stats_text.setPlainText(stats_text)
        except Exception as e:
            self.stats_text.setPlainText(f"Error getting statistics: {str(e)}")
    
    def show_detailed_statistics(self):
        """Показ подробной статистики."""
        if not self.chat_interface:
            return
        
        try:
            stats = self.chat_interface.get_statistics()
            history = self.chat_interface.get_chat_history()
            
            detailed_stats = f"""=== GopiAI Chat Statistics ===

Session Information:
- Total Messages: {stats['total_messages']}
- User Messages: {stats['user_messages']}
- AI Messages: {stats['ai_messages']}
- Models Used: {', '.join(stats['models_used']) if stats['models_used'] else 'None'}
- Session Start: {stats['session_start']}
- Last Activity: {stats['last_activity'] or 'None'}

Chat History:
- Messages in history: {len(history)}
- Available models: {', '.join(self.chat_interface.get_available_models())}
- Current model: {self.chat_interface.get_current_model() or 'Unknown'}
- WebView connected: {self.chat_interface.is_connected()}"""
            
            QMessageBox.information(self, "Detailed Statistics", detailed_stats)
        except Exception as e:
            QMessageBox.critical(self, "Statistics Error", f"Failed to get statistics: {str(e)}")
    
    def show_about(self):
        """Показ информации о приложении."""
        about_text = """GopiAI WebView Chat Example

This is a demonstration application showing how to integrate
the GopiAI WebView module with puter.js for AI chat functionality.

Features:
- Chat with Claude Sonnet 4 and Opus 4 models
- Real-time streaming responses
- Chat history export
- Statistics tracking
- Modern web interface

Built with PySide6 and puter.js."""
        
        QMessageBox.about(self, "About GopiAI WebView Chat", about_text)


def main():
    """Главная функция приложения."""
    # Создание приложения
    app = QApplication(sys.argv)
    
    # Установка стиля приложения
    app.setStyle('Fusion')
    
    # Создание и показ главного окна
    window = GopiAIChatWindow()
    window.show()
    
    # Запуск цикла событий
    sys.exit(app.exec())


if __name__ == "__main__":
    main()