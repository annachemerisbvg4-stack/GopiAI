"""
Утилиты GopiAI UI
"""

from .theme_manager import ThemeManager

# Импортируем функции из markdown_renderer
try:
    from .markdown_renderer import render_markdown, get_markdown_renderer
    __all__ = ['ThemeManager', 'render_markdown', 'get_markdown_renderer']
except ImportError:
    # Если не удалось импортировать, создаем заглушки
    def render_markdown(text):
        import html
        return html.escape(text)
    
    def get_markdown_renderer():
        return None
    
    __all__ = ['ThemeManager', 'render_markdown', 'get_markdown_renderer']
