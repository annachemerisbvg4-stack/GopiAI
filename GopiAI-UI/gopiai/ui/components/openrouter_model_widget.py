#!/usr/bin/env python3
"""
OpenRouter Model Widget для GopiAI UI
Виджет для отображения, поиска и выбора моделей OpenRouter
"""

import logging
import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QLabel, QFrame, QSplitter, QTextEdit,
    QProgressBar, QComboBox, QCheckBox, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtGui import QFont, QPixmap, QIcon

# Добавляем путь к backend для импорта клиентов
try:
    backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "GopiAI-CrewAI")
    if backend_path not in sys.path:
        sys.path.append(backend_path)
except Exception as e:
    print(f"⚠️ Не удалось добавить backend путь: {e}")

logger = logging.getLogger(__name__)

class ModelLoadWorker(QThread):
    """Воркер для асинхронной загрузки моделей OpenRouter"""
    
    models_loaded = Signal(list)  # Сигнал с загруженными моделями
    error_occurred = Signal(str)  # Сигнал об ошибке
    
    def __init__(self, openrouter_client):
        super().__init__()
        self.openrouter_client = openrouter_client
        self.force_refresh = False
    
    def set_force_refresh(self, force: bool):
        """Устанавливает принудительное обновление"""
        self.force_refresh = force
    
    def run(self):
        """Выполняет загрузку моделей в отдельном потоке"""
        try:
            logger.info("🔄 Загружаем модели OpenRouter в фоновом потоке...")
            models = self.openrouter_client.get_models_sync(force_refresh=self.force_refresh)
            self.models_loaded.emit(models)
            logger.info(f"✅ Загружено {len(models)} моделей OpenRouter")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки моделей: {e}")
            self.error_occurred.emit(str(e))

class ModelListItem(QWidget):
    """Кастомный элемент списка для отображения модели"""
    
    model_selected = Signal(dict)  # Сигнал выбора модели
    
    def __init__(self, model_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.model_data = model_data
        self.is_selected = False
        self._setup_ui()
    
    def _setup_ui(self):
        """Настраивает UI элемента списка"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)
        
        # Основная информация о модели
        header_layout = QHBoxLayout()
        
        # Название модели
        name_label = QLabel(self.model_data.get('display_name', self.model_data.get('id', 'Unknown')))
        name_font = QFont()
        name_font.setBold(True)
        name_font.setPointSize(10)
        name_label.setFont(name_font)
        header_layout.addWidget(name_label)
        
        # Статус (бесплатная/платная)
        price_info = self.model_data.get('price_info', '')
        if 'Бесплатная' in price_info:
            status_label = QLabel("🆓 FREE")
            status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            status_label = QLabel("💰 PAID")
            status_label.setStyleSheet("color: orange; font-weight: bold;")
        
        header_layout.addWidget(status_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # ID модели
        id_label = QLabel(f"ID: {self.model_data.get('id', 'unknown')}")
        id_label.setStyleSheet("color: gray; font-size: 9px;")
        layout.addWidget(id_label)
        
        # Дополнительная информация
        info_layout = QHBoxLayout()
        
        # Контекст
        context_length = self.model_data.get('context_length', 0)
        if context_length > 0:
            context_label = QLabel(f"📄 {context_length:,} токенов")
            context_label.setStyleSheet("font-size: 9px; color: #666;")
            info_layout.addWidget(context_label)
        
        # Цена
        if price_info and 'Бесплатная' not in price_info:
            price_label = QLabel(price_info)
            price_label.setStyleSheet("font-size: 9px; color: #666;")
            info_layout.addWidget(price_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # Описание (если есть)
        description = self.model_data.get('description', '')
        if description and len(description) > 0:
            desc_label = QLabel(description[:100] + "..." if len(description) > 100 else description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("font-size: 9px; color: #888; font-style: italic;")
            layout.addWidget(desc_label)
        
        # Стиль для выделения
        self.setStyleSheet("""
            ModelListItem {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                margin: 2px;
            }
            ModelListItem:hover {
                background-color: #f0f8ff;
                border-color: #4a90e2;
            }
        """)
    
    def mousePressEvent(self, event):
        """Обработка клика по элементу"""
        if event.button() == Qt.LeftButton:
            self.set_selected(True)
            self.model_selected.emit(self.model_data)
        super().mousePressEvent(event)
    
    def set_selected(self, selected: bool):
        """Устанавливает состояние выделения"""
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                ModelListItem {
                    border: 2px solid #4a90e2;
                    border-radius: 4px;
                    background-color: #e6f3ff;
                    margin: 2px;
                }
            """)
        else:
            self.setStyleSheet("""
                ModelListItem {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background-color: white;
                    margin: 2px;
                }
                ModelListItem:hover {
                    background-color: #f0f8ff;
                    border-color: #4a90e2;
                }
            """)

