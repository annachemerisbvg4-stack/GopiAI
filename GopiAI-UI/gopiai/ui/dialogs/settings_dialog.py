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

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QCheckBox, QFormLayout, QSpinBox, 
    QTabWidget, QPushButton
)


# Класс для карточки настроек
class SettingsCard(QWidget):
    def __init__(self, title, description="", parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsCard")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(8)
        
        # Заголовок
        self.title_label = QLabel(title)
        self.title_label.setObjectName("SettingsCardTitle")
        self.title_label.setProperty("class", "settings-card-title")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.main_layout.addWidget(self.title_label)
        
        # Описание
        if description:
            self.description_label = QLabel(description)
            self.description_label.setObjectName("SettingsCardDescription")
            self.description_label.setProperty("class", "settings-card-description")
            self.description_label.setStyleSheet("color: #666; font-size: 12px;")
            self.main_layout.addWidget(self.description_label)
        
        # Контейнер для контента
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 8, 0, 0)
        self.main_layout.addWidget(self.content_container)
    
    def add_content(self, widget):
        """Добавить виджет с контентом в карточку"""
        self.content_layout.addWidget(widget)


class GopiAISettingsDialog(QDialog):
    """Settings dialog for GopiAI"""
    settings_applied = Signal(dict)  # Signal for when settings are applied
    themeChanged = Signal(str)       # Signal for theme changes
    
    # Dialog codes
    class DialogCode:
        Accepted = 1
        Rejected = 0
    
    def __init__(self, parent=None, theme_manager=None):
        """Инициализация диалога настроек
        
        Args:
            parent: Родительский виджет
            theme_manager: Менеджер тем приложения
        """
        super().__init__(parent)
        self.theme_manager = theme_manager
        # Словарь для хранения настроек
        self.settings = {}
        
        # Инициализация tab_widget
        self.tab_widget = QTabWidget()

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

# Удалена функция sip_is_deleted, так как она заменена на is_qt_object_valid

