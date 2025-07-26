"""
OptimizedChatWidget - оптимизированный виджет чата для решения проблем с обрыванием сообщений
Использует буферизацию и оптимизированные Qt компоненты для стабильного отображения
"""

import logging
from typing import Optional, List
from PySide6.QtWidgets import (QPlainTextEdit, QVBoxLayout, QWidget, 
                               QScrollArea, QFrame, QHBoxLayout, QLabel)
from PySide6.QtCore import QTimer, Qt, Signal, QThread, pyqtSignal
from PySide6.QtGui import QTextCursor, QTextCharFormat, QFont, QColor, QPalette

logger = logging.getLogger(__name__)

class OptimizedChatWidget(QPlainTextEdit):
    """Оптимизированный виджет чата с буферизацией и улучшенной производительностью"""
    
    # Сигналы для взаимодействия
    message_added = Signal(str)
    scroll_to_bottom_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_buffer()
        self.setup_formatting()
        
        logger.info("[OptimizedChatWidget] Инициализирован оптимизированный чат виджет")
        
    def setup_ui(self):
        """Настройка UI для оптимальной производительности"""
        # QPlainTextEdit оптимизирован для больших текстов
        self.setReadOnly(True)
        self.setMaximumBlockCount(2000)  # Ограничение буфера для производительности
        
        # Настройка шрифта
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        
        # Настройка отображения
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Оптимизация производительности
        self.setCenterOnScroll(False)
        self.setTabStopDistance(40)
        
        logger.debug("[OptimizedChatWidget] UI настроен для оптимальной производительности")
        
    def setup_buffer(self):
        """Настройка системы буферизации для плавного отображения"""
        self.text_buffer = []
        self.max_buffer_size = 20  # Максимальный размер буфера
        self.buffer_flush_delay = 100  # Задержка сброса буфера в мс
        
        # Таймер для автоматического сброса буфера
        self.buffer_timer = QTimer()
        self.buffer_timer.timeout.connect(self.flush_buffer)
        self.buffer_timer.setSingleShot(True)
        
        logger.debug("[OptimizedChatWidget] Система буферизации настроена")
        
    def setup_formatting(self):
        """Настройка форматирования текста"""
        # Форматы для разных типов сообщений
        self.user_format = QTextCharFormat()
        self.user_format.setForeground(QColor(0, 100, 200))  # Синий для пользователя
        
        self.ai_format = QTextCharFormat()
        self.ai_format.setForeground(QColor(50, 150, 50))  # Зеленый для AI
        
        self.system_format = QTextCharFormat()
        self.system_format.setForeground(QColor(150, 150, 150))  # Серый для системы
        
        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QColor(200, 50, 50))  # Красный для ошибок
        
        logger.debug("[OptimizedChatWidget] Форматирование настроено")
        
    def append_message(self, message: str, message_type: str = "ai", auto_scroll: bool = True):
        """
        Добавление сообщения с буферизацией
        
        Args:
            message: Текст сообщения
            message_type: Тип сообщения (user, ai, system, error)
            auto_scroll: Автоматическая прокрутка к концу
        """
        try:
            # Подготавливаем сообщение с форматированием
            formatted_message = self.format_message(message, message_type)
            
            # Добавляем в буфер
            self.text_buffer.append({
                'text': formatted_message,
                'type': message_type,
                'auto_scroll': auto_scroll
            })
            
            logger.debug(f"[OptimizedChatWidget] Сообщение добавлено в буфер: {len(message)} символов")
            
            # Проверяем необходимость сброса буфера
            if len(self.text_buffer) >= self.max_buffer_size:
                self.flush_buffer()
            else:
                # Запускаем таймер для отложенного сброса
                self.buffer_timer.start(self.buffer_flush_delay)
                
        except Exception as e:
            logger.error(f"[OptimizedChatWidget] Ошибка добавления сообщения: {e}")
            # Fallback - добавляем напрямую
            self.append_text_direct(str(message))
            
    def append_text_chunk(self, text_chunk: str, message_type: str = "ai"):
        """
        Добавление части сообщения (для streaming)
        
        Args:
            text_chunk: Часть текста
            message_type: Тип сообщения
        """
        try:
            # Для streaming используем более частые обновления
            self.text_buffer.append({
                'text': text_chunk,
                'type': message_type,
                'auto_scroll': True,
                'is_chunk': True
            })
            
            # Более частый сброс для streaming
            if len(self.text_buffer) >= 5:
                self.flush_buffer()
            else:
                self.buffer_timer.start(50)  # Более быстрый сброс для streaming
                
        except Exception as e:
            logger.error(f"[OptimizedChatWidget] Ошибка добавления chunk: {e}")
            
    def flush_buffer(self):
        """Эффективный сброс буфера в UI"""
        if not self.text_buffer:
            return
            
        try:
            # Останавливаем таймер
            self.buffer_timer.stop()
            
            # Перемещаем курсор в конец
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.End)
            
            # Определяем, нужна ли прокрутка
            should_scroll = any(item.get('auto_scroll', True) for item in self.text_buffer)
            
            # Добавляем весь буфер за одну операцию для производительности
            combined_text = ""
            for item in self.text_buffer:
                text = item['text']
                if not item.get('is_chunk', False):
                    text += "\n"  # Добавляем перенос для полных сообщений
                combined_text += text
            
            # Вставляем текст
            cursor.insertText(combined_text)
            
            # Автопрокрутка если нужна
            if should_scroll:
                self.ensureCursorVisible()
                
            # Очищаем буфер
            self.text_buffer.clear()
            
            logger.debug(f"[OptimizedChatWidget] Буфер сброшен: {len(combined_text)} символов")
            
        except Exception as e:
            logger.error(f"[OptimizedChatWidget] Ошибка сброса буфера: {e}")
            
    def append_text_direct(self, text: str):
        """Прямое добавление текста без буферизации (для экстренных случаев)"""
        try:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(text + "\n")
            self.ensureCursorVisible()
            
        except Exception as e:
            logger.error(f"[OptimizedChatWidget] Ошибка прямого добавления: {e}")
            
    def format_message(self, message: str, message_type: str) -> str:
        """
        Форматирование сообщения в зависимости от типа
        
        Args:
            message: Текст сообщения
            message_type: Тип сообщения
            
        Returns:
            Отформатированное сообщение
        """
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if message_type == "user":
                return f"[{timestamp}] 👤 Пользователь: {message}"
            elif message_type == "ai":
                return f"[{timestamp}] 🤖 Ассистент: {message}"
            elif message_type == "system":
                return f"[{timestamp}] ⚙️ Система: {message}"
            elif message_type == "error":
                return f"[{timestamp}] ❌ Ошибка: {message}"
            else:
                return f"[{timestamp}] {message}"
                
        except Exception as e:
            logger.error(f"[OptimizedChatWidget] Ошибка форматирования: {e}")
            return str(message)
            
    def clear_chat(self):
        """Очистка чата"""
        try:
            self.clear()
            self.text_buffer.clear()
            self.buffer_timer.stop()
            logger.info("[OptimizedChatWidget] Чат очищен")
            
        except Exception as e:
            logger.error(f"[OptimizedChatWidget] Ошибка очистки чата: {e}")
            
    def get_chat_content(self) -> str:
        """Получение всего содержимого чата"""
        try:
            # Сначала сбрасываем буфер
            self.flush_buffer()
            return self.toPlainText()
            
        except Exception as e:
            logger.error(f"[OptimizedChatWidget] Ошибка получения контента: {e}")
            return ""
            
    def save_chat_to_file(self, filename: str) -> bool:
        """
        Сохранение чата в файл с очисткой HTML
        
        Args:
            filename: Имя файла для сохранения
            
        Returns:
            True если успешно сохранено
        """
        try:
            content = self.get_chat_content()
            
            # Импортируем санитизатор для очистки
            try:
                from ..gopiai_integration.html_sanitizer import sanitize_html_for_file
                clean_content = sanitize_html_for_file(content)
            except ImportError:
                # Fallback если санитизатор недоступен
                import re
                clean_content = re.sub(r'<[^<>]*>', '', content)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(clean_content)
                
            logger.info(f"[OptimizedChatWidget] Чат сохранен в файл: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"[OptimizedChatWidget] Ошибка сохранения в файл: {e}")
            return False
            
    def set_max_buffer_size(self, size: int):
        """Настройка максимального размера буфера"""
        self.max_buffer_size = max(1, size)
        logger.debug(f"[OptimizedChatWidget] Размер буфера установлен: {size}")
        
    def set_buffer_flush_delay(self, delay_ms: int):
        """Настройка задержки сброса буфера"""
        self.buffer_flush_delay = max(10, delay_ms)
        logger.debug(f"[OptimizedChatWidget] Задержка сброса установлена: {delay_ms}мс")

class ChatContainer(QWidget):
    """Контейнер для чата с дополнительными элементами управления"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка UI контейнера"""
        layout = QVBoxLayout(self)
        
        # Создаем оптимизированный чат виджет
        self.chat_widget = OptimizedChatWidget()
        
        # Добавляем в layout
        layout.addWidget(self.chat_widget)
        
        # Настройка layout
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)
        
        logger.info("[ChatContainer] Контейнер чата инициализирован")
        
    def get_chat_widget(self) -> OptimizedChatWidget:
        """Получение виджета чата"""
        return self.chat_widget
