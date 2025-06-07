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
        self.setStyleSheet("""
            SettingsCard {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 12px;
                margin: 4px;
            }
            SettingsCard:hover {
                background-color: #e9ecef;
            }
        """)
        
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
            desc_label.setStyleSheet("color: #6c757d; font-size: 9pt;")
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
    
    def __init__(self, theme_manager=None, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.settings = {}
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Настройки GopiAI")
        self.setMinimumSize(600, 500)
        self.resize(800, 600)
        
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
        header_layout.addStretch()
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
        
        # Заполнение списка тем
        if self.theme_manager:
            themes = self.theme_manager.get_theme_display_names()
            for theme_key, display_name in themes.items():
                self.theme_combo.addItem(display_name, theme_key)
        
        theme_combo_layout.addWidget(self.theme_combo)
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
        
        # Карточка цветов
        colors_card = SettingsCard(
            "Цвета",
            "Настройка цветовой схемы"
        )
        
        colors_layout = QFormLayout()
        
        self.accent_color_combo = QComboBox()
        self.accent_color_combo.addItems([
            "Синий", "Зелёный", "Красный", "Фиолетовый", 
            "Оранжевый", "Серый"
        ])
        colors_layout.addRow("Акцентный цвет:", self.accent_color_combo)
        
        colors_widget = QWidget()
        colors_widget.setLayout(colors_layout)
        colors_card.add_content(colors_widget)
        layout.addWidget(colors_card)
        
        layout.addStretch()
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
        
        self.toolbar_size_combo = QComboBox()
        self.toolbar_size_combo.addItems(["Маленькая", "Средняя", "Большая"])
        self.toolbar_size_combo.setCurrentText("Средняя")
        toolbar_size_layout = QHBoxLayout()
        toolbar_size_layout.addWidget(QLabel("Размер иконок:"))
        toolbar_size_layout.addWidget(self.toolbar_size_combo)
        toolbar_size_layout.addStretch()
        toolbar_layout.addLayout(toolbar_size_layout)
        
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
        if self.theme_manager:
            current_theme = self.theme_manager.get_current_theme()
            # Найти индекс текущей темы в комбобоксе
            for i in range(self.theme_combo.count()):
                if self.theme_combo.itemData(i) == current_theme:
                    self.theme_combo.setCurrentIndex(i)
                    break
                    
            # Устанавливаем темный режим если у менеджера тем есть соответствующий атрибут
            if hasattr(self.theme_manager, '_current_variant'):
                self.dark_mode_check.setChecked(self.theme_manager._current_variant == "dark")
    
    def collect_settings(self) -> dict:
        """Сбор всех настроек из интерфейса"""
        settings = {
            'theme': self.theme_combo.currentData(),
            'dark_mode': self.dark_mode_check.isChecked(),  # Добавляем состояние темного режима
            'font_size': self.font_size_spin.value(),
            'font_family': self.font_family_combo.currentText(),
            'accent_color': self.accent_color_combo.currentText(),
            'show_toolbar': self.show_toolbar_check.isChecked(),
            'toolbar_size': self.toolbar_size_combo.currentText(),
            'show_status': self.show_status_check.isChecked(),
            'show_memory': self.show_memory_check.isChecked(),
            'remember_geometry': self.remember_geometry_check.isChecked(),
            'minimize_to_tray': self.minimize_to_tray_check.isChecked(),
            'animations': self.animation_check.isChecked(),
            'cache_size': self.cache_size_spin.value(),
            'log_level': self.log_level_combo.currentText(),
            'log_to_file': self.log_to_file_check.isChecked()
        }
        return settings
    
    def apply_settings(self):
        """Применение настроек"""
        self.settings = self.collect_settings()
        
        # Применение темы и темного режима
        if self.theme_manager and self.settings.get('theme'):
            theme_name = self.settings.get('theme')
            
            # Устанавливаем темный/светлый вариант в менеджере тем
            if hasattr(self.theme_manager, '_current_variant'):
                self.theme_manager._current_variant = "dark" if self.settings.get('dark_mode', False) else "light"
            
            # Применяем тему
            self.theme_manager.apply_theme(theme_name)
            
            # Сигнал изменения темы
            self.themeChanged.emit(theme_name)
        
        # Испускание сигнала для передачи настроек в основное окно
        self.settings_applied.emit(self.settings)
    
    def accept_settings(self):
        """Принятие и применение настроек с закрытием диалога"""
        self.apply_settings()
        self.accept()
    
    def reset_settings(self):
        """Сброс настроек к значениям по умолчанию"""
        # Сброс темы
        if self.theme_combo.count() > 0:
            self.theme_combo.setCurrentIndex(0)
        
        # Сброс других настроек
        self.font_size_spin.setValue(10)
        self.font_family_combo.setCurrentIndex(0)
        self.accent_color_combo.setCurrentIndex(0)
        self.show_toolbar_check.setChecked(True)
        self.toolbar_size_combo.setCurrentText("Средняя")
        self.show_status_check.setChecked(True)
        self.show_memory_check.setChecked(False)
        self.remember_geometry_check.setChecked(True)
        self.minimize_to_tray_check.setChecked(False)
        self.animation_check.setChecked(True)
        self.cache_size_spin.setValue(100)
        self.log_level_combo.setCurrentText("INFO")
        self.log_to_file_check.setChecked(True)
