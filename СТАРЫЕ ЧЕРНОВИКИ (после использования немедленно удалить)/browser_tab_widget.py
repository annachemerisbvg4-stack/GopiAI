"""
Модуль для создания и управления вкладками браузера.
"""

import sys
import os
from PySide6.QtCore import Qt, QUrl, Signal, Slot, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QTabWidget, QFrame, QToolButton, QMenu,
    QLabel, QProgressBar, QApplication
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage

class BrowserTab(QWidget):
    """Виджет для отдельной вкладки браузера."""
    
    def __init__(self, parent=None, url=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем адресную строку и кнопки навигации
        self.navigation_bar = QFrame()
        self.nav_layout = QHBoxLayout(self.navigation_bar)
        self.nav_layout.setContentsMargins(4, 4, 4, 4)
        
        # Кнопка "Назад"
        self.back_button = QToolButton()
        self.back_button.setText("←")
        self.back_button.setToolTip("Назад")
        self.back_button.clicked.connect(self.go_back)
        self.nav_layout.addWidget(self.back_button)
        
        # Кнопка "Вперед"
        self.forward_button = QToolButton()
        self.forward_button.setText("→")
        self.forward_button.setToolTip("Вперед")
        self.forward_button.clicked.connect(self.go_forward)
        self.nav_layout.addWidget(self.forward_button)
        
        # Кнопка "Обновить"
        self.reload_button = QToolButton()
        self.reload_button.setText("⟳")
        self.reload_button.setToolTip("Обновить")
        self.reload_button.clicked.connect(self.reload_page)
        self.nav_layout.addWidget(self.reload_button)
        
        # Адресная строка
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url)
        self.nav_layout.addWidget(self.url_bar)
        
        # Добавляем навигационную панель в основной макет
        self.layout.addWidget(self.navigation_bar)
        
        # Создаем прогресс-бар для отображения загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { border: none; background-color: #f0f0f0; } QProgressBar::chunk { background-color: #4a86e8; }")
        self.layout.addWidget(self.progress_bar)
        
        # Создаем веб-просмотрщик
        self.browser = QWebEngineView()
        self.browser.page().titleChanged.connect(self.update_title)
        self.browser.page().urlChanged.connect(self.update_url)
        self.browser.page().loadProgress.connect(self.update_progress)
        self.browser.page().loadFinished.connect(self.loading_finished)
        
        # Добавляем веб-просмотрщик в основной макет
        self.layout.addWidget(self.browser)
        
        # Загружаем URL, если он был указан
        if url:
            self.load(url)
        else:
            self.load("about:blank")
    
    def load(self, url):
        """Загружает указанный URL."""
        if not url.startswith(("http://", "https://", "file://", "about:")):
            url = "http://" + url
        self.browser.load(QUrl(url))
    
    def load_url(self):
        """Загружает URL из адресной строки."""
        url = self.url_bar.text()
        self.load(url)
    
    def go_back(self):
        """Переходит на предыдущую страницу."""
        self.browser.back()
    
    def go_forward(self):
        """Переходит на следующую страницу."""
        self.browser.forward()
    
    def reload_page(self):
        """Перезагружает текущую страницу."""
        self.browser.reload()
    
    def update_title(self, title):
        """Обновляет заголовок вкладки."""
        if not title:
            title = "Новая вкладка"
        self.setWindowTitle(title)
        # Обновляем заголовок в родительском TabWidget
        if self.parent() and isinstance(self.parent(), QTabWidget):
            index = self.parent().indexOf(self)
            if index != -1:
                self.parent().setTabText(index, title[:15] + "..." if len(title) > 15 else title)
    
    def update_url(self, url):
        """Обновляет URL в адресной строке."""
        self.url_bar.setText(url.toString())
    
    def update_progress(self, progress):
        """Обновляет индикатор загрузки."""
        self.progress_bar.setValue(progress)
        # Показываем прогресс-бар при загрузке
        if progress < 100:
            self.progress_bar.show()
    
    def loading_finished(self, success):
        """Вызывается по завершении загрузки страницы."""
        # Скрываем прогресс-бар, когда загрузка завершена
        self.progress_bar.hide()
        if not success:
            self.browser.setHtml("<h1>Ошибка загрузки страницы</h1><p>Не удалось загрузить запрошенную страницу.</p>")

class MultiBrowserWidget(QWidget):
    """Виджет с несколькими вкладками браузера."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Создаем TabWidget для вкладок
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        # Кнопка для добавления новой вкладки
        self.add_tab_button = QToolButton()
        self.add_tab_button.setText("+")
        self.add_tab_button.setToolTip("Новая вкладка")
        self.add_tab_button.clicked.connect(self.add_new_tab)
        self.tabs.setCornerWidget(self.add_tab_button, Qt.Corner.TopRightCorner)
        
        self.layout.addWidget(self.tabs)
        
        # Добавляем первую вкладку
        self.add_new_tab()
    
    def add_new_tab(self, url=None):
        """Добавляет новую вкладку браузера."""
        new_tab = BrowserTab(self.tabs, url)
        index = self.tabs.addTab(new_tab, "Новая вкладка")
        self.tabs.setCurrentIndex(index)
        
        # Устанавливаем фокус на адресную строку
        new_tab.url_bar.setFocus()
        
        return new_tab
    
    def close_tab(self, index):
        """Закрывает вкладку по индексу."""
        # Не закрываем последнюю вкладку
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            # Если это последняя вкладка, очищаем её
            tab = self.tabs.widget(0)
            tab.load("about:blank")
            tab.url_bar.clear()
    
    def current_tab(self):
        """Возвращает текущую активную вкладку."""
        return self.tabs.currentWidget()
