"""
Диалог настроек GopiAI
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTabWidget, QWidget, QGroupBox, QCheckBox,
    QSlider, QSpinBox, QLineEdit, QTextEdit, QScrollArea,
    QFrame, QSizePolicy, QGridLayout, QFormLayout, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap
from pathlib import Path


class SettingsCard(QFrame):
    """Карточка настроек"""
    
    def __init__(self, title: str, description: str = "", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        # Удаляем жестко заданные стили, они будут применяться из глобальной темы
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Заголовок
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Описание
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("font-size: 9pt;")  # Убираем жестко заданный цвет
            layout.addWidget(desc_label)
        
        # Контейнер для контента
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
    
    def add_content(self, widget):
        """Добавить виджет в карточку"""
        self.content_layout.addWidget(widget)


class GopiAISettingsDialog(QDialog):
    """Диалог настроек GopiAI"""
    
    settings_applied = Signal(dict)  # Сигнал применения настроек
    themeChanged = Signal(str)       # Сигнал изменения темы
    
    # Коды диалога
    class DialogCode:
        Accepted = 1
        Rejected = 0
    
    # Функция для определения яркости цвета
    def _is_light_color(self, color):
        """Определяет, является ли цвет светлым"""
        # Убираем # если есть
        if color.startswith('#'):
            color = color[1:]
        
        # Для HEX формата #RRGGBB
        if len(color) == 6:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)            # Формула для определения яркости
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            return brightness > 128
        return True  # По умолчанию считаем светлым
    
    def __init__(self, theme_manager=None, parent=None):
        print("🔧 GopiAISettingsDialog.__init__ начат")
        super().__init__(parent)
        print("🔧 super().__init__ выполнен")
        # Добавляем свойство безрамочного окна
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.theme_manager = theme_manager
        self.settings = {}
        
        # Переменная для хранения позиции мыши при перетаскивании
        self._drag_position = None
        
        print("🔧 Вызываем setup_ui()")
        self.setup_ui()
        print("🔧 setup_ui() завершен")
        print("🔧 Вызываем load_current_settings()")
        self.load_current_settings()
        print("🔧 load_current_settings() завершен")
        print("🔧 GopiAISettingsDialog.__init__ завершен")
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Настройки GopiAI")
        self.setMinimumSize(600, 500)
        self.resize(800, 600)
        
        # Применяем текущую тему к диалогу
        if self.theme_manager:            # Получаем цвета из текущей темы
            current_theme_data = self.theme_manager.get_current_theme_data()
            if current_theme_data:
                main_color = current_theme_data.get('main_color', '#f8f9fa')
                text_color = current_theme_data.get('text_color', '#212529')
                
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
                    QTabWidget::pane {{
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                    }}
                    QTabBar::tab {{
                        background-color: {main_color};
                        color: {text_color};
                        padding: 8px 12px;
                    }}
                    QTabBar::tab:selected {{
                        background-color: {main_color}cc;
                    }}
                    SettingsCard {{
                        background-color: {main_color}cc;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 12px;
                        margin: 4px;
                    }}
                    SettingsCard:hover {{
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
                        background-color: {main_color}dd;
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
                    QScrollArea, QScrollBar {{
                        background-color: {main_color};
                        border: none;
                    }}
                """)
        
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        
        # Заголовок
        header_layout = QHBoxLayout()
        title_label = QLabel("Настройки")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Добавляем кнопку закрытия для безрамочного режима
        close_button = QPushButton("✕")
        close_button.setMaximumSize(30, 30)
        close_button.clicked.connect(self.reject)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
                color: white;
            }
        """)
        header_layout.addWidget(close_button)
        
        main_layout.addLayout(header_layout)
        
        # Tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Создание вкладок
        self.create_appearance_tab()
        self.create_interface_tab()
        self.create_advanced_tab()
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_button = QPushButton("Применить")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_settings)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
    
    def create_appearance_tab(self):
        """Создание вкладки внешнего вида"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Карточка темы
        theme_card = SettingsCard(
            "Тема приложения",
            "Выберите тему оформления интерфейса"
        )
        
        theme_layout = QVBoxLayout()
        
        # Выбор темы
        theme_combo_layout = QHBoxLayout()
        theme_label = QLabel("Тема:")
        theme_combo_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumWidth(200)
        print(f"🔧 theme_combo создан: {self.theme_combo}")
        
        # Заполнение списка тем
        if self.theme_manager:
            themes = self.theme_manager.get_theme_display_names()
            for theme_key, display_name in themes.items():
                self.theme_combo.addItem(display_name, theme_key)
            print(f"🔧 theme_combo заполнен, count = {self.theme_combo.count()}")
        
        theme_combo_layout.addWidget(self.theme_combo)
        print(f"🔧 theme_combo добавлен в layout")
        theme_combo_layout.addStretch()
        theme_layout.addLayout(theme_combo_layout)
        
        # Переключатель темного режима
        dark_mode_layout = QHBoxLayout()
        dark_mode_layout.addWidget(QLabel("Темный режим:"))
        
        self.dark_mode_check = QCheckBox()
        self.dark_mode_check.setToolTip("Включить темный режим интерфейса")
        dark_mode_layout.addWidget(self.dark_mode_check)
        dark_mode_layout.addStretch()
        theme_layout.addLayout(dark_mode_layout)
        
        # Добавляем все в карточку
        theme_widget = QWidget()
        theme_widget.setLayout(theme_layout)
        theme_card.add_content(theme_widget)
        layout.addWidget(theme_card)
        
        # Карточка шрифтов
        font_card = SettingsCard(
            "Шрифты",
            "Настройка размера и типа шрифтов"
        )
        
        font_layout = QFormLayout()
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(10)
        font_layout.addRow("Размер шрифта:", self.font_size_spin)
        
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "System Default", "Arial", "Helvetica", "Times New Roman",
            "Courier New", "Verdana", "Georgia", "Comic Sans MS"
        ])
        font_layout.addRow("Семейство шрифта:", self.font_family_combo)
        
        font_widget = QWidget()
        font_widget.setLayout(font_layout)
        font_card.add_content(font_widget)
        layout.addWidget(font_card)

    def create_interface_tab(self):
        """Создание вкладки интерфейса"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Карточка панели инструментов
        toolbar_card = SettingsCard(
            "Панель инструментов",
            "Настройка отображения панели инструментов"
        )
        
        toolbar_layout = QVBoxLayout()
        
        self.show_toolbar_check = QCheckBox("Показывать панель инструментов")
        self.show_toolbar_check.setChecked(True)
        toolbar_layout.addWidget(self.show_toolbar_check)
          # Размер панели инструментов
        toolbar_size_layout = QHBoxLayout()
        toolbar_size_layout.addWidget(QLabel("Размер иконок:"))
        
        self.toolbar_size_combo = QComboBox()
        self.toolbar_size_combo.addItems(["Маленькая", "Средняя", "Большая"])
        self.toolbar_size_combo.setCurrentText("Средняя")
        toolbar_size_layout.addWidget(self.toolbar_size_combo)
        toolbar_size_layout.addStretch()
        toolbar_layout.addLayout(toolbar_size_layout)
        
        toolbar_layout.addStretch()
        
        toolbar_widget = QWidget()
        toolbar_widget.setLayout(toolbar_layout)
        toolbar_card.add_content(toolbar_widget)
        layout.addWidget(toolbar_card)
        
        # Карточка статусной строки
        status_card = SettingsCard(
            "Статусная строка",
            "Настройка информации в статусной строке"
        )
        
        status_layout = QVBoxLayout()
        
        self.show_status_check = QCheckBox("Показывать статусную строку")
        self.show_status_check.setChecked(True)
        status_layout.addWidget(self.show_status_check)
        
        self.show_memory_check = QCheckBox("Показывать использование памяти")
        self.show_memory_check.setChecked(False)
        status_layout.addWidget(self.show_memory_check)
        
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        status_card.add_content(status_widget)
        layout.addWidget(status_card)
        
        # Карточка окон
        windows_card = SettingsCard(
            "Окна",
            "Настройка поведения окон"
        )
        
        windows_layout = QVBoxLayout()
        
        self.remember_geometry_check = QCheckBox("Запоминать размер и положение окон")
        self.remember_geometry_check.setChecked(True)
        windows_layout.addWidget(self.remember_geometry_check)
        
        self.minimize_to_tray_check = QCheckBox("Сворачивать в системный трей")
        self.minimize_to_tray_check.setChecked(False)
        windows_layout.addWidget(self.minimize_to_tray_check)
        
        windows_widget = QWidget()
        windows_widget.setLayout(windows_layout)
        windows_card.add_content(windows_widget)
        layout.addWidget(windows_card)
        
        layout.addStretch()
        self.tab_widget.addTab(scroll, "Интерфейс")
    
    def create_advanced_tab(self):
        """Создание вкладки дополнительных настроек"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Карточка производительности
        performance_card = SettingsCard(
            "Производительность",
            "Настройки для оптимизации работы приложения"
        )
        
        perf_layout = QFormLayout()
        
        self.animation_check = QCheckBox("Включить анимации")
        self.animation_check.setChecked(True)
        perf_layout.addRow("Анимации:", self.animation_check)
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setValue(100)
        self.cache_size_spin.setSuffix(" МБ")
        perf_layout.addRow("Размер кэша:", self.cache_size_spin)
        
        perf_widget = QWidget()
        perf_widget.setLayout(perf_layout)
        performance_card.add_content(perf_widget)
        layout.addWidget(performance_card)
        
        # Карточка логирования
        logging_card = SettingsCard(
            "Логирование",
            "Настройка уровня детализации логов"
        )
        
        log_layout = QFormLayout()
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        log_layout.addRow("Уровень логирования:", self.log_level_combo)
        
        self.log_to_file_check = QCheckBox("Сохранять логи в файл")
        self.log_to_file_check.setChecked(True)
        log_layout.addRow("В файл:", self.log_to_file_check)
        
        log_widget = QWidget()
        log_widget.setLayout(log_layout)
        logging_card.add_content(log_widget)
        layout.addWidget(logging_card)
        
        # Карточка сброса настроек
        reset_card = SettingsCard(
            "Сброс настроек",
            "Восстановление настроек по умолчанию"
        )
        
        reset_layout = QHBoxLayout()
        self.reset_button = QPushButton("Сбросить все настройки")
        self.reset_button.clicked.connect(self.reset_settings)
        reset_layout.addWidget(self.reset_button)
        reset_layout.addStretch()
        
        reset_widget = QWidget()
        reset_widget.setLayout(reset_layout)
        reset_card.add_content(reset_widget)
        layout.addWidget(reset_card)
        
        layout.addStretch()
        self.tab_widget.addTab(scroll, "Дополнительно")
    
    def load_current_settings(self):
        """Загрузка текущих настроек"""
        print("🔧 load_current_settings() начат")
        try:
            if self.theme_manager:
                print("🔧 theme_manager существует")
                current_theme = self.theme_manager.get_current_theme()
                print(f"🔧 current_theme = {current_theme}")
                
                # Проверяем, что theme_combo существует и действителен
                if hasattr(self, 'theme_combo') and self.theme_combo:
                    try:
                        # Защита от случая, когда C++ объект уже удален
                        if not self.theme_combo.isVisible() and not sip_is_deleted(self.theme_combo):
                            print("🔧 theme_combo существует, но невидим")
                        
                        print(f"🔧 theme_combo существует: {self.theme_combo}")
                        count = self.theme_combo.count()
                        print(f"🔧 theme_combo.count() = {count}")
                        
                        # Найти индекс текущей темы в комбобоксе
                        for i in range(count):
                            if self.theme_combo.itemData(i) == current_theme:
                                self.theme_combo.setCurrentIndex(i)
                                print(f"🔧 Установлен индекс темы: {i}")
                                break
                    except RuntimeError as e:
                        if "Internal C++ object" in str(e):
                            print(f"⚠️ C++ объект QComboBox уже удален: {e}")
                        else:
                            print(f"❌ Ошибка при работе с theme_combo: {e}")
                    except Exception as e:
                        print(f"❌ Ошибка при работе с theme_combo: {e}")
                        print(f"❌ Тип ошибки: {type(e)}")
                else:
                    print("❌ theme_combo не существует или был удален!")
                
                # Устанавливаем темный режим если у менеджера тем есть соответствующий атрибут
                try:
                    if hasattr(self, 'dark_mode_check') and hasattr(self.theme_manager, '_current_variant'):
                        self.dark_mode_check.setChecked(self.theme_manager._current_variant == "dark")
                        print(f"🔧 Установлен темный режим: {self.theme_manager._current_variant == 'dark'}")
                except Exception as e:
                    print(f"❌ Ошибка при установке темного режима: {e}")
        except Exception as e:
            print(f"⚠️ Ошибка открытия настроек: {e}")
            
        print("🔧 load_current_settings() завершен")
        
