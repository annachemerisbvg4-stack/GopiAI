"""
Улучшенный виджет браузера с поддержкой персистентного профиля.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar
from PySide6.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtCore import QUrl, Slot, Signal
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedBrowserWidget(QWidget):
    """Улучшенный виджет браузера с персистентным профилем"""
    
    # Сигналы
    page_loaded = Signal(str, str)  # url, title
    page_analyzed = Signal(str, dict)  # url, analysis
    content_extracted = Signal(str, dict)  # url, content
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_signals()
        
        # Текущее состояние
        self.current_url = ""
        self.current_title = ""
        
        logger.info("EnhancedBrowserWidget initialized")
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        # Создаем лейаут
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Создаем прогресс-бар
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximumHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: none; background-color: #f0f0f0; } "
            "QProgressBar::chunk { background-color: #4a86e8; }"
        )
        self.progress_bar.hide()
        
        # Создаем и настраиваем браузер
        self._setup_browser()
        
        # Добавляем компоненты в лейаут
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.browser)
        
        logger.debug(f"Browser widget added to layout. Size: {self.browser.size()}")
    
    def _setup_browser(self):
        """Настройка браузера с персистентным профилем"""
        try:
            # Создаем папку для профиля браузера
            profile_dir = Path.home() / ".gopiai" / "browser_profile"
            profile_dir.mkdir(parents=True, exist_ok=True)
            
            # Создаем персистентный профиль
            self.profile = QWebEngineProfile("GopiAI_Enhanced_Browser", self)
            
            # Настраиваем сохранение данных
            self.profile.setPersistentStoragePath(str(profile_dir))
            self.profile.setCachePath(str(profile_dir / "cache"))
            self.profile.setPersistentCookiesPolicy(
                QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
            )
            self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
            self.profile.setHttpCacheMaximumSize(100 * 1024 * 1024)  # 100MB cache
            
            # Настройки безопасности и удобства
            settings = self.profile.settings()
            settings.setAttribute(settings.WebAttribute.LocalStorageEnabled, True)
            settings.setAttribute(settings.WebAttribute.AutoLoadImages, True)
            settings.setAttribute(settings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(settings.WebAttribute.PluginsEnabled, True)
            settings.setAttribute(settings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(settings.WebAttribute.LocalContentCanAccessFileUrls, True)
            settings.setAttribute(settings.WebAttribute.WebGLEnabled, False)  # Отключаем для стабильности
            settings.setAttribute(settings.WebAttribute.Accelerated2dCanvasEnabled, False)
            settings.setAttribute(settings.WebAttribute.JavascriptCanOpenWindows, False)
            
            # Создаем браузер
            self.browser = QWebEngineView(self)
            
            # Создаем страницу с нашим профилем
            page = self.profile.createWebEnginePage(self.browser)
            self.browser.setPage(page)
            
            self.browser.setMinimumSize(400, 300)
            self.browser.setStyleSheet(
                "QWebEngineView {"
                "background-color: white;"
                "border: 1px solid #cccccc;"
                "}"
            )
            
            logger.info(f"Browser created with persistent profile: {profile_dir}")
            
        except Exception as e:
            logger.error(f"Error setting up browser: {e}")
            # Fallback к стандартному профилю
            self.browser = QWebEngineView(self)
            self.profile = QWebEngineProfile.defaultProfile()
            logger.warning("Using default profile as fallback")
    
    def _setup_signals(self):
        """Настройка сигналов"""
        self.browser.loadProgress.connect(self._update_progress)
        self.browser.loadStarted.connect(lambda: self.progress_bar.show())
        self.browser.loadFinished.connect(self._on_load_finished)
    
    def load_url(self, url: str) -> None:
        """
        Загружает указанный URL.
        
        Args:
            url: URL для загрузки
        """
        if not url:
            return
        
        # Нормализуем URL
        if not url.startswith(("http://", "https://", "file://", "about:")):
            url = "https://" + url
            
        logger.info(f"Loading URL: {url}")
        
        # Загружаем URL
        self.browser.load(QUrl(url))
    
    def get_current_url(self) -> str:
        """
        Возвращает текущий URL.
        
        Returns:
            str: Текущий URL
        """
        return self.current_url
    
    def get_current_title(self) -> str:
        """
        Возвращает заголовок текущей страницы.
        
        Returns:
            str: Заголовок страницы
        """
        return self.current_title
    
    @Slot(int)
    def _update_progress(self, progress: int) -> None:
        """
        Обновляет индикатор загрузки.
        
        Args:
            progress: Прогресс загрузки (0-100)
        """
        self.progress_bar.setValue(progress)
        
        if progress < 100:
            self.progress_bar.show()
        else:
            self.progress_bar.hide()
    
    @Slot(bool)
    def _on_load_finished(self, success: bool) -> None:
        """
        Обрабатывает завершение загрузки страницы.
        
        Args:
            success: Флаг успешной загрузки
        """
        self.progress_bar.hide()
        
        if not success:
            logger.warning("Page load failed")
            return
        
        # Обновляем текущий URL и заголовок
        self.current_url = self.browser.url().toString()
        self.current_title = self.browser.page().title()
        
        # Эмитируем сигнал о загрузке страницы
        self.page_loaded.emit(self.current_url, self.current_title)
        
        logger.info(f"Page loaded: {self.current_title} ({self.current_url})")
