from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton)
from PySide6.QtCore import QRect, Signal
from PySide6 import QtCore


class SlidingPanel(QWidget):
    """Боковая панель с навигационной системой"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_visible = False
        
        # История навигации для кнопок вперёд-назад
        self.navigation_history = []
        self.current_view_index = -1
        
        # Словарь видов панели
        self.views = {}
        
        self.setup_ui()
        self.setup_views()
        
    def setup_ui(self):
        """Настройка интерфейса панели"""
        self.setStyleSheet("""
            SlidingPanel {
                background-color: rgba(40, 40, 40, 0.96);
                border: 2px solid rgba(100, 100, 100, 0.8);
                border-radius: 12px;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
            }
        """)
        
        # Основной layout для содержимого панели
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)
        
        # Заголовок панели с навигацией и кнопкой закрытия
        header_layout = QHBoxLayout()
        
        # Кнопки навигации (стрелочки вперёд-назад)
        self.back_btn = QPushButton("◀")
        self.back_btn.setToolTip("Назад")
        self.back_btn.setStyleSheet("""
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
            QPushButton:hover {
                background-color: rgba(90, 90, 90, 0.9);
                border-color: rgba(120, 120, 120, 0.8);
            }
            QPushButton:pressed {
                background-color: rgba(60, 60, 60, 0.9);
            }
            QPushButton:disabled {
                background-color: rgba(50, 50, 50, 0.5);
                color: rgba(150, 150, 150, 0.5);
                border-color: rgba(80, 80, 80, 0.3);
            }
        """)
        self.back_btn.clicked.connect(self.navigate_back)
        header_layout.addWidget(self.back_btn)
        
        self.forward_btn = QPushButton("▶")
        self.forward_btn.setToolTip("Вперёд")
        self.forward_btn.setStyleSheet(self.back_btn.styleSheet())  # Тот же стиль
        self.forward_btn.clicked.connect(self.navigate_forward)
        header_layout.addWidget(self.forward_btn)
        
        # Небольшой отступ между навигацией и заголовком
        header_layout.addSpacing(10)
        
        # Заголовок панели
        self.title_label = QLabel("🔧 Панель инструментов")
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 8px 0px;
            }
        """)
        header_layout.addWidget(self.title_label)
        
        # Растяжка, чтобы кнопка закрытия была справа
        header_layout.addStretch()
        
        # Кнопка закрытия
        close_btn = QPushButton("✕")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(200, 50, 50, 0.8);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }
            QPushButton:hover {
                background-color: rgba(220, 70, 70, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(180, 30, 30, 0.9);
            }
        """)
        close_btn.clicked.connect(self.hide_panel)
        header_layout.addWidget(close_btn)
        
        self.main_layout.addLayout(header_layout)
        
        # Разделительная линия
        separator = QLabel()
        separator.setStyleSheet("""
            QLabel {
                border-bottom: 2px solid rgba(100, 100, 100, 0.6);
                margin: 8px 0px;
            }
        """)
        separator.setFixedHeight(2)
        self.main_layout.addWidget(separator)
        
        # Контейнер для содержимого (будет меняться в зависимости от текущего вида)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(8)
        self.main_layout.addLayout(self.content_layout)
        
        # Spacer для размещения содержимого сверху
        self.main_layout.addStretch()
        
        # Изначально отключаем кнопки навигации
        self.update_navigation_buttons()
        
    def setup_views(self):
        """Настройка различных видов панели"""
        # Главный вид с кнопками инструментов
        self.views['main'] = self.create_main_view()
        
        # Информационный вид
        self.views['info'] = self.create_info_view()
        
        # Показываем главный вид по умолчанию
        self.show_view('main')
        
    def create_main_view(self):
        """Создание главного вида с кнопками инструментов"""
        view_widget = QWidget()
        layout = QVBoxLayout(view_widget)
        layout.setSpacing(8)
        
        # Кнопка информации
        info_btn = QPushButton("ℹ️ Информация")
        info_btn.setToolTip("Показать информацию о панели инструментов")
        info_btn.setStyleSheet("""
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
            QPushButton:hover {
                background-color: rgba(90, 90, 90, 0.9);
                border-color: rgba(120, 120, 120, 0.8);
            }
            QPushButton:pressed {
                background-color: rgba(60, 60, 60, 0.9);
            }
        """)
        info_btn.clicked.connect(lambda: self.show_view('info'))
        layout.addWidget(info_btn)
        
        # Placeholder для будущих кнопок
        placeholder_label = QLabel("🚧 Дополнительные инструменты будут добавлены позже")
        placeholder_label.setStyleSheet("""
            QLabel {
                color: rgba(200, 200, 200, 0.7);
                font-size: 11px;
                font-style: italic;
                padding: 10px;
                border: 1px dashed rgba(100, 100, 100, 0.4);
                border-radius: 4px;
                background-color: rgba(50, 50, 50, 0.3);
            }
        """)
        layout.addWidget(placeholder_label)
        
        return view_widget
        
    def create_info_view(self):
        """Создание информационного вида"""
        view_widget = QWidget()
        layout = QVBoxLayout(view_widget)
        layout.setSpacing(10)
        
        # Заголовок информационного раздела
        info_title = QLabel("📋 Информация о панели")
        info_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 0px;
                border-bottom: 1px solid rgba(100, 100, 100, 0.5);
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(info_title)
        
        # Информационный текст
        info_text = QLabel("""
<p style="color: rgba(220, 220, 220, 0.9); font-size: 11px; line-height: 1.4;">
<b>🔧 Панель инструментов Chata Widget</b><br><br>

<b>Навигация:</b><br>
• Используйте кнопки ◀ ▶ для перемещения между видами<br>
• Кнопка ✕ закрывает панель<br><br>

<b>Текущая функциональность:</b><br>
• Информационный раздел (этот экран)<br>
• Система навигации между видами<br><br>

<b>Планируется добавить:</b><br>
• Настройки чата<br>
• Статистика использования<br>
• Дополнительные инструменты<br><br>

<i>📖 Для разработчиков: см. README_PANEL_TOOLS.md</i>
</p>
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("""
            QLabel {
                background-color: rgba(60, 60, 60, 0.3);
                border: 1px solid rgba(100, 100, 100, 0.3);
                border-radius: 6px;
                padding: 10px;
            }
        """)
        layout.addWidget(info_text)
        
        # Кнопка возврата к главному виду
        back_to_main_btn = QPushButton("🏠 Вернуться к главной")
        back_to_main_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(50, 100, 150, 0.8);
                color: white;
                border: 1px solid rgba(70, 120, 170, 0.6);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: rgba(70, 120, 170, 0.9);
                border-color: rgba(90, 140, 190, 0.8);
            }
            QPushButton:pressed {
                background-color: rgba(40, 80, 130, 0.9);
            }
        """)
        back_to_main_btn.clicked.connect(lambda: self.show_view('main'))
        layout.addWidget(back_to_main_btn)
        
        return view_widget
        
    def show_view(self, view_name):
        """Показать указанный вид и добавить в историю навигации"""
        if view_name not in self.views:
            print(f"Предупреждение: Вид '{view_name}' не найден")
            return
            
        # Очищаем текущее содержимое
        self.clear_content_layout()
        
        # Добавляем новый вид
        self.content_layout.addWidget(self.views[view_name])
        
        # Обновляем историю навигации
        # Если мы не в конце истории, удаляем все элементы после текущего
        if self.current_view_index < len(self.navigation_history) - 1:
            self.navigation_history = self.navigation_history[:self.current_view_index + 1]
        
        # Добавляем новый вид в историю (если он отличается от текущего)
        if not self.navigation_history or self.navigation_history[-1] != view_name:
            self.navigation_history.append(view_name)
            self.current_view_index = len(self.navigation_history) - 1
        
        # Обновляем заголовок
        self.update_title_for_view(view_name)
        
        # Обновляем состояние кнопок навигации
        self.update_navigation_buttons()
        
    def clear_content_layout(self):
        """Очистить layout содержимого"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
                
    def update_title_for_view(self, view_name):
        """Обновить заголовок в зависимости от текущего вида"""
        titles = {
            'main': "🔧 Панель инструментов",
            'info': "📋 Информация"
        }
        self.title_label.setText(titles.get(view_name, "🔧 Панель инструментов"))
        
    def navigate_back(self):
        """Навигация назад"""
        if self.current_view_index > 0:
            self.current_view_index -= 1
            view_name = self.navigation_history[self.current_view_index]
            
            # Показываем вид без добавления в историю
            self.clear_content_layout()
            self.content_layout.addWidget(self.views[view_name])
            self.update_title_for_view(view_name)
            self.update_navigation_buttons()
            
    def navigate_forward(self):
        """Навигация вперёд"""
        if self.current_view_index < len(self.navigation_history) - 1:
            self.current_view_index += 1
            view_name = self.navigation_history[self.current_view_index]
            
            # Показываем вид без добавления в историю
            self.clear_content_layout()
            self.content_layout.addWidget(self.views[view_name])
            self.update_title_for_view(view_name)
            self.update_navigation_buttons()
            
    def update_navigation_buttons(self):
        """Обновить состояние кнопок навигации"""
        # Кнопка "Назад" активна, если мы не в начале истории
        self.back_btn.setEnabled(self.current_view_index > 0)
        
        # Кнопка "Вперёд" активна, если мы не в конце истории
        self.forward_btn.setEnabled(self.current_view_index < len(self.navigation_history) - 1)
        
    def add_button(self, button):
        """Добавить кнопку в главный вид панели (для обратной совместимости)"""
        # Находим layout главного вида и добавляем кнопку
        main_view = self.views.get('main')
        if main_view and main_view.layout():
            # Применяем стандартный стиль
            button.setStyleSheet("""
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
                QPushButton:hover {
                    background-color: rgba(90, 90, 90, 0.9);
                    border-color: rgba(120, 120, 120, 0.8);
                }
                QPushButton:pressed {
                    background-color: rgba(60, 60, 60, 0.9);
                }
            """)
            # Вставляем кнопку перед placeholder'ом (если он есть)
            layout = main_view.layout()
            if layout.count() > 1:  # Есть placeholder
                layout.insertWidget(layout.count() - 1, button)
            else:
                layout.addWidget(button)
        
    def show_panel(self, target_rect):
        """Показать панель"""
        if self.is_visible:
            return
            
        self.is_visible = True
        
        # Панель занимает почти всю область чата
        panel_rect = QRect(
            target_rect.x() + 20,  # Небольшой отступ слева
            target_rect.y() + 20,  # Небольшой отступ сверху
            target_rect.width() - 40,  # Почти вся ширина чата
            target_rect.height() - 40  # Почти вся высота чата
        )
        
        self.setGeometry(panel_rect)
        self.show()
        
    def hide_panel(self):
        """Скрыть панель"""
        if not self.is_visible:
            return
            
        self.is_visible = False
        self.hide()
        
    def toggle_panel(self, target_rect):
        """Переключить видимость панели"""
        if self.is_visible:
            self.hide_panel()
        else:
            self.show_panel(target_rect)


