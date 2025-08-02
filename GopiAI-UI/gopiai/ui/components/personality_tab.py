#!/usr/bin/env python3
"""
Personality Tab для GopiAI UI
Вкладка для редактирования описания ассистента Гипатии
"""

import logging
import os
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QPlainTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

# Импорт системы иконок
try:
    from ..components.icon_file_system_model import UniversalIconManager
    icon_manager = UniversalIconManager.instance()
except ImportError:
    icon_manager = None

logger = logging.getLogger(__name__)

class PersonalityTab(QWidget):
    """Вкладка для редактирования персонализации Гипатии"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.system_prompts_file = None
        self.personality_start_line = 72  # Строка начала описания Гипатии
        self.personality_end_line = 150   # Строка окончания описания Гипатии
        
        self._find_system_prompts_file()
        self._setup_ui()
        self._setup_connections()
        self._load_personality_text()
        
        logger.info("PersonalityTab инициализирован")
    
    def _find_system_prompts_file(self):
        """Находит файл system_prompts.py"""
        try:
            # Пробуем найти файл system_prompts.py
            possible_paths = [
                # Относительно текущего файла
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                    "GopiAI-CrewAI", "tools", "gopiai_integration", "system_prompts.py"
                ),
                # Абсолютный путь
                r"c:\Users\crazy\GOPI_AI_MODULES\GopiAI-CrewAI\tools\gopiai_integration\system_prompts.py"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.system_prompts_file = path
                    logger.info(f"Найден файл system_prompts.py: {path}")
                    break
            
            if not self.system_prompts_file:
                logger.error("Файл system_prompts.py не найден")
                
        except Exception as e:
            logger.error(f"Ошибка поиска system_prompts.py: {e}")
    
    def _setup_ui(self):
        """Настраивает пользовательский интерфейс"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Заголовок
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Персонализация Гипатии")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Описание
        desc_label = QLabel("Здесь вы можете редактировать личность и характер ассистента Гипатии.")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Текстовое поле для редактирования
        self.personality_editor = QPlainTextEdit()
        self.personality_editor.setPlaceholderText("Загрузка текста персонализации...")
        
        # Устанавливаем шрифт для лучшей читаемости
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        self.personality_editor.setFont(font)
        
        layout.addWidget(self.personality_editor)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Загрузить")
        self.load_btn.setToolTip("Загрузить текст персонализации из файла")
        if icon_manager:
            load_icon = icon_manager.get_icon("folder-open")
            if not load_icon.isNull():
                self.load_btn.setIcon(load_icon)
        buttons_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setToolTip("Сохранить изменения в файл")
        if icon_manager:
            save_icon = icon_manager.get_icon("save")
            if not save_icon.isNull():
                self.save_btn.setIcon(save_icon)
        buttons_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("Сброс")
        self.reset_btn.setToolTip("Сбросить к исходному тексту")
        if icon_manager:
            reset_icon = icon_manager.get_icon("rotate-ccw")
            if not reset_icon.isNull():
                self.reset_btn.setIcon(reset_icon)
        buttons_layout.addWidget(self.reset_btn)
        
        buttons_layout.addStretch()
        
        # Статус
        self.status_label = QLabel("Готов к редактированию")
        buttons_layout.addWidget(self.status_label)
        
        layout.addLayout(buttons_layout)
    
    def _setup_connections(self):
        """Настраивает соединения сигналов"""
        self.load_btn.clicked.connect(self._load_personality_text)
        self.save_btn.clicked.connect(self._save_personality_text)
        self.reset_btn.clicked.connect(self._reset_personality_text)
    
    def _load_personality_text(self):
        """Загружает текст персонализации из файла"""
        if not self.system_prompts_file or not os.path.exists(self.system_prompts_file):
            self.status_label.setText("Ошибка: файл system_prompts.py не найден")
            return
        
        try:
            with open(self.system_prompts_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Извлекаем строки с описанием Гипатии (строки 72-150)
            if len(lines) >= self.personality_end_line:
                personality_lines = lines[self.personality_start_line-1:self.personality_end_line]
                personality_text = ''.join(personality_lines)
                
                # Убираем тройные кавычки, если есть
                personality_text = personality_text.strip()
                if personality_text.startswith('"""'):
                    personality_text = personality_text[3:]
                if personality_text.endswith('"""'):
                    personality_text = personality_text[:-3]
                
                self.personality_editor.setPlainText(personality_text.strip())
                self.status_label.setText("Текст загружен успешно")
                logger.info("Текст персонализации загружен")
            else:
                self.status_label.setText("Ошибка: файл слишком короткий")
                
        except Exception as e:
            self.status_label.setText(f"Ошибка загрузки: {e}")
            logger.error(f"Ошибка загрузки персонализации: {e}")
    
    def _save_personality_text(self):
        """Сохраняет изменения в файл"""
        if not self.system_prompts_file or not os.path.exists(self.system_prompts_file):
            self.status_label.setText("Ошибка: файл system_prompts.py не найден")
            return
        
        # Подтверждение сохранения
        reply = QMessageBox.question(
            self, 
            "Подтверждение сохранения",
            "Вы уверены, что хотите сохранить изменения в system_prompts.py?\n\nЭто изменит поведение ассистента Гипатии.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Читаем весь файл
            with open(self.system_prompts_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Получаем новый текст персонализации
            new_personality_text = self.personality_editor.toPlainText()
            
            # Форматируем новый текст (добавляем отступы и структуру)
            formatted_lines = []
            for line in new_personality_text.split('\n'):
                formatted_lines.append(line + '\n')
            
            # Заменяем строки с описанием Гипатии
            if len(lines) >= self.personality_end_line:
                # Заменяем строки 72-150
                new_lines = (
                    lines[:self.personality_start_line-1] + 
                    formatted_lines + 
                    lines[self.personality_end_line:]
                )
                
                # Сохраняем файл
                with open(self.system_prompts_file, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                
                self.status_label.setText("Изменения сохранены успешно")
                logger.info("Персонализация сохранена в system_prompts.py")
                
                # Показываем сообщение об успехе
                QMessageBox.information(
                    self,
                    "Сохранение завершено",
                    "Изменения персонализации Гипатии сохранены.\n\nДля применения изменений может потребоваться перезапуск системы."
                )
            else:
                self.status_label.setText("Ошибка: неверная структура файла")
                
        except Exception as e:
            self.status_label.setText(f"Ошибка сохранения: {e}")
            logger.error(f"Ошибка сохранения персонализации: {e}")
            
            QMessageBox.critical(
                self,
                "Ошибка сохранения",
                f"Не удалось сохранить изменения:\n\n{e}"
            )
    
    def _reset_personality_text(self):
        """Сбрасывает текст к исходному состоянию"""
        reply = QMessageBox.question(
            self,
            "Подтверждение сброса",
            "Вы уверены, что хотите сбросить все изменения?\n\nВсе несохраненные изменения будут потеряны.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._load_personality_text()
            logger.info("Текст персонализации сброшен")


def test_personality_tab():
    """Тестовая функция для вкладки персонализации"""
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = PersonalityTab()
    widget.setWindowTitle("Personality Tab Test")
    widget.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    test_personality_tab()
