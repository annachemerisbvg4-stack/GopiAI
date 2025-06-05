"""
Theme Selector Dialog для GopiAI Standalone Interface
==================================================

Диалог выбора темы из коллекции GopiAI с предпросмотром и применением.
"""

import os
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QFrame, QGridLayout, QWidget, QScrollArea,
    QButtonGroup, QRadioButton, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor


class ThemePreviewWidget(QFrame):
    """Виджет предпросмотра темы"""
    
    def __init__(self, theme_data: Dict[str, Any], mode: str = "light"):
        super().__init__()
        self.theme_data = theme_data
        self.mode = mode
        self.setFixedSize(120, 80)
        self.setFrameStyle(QFrame.Shape.Box)
        self._setup_preview()
    
    def _setup_preview(self):
        """Настройка предпросмотра темы"""
        if not self.theme_data or self.mode not in self.theme_data:
            self.setStyleSheet("background-color: #cccccc; border: 1px solid #888;")
            return
        
        colors = self.theme_data[self.mode]
        
        style = f"""
        QFrame {{
            background-color: {colors.get('main_color', '#ffffff')};
            border: 2px solid {colors.get('border_color', '#cccccc')};
        }}
        """
        self.setStyleSheet(style)
        
        # Добавляем элементы для предпросмотра
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Заголовок
        header = QLabel("Пример")
        header.setStyleSheet(f"color: {colors.get('titlebar_text', '#000000')}; font-weight: bold;")
        layout.addWidget(header)
        
        # Кнопка
        button = QPushButton("Кнопка")
        button.setStyleSheet(f"""
        QPushButton {{
            background-color: {colors.get('button_color', '#0078d4')};
            color: {colors.get('button_text', '#ffffff')};
            border: none;
            padding: 2px 8px;
            border-radius: 2px;
        }}
        """)
        layout.addWidget(button)


