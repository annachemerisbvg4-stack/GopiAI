# --- START OF FILE chat_async_handler.py (ИСПРАВЛЕННАЯ ВЕРСИЯ) ---

import logging
import threading
from PySide6.QtCore import QObject, Signal, QTimer, Slot

logger = logging.getLogger(__name__)

class ChatAsyncHandler(QObject):
    # ### ИЗМЕНЕНО: Добавляем новый сигнал ###
    start_polling_signal = Signal(str) # Сигнал для безопасного запуска таймера

    response_ready = Signal(object, bool)
    status_update = Signal(str)

    def __init__(self, crew_ai_client, parent=None):
        super().__init__(parent)
        self.crew_ai_client = crew_ai_client
        self._current_task_id = None
        self._polling_timer = QTimer(self)
        self._polling_timer.timeout.connect(self._check_task_status)
        
        # ### ИЗМЕНЕНО: Подключаем наш новый сигнал к слоту ###
        self.start_polling_signal.connect(self._start_polling_from_main_thread)

    def process_message(self, message_data: dict):
        """Запускает асинхронную обработку сообщения в отдельном потоке."""
        worker = threading.Thread(
            target=self._process_in_background,
            args=(message_data,),
            daemon=True,
        )
        worker.start()

    def _process_in_background(self, message_data: dict):
        try:
            response = self.crew_ai_client.process_request(message_data)
            if not response:
                raise ValueError("Received an empty response from the server.")
            
            if isinstance(response, dict) and "task_id" in response:
                # ### ИЗМЕНЕНО: Не запускаем таймер напрямую, а испускаем сигнал ###
                self.start_polling_signal.emit(response["task_id"])
            else:
                self.response_ready.emit(response, False)

        except Exception as e:
            logger.error(f"Error in background processing: {e}", exc_info=True)
            self.response_ready.emit(str(e), True)
            
    # ### ИЗМЕНЕНО: Создаем новый слот, который будет выполняться в основном потоке ###
    @Slot(str)
    def _start_polling_from_main_thread(self, task_id: str):
        """Starts the timer to poll for a task's status. Must be called from the main UI thread."""
        self._current_task_id = task_id
        self._current_polling_attempt = 0
        self._polling_timer.start(1000) # 1 секунда
        logger.info(f"Task polling started for task_id: {task_id}")
        self.status_update.emit("⏳ Обрабатываю запрос...")

    def _check_task_status(self):
        """Периодически опрашивает сервер о ходе выполнения задачи."""
        if self._current_task_id is None:
            self._polling_timer.stop()
            return

        try:
            status = self.crew_ai_client.check_task_status(self._current_task_id)
            # Ожидаем, что сервер возвращает словарь с ключами `done` и `result`
            if status.get("done"):
                self._polling_timer.stop()
                self.response_ready.emit(status.get("result"), False)
            else:
                # Обновляем статус в UI
                self.status_update.emit(status.get("status", "⏳ Обрабатываю запрос..."))
        except Exception as e:
            logger.error(f"Error while polling task status: {e}", exc_info=True)
            self._polling_timer.stop()
            self.response_ready.emit(str(e), True)

# --- КОНЕЦ ФАЙЛА chat_async_handler.py ---