class OpenRouterModelWidget(QWidget):
    """Виджет для работы с моделями OpenRouter"""
    
    model_selected = Signal(dict)  # Сигнал выбора модели
    provider_switch_requested = Signal(str)  # Сигнал переключения провайдера
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.openrouter_client = None
        self.model_config_manager = None
        self.models = []
        self.filtered_models = []
        self.selected_model = None
        self.model_items = []
        
        self._setup_ui()
        self._initialize_backend_clients()
        self._setup_connections()
        
        # Таймер для автообновления
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._auto_refresh_models)
        self.refresh_timer.start(300000)  # Обновляем каждые 5 минут
        
        logger.info("🎛️ OpenRouterModelWidget инициализирован")
    
    def _setup_ui(self):
        """Настраивает пользовательский интерфейс"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Заголовок
        header_layout = QHBoxLayout()
        
        title_label = QLabel("OpenRouter Models")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Кнопка обновления
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setToolTip("Обновить список моделей")
        self.refresh_btn.setFixedSize(30, 30)
        header_layout.addWidget(self.refresh_btn)
        
        # Кнопка переключения на основную конфигурацию
        self.switch_btn = QPushButton("🔄 Gemini")
        self.switch_btn.setToolTip("Переключиться на основную конфигурацию (Gemini)")
        header_layout.addWidget(self.switch_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Поиск и фильтры
        search_layout = QVBoxLayout()
        
        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по названию модели...")
        search_layout.addWidget(self.search_input)
        
        # Фильтры
        filters_layout = QHBoxLayout()
        
        # Фильтр по типу
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Все модели", "🆓 Только бесплатные", "💰 Только платные"])
        filters_layout.addWidget(self.type_filter)
        
        # Фильтр по провайдеру
        self.provider_filter = QComboBox()
        self.provider_filter.addItem("Все провайдеры")
        filters_layout.addWidget(self.provider_filter)
        
        search_layout.addLayout(filters_layout)
        layout.addLayout(search_layout)
        
        # Статистика
        self.stats_label = QLabel("Загрузка...")
        self.stats_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.stats_label)
        
        # Прогресс-бар для загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Список моделей
        self.models_scroll = QScrollArea()
        self.models_scroll.setWidgetResizable(True)
        self.models_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.models_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarNever)
        
        self.models_container = QWidget()
        self.models_layout = QVBoxLayout(self.models_container)
        self.models_layout.setContentsMargins(4, 4, 4, 4)
        self.models_layout.setSpacing(4)
        
        self.models_scroll.setWidget(self.models_container)
        layout.addWidget(self.models_scroll, 1)
        
        # Информация о выбранной модели
        info_group = QGroupBox("Выбранная модель")
        info_layout = QVBoxLayout(info_group)
        
        self.selected_info = QTextEdit()
        self.selected_info.setMaximumHeight(100)
        self.selected_info.setPlaceholderText("Выберите модель для просмотра информации...")
        self.selected_info.setReadOnly(True)
        info_layout.addWidget(self.selected_info)
        
        # Кнопка выбора модели
        self.select_btn = QPushButton("✅ Использовать эту модель")
        self.select_btn.setEnabled(False)
        info_layout.addWidget(self.select_btn)
        
        layout.addWidget(info_group)
    
    def _initialize_backend_clients(self):
        """Инициализирует клиенты backend"""
        try:
            from tools.gopiai_integration.openrouter_client import get_openrouter_client
            from tools.gopiai_integration.model_config_manager import get_model_config_manager
            
            self.openrouter_client = get_openrouter_client()
            self.model_config_manager = get_model_config_manager()
            
            logger.info("✅ Backend клиенты инициализированы")
            
            # Запускаем загрузку моделей
            self._load_models()
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации backend клиентов: {e}")
            self.stats_label.setText(f"❌ Ошибка подключения: {e}")
    
    def _setup_connections(self):
        """Настраивает соединения сигналов"""
        self.refresh_btn.clicked.connect(self._refresh_models)
        self.switch_btn.clicked.connect(lambda: self.provider_switch_requested.emit("gemini"))
        self.search_input.textChanged.connect(self._filter_models)
        self.type_filter.currentTextChanged.connect(self._filter_models)
        self.provider_filter.currentTextChanged.connect(self._filter_models)
        self.select_btn.clicked.connect(self._select_current_model)
    
    def _load_models(self):
        """Загружает модели OpenRouter"""
        if not self.openrouter_client:
            logger.warning("⚠️ OpenRouter клиент не инициализирован")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        self.stats_label.setText("🔄 Загружаем модели OpenRouter...")
        
        # Создаем воркер для загрузки
        self.load_worker = ModelLoadWorker(self.openrouter_client)
        self.load_worker.models_loaded.connect(self._on_models_loaded)
        self.load_worker.error_occurred.connect(self._on_load_error)
        self.load_worker.start()
    
    def _refresh_models(self):
        """Принудительно обновляет модели"""
        if not self.openrouter_client:
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.stats_label.setText("🔄 Обновляем список моделей...")
        
        # Создаем воркер с принудительным обновлением
        self.load_worker = ModelLoadWorker(self.openrouter_client)
        self.load_worker.set_force_refresh(True)
        self.load_worker.models_loaded.connect(self._on_models_loaded)
        self.load_worker.error_occurred.connect(self._on_load_error)
        self.load_worker.start()
    
    def _auto_refresh_models(self):
        """Автоматически обновляет модели"""
        if self.openrouter_client and not hasattr(self, 'load_worker') or not self.load_worker.isRunning():
            logger.info("🔄 Автообновление моделей OpenRouter...")
            self._load_models()
    
    def _on_models_loaded(self, models):
        """Обработчик успешной загрузки моделей"""
        self.progress_bar.setVisible(False)
        self.models = models
        
        # Обновляем статистику
        free_count = len([m for m in models if getattr(m, 'is_free', False)])
        paid_count = len(models) - free_count
        
        self.stats_label.setText(f"📊 Всего: {len(models)} | 🆓 Бесплатных: {free_count} | 💰 Платных: {paid_count}")
        
        # Обновляем фильтр провайдеров
        self._update_provider_filter()
        
        # Применяем фильтры
        self._filter_models()
        
        logger.info(f"✅ Загружено {len(models)} моделей OpenRouter")
    
    def _on_load_error(self, error_message):
        """Обработчик ошибки загрузки"""
        self.progress_bar.setVisible(False)
        self.stats_label.setText(f"❌ Ошибка загрузки: {error_message}")
        logger.error(f"❌ Ошибка загрузки моделей: {error_message}")
    
    def _update_provider_filter(self):
        """Обновляет список провайдеров в фильтре"""
        providers = set()
        for model in self.models:
            provider = getattr(model, 'provider', 'unknown')
            if provider and provider != 'unknown':
                providers.add(provider)
        
        current_text = self.provider_filter.currentText()
        self.provider_filter.clear()
        self.provider_filter.addItem("Все провайдеры")
        
        for provider in sorted(providers):
            self.provider_filter.addItem(f"🏢 {provider}")
        
        # Восстанавливаем выбор, если возможно
        index = self.provider_filter.findText(current_text)
        if index >= 0:
            self.provider_filter.setCurrentIndex(index)
    
    def _filter_models(self):
        """Применяет фильтры к списку моделей"""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText()
        provider_filter = self.provider_filter.currentText()
        
        filtered = []
        
        for model in self.models:
            # Фильтр по поиску
            if search_text:
                model_text = f"{getattr(model, 'id', '')} {getattr(model, 'name', '')} {getattr(model, 'description', '')}".lower()
                if search_text not in model_text:
                    continue
            
            # Фильтр по типу
            if type_filter == "🆓 Только бесплатные" and not getattr(model, 'is_free', False):
                continue
            elif type_filter == "💰 Только платные" and getattr(model, 'is_free', False):
                continue
            
            # Фильтр по провайдеру
            if provider_filter != "Все провайдеры":
                provider_name = provider_filter.replace("🏢 ", "")
                if getattr(model, 'provider', '') != provider_name:
                    continue
            
            filtered.append(model)
        
        self.filtered_models = filtered
        self._update_models_display()
    
    def _update_models_display(self):
        """Обновляет отображение списка моделей"""
        # Очищаем старые элементы
        for item in self.model_items:
            item.setParent(None)
        self.model_items.clear()
        
        # Добавляем новые элементы
        for model in self.filtered_models:
            model_data = {
                'id': getattr(model, 'id', ''),
                'display_name': getattr(model, 'get_display_name', lambda: getattr(model, 'name', getattr(model, 'id', '')))(),
                'description': getattr(model, 'description', ''),
                'context_length': getattr(model, 'context_length', 0),
                'price_info': getattr(model, 'get_price_info', lambda: '')(),
                'is_free': getattr(model, 'is_free', False),
                'provider': getattr(model, 'provider', ''),
                'model_object': model
            }
            
            item = ModelListItem(model_data)
            item.model_selected.connect(self._on_model_item_selected)
            
            self.models_layout.addWidget(item)
            self.model_items.append(item)
        
        # Добавляем растягивающийся элемент в конец
        self.models_layout.addStretch()
        
        # Обновляем счетчик отфильтрованных
        if len(self.filtered_models) != len(self.models):
            self.stats_label.setText(
                f"📊 Показано: {len(self.filtered_models)} из {len(self.models)} | "
                f"🆓 Бесплатных: {len([m for m in self.models if getattr(m, 'is_free', False)])} | "
                f"💰 Платных: {len([m for m in self.models if not getattr(m, 'is_free', False)])}"
            )
    
    def _on_model_item_selected(self, model_data):
        """Обработчик выбора элемента модели"""
        # Снимаем выделение с других элементов
        for item in self.model_items:
            if item.model_data != model_data:
                item.set_selected(False)
        
        self.selected_model = model_data
        self._update_selected_info()
        self.select_btn.setEnabled(True)
    
    def _update_selected_info(self):
        """Обновляет информацию о выбранной модели"""
        if not self.selected_model:
            self.selected_info.clear()
            return
        
        info_text = f"""
