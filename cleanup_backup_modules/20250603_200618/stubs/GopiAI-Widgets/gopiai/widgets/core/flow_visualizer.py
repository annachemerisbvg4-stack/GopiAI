import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QApplication, QDialog, QSizePolicy, QMessageBox
)
# 🚧 ЗАГЛУШКА! TODO_STUB: from gopiai.core.agent_stubs import BaseAgentStub
# from gopiai.app.flow.base import BaseFlow  # 💀 ЦИКЛИЧЕСКАЯ ЗАВИСИМОСТЬ УНИЧТОЖЕНА!
from gopiai.widgets.core.icon_adapter import get_icon
from gopiai.widgets.managers.theme_manager import ThemeManager

from .i18n.translator import tr


class FlowNodeWidget(QFrame):
    """Виджет, представляющий узел потока."""

    def __init__(self, name, node_type="agent", parent=None):
        super().__init__(parent)
        self.name = name
        self.node_type = node_type
        self.connections = []

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)

        # Получаем менеджер тем
        theme_manager = ThemeManager.instance()
        # Устанавливаем фиксированную высоту, но переменную ширину
        self.setMinimumHeight(60)
        self.setMaximumHeight(60)
        self.setMinimumWidth(120)

        # Цвета для разных типов узлов
        node_colors = {
            "agent": theme_manager.get_color("accent"),
            "tool": theme_manager.get_color("success"),
            "flow": theme_manager.get_color("warning"),
            "default": theme_manager.get_color("background")
        }
        background = node_colors.get(node_type, node_colors["default"])
        self.setStyleSheet(f"background-color: {background};")

        self._setup_ui()

    def _setup_ui(self):
        """Настраивает UI виджета узла."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Метка с названием узла
        name_label = QLabel(self.name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-weight: bold;")

        # Метка с типом узла
        type_key = f"flow_visualizer.node.{self.node_type}"
        type_label = QLabel(tr(type_key, self.node_type.capitalize()))
        type_label.setAlignment(Qt.AlignCenter)
        type_label.setStyleSheet("font-style: italic;")

        layout.addWidget(name_label)
        layout.addWidget(type_label)

    def add_connection(self, node):
        """Добавляет связь с другим узлом."""
        self.connections.append(node)


class FlowVisualizer(QWidget):
    """Виджет для визуализации потока (Flow)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes = []
        self._setup_ui()

    def _setup_ui(self):
        """Настраивает UI визуализатора."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Заголовок
        header_label = QLabel(tr("flow_visualizer.header", "Flow Structure Visualization"))
        header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_label.setAlignment(Qt.AlignCenter)

        # Область для отрисовки узлов и связей
        self.drawing_area = FlowDrawingArea()
        self.drawing_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.drawing_area)

        # Добавляем элементы в основной layout
        self.main_layout.addWidget(header_label)
        self.main_layout.addWidget(scroll_area)

    def set_flow(self, flow):
        """Устанавливает поток для визуализации."""
        self.clear()
        if isinstance(flow, BaseFlow):
            self._analyze_flow(flow)
            self.drawing_area.update()

    def clear(self):
        """Очищает визуализацию."""
        self.nodes = []
        self.drawing_area.nodes = []
        self.drawing_area.update()

    def _analyze_flow(self, flow):
        """Анализирует структуру потока и создает узлы для визуализации."""
        # Сначала добавляем сам flow как узел
        flow_node = FlowNodeWidget(flow.name, "flow")
        self.nodes.append(flow_node)

        # Если это планирующий поток, добавляем агентов
        if hasattr(flow, 'agents'):
            for agent_name, agent in flow.agents.items():
                if isinstance(agent, BaseAgent):
                    agent_node = FlowNodeWidget(agent_name, "agent")
                    self.nodes.append(agent_node)
                    flow_node.add_connection(agent_node)

                    # Добавляем инструменты агента
                    if hasattr(agent, 'available_tools') and hasattr(agent.available_tools, 'tools'):
                        for tool in agent.available_tools.tools:
                            tool_node = FlowNodeWidget(tool.name, "tool")
                            self.nodes.append(tool_node)
                            agent_node.add_connection(tool_node)

        # Заполняем область рисования узлами
        self.drawing_area.nodes = self.nodes


class FlowDrawingArea(QWidget):
    """Область для отрисовки узлов и связей потока."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes = []

    def paintEvent(self, event):
        """Отрисовывает узлы и связи."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Если узлов нет, ничего не рисуем
        if not self.nodes:
            return

        # Устанавливаем размер области рисования
        self.setMinimumSize(800, 600)

        # Размещаем узлы
        self._layout_nodes()

        # Рисуем связи
        self._draw_connections(painter)

        # Рисуем узлы
        for node in self.nodes:
            node.show()

    def _layout_nodes(self):
        """Размещает узлы на области рисования."""
        # Удаляем старые узлы
        for node in self.nodes:
            node.setParent(None)

        # Добавляем узлы на область рисования
        for node in self.nodes:
            node.setParent(self)

        # Простое расположение узлов - корневой узел вверху, остальные уровнями ниже
        if not self.nodes:
            return

        # Корневой узел (flow) размещаем вверху по центру
        root_node = self.nodes[0]
        root_node.setGeometry(self.width() // 2 - 70, 20, 140, 60)

        # Остальные узлы размещаем уровнями ниже
        # Находим узлы агентов (второй уровень)
        agent_nodes = [node for node in self.nodes if node.node_type == "agent"]
        agent_count = len(agent_nodes)

        if agent_count > 0:
            # Расстояние между агентами
            if agent_count == 1:
                agent_spacing = 0
            else:
                agent_spacing = min(200, (self.width() - 200) // max(1, agent_count - 1))

            # Начальная x-координата для первого агента
            start_x = max(20, (self.width() - (agent_count * 140 + (agent_count - 1) * agent_spacing)) // 2)

            # Размещаем агентов
            for i, agent_node in enumerate(agent_nodes):
                x = start_x + i * (140 + agent_spacing)
                agent_node.setGeometry(x, 120, 140, 60)

            # Размещаем инструменты под соответствующими агентами
            for agent_node in agent_nodes:
                tool_nodes = [node for node in self.nodes
                              if node.node_type == "tool" and agent_node in self.nodes and node in agent_node.connections]
                tool_count = len(tool_nodes)

                if tool_count > 0:
                    # Расстояние между инструментами
                    if tool_count == 1:
                        tool_spacing = 0
                    else:
                        tool_spacing = min(160, (self.width() - 160) // max(1, tool_count - 1))

                    # Начальная x-координата для первого инструмента
                    agent_center_x = agent_node.x() + agent_node.width() // 2
                    start_x = max(20, agent_center_x - ((tool_count * 140 + (tool_count - 1) * tool_spacing) // 2))

                    # Размещаем инструменты
                    for i, tool_node in enumerate(tool_nodes):
                        x = start_x + i * (140 + tool_spacing)
                        tool_node.setGeometry(x, 220, 140, 60)

    def _draw_connections(self, painter):
        """Рисует связи между узлами."""
        pen = QPen(QColor(100, 100, 100))
        pen.setWidth(2)
        painter.setPen(pen)

        for node in self.nodes:
            for connected_node in node.connections:
                # Находим координаты центров узлов
                start_x = node.x() + node.width() // 2
                start_y = node.y() + node.height()
                end_x = connected_node.x() + connected_node.width() // 2
                end_y = connected_node.y()

                # Рисуем кривую линию
                path = QPainterPath()
                path.moveTo(start_x, start_y)

                # Контрольные точки для кривой Безье
                ctrl1_x = start_x
                ctrl1_y = start_y + (end_y - start_y) // 3
                ctrl2_x = end_x
                ctrl2_y = end_y - (end_y - start_y) // 3

                path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, end_x, end_y)
                painter.drawPath(path)

                # Рисуем стрелку
                angle = 0.5  # Угол стрелки
                arrowSize = 10  # Размер стрелки

                # Вычисляем угол линии
                line_angle = 3.14159 / 2  # Вертикальная линия вниз

                # Рисуем две линии стрелки
                painter.save()
                painter.translate(end_x, end_y)
                painter.drawLine(0, 0,
                                 int(arrowSize * 3 * (-1 * angle - line_angle).real),
                                 int(arrowSize * 3 * (-1 * angle - line_angle).imag))
                painter.drawLine(0, 0,
                                 int(arrowSize * 3 * (angle - line_angle).real),
                                 int(arrowSize * 3 * (angle - line_angle).imag))
                painter.restore()


def show_flow_visualizer_dialog(flow, parent=None):
    """
    Отображает диалог с визуализацией потока.

    Args:
        flow (BaseFlow): Поток для визуализации.
        parent (QWidget): Родительский виджет.

    Returns:
        bool: True, если диалог был успешно отображен, иначе False.
    """
    try:
        # Создаем диалог
        dialog = QDialog(parent)
        dialog.setWindowTitle(tr("flow_visualizer.title", "Flow Visualizer"))
        dialog.setMinimumSize(800, 600)

        # Создаем визуализатор
        visualizer = FlowVisualizer(dialog)

        # Устанавливаем поток для визуализации
        visualizer.set_flow(flow)

        # Кнопка закрытия
        close_button = QPushButton(tr("flow_visualizer.close", "Close"), dialog)
        close_button.setIcon(get_icon("close"))
        close_button.clicked.connect(dialog.accept)

        # Устанавливаем layout
        layout = QVBoxLayout(dialog)
        layout.addWidget(visualizer)

        # Добавляем кнопку внизу
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        # Отображаем диалог
        dialog.exec()
        return True
    except Exception as e:
        QMessageBox.critical(
            parent,
            tr("dialogs.error", "Error"),
            f"Error visualizing flow: {str(e)}"
        )
        return False


# Тестовое приложение
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Создаем тестовые данные
    class TestFlow:
        def __init__(self):
            self.name = "Test Flow"
            self.agents = {
                "planner": TestAgent("Planning Agent"),
                "executor": TestAgent("Execution Agent")
            }

    class TestAgent:
        def __init__(self, name):
            self.name = name
            self.available_tools = type('obj', (object,), {
                'tools': [
                    type('obj', (object,), {'name': 'WebSearch'}),
                    type('obj', (object,), {'name': 'PythonExecute'}),
                    type('obj', (object,), {'name': 'FileOperations'})
                ]
            })

    # Создаем тестовый поток
    test_flow = TestFlow()

    # Показываем диалог визуализации
    show_flow_visualizer_dialog(test_flow)

    sys.exit(app.exec())
