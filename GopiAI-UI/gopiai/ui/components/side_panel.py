import os
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QButtonGroup, QRadioButton)
from PySide6.QtCore import QRect, Signal, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6 import QtCore


class SlidingPanel(QWidget):
    """Боковая панель с навигационной системой"""
    
    # Сигнал об изменении режима администратора
    admin_mode_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_visible = False
        self.is_admin_mode = False  # По умолчанию режим обычного пользователя
        
        # История навигации для кнопок вперёд-назад
        self.navigation_history = []
        self.current_view_index = -1
        
        # Словарь видов панели
        self.views = {}
        
        # Текущий режим пользователя (False - обычный, True - админ)
        self.is_admin_mode = False
        
        self.setup_ui()
        self.setup_views()
        
        # Инициализация режима пользователя
        self.setup_user_mode()
        
    def setup_ui(self):
        """Настройка интерфейса панели"""
        self.setStyleSheet("""
            SlidingPanel {
                border-radius: 12px;
            }
            QRadioButton {
                padding: 2px 5px;
                font-size: 11px;
            }
            QRadioButton:checked {
                font-weight: bold;
            }
            QPushButton#logsButton {
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                margin-top: 8px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
            }
            QPushButton#logsButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # Основной layout для содержимого панели
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)
        
        # Заголовок панели с навигацией и кнопкой закрытия
        header_layout = QHBoxLayout()
        
        # Кнопки навигации (стрелочки вперёд-назад)
        self.back_btn = QPushButton("◀")
        self.back_btn.setToolTip("Назад")
        self.back_btn.setStyleSheet("""
            QPushButton {
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 30px;
                max-width: 30px;
                min-height: 24px;
                max-height: 24px;
            }
            QPushButton:hover {
            }
            QPushButton:pressed {
            }
            QPushButton:disabled {
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
        self.title_label = QLabel("Панель инструментов")
        self.title_label.setStyleSheet("""
            QLabel {
                color;
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
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }
            QPushButton:hover {
            }
            QPushButton:pressed {
            }
        """)
        close_btn.clicked.connect(self.hide_panel)
        header_layout.addWidget(close_btn)
        
        self.main_layout.addLayout(header_layout)
        
        # Разделительная линия
        separator = QLabel()
        separator.setStyleSheet("""
            QLabel {
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
        
        # Добавляем переключатель режима пользователя
        self.setup_user_mode_ui()
        
        # Добавляем кнопку для открытия логов
        self.setup_logs_button()
        
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
        info_btn = QPushButton("Информация")
        info_btn.setToolTip("Показать информацию о панели инструментов")
        info_btn.setStyleSheet("""
            QPushButton {
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                text-align: left;
                min-height: 25px;
            }
            QPushButton:hover {
            }
            QPushButton:pressed {
            }
        """)
        info_btn.clicked.connect(lambda: self.show_view('info'))
        layout.addWidget(info_btn)
        
        # Placeholder для будущих кнопок
        placeholder_label = QLabel("Дополнительные инструменты будут добавлены позже")
        placeholder_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                font-style: italic;
                padding: 10px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(placeholder_label)
        
        # Добавляем информацию о текущем режиме
        self.mode_info_label = QLabel("Режим: Обычный пользователь")
        self.mode_info_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #666;
                padding: 4px 8px;
                margin-top: 8px;
                border-top: 1px solid #eee;
            }
        """)
        layout.addWidget(self.mode_info_label)
        
        return view_widget
        
    def create_info_view(self):
        """Создание информационного вида"""
        view_widget = QWidget()
        layout = QVBoxLayout(view_widget)
        layout.setSpacing(10)
        
        # Заголовок информационного раздела
        info_title = QLabel("Информация о панели")
        info_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 5px 0px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(info_title)
        
        # Информационный текст
        info_text = QLabel("""
<b>Панель инструментов Chat Widget</b><br><br>

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

<i>Для разработчиков: см. README_PANEL_TOOLS.md</i>
</p>
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("""
            QLabel {
                border-radius: 6px;
                padding: 10px;
            }
        """)
        layout.addWidget(info_text)
        
        # Кнопка возврата к главному виду
        back_to_main_btn = QPushButton("Вернуться к главной")
        back_to_main_btn.setStyleSheet("""
            QPushButton {
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                min-height: 25px;
            }
            QPushButton:hover {
            }
            QPushButton:pressed {
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
            'main': "Панель инструментов",
            'info': "Информация"
        }
        self.title_label.setText(titles.get(view_name, "Панель инструментов"))
        
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
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 12px;
                    text-align: left;
                    min-height: 25px;
                }
                QPushButton:hover {
                }
                QPushButton:pressed {
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

    # ===== Новые методы для работы с пользовательским режимом и логами =====
    
    def setup_user_mode(self):
        """Инициализация режима пользователя"""
        # Здесь можно добавить загрузку сохраненного режима из настроек
        pass
    
    def setup_user_mode_ui(self):
        """Настройка интерфейса переключения режима пользователя"""
        mode_group = QWidget()
        mode_layout = QVBoxLayout(mode_group)
        mode_layout.setContentsMargins(8, 8, 8, 8)
        mode_layout.setSpacing(4)
        
        # Заголовок
        mode_label = QLabel("Режим работы:")
        mode_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        mode_layout.addWidget(mode_label)
        
        # Группа переключателей
        self.mode_button_group = QButtonGroup(self)
        
        # Обычный пользователь
        self.normal_mode_btn = QRadioButton("Обычный пользователь (рекомендуется)")
        self.normal_mode_btn.setToolTip("Стандартный режим с базовыми правами")
        self.normal_mode_btn.setChecked(not self.is_admin_mode)
        self.normal_mode_btn.toggled.connect(lambda: self.set_admin_mode(False))
        self.mode_button_group.addButton(self.normal_mode_btn)
        mode_layout.addWidget(self.normal_mode_btn)
        
        # Администратор
        self.admin_mode_btn = QRadioButton("Администратор")
        self.admin_mode_btn.setToolTip("Расширенный режим с полными правами")
        self.admin_mode_btn.setChecked(self.is_admin_mode)
        self.admin_mode_btn.toggled.connect(lambda: self.set_admin_mode(True))
        self.mode_button_group.addButton(self.admin_mode_btn)
        mode_layout.addWidget(self.admin_mode_btn)
        
        # Добавляем внизу панели
        self.main_layout.addWidget(mode_group)
    
    def setup_logs_button(self):
        """Добавление кнопки для открытия папки с логами"""
        logs_btn = QPushButton("Открыть папку с логами")
        logs_btn.setObjectName("logsButton")
        logs_btn.clicked.connect(self.open_logs_folder)
        self.main_layout.addWidget(logs_btn)
    
    def set_admin_mode(self, is_admin):
        """Установка режима администратора"""
        self.is_admin_mode = is_admin
        if hasattr(self, 'mode_info_label'):
            mode_text = "Администратор" if is_admin else "Обычный пользователь"
            self.mode_info_label.setText(f"Режим: {mode_text}")
        
        # Здесь можно добавить логику изменения прав доступа
        # Например, показать/скрыть административные функции
        self.admin_mode_changed.emit(is_admin)
    
    def open_logs_folder(self):
        """Открытие папки с логами в проводнике системы"""
        try:
            # Путь к папке с логами (относительно корня приложения)
            logs_dir = os.path.join(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
                "logs")
            
            # Создаем папку, если её нет
            os.makedirs(logs_dir, exist_ok=True)
            
            # Открываем в проводнике
            if os.name == 'nt':  # Windows
                os.startfile(logs_dir)
            elif os.name == 'posix':  # macOS и Linux
                if sys.platform == 'darwin':
                    subprocess.run(['open', logs_dir])
                else:
                    subprocess.run(['xdg-open', logs_dir])
        except Exception as e:
            print(f"Ошибка при открытии папки с логами: {e}")


class PanelTrigger(QPushButton):
    """Кнопка для показа/скрытия боковой панели"""
    panel_toggle_requested = Signal()
    admin_mode_changed = Signal(bool)  # Сигнал об изменении режима администратора


class PanelTrigger(QPushButton):
    """Кнопка для показа/скрытия боковой панели"""
    panel_toggle_requested = Signal()
    admin_mode_changed = Signal(bool)  # Сигнал об изменении режима администратора

    def __init__(self, text="Панель инструментов", parent=None):
        super().__init__(text, parent)
        self.setup_ui()

    def setup_ui(self):
        """Настройка внешнего вида кнопки"""
        self.setStyleSheet("""
            PanelTrigger {
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                min-height: 24px;
            }
            PanelTrigger:hover {
            }
            PanelTrigger:pressed {
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
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(5)
        
        # Триггер
        self.trigger = PanelTrigger()
        self.main_layout.addWidget(self.trigger)
        
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
                # Приводим к QWidget, если это необходимо
                # Поднимаемся по иерархии родителей, пока не найдем QWidget
                while parent_widget is not None and not isinstance(parent_widget, QWidget):
                    if hasattr(parent_widget, 'parent'):
                        parent_widget = parent_widget.parent()
                    else:
                        parent_widget = None
                if isinstance(parent_widget, QWidget):
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
