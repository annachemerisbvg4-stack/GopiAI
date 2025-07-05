# 🔧 Панель инструментов Chata Widget - Система навигации

## 📖 Обзор

Этот документ описывает навигационную систему для панели инструментов Chata Widget. Панель теперь поддерживает множественные виды с возможностью навигации между ними с помощью кнопок вперёд-назад.

## 🏗️ Архитектура

### Основные компоненты

1. **SlidingPanel** - Основная панель с навигационной системой
2. **PanelTrigger** - Кнопка для открытия/закрытия панели  
3. **SidePanelContainer** - Контейнер, объединяющий триггер и панель

### Структура SlidingPanel

```python
class SlidingPanel(QWidget):
    def __init__(self, parent=None):
        # История навигации для кнопок вперёд-назад
        self.navigation_history = []
        self.current_view_index = -1
        
        # Словарь видов панели
        self.views = {}
```

## 🎯 Система видов

### Текущие виды

1. **'main'** - Главный вид с кнопками инструментов
2. **'info'** - Информационный экран о панели

### Добавление нового вида

```python
def create_new_view(self):
    """Создание нового вида"""
    view_widget = QWidget()
    layout = QVBoxLayout(view_widget)
    
    # Добавить содержимое вида
    # ...
    
    return view_widget

def setup_views(self):
    """В методе setup_views добавить:"""
    self.views['new_view'] = self.create_new_view()
```

### Переход между видами

```python
# Переход к конкретному виду
self.show_view('view_name')

# Навигация назад/вперёд (автоматически через кнопки)
self.navigate_back()
self.navigate_forward()
```

## 🎮 Навигационная система

### Кнопки навигации

- **◀ (Назад)** - Переход к предыдущему виду в истории
- **▶ (Вперёд)** - Переход к следующему виду в истории

### Логика работы истории

1. При вызове `show_view(view_name)` вид добавляется в историю
2. При навигации назад/вперёд индекс истории изменяется без добавления в историю
3. При переходе к новому виду "из середины" истории, все последующие виды удаляются

### Состояние кнопок

```python
def update_navigation_buttons(self):
    # Кнопка "Назад" активна, если не в начале истории
    self.back_btn.setEnabled(self.current_view_index > 0)
    
    # Кнопка "Вперёд" активна, если не в конце истории  
    self.forward_btn.setEnabled(self.current_view_index < len(self.navigation_history) - 1)
```

## 🎨 Стилизация

### Навигационные кнопки

```python
navigation_style = """
QPushButton {
    background-color: rgba(70, 70, 70, 0.8);
    color: white;
    border: 1px solid rgba(100, 100, 100, 0.6);
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
    min-width: 30px;
    max-width: 30px;
    min-height: 24px;
    max-height: 24px;
}
QPushButton:disabled {
    background-color: rgba(50, 50, 50, 0.5);
    color: rgba(150, 150, 150, 0.5);
    border-color: rgba(80, 80, 80, 0.3);
}
"""
```

### Кнопки инструментов

```python
tool_button_style = """
QPushButton {
    background-color: rgba(70, 70, 70, 0.8);
    color: white;
    border: 1px solid rgba(100, 100, 100, 0.6);
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    text-align: left;
    min-height: 25px;
}
"""
```

## 📝 Методы API

### Основные методы

```python
# Создание и настройка видов
def setup_views(self):
    """Настройка различных видов панели"""
    
def create_main_view(self):
    """Создание главного вида с кнопками инструментов"""
    
def create_info_view(self):
    """Создание информационного вида"""

# Навигация
def show_view(self, view_name):
    """Показать указанный вид и добавить в историю навигации"""
    
def navigate_back(self):
    """Навигация назад"""
    
def navigate_forward(self):
    """Навигация вперёд"""

# Управление содержимым
def clear_content_layout(self):
    """Очистить layout содержимого"""
    
def update_title_for_view(self, view_name):
    """Обновить заголовок в зависимости от текущего вида"""

# Обратная совместимость  
def add_button(self, button):
    """Добавить кнопку в главный вид панели"""
```

## 🚀 Расширение функциональности

### Планируемые виды

1. **'settings'** - Настройки чата
2. **'stats'** - Статистика использования  
3. **'tools'** - Дополнительные инструменты
4. **'help'** - Справочная информация

### Пример добавления вида настроек

```python
def create_settings_view(self):
    """Создание вида настроек"""
    view_widget = QWidget()
    layout = QVBoxLayout(view_widget)
    
    # Заголовок
    title = QLabel("⚙️ Настройки чата")
    layout.addWidget(title)
    
    # Элементы настроек
    theme_combo = QComboBox()
    layout.addWidget(QLabel("Тема:"))
    layout.addWidget(theme_combo)
    
    # Кнопка возврата
    back_btn = QPushButton("🏠 Вернуться к главной")
    back_btn.clicked.connect(lambda: self.show_view('main'))
    layout.addWidget(back_btn)
    
    return view_widget

# В setup_views():
self.views['settings'] = self.create_settings_view()

# В update_title_for_view():
titles = {
    'main': "🔧 Панель инструментов",
    'info': "📋 Информация",
    'settings': "⚙️ Настройки"
}
```

## 📱 Интеграция

### В ChatWidget

```python
# Создание контейнера панели
self.side_panel_container = SidePanelContainer(parent=self)

# Добавление кнопок в панель (обратная совместимость)
self.side_panel_container.add_button_to_panel(button)
```

### Доступ к панели

```python
# Получение экземпляра панели
panel = self.side_panel_container.panel

# Программный переход к виду
panel.show_view('info')

# Добавление нового вида
panel.views['new_view'] = create_custom_view()
```

## 🔧 Отладка

### Логирование

```python
# В show_view():
print(f"Переход к виду: {view_name}")
print(f"История: {self.navigation_history}")
print(f"Текущий индекс: {self.current_view_index}")
```

### Проверка состояния

```python
def debug_navigation_state(self):
    """Отладочная информация о состоянии навигации"""
    print(f"История навигации: {self.navigation_history}")
    print(f"Текущий индекс: {self.current_view_index}")
    print(f"Доступные виды: {list(self.views.keys())}")
    print(f"Кнопка 'Назад' активна: {self.back_btn.isEnabled()}")
    print(f"Кнопка 'Вперёд' активна: {self.forward_btn.isEnabled()}")
```

## 📊 Структура файлов

```
GopiAI-UI/
├── gopiai/
│   └── ui/
│       └── components/
│           ├── side_panel.py          # Основная реализация
│           ├── chat_widget.py         # Интеграция с чатом
│           └── __init__.py
└── README_PANEL_TOOLS.md             # Этот файл
```

## ✅ Чек-лист разработчика

При добавлении нового вида:

- [ ] Создать метод `create_*_view()`
- [ ] Добавить вид в `setup_views()`
- [ ] Обновить `update_title_for_view()`
- [ ] Добавить кнопку возврата в вид
- [ ] Протестировать навигацию
- [ ] Обновить документацию

## 🐛 Известные ограничения

1. История навигации не сохраняется между сессиями
2. Максимальная длина истории не ограничена (может потребовать оптимизации)
3. Анимации переходов между видами пока не реализованы

## 📞 Поддержка

При возникновении проблем с панелью инструментов:

1. Проверить логи в консоли
2. Использовать `debug_navigation_state()`
3. Убедиться, что все виды созданы корректно
4. Проверить связи сигналов и слотов

---

**Версия:** 1.0  
**Дата:** Июль 2025  
**Автор:** AI Assistant для Анютки 💖
