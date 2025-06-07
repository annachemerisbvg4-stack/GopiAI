#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Менеджер тем для GopiAI UI

Обеспечивает интерфейс для работы с темами приложения. Предоставляет методы
для применения выбранной темы, получения текущей темы и получения списка доступных тем.
Интегрируется с simple_theme_manager.py для работы с предопределенными темами.
"""

import os
import json
import logging
from typing import Dict, Optional, Union, Any
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, QCoreApplication

# Импорт из простого менеджера тем - используем абсолютный импорт для избежания циклических зависимостей
import gopiai.ui.utils.simple_theme_manager as stm

# Настройка логирования
logger = logging.getLogger(__name__)

# Путь к файлу настроек
SETTINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "settings")
THEME_FILE = os.path.join(SETTINGS_DIR, "simple_theme.json")


class ThemeManager(QObject):
    """
    Класс для управления темами пользовательского интерфейса GopiAI.
    
    Предоставляет методы для применения темы, получения текущей темы
    и списка доступных тем. Интегрируется с simple_theme_manager.py.
    """
    
    themeChanged = Signal(str)  # Сигнал об изменении темы
    
    def __init__(self):
        """Инициализация менеджера тем"""
        super().__init__()
        self._current_theme = None
        self._current_variant = "light"
        
        # Инициализация текущей темы из файла настроек
        self._init_theme()
    
    def _init_theme(self):
        """Инициализация темы из файла настроек"""
        try:
            theme_data = stm.load_theme()
            if theme_data:
                if "name" in theme_data:
                    self._current_theme = theme_data["name"]
                if "variant" in theme_data:
                    self._current_variant = theme_data["variant"]
                logger.info(f"Загружена тема: {self._current_theme} ({self._current_variant})")
        except Exception as e:
            logger.error(f"Ошибка при инициализации темы: {e}")
    
    def apply_theme(self, theme_input: Union[str, QCoreApplication]) -> bool:
        """
        Применяет выбранную тему.
        
        Args:
            theme_input: Может быть строкой с именем темы или экземпляром QApplication/QCoreApplication
            
        Returns:
            bool: True, если тема успешно применена, иначе False
        """
        try:
            # Если передано имя темы в виде строки
            if isinstance(theme_input, str):
                theme_name = theme_input
                logger.info(f"Запрос на применение темы: {theme_name}")
                
                # Обработка специального случая "simple" - используем диалог выбора темы
                if theme_name.lower() == "simple":
                    app = QApplication.instance()
                    if app:
                        theme_data = stm.choose_theme_dialog(app)
                        if theme_data:
                            self._current_theme = theme_data.get("name")
                            self._current_variant = theme_data.get("variant", "light")
                            self.themeChanged.emit(self._current_theme)
                            return True
                    return False
                
                # Поиск темы в коллекции
                found = False
                for theme in stm.THEME_COLLECTION:
                    if theme["name"].lower() == theme_name.lower():
                        variant = self._current_variant  # Сохраняем текущий вариант (light/dark)
                        
                        if variant in theme:
                            theme_data = theme[variant].copy()
                            theme_data["name"] = theme["name"]
                            theme_data["variant"] = variant
                            
                            # Сохраняем тему
                            try:
                                os.makedirs(SETTINGS_DIR, exist_ok=True)
                                with open(THEME_FILE, 'w', encoding='utf-8') as f:
                                    json.dump(theme_data, f, indent=2)
                                
                                # Обновляем текущую тему
                                self._current_theme = theme["name"]
                                
                                # Применяем тему к приложению
                                app = QApplication.instance()
                                if app:
                                    result = stm.apply_theme(app)
                                    if result:
                                        self.themeChanged.emit(self._current_theme)
                                        return True
                            except Exception as e:
                                logger.error(f"Ошибка при сохранении темы: {e}")
                        
                        found = True
                        break
                
                if not found:
                    logger.warning(f"Тема не найдена: {theme_name}")
                    return False
            
            # Если передан экземпляр QApplication/QCoreApplication
            elif isinstance(theme_input, QCoreApplication):
                logger.info("Применение темы к QApplication/QCoreApplication")
                result = stm.apply_theme(theme_input)
                return result
            
            else:
                logger.error(f"Неподдерживаемый тип параметра: {type(theme_input)}")
                return False
            
        except Exception as e:
            logger.error(f"Ошибка при применении темы: {e}")
            return False
        
        return False
    
    def get_current_theme(self) -> Optional[str]:
        """
        Возвращает имя текущей темы.
        
        Returns:
            Optional[str]: Имя текущей темы или None, если тема не установлена
        """
        return self._current_theme
    
    def get_theme_display_names(self) -> Dict[str, str]:
        """
        Возвращает словарь с именами тем для отображения в интерфейсе.
        
        Returns:
            Dict[str, str]: Словарь вида {ключ_темы: отображаемое_имя}
        """
        theme_names = {}
        
        for theme in stm.THEME_COLLECTION:
            # Используем имя темы и как ключ, и как отображаемое имя
            theme_names[theme["name"]] = theme["name"]
        
        return theme_names
    
    def show_theme_dialog(self) -> bool:
        """
        Показывает диалог выбора темы.
        
        Returns:
            bool: True, если тема была выбрана и применена, иначе False
        """
        try:
            app = QApplication.instance()
            if app:
                theme_data = stm.choose_theme_dialog(app)
                if theme_data:
                    self._current_theme = theme_data.get("name")
                    self._current_variant = theme_data.get("variant", "light")
                    self.themeChanged.emit(self._current_theme)
                    return True
        except Exception as e:
            logger.error(f"Ошибка при показе диалога выбора темы: {e}")
        
        return False