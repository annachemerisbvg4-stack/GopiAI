# 📅 TODO_STUB_SEARCH: найти командой grep -r 'TODO_STUB' .
"""
View Management Mixin for MainWindow.

This module contains methods related to dock and view management in MainWindow.
"""

from gopiai.core.logging import get_logger
logger = get_logger().logger

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QDockWidget, QMessageBox
from gopiai.widgets.i18n.translator import tr
# # 🚧 ЗАГЛУШКА! TODO_STUB: Используй gopiai.core.ui_utils

# Временные заглушки для функций из ui_utils
def apply_dock_constraints(window):
    # 🚧 ЗАГЛУШКА! TODO_STUB: Документированная заглушка
    """Временная заглушка для apply_dock_constraints"""
    pass

def fix_duplicate_docks(window):
    # 🚧 ЗАГЛУШКА! TODO_STUB: Документированная заглушка
    """Временная заглушка для fix_duplicate_docks"""
    pass

logger = get_logger().logger


class ViewManagementMixin:
    """Provides view management functionality for MainWindow."""

    def _toggle_project_explorer(self, checked=None):
        """Переключает видимость проводника проекта."""
        logger.info(f"Action: Toggle Project Explorer {checked}")

        if (
            hasattr(self, "project_explorer_dock")
            and self.project_explorer_dock
            and isinstance(self.project_explorer_dock, QDockWidget)
        ):
            if checked is None:
                # Если аргумент не передан, инвертируем текущее состояние
                checked = not self.project_explorer_dock.isVisible()

            if checked:
                # Показываем док
                self.project_explorer_dock.show()
                # Обновляем состояние в меню, если оно есть
                if (
                    hasattr(self, "toggle_project_explorer_action")
                    and self.toggle_project_explorer_action
                ):
                    self.toggle_project_explorer_action.setChecked(True)
                logger.info("Project explorer dock shown")
            else:
                # Скрываем док
                self.project_explorer_dock.hide()
                # Обновляем состояние в меню, если оно есть
                if (
                    hasattr(self, "toggle_project_explorer_action")
                    and self.toggle_project_explorer_action
                ):
                    self.toggle_project_explorer_action.setChecked(False)
                logger.info("Project explorer dock hidden")

            # Сохраняем состояние
            self.settings.setValue("project_explorer_visible", checked)
        else:
            logger.error("Cannot toggle project explorer: dock not found")

    def _toggle_chat(self, checked=None):
        """Переключает видимость чата."""
        logger.info(f"Action: Toggle Chat {checked}")

        if (
            hasattr(self, "chat_dock")
            and self.chat_dock
            and isinstance(self.chat_dock, QDockWidget)
        ):
            if checked is None:
                # Если аргумент не передан, инвертируем текущее состояние
                checked = not self.chat_dock.isVisible()

            if checked:
                # Показываем док
                self.chat_dock.show()
                # Обновляем состояние в меню, если оно есть
                if hasattr(self, "toggle_chat_action") and self.toggle_chat_action:
                    self.toggle_chat_action.setChecked(True)
                logger.info("Chat dock shown")
            else:
                # Скрываем док
                self.chat_dock.hide()
                # Обновляем состояние в меню, если оно есть
                if hasattr(self, "toggle_chat_action") and self.toggle_chat_action:
                    self.toggle_chat_action.setChecked(False)
                logger.info("Chat dock hidden")

            # Сохраняем состояние
            self.settings.setValue("chat_visible", checked)
        else:
            logger.error("Cannot toggle chat: dock not found")

    def _toggle_terminal(self, checked=None):
        """Переключает видимость терминала."""
        logger.info(f"Action: Toggle Terminal {checked}")

        if (
            hasattr(self, "terminal_dock")
            and self.terminal_dock
            and isinstance(self.terminal_dock, QDockWidget)
        ):
            if checked is None:
                # Если аргумент не передан, инвертируем текущее состояние
                checked = not self.terminal_dock.isVisible()

            if checked:
                # Показываем док
                self.terminal_dock.show()
                # Обновляем состояние в меню, если оно есть
                if (
                    hasattr(self, "toggle_terminal_action")
                    and self.toggle_terminal_action
                ):
                    self.toggle_terminal_action.setChecked(True)
                logger.info("Terminal dock shown")
            else:
                # Скрываем док
                self.terminal_dock.hide()
                # Обновляем состояние в меню, если оно есть
                if (
                    hasattr(self, "toggle_terminal_action")
                    and self.toggle_terminal_action
                ):
                    self.toggle_terminal_action.setChecked(False)
                logger.info("Terminal dock hidden")

            # Сохраняем состояние
            self.settings.setValue("terminal_visible", checked)
        else:
            logger.error("Cannot toggle terminal: dock not found")

    def _toggle_browser(self, checked=None):
        """Переключает видимость браузера."""
        logger.info(f"Action: Toggle Browser {checked}")

        if (
            hasattr(self, "browser_dock")
            and self.browser_dock
            and isinstance(self.browser_dock, QDockWidget)
        ):
            if checked is None:
                # Если аргумент не передан, инвертируем текущее состояние
                checked = not self.browser_dock.isVisible()

            if checked:
                # Показываем док
                self.browser_dock.show()
                # Обновляем состояние в меню, если оно есть
                if (
                    hasattr(self, "toggle_browser_action")
                    and self.toggle_browser_action
                ):
                    self.toggle_browser_action.setChecked(True)
                logger.info("Browser dock shown")
            else:
                # Скрываем док
                self.browser_dock.hide()
                # Обновляем состояние в меню, если оно есть
                if (
                    hasattr(self, "toggle_browser_action")
                    and self.toggle_browser_action
                ):
                    self.toggle_browser_action.setChecked(False)
                logger.info("Browser dock hidden")

            # Сохраняем состояние
            self.settings.setValue("browser_visible", checked)
        else:
            logger.error("Cannot toggle browser: dock not found")

    def _update_view_menu(self):
        """Обновляет пункты меню 'Вид' в соответствии с текущим состоянием доков."""
        try:
            if (
                hasattr(self, "toggle_project_explorer_action")
                and hasattr(self, "project_explorer_dock")
                and self.project_explorer_dock
                and isinstance(self.project_explorer_dock, QDockWidget)
            ):
                self.toggle_project_explorer_action.setChecked(
                    self.project_explorer_dock.isVisible()
                )
            if (
                hasattr(self, "toggle_chat_action")
                and hasattr(self, "chat_dock")
                and self.chat_dock
                and isinstance(self.chat_dock, QDockWidget)
            ):
                self.toggle_chat_action.setChecked(self.chat_dock.isVisible())
            if (
                hasattr(self, "toggle_terminal_action")
                and hasattr(self, "terminal_dock")
                and self.terminal_dock
                and isinstance(self.terminal_dock, QDockWidget)
            ):
                self.toggle_terminal_action.setChecked(self.terminal_dock.isVisible())
            if (
                hasattr(self, "toggle_browser_action")
                and hasattr(self, "browser_dock")
                and self.browser_dock
                and isinstance(self.browser_dock, QDockWidget)
            ):
                self.toggle_browser_action.setChecked(self.browser_dock.isVisible())
            if (
                hasattr(self, "toggle_coding_agent_action")
                and hasattr(self, "unified_chat_view")
                and self.unified_chat_view
            ):
                self.toggle_coding_agent_action.setChecked(
                    self.unified_chat_view.isVisible()
                )
        except Exception as e:
            logger.error(f"Error updating view menu: {e}")

    def reset_dock_layout(self):
        """Сбрасывает расположение панелей к виду по умолчанию."""
        logger.info("Action: Reset Dock Layout")

        # Восстанавливаем состояние окон
        try:
            # Сначала делаем все доки плавающими, чтобы избежать конфликтов
            if hasattr(self, "project_explorer_dock") and self.project_explorer_dock:
                self.project_explorer_dock.setFloating(True)
            if hasattr(self, "chat_dock") and self.chat_dock:
                self.chat_dock.setFloating(True)
            if hasattr(self, "terminal_dock") and self.terminal_dock:
                self.terminal_dock.setFloating(True)
            if hasattr(self, "browser_dock") and self.browser_dock:
                self.browser_dock.setFloating(True)

            # Затем восстанавливаем их положение и размер
            if hasattr(self, "project_explorer_dock") and self.project_explorer_dock:
                self.project_explorer_dock.setFloating(False)
                self.addDockWidget(Qt.LeftDockWidgetArea, self.project_explorer_dock)
                self.project_explorer_dock.show()
                if hasattr(self, "toggle_project_explorer_action"):
                    self.toggle_project_explorer_action.setChecked(True)

            if hasattr(self, "chat_dock") and self.chat_dock:
                self.chat_dock.setFloating(False)
                self.addDockWidget(Qt.RightDockWidgetArea, self.chat_dock)
                self.chat_dock.show()
                if hasattr(self, "toggle_chat_action"):
                    self.toggle_chat_action.setChecked(True)

            if hasattr(self, "terminal_dock") and self.terminal_dock:
                self.terminal_dock.setFloating(False)
                self.addDockWidget(Qt.BottomDockWidgetArea, self.terminal_dock)
                self.terminal_dock.show()
                if hasattr(self, "toggle_terminal_action"):
                    self.toggle_terminal_action.setChecked(True)

            if hasattr(self, "browser_dock") and self.browser_dock:
                self.browser_dock.setFloating(False)
                self.addDockWidget(Qt.RightDockWidgetArea, self.browser_dock)
                self.browser_dock.show()
                if hasattr(self, "toggle_browser_action"):
                    self.toggle_browser_action.setChecked(True)

            # Табуляция чата и браузера, если оба существуют
            if (
                hasattr(self, "chat_dock")
                and self.chat_dock
                and hasattr(self, "browser_dock")
                and self.browser_dock
            ):
                self.tabifyDockWidget(self.chat_dock, self.browser_dock)
                # Активируем вкладку чата
                self.chat_dock.raise_()

            # Исправляем проблемы с доками
            fix_duplicate_docks(self)
            apply_dock_constraints(self)

            # Сохраняем новое состояние
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())

            logger.info("Dock layout reset to default")
            QMessageBox.information(
                self,
                tr("dialog.layout_reset.title", "Layout Reset"),
                tr(
                    "dialog.layout_reset.message",
                    "Window layout has been reset to default.",
                ),
            )
        except Exception as e:
            logger.error(f"Error resetting dock layout: {e}")
            QMessageBox.critical(
                self,
                tr("dialog.error", "Error"),
                tr(
                    "dialog.layout_reset.error", "Error resetting layout: {error}"
                ).format(error=str(e)),
            )

    def reset_layout(self):
        """Полностью сбрасывает все настройки макета, включая размеры окна."""
        logger.info("Action: Reset Full Layout")
        try:
            # Сбрасываем все настройки макета
            self.settings.remove("geometry")
            self.settings.remove("windowState")
            self.settings.remove("project_explorer_visible")
            self.settings.remove("chat_visible")
            self.settings.remove("terminal_visible")
            self.settings.remove("browser_visible")

            # Единый чат также сбрасываем
            settings = QSettings(tr("app.title", "GopiAI"), "UI")
            settings.remove("unified_chat_visible")
            settings.remove("unified_chat_geometry")

            # Сообщаем пользователю о необходимости перезапуска
            QMessageBox.information(
                self,
                tr("dialog.layout_reset.title", "Layout Reset"),
                tr(
                    "dialog.layout_reset.restart",
                    "Layout settings have been reset. Please restart the application for changes to take effect.",
                ),
            )

            logger.info("Layout fully reset, application restart required")
        except Exception as e:
            logger.error(f"Error during full layout reset: {e}")
            QMessageBox.critical(
                self,
                tr("dialog.error", "Error"),
                tr(
                    "dialog.layout_reset.error",
                    "Error resetting layout settings: {error}",
                ).format(error=str(e)),
            )