class PanelTrigger(QPushButton):
    """Кнопка для показа/скрытия боковой панели"""
    
    panel_toggle_requested = Signal()
    
    def __init__(self, text="🔧 Панель инструментов", parent=None):
        super().__init__(text, parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка внешнего вида кнопки"""
        self.setStyleSheet("""
            PanelTrigger {
                color: rgba(200, 200, 200, 0.9);
                background-color: rgba(60, 60, 60, 0.8);
                border: 1px solid rgba(100, 100, 100, 0.6);
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                min-height: 24px;
            }
            PanelTrigger:hover {
                color: white;
                background-color: rgba(80, 80, 80, 0.9);
                border-color: rgba(120, 120, 120, 0.8);
            }
            PanelTrigger:pressed {
                background-color: rgba(50, 50, 50, 0.9);
            }
        """)
        self.clicked.connect(self.panel_toggle_requested.emit)
        

class SidePanelContainer(QWidget):
    """Контейнер, объединяющий триггер и боковую панель"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        # Триггер
        self.trigger = PanelTrigger()
        self.layout.addWidget(self.trigger)
        
        # Боковая панель (создается, но изначально скрыта)
        self.panel = SlidingPanel(parent=self.parent())
        self.panel.hide()
        
    def setup_connections(self):
        """Настройка подключений сигналов"""
        self.trigger.panel_toggle_requested.connect(self.toggle_panel)
        
    def toggle_panel(self):
        """Переключить видимость боковой панели"""
        if hasattr(self, 'panel'):
            # Получаем глобальные координаты триггера
            trigger_rect = self.trigger.geometry()
            parent_rect = self.mapToGlobal(trigger_rect.topLeft())
            
            # Создаем QRect для панели - используем всю область родителя (чата)
            if self.parent():
                parent_widget = self.parent()
                panel_rect = QRect(
                    0,  # Начало области чата
                    0,  # Начало области чата
                    parent_widget.width(),   # Полная ширина чата
                    parent_widget.height()   # Полная высота чата
                )
                self.panel.toggle_panel(panel_rect)
            
    def add_button_to_panel(self, button):
        """Добавить кнопку в боковую панель"""
        self.panel.add_button(button)
