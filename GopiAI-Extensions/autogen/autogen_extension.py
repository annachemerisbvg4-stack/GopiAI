"""
AutoGen UI Integration - Интеграция AutoGen в GopiAI UI
"""

from PySide6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QLineEdit, QPushButton, QComboBox, QLabel
)
from PySide6.QtCore import Qt, QThread, pyqtSignal

# Импортируем наш AutoGen модуль
try:
    from .autogen_core import autogen_manager
    AUTOGEN_AVAILABLE = True
except ImportError:
    print("⚠️ AutoGen core недоступен")
    AUTOGEN_AVAILABLE = False

class AutoGenChatWidget(QWidget):
    """Виджет для чата с AutoGen агентами"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("🤖 AutoGen Мультиагентный Чат")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title_label)
        
        # Выбор стратегии
        strategy_layout = QHBoxLayout()
        strategy_layout.addWidget(QLabel("Модель:"))
        
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "best_first (llama-3.3-70b)",
            "random (случайная Cerebras)",
            "all_rotation (все Cerebras)",
            "openai_fallback (OpenAI резерв)"
        ])
        strategy_layout.addWidget(self.strategy_combo)
        layout.addLayout(strategy_layout)
        
        # Область чата
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setPlaceholderText("Здесь будет отображаться диалог с AutoGen агентами...")
        layout.addWidget(self.chat_area)
        
        # Поле ввода
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите сообщение для AutoGen агентов...")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
        
        # Статус
        self.status_label = QLabel("Статус: Готов к работе" if AUTOGEN_AVAILABLE else "Статус: AutoGen недоступен")
        self.status_label.setStyleSheet("color: green;" if AUTOGEN_AVAILABLE else "color: red;")
        layout.addWidget(self.status_label)
        
        # Отключаем кнопки если AutoGen недоступен
        if not AUTOGEN_AVAILABLE:
            self.input_field.setEnabled(False)
            self.send_button.setEnabled(False)
            self.strategy_combo.setEnabled(False)
    
    def send_message(self):
        """Отправляет сообщение AutoGen агентам"""
        if not AUTOGEN_AVAILABLE:
            return
            
        message = self.input_field.text().strip()
        if not message:
            return
        
        # Получаем выбранную стратегию
        strategy_map = {
            0: "best_first",
            1: "random", 
            2: "all_rotation",
            3: "openai_fallback"
        }
        strategy = strategy_map.get(self.strategy_combo.currentIndex(), "best_first")
        
        # Отображаем сообщение пользователя
        self.chat_area.append(f"<b>👤 Вы:</b> {message}")
        self.input_field.clear()
        
        # Обновляем статус
        self.status_label.setText("Статус: Обрабатывается...")
        self.status_label.setStyleSheet("color: orange;")
        
        # Отключаем интерфейс на время обработки
        self.send_button.setEnabled(False)
        self.input_field.setEnabled(False)
        
        try:
            # Отправляем сообщение AutoGen
            response = autogen_manager.simple_chat(message, strategy)
            
            # Отображаем ответ
            if response:
                self.chat_area.append(f"<b>🤖 AutoGen:</b> {response}")
            else:
                self.chat_area.append("<b>⚠️ Ошибка:</b> Не удалось получить ответ")
            
            # Автопрокрутка
            self.chat_area.verticalScrollBar().setValue(
                self.chat_area.verticalScrollBar().maximum()
            )
            
        except Exception as e:
            self.chat_area.append(f"<b>❌ Ошибка:</b> {str(e)}")
        
        finally:
            # Восстанавливаем интерфейс
            self.send_button.setEnabled(True)
            self.input_field.setEnabled(True)
            self.status_label.setText("Статус: Готов к работе")
            self.status_label.setStyleSheet("color: green;")

def add_autogen_dock(main_window):
    """
    Добавляет док-виджет AutoGen в главное окно
    
    Args:
        main_window: Главное окно GopiAI
    
    Returns:
        QDockWidget: Созданный док-виджет
    """
    # Создаем док-виджет
    dock = QDockWidget("AutoGen Мультиагенты", main_window)
    dock.setObjectName("autoGenDock")
    
    # Создаем виджет чата
    chat_widget = AutoGenChatWidget()
    dock.setWidget(chat_widget)
    
    # Добавляем в главное окно
    main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
    
    print("✅ AutoGen dock добавлен в главное окно")
    return dock

def init_autogen_extension(main_window):
    """
    Инициализирует расширение AutoGen
    
    Args:
        main_window: Главное окно GopiAI
    """
    try:
        add_autogen_dock(main_window)
        
        # Обновляем статус в главном окне если есть такая возможность
        if hasattr(main_window, 'update_status_message'):
            if AUTOGEN_AVAILABLE:
                main_window.update_status_message("AutoGen мультиагенты готовы")
            else:
                main_window.update_status_message("AutoGen недоступен")
        
        print("✅ AutoGen расширение инициализировано")
    except Exception as e:
        print(f"❌ Ошибка при инициализации AutoGen: {e}")