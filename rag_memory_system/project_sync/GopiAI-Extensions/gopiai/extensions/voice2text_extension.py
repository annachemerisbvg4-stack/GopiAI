"""
GopiAI Voice2Text Extension
===========================

Расширение для голосового ввода и преобразования речи в текст
Использует модель Whisper для высокого качества распознавания

Возможности:
- Запись голоса с микрофона
- Преобразование в текст через Whisper
- Вставка текста в активный редактор
- Перевод голосовых сообщений
- Настройка качества и языка
"""

import os
import sys
import threading
import wave
import tempfile
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTextEdit, QLabel, QComboBox, QProgressBar,
    QMessageBox, QCheckBox, QSpinBox, QGroupBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont

try:
    import pyaudio
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    # Пытаемся импортировать whisper
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class AudioRecorder:
    """Класс для записи аудио с микрофона"""
    
    def __init__(self):
        self.is_recording = False
        self.frames = []
        self.audio = None
        self.stream = None
        
        # Параметры записи
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  # Whisper работает лучше с 16kHz
        
    def start_recording(self):
        """Начало записи"""
        if not AUDIO_AVAILABLE:
            raise Exception("PyAudio не установлен")
            
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        self.is_recording = True
        self.frames = []
        
    def record_chunk(self):
        """Запись одного фрагмента"""
        if self.is_recording and self.stream:
            data = self.stream.read(self.chunk)
            self.frames.append(data)
            return True
        return False
        
    def stop_recording(self):
        """Остановка записи"""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
            
    def save_recording(self, filename):
        """Сохранение записи в файл"""
        if not self.audio:
            raise RuntimeError("Audio interface is not initialized")
            
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))