<b>Модель:</b> {self.selected_model['display_name']}<br>
<b>ID:</b> {self.selected_model['id']}<br>
<b>Провайдер:</b> {self.selected_model['provider']}<br>
<b>Тип:</b> {self.selected_model['price_info']}<br>
"""
        
        if self.selected_model['context_length'] > 0:
            info_text += f"<b>Контекст:</b> {self.selected_model['context_length']:,} токенов<br>"
        
        if self.selected_model['description']:
            info_text += f"<b>Описание:</b> {self.selected_model['description'][:200]}{'...' if len(self.selected_model['description']) > 200 else ''}"
        
        self.selected_info.setHtml(info_text)
    
    def _select_current_model(self):
        """Выбирает текущую модель"""
        if self.selected_model:
            logger.info(f"🎯 Выбрана модель OpenRouter: {self.selected_model['id']}")
            self.model_selected.emit(self.selected_model)
    
    def get_current_model(self):
        """Возвращает текущую выбранную модель"""
        return self.selected_model
    
    def set_model_by_id(self, model_id: str):
        """Устанавливает модель по ID"""
        for model_data in self.filtered_models:
            if model_data.get('id') == model_id:
                self._on_model_item_selected(model_data)
                break

def test_openrouter_widget():
    """Тестовая функция для виджета OpenRouter"""
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    widget = OpenRouterModelWidget()
    widget.setWindowTitle("OpenRouter Models Test")
    widget.resize(400, 600)
    widget.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    test_openrouter_widget()
