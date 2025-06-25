"""
Пример расширения для GopiAI Standalone Interface
================================================

Демонстрирует, как легко добавлять новую функциональность
без изменения основного файла интерфейса.

Это расширение добавляет:
- Панель быстрых заметок
- Калькулятор
- Список задач
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QListWidget, QLineEdit,
    QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt


class QuickNotesWidget(QWidget):
    """Виджет быстрых заметок"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("quickNotes")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        # Заголовок
        header = QLabel("📝 Быстрые заметки")
        header.setObjectName("panelHeader")
        header.setFixedHeight(30)
        layout.addWidget(header)
        
        # Устанавливаем название виджета для вкладок
        self.setWindowTitle("📝 Заметки")
        
        # Область заметок
        self.notes_area = QTextEdit()
        self.notes_area.setPlaceholderText("Введите ваши заметки здесь...")
        layout.addWidget(self.notes_area, 1)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Сохранить")
        clear_btn = QPushButton("🗑️ Очистить")
        
        save_btn.clicked.connect(self._save_notes)
        clear_btn.clicked.connect(self._clear_notes)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(clear_btn)
        layout.addLayout(buttons_layout)

    def _save_notes(self):
        notes = self.notes_area.toPlainText()
        try:
            with open("quick_notes.txt", "w", encoding="utf-8") as f:
                f.write(notes)
            QMessageBox.information(self, "Сохранено", "Заметки сохранены в quick_notes.txt")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить: {e}")

    def _clear_notes(self):
        self.notes_area.clear()


class SimpleCalculatorWidget(QWidget):
    """Простой калькулятор"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("calculator")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        # Заголовок
        header = QLabel("🔢 Калькулятор")
        header.setObjectName("panelHeader")
        header.setFixedHeight(30)
        layout.addWidget(header)
        
        # Устанавливаем название виджета для вкладок
        self.setWindowTitle("🔢 Калькулятор")
        
        # Поле ввода
        self.expression_input = QLineEdit()
        self.expression_input.setPlaceholderText("Введите выражение (например: 2+2*3)")
        self.expression_input.returnPressed.connect(self._calculate)
        layout.addWidget(self.expression_input)
        
        # Результат
        self.result_label = QLabel("Результат: ")
        self.result_label.setStyleSheet("color: #00ff00; font-weight: bold;")
        layout.addWidget(self.result_label)
        
        # Кнопка вычисления
        calc_btn = QPushButton("= Вычислить")
        calc_btn.clicked.connect(self._calculate)
        layout.addWidget(calc_btn)
        
        # Заполнитель
        layout.addStretch()

    def _calculate(self):
        expression = self.expression_input.text().strip()
        if not expression:
            return
            
        try:
            # Безопасное вычисление (только математические операции)
            allowed_chars = set("0123456789+-*/().^ ")
            if all(c in allowed_chars for c in expression):
                expression = expression.replace("^", "**")  # Степень
                result = eval(expression)
                self.result_label.setText(f"Результат: {result}")
            else:
                self.result_label.setText("Ошибка: недопустимые символы")
        except Exception as e:
            self.result_label.setText(f"Ошибка: {e}")


class TaskListWidget(QWidget):
    """Список задач"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("taskList")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        # Заголовок
        header = QLabel("✅ Список задач")
        header.setObjectName("panelHeader")
        header.setFixedHeight(30)
        layout.addWidget(header)
        
        # Устанавливаем название виджета для вкладок
        self.setWindowTitle("✅ Задачи")
        
        # Поле для новой задачи
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Введите новую задачу...")
        self.task_input.returnPressed.connect(self._add_task)
        
        add_btn = QPushButton("➕")
        add_btn.setFixedSize(30, 30)
        add_btn.clicked.connect(self._add_task)
        
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)
        
        # Список задач
        self.task_list = QListWidget()
        self.task_list.itemDoubleClicked.connect(self._toggle_task)
        layout.addWidget(self.task_list, 1)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        complete_btn = QPushButton("✅ Выполнено")
        delete_btn = QPushButton("🗑️ Удалить")
        clear_btn = QPushButton("🧹 Очистить все")
        
        complete_btn.clicked.connect(self._complete_task)
        delete_btn.clicked.connect(self._delete_task)
        clear_btn.clicked.connect(self._clear_all)
        
        buttons_layout.addWidget(complete_btn)
        buttons_layout.addWidget(delete_btn)
        buttons_layout.addWidget(clear_btn)
        layout.addLayout(buttons_layout)

    def _add_task(self):
        task_text = self.task_input.text().strip()
        if task_text:
            item = QListWidgetItem(f"⏳ {task_text}")
            item.setData(Qt.ItemDataRole.UserRole, False)  # Не выполнено
            self.task_list.addItem(item)
            self.task_input.clear()

    def _toggle_task(self, item):
        completed = item.data(Qt.ItemDataRole.UserRole)
        task_text = item.text()[2:]  # Убираем иконку
        
        if completed:
            item.setText(f"⏳ {task_text}")
            item.setData(Qt.ItemDataRole.UserRole, False)
        else:
            item.setText(f"✅ {task_text}")
            item.setData(Qt.ItemDataRole.UserRole, True)

    def _complete_task(self):
        current_item = self.task_list.currentItem()
        if current_item:
            self._toggle_task(current_item)

    def _delete_task(self):
        current_row = self.task_list.currentRow()
        if current_row >= 0:
            self.task_list.takeItem(current_row)

    def _clear_all(self):
        self.task_list.clear()


def init_productivity_extension(main_window):
    """
    Инициализация расширения продуктивности
    
    Добавляет новые панели в интерфейс:
    - Быстрые заметки
    - Калькулятор  
    - Список задач
    """
    try:
        # Создаем виджеты
        notes_widget = QuickNotesWidget()
        calc_widget = SimpleCalculatorWidget() 
        tasks_widget = TaskListWidget()
        # Добавляем их в интерфейс как вкладки в нижней панели
        if hasattr(main_window, 'add_dock_widget'):
            main_window.add_dock_widget("quick_notes", notes_widget, "bottom")
            main_window.add_dock_widget("calculator", calc_widget, "bottom")
            main_window.add_dock_widget("tasks", tasks_widget, "bottom")
            
        print("✅ Расширение продуктивности загружено!")
        print("   📝 Быстрые заметки")
        print("   🔢 Калькулятор")
        print("   ✅ Список задач")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке расширения продуктивности: {e}")
        return False


# Автоматическая инициализация при импорте
def auto_init(main_window):
    """Автоматическая инициализация расширения"""
    return init_productivity_extension(main_window)
