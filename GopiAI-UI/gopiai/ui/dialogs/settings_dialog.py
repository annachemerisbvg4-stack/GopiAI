"""
Диалог настроек GopiAI

Этот модуль содержит диалог настроек для приложения GopiAI,
включая настройки тем и другие параметры приложения.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QLabel, QPushButton, QComboBox, QCheckBox, QSpinBox, 
    QLineEdit, QTextEdit, QScrollArea, QFrame
)


def is_qt_object_valid(obj):
    """
    Безопасно проверяет валидность Qt объекта без зависимости от sip.
    
    Args:
        obj: Qt объект для проверки
        
    Returns:
        bool: True если объект валиден, False в противном случае
    """
    if obj is None:
        return False
    
    try:
        # Пробуем вызвать метод, который есть у всех QObject
        obj.isVisible()
        return True
    except RuntimeError:
        # C++ объект уже удален
        return False
    except Exception:
        # При любой другой ошибке считаем объект невалидным
        return False


class GopiAISettingsDialog(QDialog):
    """
    Диалог настроек GopiAI.
    
    Предоставляет интерфейс для настройки тем и других параметров приложения.
    """
    
    # Сигналы
    settings_applied = Signal(dict)  # Сигнал применения настроек
    themeChanged = Signal(str)       # Сигнал изменения темы
    
    # Коды диалога
    class DialogCode:
        Accepted = 1
        Rejected = 0
    
    def __init__(self, theme_manager=None, parent=None):
        """
        Инициализирует диалог настроек.
        
        Args:
            theme_manager: Менеджер тем
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.settings = {}
        
        self.setup_ui()
        self.load_current_settings()
    
    def _is_light_color(self, color):
        """
        Определяет, является ли цвет светлым.
        
        Args:
            color (str): Цвет в HEX формате
            
        Returns:
            bool: True если цвет светлый, False если темный
        """
        # Убираем # если есть
        if color.startswith('#'):
            color = color[1:]
        
        # Для HEX формата #RRGGBB
        if len(color) == 6:
            try:
                r = int(color[0:2], 16)
                g = int(color[2:4], 16)
                b = int(color[4:6], 16)
                
                # Формула для определения яркости
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                return brightness > 128
            except ValueError:
                pass
        
        return True  # По умолчанию считаем светлым
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Настройки GopiAI")
        self.setMinimumSize(600, 500)
        self.resize(800, 600)
        
        # Основной макет
        main_layout = QVBoxLayout(self)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Создание вкладок
        self._create_appearance_tab()
        self._create_general_tab()
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Отмена")
        self.apply_button = QPushButton("Применить")
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        
        main_layout.addLayout(button_layout)
        
        # Подключение сигналов
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.apply_settings)
        
        # Применяем текущую тему к диалогу
        self._apply_current_theme()
    
    def _create_appearance_tab(self):
        """Создание вкладки внешнего вида"""
        appearance_widget = QWidget()
        layout = QVBoxLayout(appearance_widget)
          # Настройки темы
        theme_frame = QFrame()
        theme_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        theme_layout = QVBoxLayout(theme_frame)
        
        theme_layout.addWidget(QLabel("Тема:"))
        self.theme_combo = QComboBox()
        theme_layout.addWidget(self.theme_combo)
        
        # Темный режим
        self.dark_mode_check = QCheckBox("Темный режим")
        theme_layout.addWidget(self.dark_mode_check)
        
        layout.addWidget(theme_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(appearance_widget, "Внешний вид")
        
        # Заполнение списка тем
        self._populate_themes()
    
    def _create_general_tab(self):
        """Создание общей вкладки"""
        general_widget = QWidget()
        layout = QVBoxLayout(general_widget)
          # Общие настройки
        general_frame = QFrame()
        general_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        general_layout = QVBoxLayout(general_frame)
        
        general_layout.addWidget(QLabel("Общие настройки"))
        
        # Автосохранение
        self.autosave_check = QCheckBox("Автосохранение")
        general_layout.addWidget(self.autosave_check)
        
        # Интервал автосохранения
        autosave_layout = QHBoxLayout()
        autosave_layout.addWidget(QLabel("Интервал автосохранения (мин):"))
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(1, 60)
        self.autosave_interval.setValue(5)
        autosave_layout.addWidget(self.autosave_interval)
        general_layout.addLayout(autosave_layout)
        
        layout.addWidget(general_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(general_widget, "Общие")
    
    def _populate_themes(self):
        """Заполнение списка доступных тем"""
        if not self.theme_manager:
            return
        
        try:
            themes = self.theme_manager.get_available_themes()
            self.theme_combo.clear()
            
            for theme_name in themes:
                self.theme_combo.addItem(theme_name, theme_name)
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке тем: {e}")
    
    def _apply_current_theme(self):
        """Применение текущей темы к диалогу"""
        if not self.theme_manager:
            return
        
        try:
            # Получаем цвета из текущей темы
            current_theme_data = self.theme_manager.get_current_theme_data()
            if current_theme_data:
                main_color = current_theme_data.get('main_color', '#f8f9fa')
                text_color = current_theme_data.get('text_color', '#212529')
                accent_color = current_theme_data.get('accent_color', '#4dabf7')
                
                self._apply_theme_to_dialog(main_color, text_color, accent_color)
        except Exception as e:
            print(f"⚠️ Ошибка при применении темы: {e}")
    
    def _apply_theme_to_dialog(self, main_color, text_color, accent_color):
        """Применение темы к диалогу"""
        # Определяем текст на основе яркости фона
        is_light_bg = self._is_light_color(main_color)
        button_text_color = "#1a1a1a" if is_light_bg else "#ffffff"
        
        # Применяем стили ко всему диалогу
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {main_color};
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QPushButton {{
                background-color: {main_color}dd;
                color: {button_text_color};
                border: 1px solid #dee2e6;
                padding: 5px 10px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {main_color}ee;
            }}
            QPushButton:pressed {{
                background-color: {main_color}cc;
            }}
            QPushButton:disabled {{
                background-color: {main_color}88;
            }}
            QTabWidget::pane {{
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {main_color};
                color: {text_color};
                padding: 8px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {accent_color}22;
                border-bottom: 2px solid {accent_color};
            }}
            QTabBar::tab:hover {{
                background-color: {main_color}dd;
            }}
            QFrame {{
                background-color: {main_color}cc;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 12px;
                margin: 4px;
            }}
            QFrame:hover {{
                background-color: {main_color}ee;
            }}
            QComboBox {{
                background-color: {main_color}ee;
                color: {text_color};
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 3px;
            }}
            QComboBox:hover {{
                border: 1px solid #bbb;
            }}
            QComboBox::drop-down {{
                border: 0px;
            }}
            QComboBox::down-arrow {{
                width: 10px;
                height: 10px;
            }}
            QCheckBox {{
                color: {text_color};
            }}
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border: 1px solid #dee2e6;
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {accent_color};
                border: 1px solid {accent_color};
            }}
            QSpinBox, QLineEdit, QTextEdit {{
                background-color: {main_color}ee;
                color: {text_color};
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 3px;
            }}
            QSpinBox:hover, QLineEdit:hover, QTextEdit:hover {{
                border: 1px solid #bbb;
            }}
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {main_color}aa;
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {accent_color}aa;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {accent_color};
            }}
        """)
    
    def load_current_settings(self):
        """Загрузка текущих настроек"""
        print("🔧 Загрузка текущих настроек...")
        
        try:
            if not self.theme_manager:
                print("❌ Менеджер тем не доступен")
                return
            
            # Загрузка текущей темы
            current_theme = self.theme_manager.get_current_theme()
            print(f"🔧 Текущая тема: {current_theme}")
            
            # Установка темы в комбобокс
            if hasattr(self, 'theme_combo') and is_qt_object_valid(self.theme_combo):
                for i in range(self.theme_combo.count()):
                    if self.theme_combo.itemData(i) == current_theme:
                        self.theme_combo.setCurrentIndex(i)
                        print(f"🔧 Установлен индекс темы: {i}")
                        break
            
            # Установка темного режима
            if hasattr(self, 'dark_mode_check') and is_qt_object_valid(self.dark_mode_check):
                if hasattr(self.theme_manager, '_current_variant'):
                    is_dark = self.theme_manager._current_variant == "dark"
                    self.dark_mode_check.setChecked(is_dark)
                    print(f"🔧 Установлен темный режим: {is_dark}")
            
            print("🔧 Настройки загружены успешно")
            
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке настроек: {e}")
    
    def collect_settings(self):
        """Сбор всех настроек из интерфейса"""
        settings = {}
        
        try:
            # Настройки темы
            if hasattr(self, 'theme_combo') and is_qt_object_valid(self.theme_combo):
                settings['theme'] = self.theme_combo.currentData()
            
            if hasattr(self, 'dark_mode_check') and is_qt_object_valid(self.dark_mode_check):
                settings['dark_mode'] = self.dark_mode_check.isChecked()
            
            # Общие настройки
            if hasattr(self, 'autosave_check') and is_qt_object_valid(self.autosave_check):
                settings['autosave'] = self.autosave_check.isChecked()
            
            if hasattr(self, 'autosave_interval') and is_qt_object_valid(self.autosave_interval):
                settings['autosave_interval'] = self.autosave_interval.value()
            
            print(f"🔧 Собранные настройки: {settings}")
            
        except Exception as e:
            print(f"⚠️ Ошибка при сборе настроек: {e}")
        
        return settings
    
    def apply_settings(self):
        """Применение настроек"""
        try:
            self.settings = self.collect_settings()
            
            # Применение темы и темного режима
            if self.theme_manager and 'theme' in self.settings:
                theme_name = self.settings.get('theme')
                
                # Устанавливаем темный/светлый вариант в менеджере тем
                if hasattr(self.theme_manager, '_current_variant') and 'dark_mode' in self.settings:
                    self.theme_manager._current_variant = "dark" if self.settings.get('dark_mode', False) else "light"
                
                # Применяем тему
                self.theme_manager.apply_theme(theme_name)
                
                # Обновляем стили диалога
                self._apply_current_theme()
                
                # Сигнал изменения темы
                self.themeChanged.emit(theme_name)
            
            # Испускание сигнала для передачи настроек в основное окно
            self.settings_applied.emit(self.settings)
            
            print("🔧 Настройки применены успешно")
            
        except Exception as e:
            print(f"⚠️ Ошибка при применении настроек: {e}")
    
    def accept(self):
        """Обработчик нажатия OK"""
        self.apply_settings()
        super().accept()
    
    def reject(self):
        """Обработчик нажатия Отмена"""
        super().reject()
