"""
Улучшенный виджет браузера с поддержкой персистентного профиля.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
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
            page = QWebEnginePage(self.profile, self.browser)
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

    # --- Методы управления браузером для интеграции с backend командами ---
    def navigate(self, url: str) -> None:
        """Перейти по адресу URL (alias к load_url)."""
        self.load_url(url)

    def execute_js(self, script: str, callback=None) -> None:
        """Выполнить произвольный JavaScript на странице."""
        try:
            page: QWebEnginePage = self.browser.page()
            page.runJavaScript(script, callback)
            logger.debug(f"[BROWSER] Executed JS: {script[:120]}..." if len(script) > 120 else f"[BROWSER] Executed JS: {script}")
        except Exception as e:
            logger.error(f"[BROWSER] JS execution error: {e}")

    def click(self, selector: str) -> None:
        """Клик по элементу через CSS-селектор."""
        if not selector:
            return
        js = (
            "(function(){\n"
            "  var el = document.querySelector(" + jsonSelector(selector) + ");\n"
            "  if (el) { el.scrollIntoView({behavior:'instant',block:'center'}); el.click(); true } else { false }\n"
            "})();"
        )
        self.execute_js(js)

    def type_text(self, selector: str, text: str, clear: bool = False) -> None:
        """Ввод текста в поле по CSS-селектору."""
        if not selector:
            return
        safe_text = (text or "").replace("\\", "\\\\").replace("\n", "\\n").replace("\"", "\\\"")
        js = (
            "(function(){\n"
            "  var el = document.querySelector(" + jsonSelector(selector) + ");\n"
            "  if (!el) return false;\n"
            "  el.focus();\n"
            + ("  el.value='';\n" if clear else "") +
            f"  el.value = (el.value || '') + \"{safe_text}\";\n"+
            "  el.dispatchEvent(new Event('input', {bubbles:true}));\n"
            "  el.dispatchEvent(new Event('change', {bubbles:true}));\n"
            "  return true;\n"
            "})();"
        )
        self.execute_js(js)

    def scroll_page(self, direction: str = "down", amount: int = 500) -> None:
        """Прокрутка страницы. direction: up|down|to_top|to_bottom"""
        direction = (direction or "down").lower()
        if direction in ("to_top", "top"):
            js = "window.scrollTo(0,0);"
        elif direction in ("to_bottom", "bottom"):
            js = "window.scrollTo(0, document.body.scrollHeight || document.documentElement.scrollHeight);"
        else:
            dy = abs(int(amount or 500)) * (-1 if direction == "up" else 1)
            js = f"window.scrollBy(0, {dy});"
        self.execute_js(js)

    def apply_actions(self, actions):
        """Выполняет список действий браузера, полученных из backend.
        Ожидаемый формат элементов:
          {"action": "navigate"|"click"|"type"|"scroll"|"execute_js", ...}
        """
        try:
            if not actions:
                return
            if isinstance(actions, dict):
                actions = [actions]

            for idx, act in enumerate(actions):
                if not isinstance(act, dict):
                    continue
                action = str(act.get("action", "")).lower()
                logger.info(f"[BROWSER] Apply action #{idx+1}: {action} -> {act}")
                if action == "navigate" and act.get("target"):
                    self.navigate(str(act.get("target")))
                elif action == "click" and act.get("selector"):
                    self.click(str(act.get("selector")))
                elif action == "type" and act.get("selector") is not None:
                    self.type_text(str(act.get("selector")), str(act.get("text", "")), bool(act.get("clear", False)))
                elif action == "scroll":
                    self.scroll_page(str(act.get("direction", "down")), int(act.get("amount", 500)))
                elif action in ("execute_js", "run_js") and act.get("script"):
                    self.execute_js(str(act.get("script")))
                else:
                    logger.warning(f"[BROWSER] Неизвестное действие или недостаточно параметров: {act}")
        except Exception as e:
            logger.error(f"[BROWSER] Ошибка применения действий: {e}")


# Вспомогательная функция для безопасного оборачивания селектора в JS-строку
def jsonSelector(selector: str) -> str:
    s = (selector or "").replace("\\", "\\\\").replace("\"", "\\\"")
    return f'"{s}"'
