#!/usr/bin/env python3
"""
Model Selector Widget для GopiAI UI
Виджет для переключения между провайдерами моделей (Gemini/OpenRouter)
"""

import logging
import sys
import os
from typing import Dict, List, Optional, Any

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QGroupBox,
    QFrame,
    QLineEdit,
    QTextEdit,
    QProgressBar,
    QCheckBox,
    QSplitter,
    QTabWidget,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon

# Import icon system for global icons
try:
    from ..utils.icon_system import AutoIconSystem
except ImportError:
    AutoIconSystem = None

# Добавляем путь к backend для импорта клиентов
try:
    backend_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "GopiAI-CrewAI",
    )
    if backend_path not in sys.path:
        sys.path.append(backend_path)
except Exception as e:
    print(f"⚠️ Не удалось добавить backend путь: {e}")

logger = logging.getLogger(__name__)


class ModelSelectorWidget(QWidget):
    """Виджет для выбора и переключения между провайдерами моделей"""

    provider_changed = Signal(str)  # Сигнал изменения провайдера
    model_changed = Signal(str, str)  # Сигнал изменения модели (provider, model_id)
    api_key_updated = Signal(str, str)  # Сигнал обновления API ключа (env_var, key)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_config_manager = None
        self.current_provider = "gemini"
        self.current_model = None
        self.available_models = {}

        # Initialize icon system
        self.icon_system = AutoIconSystem() if AutoIconSystem else None

        self._setup_ui()
        self._initialize_backend()
        self._setup_connections()
        self._load_current_configuration()

        # Таймер для обновления статуса
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(5000)  # Обновляем каждые 5 секунд

        logger.info("ModelSelectorWidget инициализирован")

    def _setup_ui(self):
        """Настраивает пользовательский интерфейс"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Заголовок
        header_label = QLabel("Конфигурация моделей")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(12)
        header_label.setFont(header_font)
        layout.addWidget(header_label)

        # Выбор провайдера
        provider_group = QGroupBox("Провайдер")
        provider_layout = QVBoxLayout(provider_group)

        # Переключатель провайдера
        provider_switch_layout = QHBoxLayout()

        self.gemini_btn = QPushButton("Gemini")
        self.gemini_btn.setCheckable(True)
        self.gemini_btn.setChecked(True)
        self.gemini_btn.setObjectName("gemini_provider_btn")
        if self.icon_system:
            self.icon_system.apply_icons_to_widget(self.gemini_btn)
        provider_switch_layout.addWidget(self.gemini_btn)

        self.openrouter_btn = QPushButton("OpenRouter")
        self.openrouter_btn.setCheckable(True)
        self.openrouter_btn.setObjectName("openrouter_provider_btn")
        if self.icon_system:
            self.icon_system.apply_icons_to_widget(self.openrouter_btn)
        provider_switch_layout.addWidget(self.openrouter_btn)

        provider_layout.addLayout(provider_switch_layout)

        # Статус провайдера
        self.provider_status = QLabel("Gemini активен")
        self.provider_status.setObjectName("provider_status_label")
        provider_layout.addWidget(self.provider_status)

        layout.addWidget(provider_group)

        # Выбор модели
        model_group = QGroupBox("Модель")
        model_layout = QVBoxLayout(model_group)

        # Комбобокс для выбора модели
        model_select_layout = QHBoxLayout()
        model_select_layout.addWidget(QLabel("Модель:"))

        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(200)
        model_select_layout.addWidget(self.model_combo)

        # Кнопка обновления списка моделей
        self.refresh_models_btn = QPushButton()
        self.refresh_models_btn.setToolTip("Обновить список моделей")
        self.refresh_models_btn.setFixedSize(30, 30)
        self.refresh_models_btn.setObjectName("refresh_models_btn")
        if self.icon_system:
            self.icon_system.apply_icons_to_widget(self.refresh_models_btn)
        model_select_layout.addWidget(self.refresh_models_btn)

        model_layout.addLayout(model_select_layout)

        # Информация о текущей модели
        self.model_info = QTextEdit()
        self.model_info.setMaximumHeight(80)
        self.model_info.setPlaceholderText("Информация о выбранной модели...")
        self.model_info.setReadOnly(True)
        model_layout.addWidget(self.model_info)

        layout.addWidget(model_group)

        # API ключи
        api_group = QGroupBox("API Ключи")
        api_layout = QVBoxLayout(api_group)

        # Gemini API Key
        gemini_key_layout = QHBoxLayout()
        gemini_key_layout.addWidget(QLabel("Google API:"))

        self.gemini_key_input = QLineEdit()
        self.gemini_key_input.setPlaceholderText("Введите Google API ключ...")
        self.gemini_key_input.setEchoMode(QLineEdit.Password)
        gemini_key_layout.addWidget(self.gemini_key_input)

        self.gemini_key_btn = QPushButton()
        self.gemini_key_btn.setToolTip("Сохранить Google API ключ")
        self.gemini_key_btn.setFixedSize(30, 30)
        self.gemini_key_btn.setObjectName("save_gemini_key_btn")
        if self.icon_system:
            self.icon_system.apply_icons_to_widget(self.gemini_key_btn)
        gemini_key_layout.addWidget(self.gemini_key_btn)

        api_layout.addLayout(gemini_key_layout)

        # OpenRouter API Key
        openrouter_key_layout = QHBoxLayout()
        openrouter_key_layout.addWidget(QLabel("OpenRouter:"))

        self.openrouter_key_input = QLineEdit()
        self.openrouter_key_input.setPlaceholderText("Введите OpenRouter API ключ...")
        self.openrouter_key_input.setEchoMode(QLineEdit.Password)
        openrouter_key_layout.addWidget(self.openrouter_key_input)

        self.openrouter_key_btn = QPushButton()
        self.openrouter_key_btn.setToolTip("Сохранить OpenRouter API ключ")
        self.openrouter_key_btn.setFixedSize(30, 30)
        self.openrouter_key_btn.setObjectName("save_openrouter_key_btn")
        if self.icon_system:
            self.icon_system.apply_icons_to_widget(self.openrouter_key_btn)
        openrouter_key_layout.addWidget(self.openrouter_key_btn)

        api_layout.addLayout(openrouter_key_layout)

        # Статус API ключей
        self.api_status = QLabel("Статус API ключей...")
        self.api_status.setObjectName("api_status_label")
        api_layout.addWidget(self.api_status)

        layout.addWidget(api_group)

        # Статистика использования
        stats_group = QGroupBox("Статистика")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_label = QLabel("Загрузка статистики...")
        self.stats_label.setObjectName("stats_label")
        stats_layout.addWidget(self.stats_label)

        layout.addWidget(stats_group)

        # Кнопки действий
        actions_layout = QHBoxLayout()

        self.test_connection_btn = QPushButton("Тест соединения")
        self.test_connection_btn.setObjectName("test_connection_btn")
        if self.icon_system:
            self.icon_system.apply_icons_to_widget(self.test_connection_btn)
        actions_layout.addWidget(self.test_connection_btn)

        self.reset_config_btn = QPushButton("Сброс")
        self.reset_config_btn.setObjectName("reset_config_btn")
        if self.icon_system:
            self.icon_system.apply_icons_to_widget(self.reset_config_btn)
        actions_layout.addWidget(self.reset_config_btn)

        layout.addLayout(actions_layout)

        # Растягивающийся элемент
        layout.addStretch()

    def _initialize_backend(self):
        """Инициализирует backend клиенты"""
        try:
            from tools.gopiai_integration.model_config_manager import (
                get_model_config_manager,
            )

            self.model_config_manager = get_model_config_manager()
            logger.info("Backend клиенты инициализированы")

        except Exception as e:
            logger.error(f"Ошибка инициализации backend: {e}")
            self.provider_status.setText(f"Ошибка подключения: {e}")
            self.provider_status.setProperty("status", "error")

    def _setup_connections(self):
        """Настраивает соединения сигналов"""
        # Переключение провайдеров
        self.gemini_btn.clicked.connect(lambda: self._switch_provider("gemini"))
        self.openrouter_btn.clicked.connect(lambda: self._switch_provider("openrouter"))

        # Выбор модели
        self.model_combo.currentTextChanged.connect(self._on_model_selected)
        self.refresh_models_btn.clicked.connect(self._refresh_models)

        # API ключи
        self.gemini_key_btn.clicked.connect(
            lambda: self._save_api_key("GOOGLE_API_KEY", self.gemini_key_input.text())
        )
        self.openrouter_key_btn.clicked.connect(
            lambda: self._save_api_key(
                "OPENROUTER_API_KEY", self.openrouter_key_input.text()
            )
        )

        # Действия
        self.test_connection_btn.clicked.connect(self._test_connection)
        self.reset_config_btn.clicked.connect(self._reset_configuration)

    def _load_current_configuration(self):
        """Загружает текущую конфигурацию"""
        if not self.model_config_manager:
            return

        try:
            current_config = self.model_config_manager.get_current_configuration()

            if current_config:
                self.current_provider = current_config.provider.value
                self.current_model = current_config.model_id

                # Обновляем UI
                self._update_provider_buttons()
                self._load_models_for_provider()
                self._update_model_info()

                logger.info(f"Загружена конфигурация: {current_config.display_name}")
            else:
                logger.warning("Нет активной конфигурации")

        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")

    def _switch_provider(self, provider: str):
        """Переключает провайдера"""
        if provider == self.current_provider:
            return

        try:
            logger.info(f"Переключение на провайдера: {provider}")

            if self.model_config_manager:
                success = self.model_config_manager.switch_to_provider(
                    self.model_config_manager.ModelProvider.GEMINI
                    if provider == "gemini"
                    else self.model_config_manager.ModelProvider.OPENROUTER
                )

                if success:
                    self.current_provider = provider
                    self._update_provider_buttons()
                    self._load_models_for_provider()
                    self.provider_changed.emit(provider)

                    logger.info(f"Переключение на {provider} успешно")
                else:
                    logger.warning(f"Не удалось переключиться на {provider}")
                    # Возвращаем предыдущее состояние
                    self._update_provider_buttons()

        except Exception as e:
            logger.error(f"Ошибка переключения провайдера: {e}")
            self._update_provider_buttons()

    def _update_provider_buttons(self):
        """Обновляет состояние кнопок провайдеров"""
        if self.current_provider == "gemini":
            self.gemini_btn.setChecked(True)
            self.openrouter_btn.setChecked(False)
            self.provider_status.setText("Gemini активен")
            self.provider_status.setProperty("status", "success")
        else:
            self.gemini_btn.setChecked(False)
            self.openrouter_btn.setChecked(True)
            self.provider_status.setText("OpenRouter активен")
            self.provider_status.setProperty("status", "success")

    def _load_models_for_provider(self):
        """Загружает модели для текущего провайдера"""
        if not self.model_config_manager:
            return

        try:
            # Получаем модели для текущего провайдера
            if self.current_provider == "gemini":
                provider_enum = self.model_config_manager.ModelProvider.GEMINI
            else:
                provider_enum = self.model_config_manager.ModelProvider.OPENROUTER

            models = self.model_config_manager.get_configurations_by_provider(
                provider_enum
            )
            available_models = [m for m in models if m.is_available()]

            # Обновляем комбобокс
            self.model_combo.clear()

            for model in available_models:
                display_text = f"{model.display_name}"
                if model.is_default:
                    display_text += " (по умолчанию)"

                self.model_combo.addItem(display_text, model.model_id)

            # Устанавливаем текущую модель
            if self.current_model:
                index = self.model_combo.findData(self.current_model)
                if index >= 0:
                    self.model_combo.setCurrentIndex(index)

            self.available_models[self.current_provider] = available_models

            logger.info(
                f"Загружено {len(available_models)} моделей для {self.current_provider}"
            )

        except Exception as e:
            logger.error(f"Ошибка загрузки моделей: {e}")

    def _on_model_selected(self):
        """Обработчик выбора модели"""
        model_id = self.model_combo.currentData()
        if model_id and model_id != self.current_model:
            try:
                if self.model_config_manager:
                    provider_enum = (
                        self.model_config_manager.ModelProvider.GEMINI
                        if self.current_provider == "gemini"
                        else self.model_config_manager.ModelProvider.OPENROUTER
                    )

                    success = self.model_config_manager.set_current_configuration(
                        provider_enum, model_id
                    )

                    if success:
                        self.current_model = model_id
                        self._update_model_info()
                        self.model_changed.emit(self.current_provider, model_id)

                        logger.info(
                            f"Выбрана модель: {self.current_provider}/{model_id}"
                        )
                    else:
                        logger.warning(f"Не удалось установить модель: {model_id}")

            except Exception as e:
                logger.error(f"Ошибка выбора модели: {e}")

    def _update_model_info(self):
        """Обновляет информацию о текущей модели"""
        if not self.model_config_manager:
            return

        try:
            current_config = self.model_config_manager.get_current_configuration()

            if current_config:
                info_html = f"""
                <b>Модель:</b> {current_config.display_name}<br>
                <b>ID:</b> {current_config.model_id}<br>
                <b>Провайдер:</b> {current_config.provider.value}<br>
                <b>API ключ:</b> {current_config.api_key_env}<br>
                <b>Доступна:</b> {'Да' if current_config.is_available() else 'Нет'}
                """

                self.model_info.setHtml(info_html)
            else:
                self.model_info.clear()

        except Exception as e:
            logger.error(f"Ошибка обновления информации о модели: {e}")

    def _refresh_models(self):
        """Обновляет список моделей"""
        logger.info("Обновление списка моделей...")
        self._load_models_for_provider()

        # Если это OpenRouter, также обновляем модели через API
        if self.current_provider == "openrouter":
            try:
                from tools.gopiai_integration.openrouter_client import (
                    get_openrouter_client,
                )

                client = get_openrouter_client()
                models = client.get_models_sync(force_refresh=True)

                if models and self.model_config_manager:
                    self.model_config_manager.add_openrouter_models(models)
                    self._load_models_for_provider()  # Перезагружаем список

                    logger.info(f"Обновлено {len(models)} моделей OpenRouter")

            except Exception as e:
                logger.error(f"Ошибка обновления моделей OpenRouter: {e}")

    def _save_api_key(self, env_var: str, api_key: str):
        """Сохраняет API ключ"""
        if not api_key.strip():
            logger.warning("Пустой API ключ")
            return

        try:
            # Сохраняем в переменные окружения (временно)
            os.environ[env_var] = api_key.strip()

            # Эмитируем сигнал для сохранения в конфигурации
            self.api_key_updated.emit(env_var, api_key.strip())

            logger.info(f"API ключ {env_var} сохранен")
            self._update_api_status()

            # Очищаем поле ввода
            if env_var == "GOOGLE_API_KEY":
                self.gemini_key_input.clear()
            else:
                self.openrouter_key_input.clear()

        except Exception as e:
            logger.error(f"Ошибка сохранения API ключа: {e}")

    def _update_api_status(self):
        """Обновляет статус API ключей"""
        google_key = os.getenv("GOOGLE_API_KEY")
        openrouter_key = os.getenv("OPENROUTER_API_KEY")

        status_parts = []

        if google_key:
            status_parts.append("Google: Да")
        else:
            status_parts.append("Google: Нет")

        if openrouter_key:
            status_parts.append("OpenRouter: Да")
        else:
            status_parts.append("OpenRouter: Нет")

        self.api_status.setText(" | ".join(status_parts))

    def _update_status(self):
        """Обновляет общий статус"""
        self._update_api_status()

        if self.model_config_manager:
            try:
                status = self.model_config_manager.get_provider_status()

                stats_text = []
                for provider, info in status.items():
                    if info["available_models"] > 0:
                        stats_text.append(
                            f"{provider.upper()}: {info['available_models']} моделей"
                        )

                if stats_text:
                    self.stats_label.setText(" | ".join(stats_text))
                else:
                    self.stats_label.setText("Нет доступных моделей")

            except Exception as e:
                logger.error(f"Ошибка обновления статуса: {e}")

    def _test_connection(self):
        """Тестирует соединение с текущим провайдером"""
        logger.info(f"Тестирование соединения с {self.current_provider}...")

        try:
            if self.current_provider == "openrouter":
                from tools.gopiai_integration.openrouter_client import (
                    get_openrouter_client,
                )

                client = get_openrouter_client()
                if client.test_connection():
                    self.provider_status.setText("OpenRouter: соединение успешно")
                    self.provider_status.setProperty("status", "success")
                else:
                    self.provider_status.setText("OpenRouter: ошибка соединения")
                    self.provider_status.setProperty("status", "error")
            else:
                # Для Gemini просто проверяем наличие API ключа
                if os.getenv("GOOGLE_API_KEY"):
                    self.provider_status.setText("Gemini: API ключ найден")
                    self.provider_status.setProperty("status", "success")
                else:
                    self.provider_status.setText("Gemini: нет API ключа")
                    self.provider_status.setProperty("status", "error")

        except Exception as e:
            logger.error(f"Ошибка тестирования соединения: {e}")
            self.provider_status.setText(f"Ошибка: {e}")
            self.provider_status.setProperty("status", "error")

    def _reset_configuration(self):
        """Сбрасывает конфигурацию к значениям по умолчанию"""
        try:
            logger.info("Сброс конфигурации...")

            if self.model_config_manager:
                # Переключаемся на Gemini по умолчанию
                success = self.model_config_manager.switch_to_provider(
                    self.model_config_manager.ModelProvider.GEMINI
                )

                if success:
                    self.current_provider = "gemini"
                    self._update_provider_buttons()
                    self._load_models_for_provider()

                    logger.info("Конфигурация сброшена")
                else:
                    logger.warning("Не удалось сбросить конфигурацию")

        except Exception as e:
            logger.error(f"Ошибка сброса конфигурации: {e}")

    def get_current_provider(self) -> str:
        """Возвращает текущего провайдера"""
        return self.current_provider

    def get_current_model(self) -> Optional[str]:
        """Возвращает текущую модель"""
        return self.current_model

    def set_provider(self, provider: str):
        """Устанавливает провайдера программно"""
        self._switch_provider(provider)

    def set_model(self, model_id: str):
        """Устанавливает модель программно"""
        index = self.model_combo.findData(model_id)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)


def test_model_selector_widget():
    """Тестовая функция для виджета выбора моделей"""
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    widget = ModelSelectorWidget()
    widget.setWindowTitle("Model Selector Test")
    widget.resize(350, 500)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    # Настройка логирования для тестирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    test_model_selector_widget()
