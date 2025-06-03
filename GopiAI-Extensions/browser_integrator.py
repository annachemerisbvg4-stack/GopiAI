"""
Модуль для интеграции улучшенного браузера с существующей архитектурой приложения.
"""

from gopiai.core.logging import get_logger
logger = get_logger().logger
from typing import Dict, Any, Optional

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QWidget

from gopiai.app.ui.enhanced_browser_widget import EnhancedBrowserWidget, get_enhanced_browser_widget

logger = get_logger().logger

class BrowserIntegrator(QObject):
    """
    Интегрирует улучшенный браузер с существующей архитектурой приложения.
    """
    
    # Сигналы для интеграции с ИИ
    browser_content_ready = Signal(str, str, dict)  # url, title, content_data
    browser_analysis_ready = Signal(str, dict)  # url, analysis_results
    
    def __init__(self, parent=None):
        """
        Инициализирует интегратор браузера.
        
        Args:
            parent: Родительский объект
        """
        super().__init__(parent)
        self.browser_widget = None
        logger.info("BrowserIntegrator initialized")
    
    def setup_browser(self, parent_widget=None) -> EnhancedBrowserWidget:
        """
        Создает и настраивает улучшенный браузер.
        
        Args:
            parent_widget: Родительский виджет для браузера
            
        Returns:
            EnhancedBrowserWidget: Настроенный виджет браузера
        """
        logger.info("Setting up enhanced browser")
        
        # Создаем улучшенный браузер
        self.browser_widget = get_enhanced_browser_widget(parent_widget)
        
        # Подключаем сигналы
        self.browser_widget.page_loaded.connect(self._on_page_loaded)
        self.browser_widget.page_analyzed.connect(self._on_page_analyzed)
        self.browser_widget.content_extracted.connect(self._on_content_extracted)
        
        return self.browser_widget
    
    def integrate_with_existing_browser(self, existing_browser_widget: QWidget) -> None:
        """
        Интегрирует функциональность с существующим браузером.
        
        Args:
            existing_browser_widget: Существующий виджет браузера
        """
        logger.info("Integrating with existing browser")
        
        # В существующей реализации мы не можем заменить виджет браузера,
        # но можем добавить к нему новую функциональность асинхронной обработки
        
        # Создаем экземпляры процессоров отдельно
        from gopiai.app.ui.browser_processor import AsyncPagePreProcessor, ContentOptimizer
        from gopiai.app.ui.action_predictor import ActionPredictor
        
        self.page_processor = AsyncPagePreProcessor(max_cache_size=50)
        self.content_optimizer = ContentOptimizer()
        
        try:
            # Пытаемся получить WebEngineView из существующего виджета
            if hasattr(existing_browser_widget, "web_view"):
                browser_view = existing_browser_widget.web_view
                self.action_predictor = ActionPredictor(browser_view, self.page_processor)
                logger.info("Successfully integrated with existing browser")
            else:
                logger.warning("Existing browser widget doesn't have web_view attribute")
        except Exception as e:
            logger.error(f"Error integrating with existing browser: {str(e)}")
    
    @Slot(str, str)
    def _on_page_loaded(self, url: str, title: str) -> None:
        """
        Обрабатывает загрузку страницы.
        
        Args:
            url: URL загруженной страницы
            title: Заголовок страницы
        """
        logger.info(f"Page loaded: {title} ({url})")
        
        # Если браузер не инициализирован, выходим
        if not self.browser_widget:
            return
            
        # Запускаем анализ страницы
        self.browser_widget.analyze_current_page()
    
    @Slot(str, dict)
    def _on_page_analyzed(self, url: str, analysis_results: Dict[str, Any]) -> None:
        """
        Обрабатывает результаты анализа страницы.
        
        Args:
            url: URL проанализированной страницы
            analysis_results: Результаты анализа
        """
        logger.info(f"Page analyzed: {url}")
        
        # Эмитируем сигнал для интеграции с ИИ
        self.browser_analysis_ready.emit(url, analysis_results)
    
    @Slot(str, dict)
    def _on_content_extracted(self, url: str, content_data: Dict[str, Any]) -> None:
        """
        Обрабатывает извлеченное содержимое страницы.
        
        Args:
            url: URL страницы
            content_data: Извлеченное содержимое
        """
        logger.info(f"Content extracted from: {url}")
        
        # Получаем заголовок страницы
        title = content_data.get("title", "")
        
        # Эмитируем сигнал для интеграции с ИИ
        self.browser_content_ready.emit(url, title, content_data)
    
    def analyze_current_page(self, goal: Optional[str] = None) -> None:
        """
        Запускает анализ текущей страницы.
        
        Args:
            goal: Цель анализа
        """
        logger.info(f"Requesting analysis of current page with goal: {goal}")
        
        # Если браузер не инициализирован, выходим
        if not self.browser_widget:
            logger.warning("Browser widget not initialized")
            return
            
        # Запускаем анализ страницы
        self.browser_widget.analyze_current_page(goal)
    
    def extract_content(self, goal: Optional[str] = None) -> None:
        """
        Запускает извлечение содержимого текущей страницы.
        
        Args:
            goal: Цель извлечения
        """
        logger.info(f"Requesting content extraction with goal: {goal}")
        
        # Если браузер не инициализирован, выходим
        if not self.browser_widget:
            logger.warning("Browser widget not initialized")
            return
            
        # Запускаем извлечение содержимого
        self.browser_widget.extract_content(goal)
    
    def predict_actions(self, goal: Optional[str] = None) -> None:
        """
        Запускает предсказание следующих действий.
        
        Args:
            goal: Цель пользователя
        """
        logger.info(f"Requesting action prediction with goal: {goal}")
        
        # Если браузер не инициализирован, выходим
        if not self.browser_widget:
            logger.warning("Browser widget not initialized")
            return
            
        # Запускаем предсказание действий
        self.browser_widget.predict_actions(goal)
    
    def clear_cache(self) -> None:
        """Очищает кэш страниц."""
        logger.info("Clearing browser cache")
        
        # Если браузер не инициализирован, выходим
        if not self.browser_widget:
            logger.warning("Browser widget not initialized")
            return
            
        # Очищаем кэш
        self.browser_widget.clear_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику браузера.
        
        Returns:
            Dict: Статистика браузера
        """
        # Если браузер не инициализирован, возвращаем пустой словарь
        if not self.browser_widget:
            return {}
            
        # Возвращаем статистику
        return self.browser_widget.get_stats()


# Создаем глобальный экземпляр интегратора
browser_integrator = BrowserIntegrator()


def get_browser_integrator() -> BrowserIntegrator:
    """
    Возвращает глобальный экземпляр интегратора браузера.
    
    Returns:
        BrowserIntegrator: Экземпляр интегратора браузера
    """
    return browser_integrator
