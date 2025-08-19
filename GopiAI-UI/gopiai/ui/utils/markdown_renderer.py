"""
Минимальная утилита для рендеринга Markdown в HTML.
"""

import html

def render_markdown(text):
    """Простая функция для рендеринга markdown."""
    if not text:
        return ""
    
    # Просто заменяем звездочки на HTML-теги
    text = html.escape(text)
    text = text.replace('**', '<strong>').replace('**', '</strong>')
    text = text.replace('*', '<em>').replace('*', '</em>')
    
    # Разбиваем на параграфы
    paragraphs = []
    for line in text.split('\n'):
        if line.strip():
            paragraphs.append(f'<p>{line}</p>')
    
    return '\n'.join(paragraphs)

def get_markdown_renderer():
    """Заглушка для совместимости."""
    return None