class ThemeSelectorDialog(QDialog):
    """Диалог выбора темы GopiAI"""
    
    # Сигналы
    theme_applied = Signal(dict, str)  # theme_data, mode
    
    def __init__(self, parent=None, current_theme=None):
        super().__init__(parent)
        self.current_theme = current_theme
        self.selected_theme = None
        self.selected_mode = "light"
        self._setup_ui()
        self._load_themes()
        self._connect_signals()
    
    def _setup_ui(self):
        """Настройка интерфейса диалога"""
        self.setWindowTitle("🎨 Выбор темы GopiAI")
        self.setModal(True)
        self.resize(600, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Заголовок
        title = QLabel("Выберите тему из коллекции GopiAI")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Центральная область
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)
        
        # Левая панель - список тем
        left_panel = QGroupBox("Темы")
        left_layout = QVBoxLayout(left_panel)
        
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumHeight(30)
        left_layout.addWidget(self.theme_combo)
        
        # Режим темы
        mode_group = QGroupBox("Режим")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_group = QButtonGroup(self)
        self.light_radio = QRadioButton("☀️ Светлая")
        self.dark_radio = QRadioButton("🌙 Тёмная")
        
        self.mode_group.addButton(self.light_radio, 0)
        self.mode_group.addButton(self.dark_radio, 1)
        
        mode_layout.addWidget(self.light_radio)
        mode_layout.addWidget(self.dark_radio)
        
        left_layout.addWidget(mode_group)
        left_layout.addStretch()
        
        content_layout.addWidget(left_panel)
        
        # Правая панель - предпросмотр
        right_panel = QGroupBox("Предпросмотр")
        right_layout = QVBoxLayout(right_panel)
        
        # Сохраняем ссылку на layout для предпросмотра
        self.preview_layout = right_layout
        
        self.preview_widget = ThemePreviewWidget({})
        right_layout.addWidget(self.preview_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Информация о теме
        self.theme_info = QLabel("Выберите тему для предпросмотра")
        self.theme_info.setWordWrap(True)
        self.theme_info.setStyleSheet("padding: 10px; background-color: #f5f5f5; border-radius: 4px;")
        right_layout.addWidget(self.theme_info)
        
        right_layout.addStretch()
        content_layout.addWidget(right_panel)
        
        # Кнопки действий
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("✅ Применить тему")
        self.apply_btn.setMinimumHeight(35)
        self.apply_btn.setStyleSheet("""
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        """)
        
        self.preview_btn = QPushButton("👀 Предпросмотр")
        self.preview_btn.setMinimumHeight(35)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setMinimumHeight(35)
        
        button_layout.addWidget(self.preview_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # Подключение кнопок
        self.apply_btn.clicked.connect(self._apply_theme)
        self.preview_btn.clicked.connect(self._preview_theme)
        cancel_btn.clicked.connect(self.reject)
          # По умолчанию светлая тема
        self.light_radio.setChecked(True)
        
    def _load_themes(self):
        """Загрузка доступных тем"""
        # Попробуем импортировать все темы из GopiAI-Core
        themes = []
        try:
            # Прямой импорт через sys.path (так как в путях есть дефисы)
            import sys
            import os
            theme_path = os.path.join(os.path.dirname(__file__), '..', 'GopiAI-Core', 'gopiai', 'core')
            if theme_path not in sys.path:
                sys.path.append(theme_path)
            from utils.simple_theme_manager import THEME_COLLECTION
        except ImportError as e:
            print(f"⚠️ Не удалось импортировать THEME_COLLECTION ({e}), используем fallback темы")
            THEME_COLLECTION = [
                {
                    "name": "Material Sky",
                    "description": "Тема, основанная на Material Design",
                    "light": {
                        "main_color": "#fcf8f8",
                        "text_color": "#1c1b1c",
                        "button_color": "#3d6281",
                        "button_text": "#ffffff",
                        "border_color": "#75777b",
                        "titlebar_text": "#001d31"
                    },
                    "dark": {
                        "main_color": "#131314",
                        "text_color": "#e5e2e2",
                        "button_color": "#a5caee",
                        "button_text": "#ffffff",
                        "border_color": "#8f9195",
                        "titlebar_text": "#cde5ff"
                    }
                },
                {
                    "name": "Emerald Garden",
                    "description": "Зелёная природная тема",
                    "light": {
                        "main_color": "#f8fff8",
                        "text_color": "#1b5e20",
                        "button_color": "#4caf50",
                        "button_text": "#ffffff",
                        "border_color": "#c8e6c9",
                        "titlebar_text": "#2e7d32"
                    },
                    "dark": {
                        "main_color": "#0d1f0d",
                        "text_color": "#c8e6c9",
                        "button_color": "#4caf50",
                        "button_text": "#ffffff",
                        "border_color": "#2e7d32",
                        "titlebar_text": "#a5d6a7"
                    }
                }
            ]

        # Используем полную коллекцию тем
        for theme_data in THEME_COLLECTION:
            theme_name = theme_data.get("name", "Неизвестная тема")
            themes.append((theme_name, theme_data))
        print(f"✅ Загружено {len(themes)} тем из THEME_COLLECTION")
        # Добавляем темы в комбобокс
        for name, theme_data in themes:
            emoji = self._get_theme_emoji(theme_data)
            self.theme_combo.addItem(f"{emoji} {name}", theme_data)
    
    def _get_theme_emoji(self, theme_data):
        """Получить эмодзи для темы на основе её названия"""
        name = theme_data.get("name", "").lower()
        
        emoji_map = {
            "material sky": "☁️",
            "emerald garden": "🌿", 
            "crimson relic": "🌹",
            "golden ember": "🔥",
            "sunlit meadow": "🌻",
            "mint frost": "🌨️",
            "violet dream": "💜",
            "indigo candy": "🍭",
            "pink mirage": "🌸",
            "olive library": "📚",
            "lavender mist": "🌾",
            "graphite night": "🌙",
            "pumpkin field": "🎃",
            "scarlet fire": "❤️",
            "tropical bouquet": "🌺",
        }
        
        return emoji_map.get(name, "🎨")
    
    def _connect_signals(self):
        """Подключение сигналов"""
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        self.mode_group.buttonClicked.connect(self._on_mode_changed)
    
    def _on_theme_changed(self):
        """Обработка изменения темы"""
        self.selected_theme = self.theme_combo.currentData()
        self._update_preview()
        self._update_theme_info()
    def _on_mode_changed(self):
        """Обработка изменения режима"""
        self.selected_mode = "light" if self.light_radio.isChecked() else "dark"
        self._update_preview()
    
    def _update_preview(self):
        """Обновление предпросмотра"""
        if self.selected_theme:
            # Просто пересоздаем виджет предпросмотра без сложного layout mangling
            self.preview_widget.deleteLater()
            self.preview_widget = ThemePreviewWidget(self.selected_theme, self.selected_mode)
            
            # Находим контейнер для предпросмотра и добавляем новый виджет
            if hasattr(self, 'preview_layout'):
                self.preview_layout.addWidget(self.preview_widget, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def _update_theme_info(self):
        """Обновление информации о теме"""
        if self.selected_theme:
            name = self.selected_theme.get("name", "Неизвестная тема")
            description = self.selected_theme.get("description", "Описание недоступно")
            
            mode_colors = self.selected_theme.get(self.selected_mode, {})
            
            info_text = f"""
            <b>{name}</b><br>
            <i>{description}</i><br><br>
            <b>Режим:</b> {"Светлый" if self.selected_mode == "light" else "Тёмный"}<br>
            <b>Основной цвет:</b> {mode_colors.get('main_color', 'N/A')}<br>
            <b>Цвет кнопок:</b> {mode_colors.get('button_color', 'N/A')}
            """
            
            self.theme_info.setText(info_text)
        else:
            self.theme_info.setText("Выберите тему для предпросмотра")
    
    def _preview_theme(self):
        """Предпросмотр темы (временное применение)"""
        if self.selected_theme:
            self.theme_applied.emit(self.selected_theme, self.selected_mode)
            QMessageBox.information(self, "Предпросмотр", 
                f"Тема '{self.selected_theme['name']}' временно применена для предпросмотра")
    
    def _apply_theme(self):
        """Применение выбранной темы"""
        if self.selected_theme:
            self.theme_applied.emit(self.selected_theme, self.selected_mode)
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите тему")
    
    def get_selected_theme(self):
        """Получение выбранной темы"""
        return self.selected_theme, self.selected_mode


def show_theme_selector(parent=None, current_theme=None):
    """
    Показать диалог выбора темы
    
    Args:
        parent: Родительский виджет
        current_theme: Текущая тема
        
    Returns:
        Tuple (theme_data, mode) или None если отменено
    """
    dialog = ThemeSelectorDialog(parent, current_theme)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_selected_theme()
    
    return None