# Вспомогательные функции
def is_qt_object_valid(obj):
    """Безопасно проверяет валидность Qt объекта без зависимости от sip"""
    if obj is None:
        return False
    try:
        # Пробуем вызвать какой-нибудь метод, который есть у всех QObject
        # isVisible() - безопасный метод, который должен быть у всех виджетов
        return obj.isVisible() or True  # Возвращаем True даже если невидим, главное что метод отработал
    except RuntimeError:
        # Если метод вызвал RuntimeError, значит C++ объект уже удален
        return False
    except Exception:
        # При любой другой ошибке считаем объект невалидным
        return False


class GopiAISettingsDialog(QDialog):
    """Диалог настроек GopiAI"""
    
    settings_applied = Signal(dict)  # Сигнал применения настроек
    themeChanged = Signal(str)       # Сигнал изменения темы
    
    # Коды диалога
    class DialogCode:
        Accepted = 1
        Rejected = 0
    
    # Функция для определения яркости цвета
    def _is_light_color(self, color):
        """Определяет, является ли цвет светлым"""
        # Убираем # если есть
        if color.startswith('#'):
            color = color[1:]
        
        # Для HEX формата #RRGGBB
        if len(color) == 6:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)            # Формула для определения яркости
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            return brightness > 128
        return True  # По умолчанию считаем светлым
    
    def __init__(self, theme_manager=None, parent=None):
        print("🔧 GopiAISettingsDialog.__init__ начат")
        super().__init__(parent)
        print("🔧 super().__init__ выполнен")
        # Добавляем свойство безрамочного окна
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.theme_manager = theme_manager
        self.settings = {}
        
        # Переменная для хранения позиции мыши при перетаскивании
        self._drag_position = None
        
        print("🔧 Вызываем setup_ui()")
        self.setup_ui()
        print("🔧 setup_ui() завершен")
        print("🔧 Вызываем load_current_settings()")
        self.load_current_settings()
        print("🔧 load_current_settings() завершен")
        print("🔧 GopiAISettingsDialog.__init__ завершен")
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Настройки GopiAI")
        self.setMinimumSize(600, 500)
        self.resize(800, 600)
        
        # Применяем текущую тему к диалогу
        if self.theme_manager:            # Получаем цвета из текущей темы
            current_theme_data = self.theme_manager.get_current_theme_data()
            if current_theme_data:
                main_color = current_theme_data.get('main_color', '#f8f9fa')
                text_color = current_theme_data.get('text_color', '#212529')
                
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
                    QTabWidget::pane {{
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                    }}
                    QTabBar::tab {{
                        background-color: {main_color};
                        color: {text_color};
                        padding: 8px 12px;
                    }}
                    QTabBar::tab:selected {{
                        background-color: {main_color}cc;
                    }}
                    SettingsCard {{
                        background-color: {main_color}cc;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 12px;
                        margin: 4px;
                    }}
                    SettingsCard:hover {{
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
                        background-color: {main_color}dd;
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
                    QScrollArea, QScrollBar {{
                        background-color: {main_color};
                        border: none;
                    }}
                """)
        
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        
        # Заголовок
        header_layout = QHBoxLayout()
        title_label = QLabel("Настройки")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Добавляем кнопку закрытия для безрамочного режима
        close_button = QPushButton("✕")
        close_button.setMaximumSize(30, 30)
        close_button.clicked.connect(self.reject)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
                color: white;
            }
        """)
        header_layout.addWidget(close_button)
        
        main_layout.addLayout(header_layout)
        
        # Tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Создание вкладок
        self.create_appearance_tab()
        self.create_interface_tab()
        self.create_advanced_tab()
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_button = QPushButton("Применить")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_settings)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
    
    def create_appearance_tab(self):
        """Создание вкладки внешнего вида"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Карточка темы
        theme_card = SettingsCard(
            "Тема приложения",
            "Выберите тему оформления интерфейса"
        )
        
        theme_layout = QVBoxLayout()
        
        # Выбор темы
        theme_combo_layout = QHBoxLayout()
        theme_label = QLabel("Тема:")
        theme_combo_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumWidth(200)
        print(f"🔧 theme_combo создан: {self.theme_combo}")
        
        # Заполнение списка тем
        if self.theme_manager:
            themes = self.theme_manager.get_theme_display_names()
            for theme_key, display_name in themes.items():
                self.theme_combo.addItem(display_name, theme_key)
            print(f"🔧 theme_combo заполнен, count = {self.theme_combo.count()}")
        
        theme_combo_layout.addWidget(self.theme_combo)
        print(f"🔧 theme_combo добавлен в layout")
        theme_combo_layout.addStretch()
        theme_layout.addLayout(theme_combo_layout)
        
        # Переключатель темного режима
        dark_mode_layout = QHBoxLayout()
        dark_mode_layout.addWidget(QLabel("Темный режим:"))
        
        self.dark_mode_check = QCheckBox()
        self.dark_mode_check.setToolTip("Включить темный режим интерфейса")
        dark_mode_layout.addWidget(self.dark_mode_check)
        dark_mode_layout.addStretch()
        theme_layout.addLayout(dark_mode_layout)
        
        # Добавляем все в карточку
        theme_widget = QWidget()
        theme_widget.setLayout(theme_layout)
        theme_card.add_content(theme_widget)
        layout.addWidget(theme_card)
        
        # Карточка шрифтов
        font_card = SettingsCard(
            "Шрифты",
            "Настройка размера и типа шрифтов"
        )
        
        font_layout = QFormLayout()
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(10)
        font_layout.addRow("Размер шрифта:", self.font_size_spin)
        
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "System Default", "Arial", "Helvetica", "Times New Roman",
            "Courier New", "Verdana", "Georgia", "Comic Sans MS"
        ])
        font_layout.addRow("Семейство шрифта:", self.font_family_combo)
        
        font_widget = QWidget()
        font_widget.setLayout(font_layout)
        font_card.add_content(font_widget)
        layout.addWidget(font_card)
        
        # Добавляем вкладку в TabWidget
        self.tab_widget.addTab(scroll, "Внешний вид")

    def create_interface_tab(self):
        """Создание вкладки интерфейса"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Карточка панели инструментов
        toolbar_card = SettingsCard(
            "Панель инструментов",
            "Настройка отображения панели инструментов"
        )
        
        toolbar_layout = QVBoxLayout()
        
        self.show_toolbar_check = QCheckBox("Показывать панель инструментов")
        self.show_toolbar_check.setChecked(True)
        toolbar_layout.addWidget(self.show_toolbar_check)
          # Размер панели инструментов
        toolbar_size_layout = QHBoxLayout()
        toolbar_size_layout.addWidget(QLabel("Размер иконок:"))
        
        self.toolbar_size_combo = QComboBox()
        self.toolbar_size_combo.addItems(["Маленькая", "Средняя", "Большая"])
        self.toolbar_size_combo.setCurrentText("Средняя")
        toolbar_size_layout.addWidget(self.toolbar_size_combo)
        toolbar_size_layout.addStretch()
        toolbar_layout.addLayout(toolbar_size_layout)
        
        toolbar_layout.addStretch()
        
        toolbar_widget = QWidget()
        toolbar_widget.setLayout(toolbar_layout)
        toolbar_card.add_content(toolbar_widget)
        layout.addWidget(toolbar_card)
        
        # Карточка статусной строки
        status_card = SettingsCard(
            "Статусная строка",
            "Настройка информации в статусной строке"
        )
        
        status_layout = QVBoxLayout()
        
        self.show_status_check = QCheckBox("Показывать статусную строку")
        self.show_status_check.setChecked(True)
        status_layout.addWidget(self.show_status_check)
        
        self.show_memory_check = QCheckBox("Показывать использование памяти")
        self.show_memory_check.setChecked(False)
        status_layout.addWidget(self.show_memory_check)
        
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        status_card.add_content(status_widget)
        layout.addWidget(status_card)
        
        # Карточка окон
        windows_card = SettingsCard(
            "Окна",
            "Настройка поведения окон"
        )
        
        windows_layout = QVBoxLayout()
        
        self.remember_geometry_check = QCheckBox("Запоминать размер и положение окон")
        self.remember_geometry_check.setChecked(True)
        windows_layout.addWidget(self.remember_geometry_check)
        
        self.minimize_to_tray_check = QCheckBox("Сворачивать в системный трей")
        self.minimize_to_tray_check.setChecked(False)
        windows_layout.addWidget(self.minimize_to_tray_check)
        
        windows_widget = QWidget()
        windows_widget.setLayout(windows_layout)
        windows_card.add_content(windows_widget)
        layout.addWidget(windows_card)
        
        layout.addStretch()
        self.tab_widget.addTab(scroll, "Интерфейс")
    
    def create_advanced_tab(self):
        """Создание вкладки дополнительных настроек"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Карточка производительности
        performance_card = SettingsCard(
            "Производительность",
            "Настройки для оптимизации работы приложения"
        )
        
        perf_layout = QFormLayout()
        
        self.animation_check = QCheckBox("Включить анимации")
        self.animation_check.setChecked(True)
        perf_layout.addRow("Анимации:", self.animation_check)
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setValue(100)
        self.cache_size_spin.setSuffix(" МБ")
        perf_layout.addRow("Размер кэша:", self.cache_size_spin)
        
        perf_widget = QWidget()
        perf_widget.setLayout(perf_layout)
        performance_card.add_content(perf_widget)
        layout.addWidget(performance_card)
        
        # Карточка логирования
        logging_card = SettingsCard(
            "Логирование",
            "Настройка уровня детализации логов"
        )
        
        log_layout = QFormLayout()
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        log_layout.addRow("Уровень логирования:", self.log_level_combo)
        
        self.log_to_file_check = QCheckBox("Сохранять логи в файл")
        self.log_to_file_check.setChecked(True)
        log_layout.addRow("В файл:", self.log_to_file_check)
        
        log_widget = QWidget()
        log_widget.setLayout(log_layout)
        logging_card.add_content(log_widget)
        layout.addWidget(logging_card)
        
        # Карточка сброса настроек
        reset_card = SettingsCard(
            "Сброс настроек",
            "Восстановление настроек по умолчанию"
        )
        
        reset_layout = QHBoxLayout()
        self.reset_button = QPushButton("Сбросить все настройки")
        self.reset_button.clicked.connect(self.reset_settings)
        reset_layout.addWidget(self.reset_button)
        reset_layout.addStretch()
        
        reset_widget = QWidget()
        reset_widget.setLayout(reset_layout)
        reset_card.add_content(reset_widget)
        layout.addWidget(reset_card)
        
        layout.addStretch()
        self.tab_widget.addTab(scroll, "Дополнительно")
    
    def load_current_settings(self):
        """Загрузка текущих настроек"""
        print("🔧 load_current_settings() начат")
        try:
            if self.theme_manager:
                print("🔧 theme_manager существует")
                current_theme = self.theme_manager.get_current_theme()
                print(f"🔧 current_theme = {current_theme}")
                
                # Проверяем, что theme_combo существует и действителен
                if hasattr(self, 'theme_combo') and self.theme_combo:
                    try:
                        # Безопасная проверка валидности объекта
                        if not is_qt_object_valid(self.theme_combo):
                            print("⚠️ theme_combo недействителен, пропускаем установку текущей темы")
                            return
                        
                        print(f"🔧 theme_combo существует: {self.theme_combo}")
                        count = self.theme_combo.count()
                        print(f"🔧 theme_combo.count() = {count}")
                        
                        # Найти индекс текущей темы в комбобоксе
                        for i in range(count):
                            try:
                                if self.theme_combo.itemData(i) == current_theme:
                                    self.theme_combo.setCurrentIndex(i)
                                    print(f"🔧 Установлен индекс темы: {i}")
                                    break
                            except Exception as e:
                                print(f"⚠️ Ошибка при получении данных из theme_combo: {e}")
                                break
                    except RuntimeError as e:
                        if "Internal C++ object" in str(e):
                            print(f"⚠️ C++ объект QComboBox уже удален: {e}")
                        else:
                            print(f"❌ Ошибка при работе с theme_combo: {e}")
                    except Exception as e:
                        print(f"❌ Ошибка при работе с theme_combo: {e}")
                        print(f"❌ Тип ошибки: {type(e)}")
                else:
                    print("❌ theme_combo не существует или был удален!")
                
                # Устанавливаем темный режим если у менеджера тем есть соответствующий атрибут
                try:
                    if hasattr(self, 'dark_mode_check') and hasattr(self.theme_manager, '_current_variant'):
                        # Проверяем, что dark_mode_check действителен
                        if not is_qt_object_valid(self.dark_mode_check):
                            print("⚠️ dark_mode_check недействителен, пропускаем установку темного режима")
                            return
                            
                        self.dark_mode_check.setChecked(self.theme_manager._current_variant == "dark")
                        print(f"🔧 Установлен темный режим: {self.theme_manager._current_variant == 'dark'}")
                except Exception as e:
                    print(f"❌ Ошибка при установке темного режима: {e}")
        except Exception as e:
            print(f"⚠️ Ошибка открытия настроек: {e}")
            
        print("🔧 load_current_settings() завершен")
    
    def collect_settings(self) -> dict:
        """Сбор всех настроек из интерфейса"""
        settings = {}
        try:
            # Безопасное получение значений из виджетов
            if is_qt_object_valid(self.theme_combo):
                settings['theme'] = self.theme_combo.currentData()
            if is_qt_object_valid(self.dark_mode_check):
                settings['dark_mode'] = self.dark_mode_check.isChecked()
            if is_qt_object_valid(self.font_size_spin):
                settings['font_size'] = self.font_size_spin.value()
            if is_qt_object_valid(self.font_family_combo):
                settings['font_family'] = self.font_family_combo.currentText()
            if is_qt_object_valid(self.show_toolbar_check):
                settings['show_toolbar'] = self.show_toolbar_check.isChecked()
            if is_qt_object_valid(self.toolbar_size_combo):
                settings['toolbar_size'] = self.toolbar_size_combo.currentText()
            if is_qt_object_valid(self.show_status_check):
                settings['show_status'] = self.show_status_check.isChecked()
            if is_qt_object_valid(self.show_memory_check):
                settings['show_memory'] = self.show_memory_check.isChecked()
            if is_qt_object_valid(self.remember_geometry_check):
                settings['remember_geometry'] = self.remember_geometry_check.isChecked()
            if is_qt_object_valid(self.minimize_to_tray_check):
                settings['minimize_to_tray'] = self.minimize_to_tray_check.isChecked()
            if is_qt_object_valid(self.animation_check):
                settings['animations'] = self.animation_check.isChecked()
            if is_qt_object_valid(self.cache_size_spin):
                settings['cache_size'] = self.cache_size_spin.value()
            if is_qt_object_valid(self.log_level_combo):
                settings['log_level'] = self.log_level_combo.currentText()
            if is_qt_object_valid(self.log_to_file_check):
                settings['log_to_file'] = self.log_to_file_check.isChecked()
        except Exception as e:
            print(f"⚠️ Ошибка при сборе настроек: {e}")
            
        return settings
    
    # События мыши для перетаскивания безрамочного окна
    def mousePressEvent(self, event):
        """Обработка нажатия кнопки мыши для начала перетаскивания"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Обработка движения мыши для перетаскивания окна"""
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_position is not None:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Обработка отпускания кнопки мыши для завершения перетаскивания"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = None
            event.accept()
    
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
                
                # Применяем тему также к диалогу настроек для мгновенного обновления
                self._update_dialog_theme()
                
                # Сигнал изменения темы
                self.themeChanged.emit(theme_name)
            
            # Испускание сигнала для передачи настроек в основное окно
            self.settings_applied.emit(self.settings)
        except Exception as e:
            print(f"⚠️ Ошибка при применении настроек: {e}")
    
    def _update_dialog_theme(self):
        """Обновляет тему диалога настроек, применяя текущие цвета из менеджера тем"""
        try:
            if self.theme_manager:
                # Получаем данные текущей темы
                current_theme_data = self.theme_manager.get_current_theme_data()
                if current_theme_data:
                    main_color = current_theme_data.get('main_color', '#f8f9fa')
                    text_color = current_theme_data.get('text_color', '#212529')
                    
                    # Определяем текст на основе яркости фона
                    is_light_bg = self._is_light_color(main_color)
                    button_text_color = "#1a1a1a" if is_light_bg else "#ffffff"
                    
                    # Обновляем стили всех виджетов
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
                        }}
                        QTabBar::tab:selected {{
                            background-color: {main_color}cc;
                        }}
                        QTabBar::tab:hover {{
                            background-color: {main_color}dd;
                        }}
                        SettingsCard {{
                            background-color: {main_color}cc;
                            border: 1px solid #dee2e6;
                            border-radius: 8px;
                            padding: 12px;
                            margin: 4px;
                        }}
                        SettingsCard:hover {{
                            background-color: {main_color}ee;
                        }}
                        SettingsCard:pressed {{
                            background-color: {main_color}dd;
                        }}
                        SettingsCard:disabled {{
                            background-color: {main_color}66;
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
                            background-color: {main_color}dd;
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
                        QScrollArea, QScrollBar {{
                            background-color: {main_color};
                            border: none;
                        }}
                    """)
                    
                    # Принудительно обновляем все дочерние виджеты
                    for child in self.findChildren(QWidget):
                        if is_qt_object_valid(child):
                            child.update()
                    
                    # Обновляем также сам диалог
                    self.update()
        except Exception as e:
            print(f"⚠️ Ошибка при обновлении темы диалога: {e}")
    
    def accept_settings(self):
        """Принятие и применение настроек с закрытием диалога"""
        try:
            self.apply_settings()
            self.accept()
        except Exception as e:
            print(f"⚠️ Ошибка при принятии настроек: {e}")
    
    def reset_settings(self):
        """Сброс настроек к значениям по умолчанию"""
        try:
            # Сброс темы
            if is_qt_object_valid(self.theme_combo) and self.theme_combo.count() > 0:
                self.theme_combo.setCurrentIndex(0)
            
            # Сброс темного режима
            if is_qt_object_valid(self.dark_mode_check):
                self.dark_mode_check.setChecked(False)
            
            # Сброс других настроек
            if is_qt_object_valid(self.font_size_spin):
                self.font_size_spin.setValue(10)
            if is_qt_object_valid(self.font_family_combo):
                self.font_family_combo.setCurrentIndex(0)
            if is_qt_object_valid(self.show_toolbar_check):
                self.show_toolbar_check.setChecked(True)
            if is_qt_object_valid(self.toolbar_size_combo):
                self.toolbar_size_combo.setCurrentText("Средняя")
            if is_qt_object_valid(self.show_status_check):
                self.show_status_check.setChecked(True)
            if is_qt_object_valid(self.show_memory_check):
                self.show_memory_check.setChecked(False)
            if is_qt_object_valid(self.remember_geometry_check):
                self.remember_geometry_check.setChecked(True)
            if is_qt_object_valid(self.minimize_to_tray_check):
                self.minimize_to_tray_check.setChecked(False)
            if is_qt_object_valid(self.animation_check):
                self.animation_check.setChecked(True)
            if is_qt_object_valid(self.cache_size_spin):
                self.cache_size_spin.setValue(100)
            if is_qt_object_valid(self.log_level_combo):
                self.log_level_combo.setCurrentText("INFO")
            if is_qt_object_valid(self.log_to_file_check):
                self.log_to_file_check.setChecked(True)
        except Exception as e:
            print(f"⚠️ Ошибка при сбросе настроек: {e}")