# Удалено дублирующее определение класса GopiAISettingsDialog

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
        self.create_appearance_tab()
        self.create_general_tab()
        
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
        if self.theme_manager:            # Получаем цвета из текущей темы
            current_theme_data = self.theme_manager.get_current_theme_data()
            if current_theme_data:
                main_color = current_theme_data.get('main_color', '#f8f9fa')
                text_color = current_theme_data.get('text_color', '#212529')
                accent_color = current_theme_data.get('accent_color', '#4dabf7')
                
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
                        width: 12px;
                        margin: 0px;
                        border-radius: 6px;
                    }}
                    QScrollBar::handle:vertical {{
                        background-color: {text_color}44;
                        min-height: 20px;
                        border-radius: 6px;
                    }}
                    QScrollBar::handle:vertical:hover {{
                        background-color: {text_color}88;
                    }}
                    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                        height: 0px;
                    }}
                """)

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
        # Подключаем обработчик изменения темы для предпросмотра
        self.theme_combo.currentIndexChanged.connect(self._preview_theme_change)
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
        # Подключаем обработчик изменения темного режима для предпросмотра
        self.dark_mode_check.toggled.connect(self._preview_theme_change)
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

    def create_general_tab(self):
        """Создание вкладки общих настроек"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)
        
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        # Карточка общих настроек
        general_card = SettingsCard(
            "Общие настройки",
            "Основные настройки приложения"
        )
        
        general_layout = QFormLayout()
        
        # Настройки автосохранения
        self.autosave_check = QCheckBox()
        self.autosave_check.setChecked(True)
        general_layout.addRow("Автосохранение:", self.autosave_check)
        
        # Интервал автосохранения
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(1, 60)
        self.autosave_interval.setValue(5)
        self.autosave_interval.setSuffix(" мин")
        general_layout.addRow("Интервал автосохранения:", self.autosave_interval)
        
        general_widget = QWidget()
        general_widget.setLayout(general_layout)
        general_card.add_content(general_widget)
        layout.addWidget(general_card)
        
        # Добавляем вкладку в TabWidget
        self.tab_widget.addTab(scroll, "Общие")

    def _preview_theme_change(self):
        """Предварительный просмотр изменения темы без применения к приложению"""
        try:
            # Только если у нас есть менеджер тем и выбрана тема
            if not self.theme_manager or not is_qt_object_valid(self.theme_combo):
                return
                
            # Получаем выбранную тему
            selected_theme = self.theme_combo.currentData()
            if not selected_theme:
                return
                
            # Получаем данные темы
            theme_data = self.theme_manager.get_theme_data(selected_theme)
            if not theme_data:
                return
                
            # Учитываем темный режим
            is_dark_mode = False
            if is_qt_object_valid(self.dark_mode_check):
                is_dark_mode = self.dark_mode_check.isChecked()
                
            # Получаем цвета с учетом темного режима
            variant = "dark" if is_dark_mode else "light"
            main_color = theme_data.get(f'{variant}_main_color', theme_data.get('main_color', '#f8f9fa'))
            text_color = theme_data.get(f'{variant}_text_color', theme_data.get('text_color', '#212529'))
            accent_color = theme_data.get(f'{variant}_accent_color', theme_data.get('accent_color', '#4dabf7'))
            
            # Применяем стили только к диалогу настроек для предпросмотра
            self._apply_theme_to_dialog(main_color, text_color, accent_color)
        except Exception as e:
            print(f"⚠️ Ошибка при предпросмотре темы: {e}")
            
    def _apply_theme_to_dialog(self, main_color, text_color, accent_color='#4dabf7'):
        """Применяет указанные цвета темы к диалогу настроек"""
        try:
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
                    width: 12px;
                    margin: 0px;
                    border-radius: 6px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {text_color}44;
                    min-height: 20px;
                    border-radius: 6px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: {text_color}88;
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
            """)
            
            # Принудительно обновляем все дочерние виджеты
            for child in self.findChildren(QWidget):
                if is_qt_object_valid(child):
                    child.update()
            
            # Обновляем также сам диалог
            self.update()
        except Exception as e:
            print(f"⚠️ Ошибка при применении темы к диалогу: {e}")

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
                
                # Получаем актуальные данные темы после применения
                current_theme_data = self.theme_manager.get_current_theme_data()
                if current_theme_data:
                    variant = "dark" if self.settings.get('dark_mode', False) else "light"
                    main_color = current_theme_data.get(f'{variant}_main_color', current_theme_data.get('main_color', '#f8f9fa'))
                    text_color = current_theme_data.get(f'{variant}_text_color', current_theme_data.get('text_color', '#212529'))
                    accent_color = current_theme_data.get(f'{variant}_accent_color', current_theme_data.get('accent_color', '#4dabf7'))
                    
                    # Применяем тему к диалогу настроек
                    self._apply_theme_to_dialog(main_color, text_color, accent_color)
                
                # Сигнал изменения темы
                self.themeChanged.emit(theme_name)
            
            # Испускание сигнала для передачи настроек в основное окно
            self.settings_applied.emit(self.settings)
        except Exception as e:
            print(f"⚠️ Ошибка при применении настроек: {e}")
        
    def _update_dialog_theme(self):
        """Устаревший метод, используйте _apply_theme_to_dialog"""
        try:
            if self.theme_manager:
                # Получаем данные текущей темы
                current_theme_data = self.theme_manager.get_current_theme_data()
                if current_theme_data:
                    # Определяем вариант (светлый/темный)
                    variant = "dark" if hasattr(self.theme_manager, '_current_variant') and self.theme_manager._current_variant == "dark" else "light"
                    
                    # Получаем цвета с учетом варианта
                    main_color = current_theme_data.get(f'{variant}_main_color', current_theme_data.get('main_color', '#f8f9fa'))
                    text_color = current_theme_data.get(f'{variant}_text_color', current_theme_data.get('text_color', '#212529'))
                    accent_color = current_theme_data.get(f'{variant}_accent_color', current_theme_data.get('accent_color', '#4dabf7'))
                    
                    # Применяем тему к диалогу
                    self._apply_theme_to_dialog(main_color, text_color, accent_color)
        except Exception as e:
            print(f"⚠️ Ошибка при обновлении темы диалога: {e}")
        print("🔧 _update_dialog_theme() завершен")

    def collect_settings(self):
        """Сбор настроек из UI элементов"""
        settings = {}
        
        # Сбор настроек темы
        if hasattr(self, 'theme_combo') and is_qt_object_valid(self.theme_combo):
            settings['theme'] = self.theme_combo.currentData()
        
        # Сбор настройки темного режима
        if hasattr(self, 'dark_mode_check') and is_qt_object_valid(self.dark_mode_check):
            settings['dark_mode'] = self.dark_mode_check.isChecked()
            
        # Сбор настроек шрифта
        if hasattr(self, 'font_size_spin') and is_qt_object_valid(self.font_size_spin):
            settings['font_size'] = self.font_size_spin.value()
            
        if hasattr(self, 'font_family_combo') and is_qt_object_valid(self.font_family_combo):
            settings['font_family'] = self.font_family_combo.currentText()
            
        return settings