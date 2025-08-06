"""
Window Events Mixin for MainWindow.

This module contains methods for handling window events in the MainWindow class.
"""

# Typed logger import with robust fallbacks for both runtime and Pyright
from __future__ import annotations

from typing import Protocol, runtime_checkable, Any, Optional

# Define a minimal protocol so Pyright knows the shape
@runtime_checkable
class _HasLogger(Protocol):
    logger: "LoggerLike"

class LoggerLike(Protocol):
    def debug(self, msg: str, *args, **kwargs) -> None: ...
    def info(self, msg: str, *args, **kwargs) -> None: ...
    def warning(self, msg: str, *args, **kwargs) -> None: ...
    def error(self, msg: str, *args, **kwargs) -> None: ...
    def exception(self, msg: str, *args, **kwargs) -> None: ...

# Try preferred imports but keep Pyright happy with type: ignore
try:
    from gopiai.core.logging import get_logger  # type: ignore[reportMissingImports]
except Exception:
    try:
        from gopiai_core.logging import get_logger  # type: ignore[reportMissingImports]
    except Exception:
        # Final fallback: minimal stdlib logger
        import logging as _logging

        class _Shim:
            def __init__(self) -> None:
                _logger = _logging.getLogger("gopiai.widgets.window_events")
                if not _logger.handlers:
                    handler = _logging.StreamHandler()
                    formatter = _logging.Formatter(
                        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    )
                    handler.setFormatter(formatter)
                    _logger.addHandler(handler)
                    _logger.setLevel(_logging.INFO)
                # Narrow type to our protocol interface
                self.logger: LoggerLike = _logger  # type: ignore[assignment]

        def get_logger() -> _HasLogger:
            # Return as protocol type to satisfy Pyright
            return _Shim()

# Ensure logger is typed as LoggerLike for Pyright
logger: LoggerLike = get_logger().logger  # type: ignore[reportAttributeAccessIssue]

from PySide6.QtCore import QEvent


class WindowEventsMixin:
    """Provides window event handling functionality for MainWindow.

    Note for type checkers:
    This mixin is intended to be used with a QWidget/QMainWindow subclass.
    Attributes like `settings`, `saveGeometry`, `saveState`, `unified_chat_view`,
    `central_tabs`, `_close_tab`, `isMaximized`, `showNormal`, `showMaximized`,
    and event methods are provided by the consuming Qt widget class at runtime.
    """

    # Hints for static type checkers to suppress "unknown attribute" noise.
    # These are Optional and exist at runtime on the concrete MainWindow subclass.
    # Use Optional[Any] to relax protocol for Pyright; concrete class supplies these at runtime
    settings: Any  # runtime-provided settings object with setValue(...)
    unified_chat_view: Any  # QWidget-like with saveGeometry(), isVisible(), close()
    central_tabs: Any  # QTabWidget-like with count()

    def saveGeometry(self) -> Any: ...  # type: ignore[empty-body]
    def saveState(self) -> Any: ...  # type: ignore[empty-body]
    def _close_tab(self, index: int) -> None: ...  # type: ignore[empty-body]
    def isMaximized(self) -> bool: ...  # type: ignore[empty-body]
    def showNormal(self) -> None: ...  # type: ignore[empty-body]
    def showMaximized(self) -> None: ...  # type: ignore[empty-body]
    def windowState(self) -> Any: ...  # type: ignore[empty-body]
    def resizeEvent(self, event: Any) -> None: ...  # type: ignore[empty-body]
    def changeEvent(self, event: Any) -> None: ...  # type: ignore[empty-body]
    def moveEvent(self, event: Any) -> None: ...  # type: ignore[empty-body]
    def eventFilter(self, watched: Any, event: Any) -> bool: ...  # type: ignore[empty-body]

    def closeEvent(self, event):
        """Обрабатывает закрытие главного окна приложения."""
        try:
            # Сохраняем состояние главного окна перед закрытием
            if hasattr(self, "settings"):
                try:
                    # Геометрия центрального виджета
                    self.settings.setValue("geometry", self.saveGeometry())
                    self.settings.setValue("windowState", self.saveState())

                    # Геометрия единого чата
                    if hasattr(self, "unified_chat_view") and self.unified_chat_view:
                        try:
                            geom = self.unified_chat_view.saveGeometry()
                            self.settings.setValue("unified_chat_geometry", geom)
                            self.settings.setValue(
                                "unified_chat_visible",
                                self.unified_chat_view.isVisible(),
                            )
                            logger.info("Saved unified chat view state")
                        except Exception as e:
                            logger.error(
                                f"Error saving unified chat view geometry: {e}"
                            )
                except Exception as e:
                    logger.error(f"Error saving window state: {e}")

            # Закрываем все вкладки перед закрытием основного окна
            if hasattr(self, "central_tabs") and self.central_tabs:
                logger.info("Closing all tabs before window close")
                tab_count = self.central_tabs.count()
                for i in range(tab_count - 1, -1, -1):
                    try:
                        self._close_tab(i)
                    except Exception as e:
                        logger.error(f"Error closing tab {i}: {e}")

            # Освобождаем ресурсы единого чата
            if hasattr(self, "unified_chat_view") and self.unified_chat_view:
                try:
                    self.unified_chat_view.close()
                    logger.info("Unified chat view closed")
                except Exception as e:
                    logger.error(f"Error closing unified chat view: {e}")

        except Exception as e:
            logger.error(f"Error in closeEvent: {e}")

        event.accept()

    def resizeEvent(self, event):
        """Обрабатывает изменение размера окна."""
        try:
            super().resizeEvent(event)  # type: ignore[attr-defined]
        except Exception:
            pass
        # Здесь можно добавить дополнительную логику при изменении размера

    def changeEvent(self, event):
        """Обрабатывает события изменения состояния окна."""
        if event.type() == QEvent.Type.WindowStateChange:  # type: ignore[attr-defined]
            # Обрабатываем изменение состояния окна
            try:
                logger.debug(f"Window state changed to {self.windowState()}")  # type: ignore[attr-defined]
            except Exception:
                logger.debug("Window state changed")
        try:
            super().changeEvent(event)  # type: ignore[attr-defined]
        except Exception:
            pass

    def moveEvent(self, event):
        """Обрабатывает перемещение окна."""
        try:
            super().moveEvent(event)  # type: ignore[attr-defined]
        except Exception:
            pass
        # Здесь можно добавить дополнительную логику при перемещении окна

    def _toggle_maximized(self):
        """Переключает между полноэкранным и обычным режимом окна."""
        if self.isMaximized():
            self.showNormal()
            logger.debug("Window restored from maximized state")
        else:
            self.showMaximized()
            logger.debug("Window maximized")

    def eventFilter(self, watched, event):
        """Фильтр событий для главного окна.

        Позволяет перехватывать и обрабатывать события до того, как они будут
        доставлены объектам, за которыми ведется наблюдение.
        """
        # Пример обработки глобальных горячих клавиш или других событий
        try:
            return super().eventFilter(watched, event)  # type: ignore[attr-defined]
        except Exception:
            return False
