"""
Модуль для обратной совместимости с кодом, использующим FlowVisualizationDialog.
Заглушка для функциональности визуализации потока.
"""

# Заглушка для функции визуализации потока
def show_flow_visualizer_dialog(*args, **kwargs):
    """Заглушка для диалога визуализации потока"""
    print("FlowVisualizationDialog временно недоступен")
    return None

# Для обратной совместимости с main_window.py
FlowVisualizationDialog = show_flow_visualizer_dialog
