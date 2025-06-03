#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🎯 Единая система конфигурации для всех модулей GopiAI

Заменяет разрозненные настройки из:
- gopiai.app.utils.settings
- Самодельные конфигурации по всему проекту  

Теперь ВСЕ модули используют ОДНУ конфигурацию отсюда!
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, asdict, field

@dataclass
class UIConfig:
    """Конфигурация UI компонентов"""
    theme: str = "dark"
    font_size: int = 12
    font_family: str = "Consolas"
    icon_theme: str = "lucide"
    window_geometry: Dict[str, int] = field(default_factory=lambda: {
        "width": 1200, "height": 800, "x": 100, "y": 100
    })

@dataclass
class LoggingConfig:
    """Конфигурация логирования"""
    level: str = "INFO"
    file_logging: bool = True
    console_logging: bool = True
    max_log_files: int = 10
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

@dataclass
class AgentConfig:
    """Конфигурация AI агентов"""
    default_model: str = "gpt-4"
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30
    retry_attempts: int = 3

@dataclass
class BrowserConfig:
    """Конфигурация браузера"""
    headless: bool = False
    user_agent: str = "GopiAI Browser Agent"
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout: int = 30

@dataclass
class GopiAIConfig:
    """Главная конфигурация GopiAI"""
    ui: UIConfig = field(default_factory=UIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    
    # Дополнительные настройки
    debug_mode: bool = False
    auto_save: bool = True
    language: str = "ru"

class ConfigManager:
    """Менеджер конфигурации GopiAI 🎯"""
    
    def __init__(self):
        self._config_file = Path.home() / ".gopiai" / "config.json"
        self._config = self._load_config()
    
    def _load_config(self) -> GopiAIConfig:
        """Загрузить конфигурацию из файла"""
        try:
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Создаем конфиг из данных
                return GopiAIConfig(
                    ui=UIConfig(**data.get('ui', {})),
                    logging=LoggingConfig(**data.get('logging', {})),
                    agent=AgentConfig(**data.get('agent', {})),
                    browser=BrowserConfig(**data.get('browser', {})),
                    debug_mode=data.get('debug_mode', False),
                    auto_save=data.get('auto_save', True),
                    language=data.get('language', 'ru')
                )
            else:
                # Создаем конфиг по умолчанию
                config = GopiAIConfig()
                self._save_config(config)
                return config
                
        except Exception as e:
            print(f"⚠️ Ошибка загрузки конфигурации: {e}")
            return GopiAIConfig()
    
    def _save_config(self, config: GopiAIConfig):
        """Сохранить конфигурацию в файл"""
        try:
            # Создаем директорию если не существует
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Сохраняем конфиг
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(config), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Ошибка сохранения конфигурации: {e}")
    
    @property
    def config(self) -> GopiAIConfig:
        """Получить конфигурацию"""
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение конфигурации по ключу"""
        try:
            keys = key.split('.')
            value = self._config
            
            for k in keys:
                value = getattr(value, k)
            
            return value
        except (AttributeError, KeyError):
            return default
    
    def set(self, key: str, value: Any, save: bool = True):
        """Установить значение конфигурации"""
        try:
            keys = key.split('.')
            target = self._config
            
            # Навигируемся к родительскому объекту
            for k in keys[:-1]:
                target = getattr(target, k)
            
            # Устанавливаем значение
            setattr(target, keys[-1], value)
            
            # Сохраняем если нужно
            if save:
                self._save_config(self._config)
                
        except (AttributeError, KeyError) as e:
            print(f"⚠️ Ошибка установки конфигурации {key}: {e}")
    
    def reload(self):
        """Перезагрузить конфигурацию"""
        self._config = self._load_config()
    
    def save(self):
        """Сохранить текущую конфигурацию"""
        self._save_config(self._config)

# Глобальный экземпляр менеджера (ленивая инициализация)
_global_config_manager: Optional[ConfigManager] = None

def _get_manager() -> ConfigManager:
    """Получить глобальный менеджер конфигурации"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager

# Удобные функции для импорта
def get_config() -> GopiAIConfig:
    """Получить глобальную конфигурацию GopiAI"""
    return _get_manager().config

def get_config_manager() -> ConfigManager:
    """Получить менеджер конфигурации GopiAI"""
    return _get_manager()

def get_setting(key: str, default: Any = None) -> Any:
    """Получить значение настройки по ключу"""
    return _get_manager().get(key, default)

def set_setting(key: str, value: Any, save: bool = True):
    """Установить значение настройки"""
    _get_manager().set(key, value, save)

# Для обратной совместимости с gopiai.app.utils.settings
def config():
    """Получить конфигурацию (для обратной совместимости)"""
    return get_config()
