"""
Emoji to Icon Utility
=====================

Утилита для замены emoji на красивые иконки в интерфейсе GopiAI.
"""

from typing import Optional, Dict
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QLabel

# Маппинг emoji к именам иконок Lucide
EMOJI_TO_ICON_MAP: Dict[str, str] = {
    # Навигация
    "🏠": "home",
    "⬆️": "arrow-up", 
    "⬇️": "arrow-down",
    "⬅️": "arrow-left",
    "➡️": "arrow-right",
    "🔙": "arrow-left",
    "🔄": "refresh-cw",
    
    # Файлы и папки
    "📁": "folder",
    "📂": "folder-open",
    "📄": "file-text",
    "📝": "edit-3",
    "💾": "save",
    "🗂️": "folder-tree",
    "📦": "package",
    
    # UI элементы и управление
    "🔧": "settings",
    "⚙️": "cog",
    "🎨": "palette",
    "🎯": "target",
    "🚀": "rocket",
    "🔍": "search",
    "🔎": "search",
    
    # Действия
    "➕": "plus",
    "❌": "x",
    "✅": "check",
    "⚠️": "alert-triangle",
    "❗": "alert-circle",
    "💡": "lightbulb",
    
    # Устройства
    "💻": "monitor",
    "🖥️": "pc", 
    "📱": "smartphone",
    "🔌": "plug",
    "🌐": "globe",
    "📡": "wifi",
    
    # Окно и интерфейс
    "—": "minimize",
    "❐": "square",
    "□": "maximize",
    "×": "x",
    
    # Статусы
    "🟢": "check-circle",
    "🔴": "x-circle", 
    "🟡": "alert-circle",
    "🔵": "info",
    
    # Темы
    "🌙": "moon",
    "☀️": "sun",
    
    # Дополнительные
    "📊": "bar-chart-3",
    "📈": "trending-up",
    "📉": "trending-down",
    "🔗": "link",
    "📋": "clipboard",
    "🎵": "music",
    "🎥": "video",
    "📷": "camera",
    "🎮": "gamepad-2",
}


class EmojiToIconConverter:
    """Конвертер emoji в иконки"""
    
    def __init__(self, icon_manager=None):
        """
        Инициализация конвертера
        
        Args:
            icon_manager: Менеджер иконок (например, UniversalIconManager)
        """
        self.icon_manager = icon_manager
        
    def convert_button_emoji_to_icon(self, button: QPushButton, emoji: str) -> bool:
        """
        Конвертирует emoji на кнопке в иконку
        
        Args:
            button: Кнопка для обновления
            emoji: Emoji для замены
            
        Returns:
            bool: True если конвертация успешна
        """
        if not self.icon_manager:
            return False
            
        icon_name = EMOJI_TO_ICON_MAP.get(emoji)
        if not icon_name:
            return False
            
        try:
            icon = self.icon_manager.get_icon(icon_name)
            if icon and not icon.isNull():
                button.setIcon(icon)
                # Очищаем текст, так как теперь используем иконку
                if button.text() == emoji:
                    button.setText("")
                return True
        except Exception as e:
            print(f"⚠️ Ошибка конвертации emoji {emoji} в иконку: {e}")
            
        return False
    
    def convert_label_emoji_to_icon(self, label: QLabel, emoji: str) -> bool:
        """
        Конвертирует emoji в заголовке в иконку
        
        Args:
            label: Заголовок для обновления
            emoji: Emoji для замены
            
        Returns:
            bool: True если конвертация успешна
        """
        if not self.icon_manager:
            return False
            
        icon_name = EMOJI_TO_ICON_MAP.get(emoji)
        if not icon_name:
            return False
            
        try:
            icon = self.icon_manager.get_icon(icon_name)
            if icon and not icon.isNull():
                # Заменяем emoji в тексте
                current_text = label.text()
                new_text = current_text.replace(emoji, "").strip()
                label.setText(new_text)
                
                # Устанавливаем иконку как pixmap
                pixmap = icon.pixmap(16, 16)
                label.setPixmap(pixmap)
                return True
        except Exception as e:
            print(f"⚠️ Ошибка конвертации emoji {emoji} в иконку: {e}")
            
        return False
    
    def get_icon_for_emoji(self, emoji: str) -> Optional[QIcon]:
        """
        Получает иконку для emoji
        
        Args:
            emoji: Emoji для конвертации
            
        Returns:
            QIcon или None
        """
        if not self.icon_manager:
            return None
            
        icon_name = EMOJI_TO_ICON_MAP.get(emoji)
        if not icon_name:
            return None
            
        try:
            return self.icon_manager.get_icon(icon_name)
        except Exception as e:
            print(f"⚠️ Ошибка получения иконки для emoji {emoji}: {e}")
            return None
    
    def replace_emoji_in_text(self, text: str) -> str:
        """
        Заменяет все emoji в тексте на названия иконок
        
        Args:
            text: Исходный текст с emoji
            
        Returns:
            str: Текст с замененными emoji
        """
        result = text
        for emoji, icon_name in EMOJI_TO_ICON_MAP.items():
            result = result.replace(emoji, f"[{icon_name}]")
        return result


def apply_icons_to_component(component, icon_manager=None):
    """
    Применяет иконки ко всем подходящим элементам компонента
    
    Args:
        component: Компонент для обновления
        icon_manager: Менеджер иконок
    """
    if not icon_manager:
        return
        
    converter = EmojiToIconConverter(icon_manager)
    
    # Находим все кнопки и заменяем emoji
    buttons = component.findChildren(QPushButton)
    for button in buttons:
        text = button.text()
        if text in EMOJI_TO_ICON_MAP:
            converter.convert_button_emoji_to_icon(button, text)
    
    # Находим все заголовки и заменяем emoji
    labels = component.findChildren(QLabel)
    for label in labels:
        text = label.text()
        for emoji in EMOJI_TO_ICON_MAP:
            if emoji in text:
                converter.convert_label_emoji_to_icon(label, emoji)
                break


__all__ = [
    'EMOJI_TO_ICON_MAP',
    'EmojiToIconConverter', 
    'apply_icons_to_component'
]