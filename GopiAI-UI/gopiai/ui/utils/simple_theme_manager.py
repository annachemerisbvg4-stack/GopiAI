#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Простой менеджер тем с минимальным количеством функций и без усложнений.
"""
import os
import json
import logging
import math
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt

# Настройка логирования
logger = logging.getLogger(__name__)

# Путь к файлу настроек
SETTINGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "settings")
THEME_FILE = os.path.join(SETTINGS_DIR, "simple_theme.json")

# --- КОЛЛЕКЦИЯ ТЕМ ---
MATERIAL_SKY_THEME = {
    "name": "Material Sky",
    "description": "Тема, сгенерированная на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#cde5ff",
        "control_color": "#006398",
        "accent_color": "#7a4c8f",
        "titlebar_background": "#cde5ff",
        "button_color": "#3d6281",
        "button_hover_color": "#4d6d88",
        "button_active_color": "#006398",
        "text_color": "#1c1b1c",
        "border_color": "#75777b",
        "titlebar_text": "#001d31"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#004b73",
        "control_color": "#93ccff",
        "accent_color": "#e9b3ff",
        "titlebar_background": "#004b73",
        "button_color": "#a5caee",
        "button_hover_color": "#234a68",
        "button_active_color": "#003351",
        "text_color": "#e5e2e2",
        "border_color": "#8f9195",
        "titlebar_text": "#cde5ff"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

EMERALD_GARDEN_THEME = {
    "name": "Emerald Garden",
    "description": "Зелёная тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#b9f47d",
        "control_color": "#3b6a00",
        "accent_color": "#006c53",
        "titlebar_background": "#b9f47d",
        "button_color": "#4f6538",
        "button_hover_color": "#9ed764",
        "button_active_color": "#3b6a00",
        "text_color": "#1c1b1b",
        "border_color": "#767870",
        "titlebar_text": "#0e2000"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#2b5000",
        "control_color": "#9ed764",
        "accent_color": "#5ddcb5",
        "titlebar_background": "#2b5000",
        "button_color": "#b5cf98",
        "button_hover_color": "#384d22",
        "button_active_color": "#1c3700",
        "text_color": "#e5e2e0",
        "border_color": "#909189",
        "titlebar_text": "#b9f47d"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

CRIMSON_RELIC_THEME = {
    "name": "Crimson Relic",
    "description": "Красная тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#ffdad7",
        "control_color": "#c00020",
        "accent_color": "#875219",
        "titlebar_background": "#ffdad7",
        "button_color": "#894e4b",
        "button_hover_color": "#ffb3ae",
        "button_active_color": "#c00020",
        "text_color": "#1e1b1b",
        "border_color": "#817473",
        "titlebar_text": "#410005"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#930016",
        "control_color": "#ffb3ae",
        "accent_color": "#ffb876",
        "titlebar_background": "#930016",
        "button_color": "#ffb3ae",
        "button_hover_color": "#6d3735",
        "button_active_color": "#68000c",
        "text_color": "#e8e1e0",
        "border_color": "#9b8e8c",
        "titlebar_text": "#ffdad7"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

GOLDEN_EMBER_THEME = {
    "name": "Golden Ember",
    "description": "Оранжево-золотая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#ffdbcf",
        "control_color": "#a43d0b",
        "accent_color": "#6e5e00",
        "titlebar_background": "#ffdbcf",
        "button_color": "#88503a",
        "button_hover_color": "#ffb59a",
        "button_active_color": "#a43d0b",
        "text_color": "#1d1b1b",
        "border_color": "#807571",
        "titlebar_text": "#380d00"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#802a00",
        "control_color": "#ffb59a",
        "accent_color": "#ddc661",
        "titlebar_background": "#802a00",
        "button_color": "#ffb59a",
        "button_hover_color": "#6c3925",
        "button_active_color": "#5b1b00",
        "text_color": "#e7e1e0",
        "border_color": "#9b8e8a",
        "titlebar_text": "#ffdbcf"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

SUNLIT_MEADOW_THEME = {
    "name": "Sunlit Meadow",
    "description": "Жёлто-зелёная тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#ffdf91",
        "control_color": "#755b00",
        "accent_color": "#506600",
        "titlebar_background": "#ffdf91",
        "button_color": "#715c21",
        "button_hover_color": "#f3c015",
        "button_active_color": "#755b00",
        "text_color": "#1c1b1a",
        "border_color": "#7c766d",
        "titlebar_text": "#241a00"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#594400",
        "control_color": "#f3c015",
        "accent_color": "#b2d34e",
        "titlebar_background": "#594400",
        "button_color": "#e0c47e",
        "button_hover_color": "#574409",
        "button_active_color": "#3e2e00",
        "text_color": "#e6e2df",
        "border_color": "#969086",
        "titlebar_text": "#ffdf91"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

MINT_FROST_THEME = {
    "name": "Mint Frost",
    "description": "Мятно-серо-лавандовая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#c8ead9",
        "control_color": "#466557",
        "accent_color": "#585d77",
        "titlebar_background": "#c8ead9",
        "button_color": "#54615b",
        "button_hover_color": "#adcebe",
        "button_active_color": "#466557",
        "text_color": "#1c1b1b",
        "border_color": "#747875",
        "titlebar_text": "#012016"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#2f4d40",
        "control_color": "#adcebe",
        "accent_color": "#c1c5e3",
        "titlebar_background": "#2f4d40",
        "button_color": "#bccac2",
        "button_hover_color": "#3d4a44",
        "button_active_color": "#18362a",
        "text_color": "#e5e2e1",
        "border_color": "#8e928e",
        "titlebar_text": "#c8ead9"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

VIOLET_DREAM_THEME = {
    "name": "Violet Dream",
    "description": "Сине-фиолетовая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#e0e0ff",
        "control_color": "#3e4ade",
        "accent_color": "#82478f",
        "titlebar_background": "#e0e0ff",
        "button_color": "#555a90",
        "button_hover_color": "#bec2ff",
        "button_active_color": "#3e4ade",
        "text_color": "#1c1b1c",
        "border_color": "#78767c",
        "titlebar_text": "#000569"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#202cc7",
        "control_color": "#bec2ff",
        "accent_color": "#f4aeff",
        "titlebar_background": "#202cc7",
        "button_color": "#bec2ff",
        "button_hover_color": "#3e4276",
        "button_active_color": "#000ca5",
        "text_color": "#e5e1e2",
        "border_color": "#929096",
        "titlebar_text": "#e0e0ff"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

INDIGO_CANDY_THEME = {
    "name": "Indigo Candy",
    "description": "Индиго-розовая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#e1e0ff",
        "control_color": "#4b50c6",
        "accent_color": "#8b428d",
        "titlebar_background": "#e1e0ff",
        "button_color": "#585a89",
        "button_hover_color": "#c0c1ff",
        "button_active_color": "#4b50c6",
        "text_color": "#1c1b1c",
        "border_color": "#78767c",
        "titlebar_text": "#04006d"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#3235ad",
        "control_color": "#c0c1ff",
        "accent_color": "#ffa9fd",
        "titlebar_background": "#3235ad",
        "button_color": "#c1c2f7",
        "button_hover_color": "#41436f",
        "button_active_color": "#161598",
        "text_color": "#e5e1e2",
        "border_color": "#929095",
        "titlebar_text": "#e1e0ff"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

PINK_MIRAGE_THEME = {
    "name": "Pink Mirage",
    "description": "Розово-фиолетовая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#ffd7f2",
        "control_color": "#ab00a1",
        "accent_color": "#894d55",
        "titlebar_background": "#ffd7f2",
        "button_color": "#8b4580",
        "button_hover_color": "#ffabed",
        "button_active_color": "#ab00a1",
        "text_color": "#1d1b1c",
        "border_color": "#7d7579",
        "titlebar_text": "#390035"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#83007b",
        "control_color": "#ffabed",
        "accent_color": "#ffb2bb",
        "titlebar_background": "#83007b",
        "button_color": "#ffabed",
        "button_hover_color": "#6f2d66",
        "button_active_color": "#5d0057",
        "text_color": "#e7e1e2",
        "border_color": "#988e93",
        "titlebar_text": "#ffd7f2"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

OLIVE_LIBRARY_THEME = {
    "name": "Olive Library",
    "description": "Оливково-бежево-серая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#eae2c9",
        "control_color": "#635e4a",
        "accent_color": "#596154",
        "titlebar_background": "#eae2c9",
        "button_color": "#615e54",
        "button_hover_color": "#cec6ae",
        "button_active_color": "#635e4a",
        "text_color": "#1c1b1b",
        "border_color": "#797770",
        "titlebar_text": "#1f1c0c"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#4b4734",
        "control_color": "#cec6ae",
        "accent_color": "#c1c9b9",
        "titlebar_background": "#4b4734",
        "button_color": "#cbc6ba",
        "button_hover_color": "#49473e",
        "button_active_color": "#34301f",
        "text_color": "#e5e2e1",
        "border_color": "#939189",
        "titlebar_text": "#eae2c9"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

LAVENDER_MIST_THEME = {
    "name": "Lavender Mist",
    "description": "Лавандово-серая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#e0e1f2",
        "control_color": "#5b5e6b",
        "accent_color": "#6a5a64",
        "titlebar_background": "#e0e1f2",
        "button_color": "#5e5e63",
        "button_hover_color": "#c4c6d5",
        "button_active_color": "#5b5e6b",
        "text_color": "#1c1b1b",
        "border_color": "#78767b",
        "titlebar_text": "#181b26"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#434653",
        "control_color": "#c4c6d5",
        "accent_color": "#d6c1cd",
        "titlebar_background": "#434653",
        "button_color": "#c7c6cc",
        "button_hover_color": "#46464b",
        "button_active_color": "#2d303c",
        "text_color": "#e5e2e1",
        "border_color": "#929094",
        "titlebar_text": "#e0e1f2"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

GRAPHITE_NIGHT_THEME = {
    "name": "Graphite Night",
    "description": "Графитово-серая тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#dde4e3",
        "control_color": "#586060",
        "accent_color": "#605d64",
        "titlebar_background": "#dde4e3",
        "button_color": "#5c5f5e",
        "button_hover_color": "#c1c8c7",
        "button_active_color": "#586060",
        "text_color": "#1c1b1b",
        "border_color": "#747779",
        "titlebar_text": "#161d1d"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#414848",
        "control_color": "#c1c8c7",
        "accent_color": "#cac5cd",
        "titlebar_background": "#414848",
        "button_color": "#c5c7c6",
        "button_hover_color": "#444747",
        "button_active_color": "#2b3232",
        "text_color": "#e5e2e1",
        "border_color": "#8e9192",
        "titlebar_text": "#dde4e3"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

PUMPKIN_FIELD_THEME = {
    "name": "Pumpkin Field",
    "description": "Тыквенно-оранжевая с зелёным акцентом тема на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#ffdcc6",
        "control_color": "#944a00",
        "accent_color": "#5d6300",
        "titlebar_background": "#ffdcc6",
        "button_color": "#815433",
        "button_hover_color": "#ffb784",
        "button_active_color": "#944a00",
        "text_color": "#1d1b1a",
        "border_color": "#80756f",
        "titlebar_text": "#301400"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#713700",
        "control_color": "#ffb784",
        "accent_color": "#c6ce56",
        "titlebar_background": "#713700",
        "button_color": "#f5ba92",
        "button_hover_color": "#653d1e",
        "button_active_color": "#4f2500",
        "text_color": "#e7e1e0",
        "border_color": "#9a8e88",
        "titlebar_text": "#ffdcc6"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

SCARLET_FIRE_THEME = {
    "name": "Scarlet Fire",
    "description": "Алый, насыщенно-красный вариант на основе Angular Material tokens. Светлый и тёмный вариант.",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#ffdad5",
        "control_color": "#c00007",
        "accent_color": "#875203",
        "titlebar_background": "#ffdad5",
        "button_color": "#884f46",
        "button_hover_color": "#ffb4a9",
        "button_active_color": "#c00007",
        "text_color": "#1e1b1a",
        "border_color": "#817472",
        "titlebar_text": "#410001"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#930004",
        "control_color": "#ffb4a9",
        "accent_color": "#ffb867",
        "titlebar_background": "#930004",
        "button_color": "#ffb4a9",
        "button_hover_color": "#6c3831",
        "button_active_color": "#690002",
        "text_color": "#e8e1e0",
        "border_color": "#9c8d8b",
        "titlebar_text": "#ffdad5"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

DUSTY_ROSE_THEME = {
    "name": "Dusty Rose",
    "description": "Пыльная роза: аромат розового сада под дождливым небом",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#835245",
        "control_color": "#ffdbd1",
        "accent_color": "#44664c",
        "titlebar_background": "#735852",
        "button_color": "#aad0b0",
        "button_hover_color": "#fedbd2",
        "button_active_color": "#683b2f",
        "text_color": "#1c1b1b",
        "border_color": "#7f7572",
        "titlebar_text": "#1c1b1b"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#735852",
        "control_color": "#ffdbd1",
        "accent_color": "#44664c",
        "titlebar_background": "#ffdbd1",
        "button_color": "#aad0b0",
        "button_hover_color": "#245100",
        "button_active_color": "#683b2f",
        "text_color": "#ffdbd1",
        "border_color": "#7f7572",
        "titlebar_text": "#fedbd2"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

TROPICAL_BOUQUET_THEME = {
    "name": "Tropical Bouquet",
    "description": "Тропическая тема: попугайчики, бугенвиллия, салатовые и розовые акценты. Светлый — нежный, тёмный — неоновый!",
    "light": {
        "main_color": "#ffffff",
        "header_color": "#ffd9e2",
        "control_color": "#b90063",
        "accent_color": "#506600",
        "titlebar_background": "#ffd9e2",
        "button_color": "#326b00",
        "button_hover_color": "#ffb1c8",
        "button_active_color": "#b90063",
        "text_color": "#1d1b1b",
        "border_color": "#807477",
        "titlebar_text": "#3e001d"
    },
    "dark": {
        "main_color": "#333333",
        "header_color": "#8e004a",
        "control_color": "#ffb1c8",
        "accent_color": "#aad600",
        "titlebar_background": "#8e004a",
        "button_color": "#70e000",
        "button_hover_color": "#245100",
        "button_active_color": "#650033",
        "text_color": "#e7e1e1",
        "border_color": "#9a8e90",
        "titlebar_text": "#ffd9e2"
    },
    "font_family": "Roboto",
    "font_weights": {"bold": 700, "medium": 500, "regular": 400}
}

THEME_COLLECTION = [MATERIAL_SKY_THEME, EMERALD_GARDEN_THEME, CRIMSON_RELIC_THEME, GOLDEN_EMBER_THEME, SUNLIT_MEADOW_THEME, MINT_FROST_THEME, VIOLET_DREAM_THEME, INDIGO_CANDY_THEME, PINK_MIRAGE_THEME, OLIVE_LIBRARY_THEME, LAVENDER_MIST_THEME, GRAPHITE_NIGHT_THEME, PUMPKIN_FIELD_THEME, SCARLET_FIRE_THEME, TROPICAL_BOUQUET_THEME]

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С ТЕМАМИ ---
def theme_palette_to_struct(palette):
    def safe(idx, default):
        try:
            return palette[idx]
        except IndexError:
            return default
    return {
        "main_color": safe(1, palette[0]),
        "header_color": safe(2, palette[0]),
        "control_color": safe(6, palette[0]),
        "accent_color": safe(7, palette[0]),
        "titlebar_background": safe(2, palette[0]),
        "button_color": safe(3, palette[0]),
        "button_hover_color": _lighten_color(safe(3, palette[0]), 15),
        "button_active_color": safe(6, palette[0]),
        "text_color": "#222" if _is_light(safe(1, palette[0])) else "#fff",
        "border_color": _darken_color(safe(1, palette[0]), 10),
        "titlebar_text": "#fff" if not _is_light(safe(2, palette[0])) else "#222"
    }

def _is_light(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return luminance > 180

def _lighten_color(hex_color, percent=20):
    """Осветляет цвет на указанный процент."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = min(255, int(r * (1 + percent / 100)))
    g = min(255, int(g * (1 + percent / 100)))
    b = min(255, int(b * (1 + percent / 100)))
    return f"#{r:02x}{g:02x}{b:02x}"

