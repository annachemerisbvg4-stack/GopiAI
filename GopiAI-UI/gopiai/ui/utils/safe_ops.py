import functools
import logging
from typing import Callable, Any, Optional

# Use unified logger if configured, fallback to root logger
logger = logging.getLogger("GopiAI") or logging.getLogger(__name__)


def safe_widget_operation(operation_name: str = "ui_operation") -> Callable:
    """
    Decorator for UI widget methods to safely catch and log exceptions
    without crashing the entire application.

    Usage:
        @safe_widget_operation("context_menu_creation")
        def contextMenuEvent(self, event): ...
    """
    def _decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def _wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log full stack trace with operation tag
                logger.exception("UI safe op failed [%s]: %s", operation_name, e)
                # For UI handlers it's safer to return None
                return None
        return _wrapped
    return _decorator


def stable_widget_creation(fallback_factory: Optional[Callable[..., Any]] = None) -> Callable:
    """
    Decorator to wrap widget/tab creation functions. If creation fails,
    logs the error and uses provided fallback_factory to create a safe widget/tab.

    Usage:
        @stable_widget_creation(fallback_factory=lambda self, title: self._create_fallback_text_editor(title))
        def add_new_tab(self, title): ...
    """
    def _decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def _wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception("Widget creation failed: %s", e)
                if fallback_factory is not None:
                    try:
                        # Support methods (self-first) as well as plain callables
                        return fallback_factory(*args, **kwargs)
                    except Exception as fe:
                        logger.exception("Fallback factory also failed: %s", fe)
                        return None
                return None
        return _wrapped
    return _decorator