class WhisperThread(QThread):
    """Поток для обработки аудио через Whisper"""
    
    transcription_ready = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, audio_file, model_path, language: Optional[str] = None):
        super().__init__()
        self.audio_file = audio_file
        self.model_path = model_path
        self.language = language if language is not None else "ru"
        
    def run(self):
        """Запуск транскрипции"""
        try:
            if WHISPER_AVAILABLE:
                # Используем библиотеку whisper
                model = whisper.load_model("small")
                result = model.transcribe(self.audio_file, language=self.language)
                text = str(result["text"]).strip() if isinstance(result["text"], list) else result["text"].strip()
            else:
                # Заглушка, если whisper не доступен
                text = f"[ЗАГЛУШКА] Голосовой ввод: аудио файл {os.path.basename(self.audio_file)}"
                
            self.transcription_ready.emit(text)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class Voice2TextWidget(QWidget):
    """Виджет для голосового ввода"""
    
    text_transcribed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("voice2text")
        self.setWindowTitle("🎤 Голосовой ввод")
        
        # Путь к модели
        self.model_path = self._find_model_path()
        
        # Аудио рекордер
        self.recorder = AudioRecorder() if AUDIO_AVAILABLE else None
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self._update_recording)
        
        # Поток транскрипции
        self.whisper_thread = None
        
        self._setup_ui()
        
    def _find_model_path(self):
        """Поиск пути к модели Whisper"""
        # Ищем модель в структуре проекта
        current_dir = Path(__file__).parent
        model_path = current_dir / "Voice2Text_Extension" / "models" / "whisper" / "ggml-small.bin"
        
        if model_path.exists():
            return str(model_path)
        
        # Альтернативные пути
        alt_paths = [
            Path(__file__).parent.parent / "Voice2Text_Extension" / "models" / "whisper" / "ggml-small.bin",
            Path("models/whisper/ggml-small.bin"),
        ]
        
        for path in alt_paths:
            if path.exists():
                return str(path)
                
        return None
        
    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок
        header = QLabel("🎤 Голосовой ввод")
        header.setObjectName("panelHeader")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Статус системы
        status_group = QGroupBox("Статус системы")
        status_layout = QVBoxLayout(status_group)
        
        self.audio_status = QLabel("🔴 Аудио: Недоступно" if not AUDIO_AVAILABLE else "🟢 Аудио: Готово")
        self.whisper_status = QLabel("🔴 Whisper: Недоступен" if not WHISPER_AVAILABLE else "🟢 Whisper: Готов")
        self.model_status = QLabel(f"🟢 Модель: Найдена" if self.model_path else "🔴 Модель: Не найдена")
        
        status_layout.addWidget(self.audio_status)
        status_layout.addWidget(self.whisper_status)
        status_layout.addWidget(self.model_status)
        layout.addWidget(status_group)
        
        # Настройки
        settings_group = QGroupBox("Настройки")
        settings_layout = QVBoxLayout(settings_group)
        
        # Язык
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Язык:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["ru", "en", "auto"])
        self.language_combo.setCurrentText("ru")
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch()
        settings_layout.addLayout(lang_layout)
        
        # Автовставка
        self.auto_insert_check = QCheckBox("Автоматически вставлять в активный редактор")
        self.auto_insert_check.setChecked(True)
        settings_layout.addWidget(self.auto_insert_check)
        
        layout.addWidget(settings_group)
        
        # Кнопки управления
        controls_layout = QHBoxLayout()
        
        self.record_button = QPushButton("🎤 Начать запись")
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)
        self.record_button.clicked.connect(self._toggle_recording)
        self.record_button.setEnabled(AUDIO_AVAILABLE)
        
        self.transcribe_button = QPushButton("📝 Обработать файл")
        self.transcribe_button.clicked.connect(self._transcribe_file)
        
        controls_layout.addWidget(self.record_button)
        controls_layout.addWidget(self.transcribe_button)
        layout.addLayout(controls_layout)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Результат
        result_group = QGroupBox("Результат")
        result_layout = QVBoxLayout(result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("Здесь появится распознанный текст...")
        self.result_text.setMaximumHeight(150)
        result_layout.addWidget(self.result_text)
        
        # Кнопки для работы с результатом
        result_buttons = QHBoxLayout()
        
        self.copy_button = QPushButton("📋 Копировать")
        self.copy_button.clicked.connect(self._copy_text)
        
        self.insert_button = QPushButton("📝 Вставить в редактор")
        self.insert_button.clicked.connect(self._insert_text)
        
        self.clear_button = QPushButton("🗑️ Очистить")
        self.clear_button.clicked.connect(self.result_text.clear)
        
        result_buttons.addWidget(self.copy_button)
        result_buttons.addWidget(self.insert_button)
        result_buttons.addWidget(self.clear_button)
        result_layout.addLayout(result_buttons)
        
        layout.addWidget(result_group)
        layout.addStretch()
        
    def _toggle_recording(self):
        """Переключение записи"""
        if not self.recorder:
            QMessageBox.warning(self, "Ошибка", "Аудио система недоступна")
            return
            
        if not self.recorder.is_recording:
            self._start_recording()
        else:
            self._stop_recording()
            
    def _start_recording(self):
        """Начало записи"""
        if not AUDIO_AVAILABLE or not self.recorder:
            QMessageBox.warning(self, "Ошибка", "Аудио система недоступна")
            return
            
        try:
            self.recorder.start_recording()
            self.record_button.setText("⏹️ Остановить запись")
            self.record_button.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            
            # Запускаем таймер для записи фрагментов
            self.recording_timer.start(100)  # каждые 100мс
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка записи", str(e))
            
    def _update_recording(self):
        """Обновление записи"""
        if self.recorder and not self.recorder.record_chunk():
            self.recording_timer.stop()
            
    def _stop_recording(self):
        """Остановка записи"""
        self.recording_timer.stop()
        if self.recorder:
            self.recorder.stop_recording()          
        self.record_button.setText("🎤 Начать запись")
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        # Сохраняем запись и обрабатываем
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        if self.recorder:
            self.recorder.save_recording(temp_file.name)
            temp_file.close()
            self._process_audio_file(temp_file.name)
        else:
            temp_file.close()
            os.unlink(temp_file.name)
            QMessageBox.warning(self, "Ошибка", "Аудио система недоступна")       
    def _transcribe_file(self):
        """Транскрипция выбранного файла"""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите аудио файл", 
            "", 
            "Аудио файлы (*.wav *.mp3 *.m4a *.ogg);;Все файлы (*.*)"
        )
        
        if file_path:
            self._process_audio_file(file_path)
            
    def _process_audio_file(self, file_path):
        """Обработка аудио файла"""
        if not self.model_path and not WHISPER_AVAILABLE:
            QMessageBox.warning(self, "Ошибка", "Модель Whisper недоступна")
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Запускаем транскрипцию в отдельном потоке
        language = self.language_combo.currentText()
        if language == "auto":
            language = None
            
        self.whisper_thread = WhisperThread(file_path, self.model_path, language)
        self.whisper_thread.transcription_ready.connect(self._on_transcription_ready)
        self.whisper_thread.error_occurred.connect(self._on_transcription_error)
        self.whisper_thread.finished.connect(lambda: self.progress_bar.setVisible(False))
        self.whisper_thread.start()
        
    def _on_transcription_ready(self, text):
        """Обработка готовой транскрипции"""
        self.result_text.setPlainText(text)
        
        # Автоматическая вставка в редактор
        if self.auto_insert_check.isChecked():
            self._insert_text()
            
        self.text_transcribed.emit(text)
        
    def _on_transcription_error(self, error):
        """Обработка ошибки транскрипции"""
        QMessageBox.critical(self, "Ошибка транскрипции", error)
        
    def _copy_text(self):
        """Копирование текста в буфер обмена"""
        from PySide6.QtWidgets import QApplication
        
        text = self.result_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Готово", "Текст скопирован в буфер обмена")
            
    def _insert_text(self):
        """Вставка текста в активный редактор"""
        text = self.result_text.toPlainText()
        if text:
            # Ищем главное окно и активный редактор
            main_window = self.window()
            try:
                # Try to get the current editor through the main window's interface
                if hasattr(main_window, 'get_current_editor'):
                    current_editor = main_window.get_current_editor()
                    if current_editor and hasattr(current_editor, 'insertPlainText'):
                        current_editor.insertPlainText(text + " ")
                        QMessageBox.information(self, "Готово", "Текст вставлен в редактор")
                        return
                # Fallback to traditional tab structure if available
                elif hasattr(main_window, 'tab_document') and hasattr(main_window.tab_document, 'tab_widget'):
                    current_tab = main_window.tab_document.tab_widget.currentWidget()
                    if current_tab and hasattr(current_tab, 'insertPlainText'):
                        current_tab.insertPlainText(text + " ")
                        QMessageBox.information(self, "Готово", "Текст вставлен в редактор")
                        return
                QMessageBox.warning(self, "Предупреждение", "Активный редактор не найден")
            except AttributeError:
                QMessageBox.warning(self, "Предупреждение", "Редактор недоступен")


def init_voice2text_extension(main_window):
    """
    Инициализация расширения голосового ввода
    
    Args:
        main_window: Главное окно приложения
    """
    try:
        # Создаем виджет голосового ввода
        voice_widget = Voice2TextWidget()
        
        # Добавляем в интерфейс
        if hasattr(main_window, 'add_dock_widget'):
            main_window.add_dock_widget("voice2text", voice_widget, "bottom")
            
        print("✅ Расширение голосового ввода загружено!")
        print(f"   🎤 Аудио: {'Доступно' if AUDIO_AVAILABLE else 'Недоступно (установите pyaudio)'}")
        print(f"   🧠 Whisper: {'Доступен' if WHISPER_AVAILABLE else 'Недоступен (установите openai-whisper)'}")
        print(f"   📁 Модель: {'Найдена' if voice_widget.model_path else 'Не найдена'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке расширения голосового ввода: {e}")
        return False


def auto_init(main_window):
    """Автоматическая инициализация расширения"""
    return init_voice2text_extension(main_window)


if __name__ == "__main__":
    # Тестирование виджета
    from PySide6.QtWidgets import QApplication
    
    app = QApplication([])
    widget = Voice2TextWidget()
    widget.show()
    app.exec()