def _darken_color(hex_color, percent=20):
    """Затемняет цвет на указанный процент."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = max(0, int(r * (1 - percent / 100)))
    g = max(0, int(g * (1 - percent / 100)))
    b = max(0, int(b * (1 - percent / 100)))
    return f"#{r:02x}{g:02x}{b:02x}"

def _adjust_text_contrast(theme):
    """Автоматически настраивает контраст текста для всех элементов темы."""
    # Список элементов, для которых нужно проверить контраст текста
    elements_with_text = {
        "main_color": "text_color",
        "button_color": "button_text",
        "header_color": "header_text",
        "titlebar_background": "titlebar_text",
        "control_color": "control_text",
        "button_hover_color": "button_hover_text",
        "button_active_color": "button_active_text"
    }
    
    for bg_element, text_element in elements_with_text.items():
        if bg_element in theme:
            # Если это titlebar_text и он уже есть в теме, не переопределяем
            if bg_element == "titlebar_background" and "titlebar_text" in theme:
                continue
                
            bg_color = theme.get(bg_element)
            if isinstance(bg_color, str) and bg_color.startswith("#"):
                is_light = _is_light(bg_color)
                
                # Определяем более контрастные цвета для лучшей читаемости
                # Для светлого фона - чёрный текст, для тёмного - белый
                if text_element not in theme:  # Не перезаписываем, если уже задан
                    theme[text_element] = "#000000" if is_light else "#cccccc"
                    
                # Особая обработка для кнопок - нужен максимальный контраст
                if bg_element.startswith("button_"):
                    theme[text_element] = "#000000" if is_light else "#cccccc"
    
    return theme

def generate_default_colors():
    """Генерирует дефолтные цвета на основе начального положения маркеров на цветовом колесе."""
    primary_color = QColor(0, 120, 255)  # #0078FF - ярко-синий
    bg_color = QColor(240, 240, 240)  # #F0F0F0 - светло-серый
    header_color = QColor(0, 50, 100)  # #003264 - темно-синий
    button_color = QColor(255, 80, 0)  # #FF5000 - оранжевый
    accent_color = QColor(255, 0, 100)  # #FF0064 - розовый
    return [primary_color, bg_color, header_color, button_color, accent_color]

def save_theme(colors):
    """Простая функция для сохранения темы в файл."""
    try:
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        theme_data = {}
        if len(colors) >= 4:
            main_color = colors[0]
            bg_color = colors[1]
            header_color = colors[2]
            button_color = colors[3]
            bg_luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue())
            text_color = "#cccccc" if bg_luminance < 128 else "#000000"
            theme_data.update({
                "main_color": bg_color.name(),
                "header_color": header_color.name(),
                "control_color": main_color.name(),
                "accent_color": main_color.name(),
                "titlebar_background": header_color.name(),
                "button_color": button_color.name(),
                "button_hover_color": _lighten_color(button_color.name()),
                "button_active_color": main_color.name(),
                "text_color": text_color,
                "border_color": _darken_color(bg_color.name(), 10),
                "titlebar_text": "#cccccc"
            })
            theme_data["_original_colors"] = [
                {"index": 0, "name": "primary", "hex": main_color.name(),
                 "rgb": [main_color.red(), main_color.green(), main_color.blue()]},
                {"index": 1, "name": "background", "hex": bg_color.name(),
                 "rgb": [bg_color.red(), bg_color.green(), bg_color.blue()]},
                {"index": 2, "name": "header", "hex": header_color.name(),
                 "rgb": [header_color.red(), header_color.green(), header_color.blue()]},
                {"index": 3, "name": "button", "hex": button_color.name(),
                 "rgb": [button_color.red(), button_color.green(), button_color.blue()]}
            ]
        with open(THEME_FILE, 'w', encoding='utf-8') as f:
            json.dump(theme_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении темы: {e}")
        return False

def load_theme():
    """Простая функция для загрузки темы из файла."""
    try:
        if os.path.exists(THEME_FILE):
            with open(THEME_FILE, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
                return theme_data
    except Exception as e:
        logger.error(f"Ошибка при загрузке темы: {e}")
    return None

def apply_theme(app):
    """Применяет тему к приложению."""
    if not app:
        logger.error("QApplication не предоставлен")
        return False
    theme = load_theme()
    if not theme:
        default_colors = generate_default_colors()
        save_result = save_theme(default_colors)
        theme = load_theme()
        if not theme:
            return False
            
    # Автоматически настраиваем контраст текста для всех элементов
    theme = _adjust_text_contrast(theme)
    try:
        palette = QPalette()
        main_color = QColor(theme.get("main_color", "#cccccc"))
        text_color = QColor(theme.get("text_color", "#000000"))
        accent_color = QColor(theme.get("accent_color", "#0078D7"))
        border_color = QColor(theme.get("border_color", "#CCCCCC"))
        button_color = QColor(theme.get("button_color", "#E0E0E0"))
        header_color = QColor(theme.get("header_color", "#F0F0F0"))
        
        # Специфические цвета текста для различных элементов
        button_text_color = QColor(theme.get("button_text", "#000000" if _is_light(theme.get("button_color", "#E0E0E0")) else "#cccccc"))
        button_hover_text_color = QColor(theme.get("button_hover_text", "#000000" if _is_light(theme.get("button_hover_color", "#F0F0F0")) else "#cccccc"))
        button_active_text_color = QColor(theme.get("button_active_text", "#000000" if _is_light(theme.get("button_active_color", "#0078D7")) else "#cccccc"))
        
        # Устанавливаем цвета элементов
        palette.setColor(QPalette.ColorRole.Window, main_color)
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        palette.setColor(QPalette.ColorRole.Base, main_color)
        palette.setColor(QPalette.ColorRole.AlternateBase, main_color.lighter(110))
        palette.setColor(QPalette.ColorRole.ToolTipBase, main_color)
        palette.setColor(QPalette.ColorRole.ToolTipText, text_color)
        palette.setColor(QPalette.ColorRole.Text, text_color)
        palette.setColor(QPalette.ColorRole.Button, button_color)
        
        # Применяем специфические цвета текста для кнопок вместо общего text_color
        palette.setColor(QPalette.ColorRole.ButtonText, button_text_color)
        
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Link, accent_color)
        palette.setColor(QPalette.ColorRole.Highlight, accent_color)
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        # Добавляем стиль для улучшения контраста всех виджетов
        app.setStyleSheet(f"""
        /* Стили для кнопок */
        QPushButton {{
            color: {button_text_color.name()};
            background-color: {button_color.name()};
            border: 1px solid {border_color.name()};
        }}
        QPushButton:hover {{
            color: {button_hover_text_color.name()};
            background-color: {theme.get("button_hover_color", "#F0F0F0")};
        }}
        QPushButton:pressed {{
            color: {button_active_text_color.name()};
            background-color: {theme.get("button_active_color", "#0078D7")};
        }}
        
        /* Стили для всех других виджетов */
        QLabel {{
            color: {text_color.name()};
        }}
        QComboBox {{
            color: {button_text_color.name()};
            background-color: {button_color.name()};
            border: 1px solid {border_color.name()};
        }}
        QComboBox QAbstractItemView {{
            color: {text_color.name()};
            background-color: {main_color.name()};
            selection-background-color: {accent_color.name()};
            selection-color: #cccccc;
        }}
        QLineEdit, QTextEdit, QPlainTextEdit {{
            color: {text_color.name()};
            background-color: {main_color.name()};
            border: 1px solid {border_color.name()};
        }}
        QMenuBar::item:selected, QMenu::item:selected {{
            color: #cccccc;
            background-color: {accent_color.name()};
        }}
        QCheckBox, QRadioButton {{
            color: {text_color.name()};
        }}
        QTabBar::tab {{
            color: {button_text_color.name()};
            background-color: {button_color.name()};
        }}
        QTabBar::tab:selected {{
            color: {button_active_text_color.name()};
            background-color: {theme.get("button_active_color", "#0078D7")};
        }}
        QToolTip {{
            color: {text_color.name()};
            background-color: {main_color.name()};
            border: 1px solid {border_color.name()};
        }}
        QTreeView, QListView, QTableView {{
            color: {text_color.name()};
            background-color: {main_color.name()};
        }}
        QTreeView::item:selected, QListView::item:selected, QTableView::item:selected {{
            color: #cccccc;
            background-color: {accent_color.name()};
        }}
        QHeaderView::section {{
            color: {text_color.name()};
            background-color: {header_color.name()};
        }}
        QToolButton {{
            color: {button_text_color.name()};
            background-color: {button_color.name()};
        }}
        QToolButton:hover {{
            color: {button_hover_text_color.name()};
            background-color: {theme.get("button_hover_color", "#F0F0F0")};
        }}
        QToolButton:pressed {{
            color: {button_active_text_color.name()};
            background-color: {theme.get("button_active_color", "#0078D7")};
        }}
        """)
        app.setPalette(palette)
        app.setStyle("Fusion")
        return True
    except Exception as e:
        logger.error(f"Ошибка при применении темы: {e}")
        return False

def choose_theme_dialog(app):
    """Показывает диалог выбора темы."""
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QCheckBox
    from PySide6.QtCore import Qt

    class ThemeDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Выбор темы")
            self.setMinimumWidth(400)
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)

            # Основной layout
            layout = QVBoxLayout(self)

            # Заголовок
            title_layout = QHBoxLayout()
            title = QLabel("Выбор темы")
            title.setStyleSheet("font-size: 16px; font-weight: bold;")
            title_layout.addWidget(title)
            title_layout.addStretch()

            # Кнопка закрытия
            close_button = QPushButton("×")
            close_button.setFixedSize(30, 30)
            close_button.clicked.connect(self.reject)
            title_layout.addWidget(close_button)
            layout.addLayout(title_layout)

            # Выбор темы
            theme_layout = QHBoxLayout()
            theme_label = QLabel("Тема:")
            self.theme_combo = QComboBox()
            for theme in THEME_COLLECTION:
                self.theme_combo.addItem(theme["name"])
            theme_layout.addWidget(theme_label)
            theme_layout.addWidget(self.theme_combo)
            layout.addLayout(theme_layout)

            # Выбор варианта (светлый/темный)
            variant_layout = QHBoxLayout()
            variant_label = QLabel("Вариант:")
            self.dark_mode = QCheckBox("Темный режим")
            variant_layout.addWidget(variant_label)
            variant_layout.addWidget(self.dark_mode)
            layout.addLayout(variant_layout)

            # Кнопки
            buttons_layout = QHBoxLayout()
            buttons_layout.addStretch()
            apply_button = QPushButton("Применить")
            apply_button.clicked.connect(self.accept)
            cancel_button = QPushButton("Отмена")
            cancel_button.clicked.connect(self.reject)
            buttons_layout.addWidget(cancel_button)
            buttons_layout.addWidget(apply_button)
            layout.addLayout(buttons_layout)

            # Перетаскивание окна
            self._drag_pos = None

        def mousePressEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

        def mouseMoveEvent(self, event):
            if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos:
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                event.accept()

        def mouseReleaseEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                self._drag_pos = None
                event.accept()

    dialog = ThemeDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        theme_index = dialog.theme_combo.currentIndex()
        is_dark = dialog.dark_mode.isChecked()

        if 0 <= theme_index < len(THEME_COLLECTION):
            theme = THEME_COLLECTION[theme_index]
            variant = "dark" if is_dark else "light"

            if variant in theme:
                theme_data = theme[variant].copy()
                theme_data["name"] = theme["name"]
                theme_data["variant"] = variant

                # Сохраняем тему
                try:
                    os.makedirs(SETTINGS_DIR, exist_ok=True)
                    with open(THEME_FILE, 'w', encoding='utf-8') as f:
                        json.dump(theme_data, f, indent=2)

                    # Применяем тему
                    apply_theme(app)
                    return theme_data
                except Exception as e:
                    logger.error(f"Ошибка при сохранении темы: {e}")

    return None

# Добавляем импорт Qt для apply_theme
from PySide6.QtCore import Qt