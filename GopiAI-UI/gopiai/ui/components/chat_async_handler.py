# --- START OF FILE chat_async_handler.py (MODIFIED) ---

import logging
import threading
import queue
from typing import Dict, Any, Optional
from PySide6.QtCore import QObject, Signal

from gopiai.services.gemini_cli_service import GeminiCliService

# Настройка логирования
logger = logging.getLogger(__name__)

class ChatAsyncHandler(QObject):
    """Асинхронный обработчик чата для Gemini CLI с поддержкой OAuth."""
    
    # Сигналы для UI
    response_ready = Signal(dict)
    status_update = Signal(str)
    message_error = Signal(str)
    oauth_url_received = Signal(str) # Новый сигнал для URL

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        logger.info("[ChatAsyncHandler] Обработчик для Gemini CLI инициализирован")

    def send_message(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Запускает асинхронную обработку сообщения с Gemini CLI.
        """
        try:
            logger.info(f"[ChatAsyncHandler] Начинаем обработку сообщения: {message[:50]}...")
            
            # 1. Создаем очередь для этого конкретного запроса
            response_queue = queue.Queue()
            
            # 2. Создаем наш сервис, передавая ему очередь
            cli_service = GeminiCliService(output_queue=response_queue)
            
            # 3. Запускаем listener в отдельном потоке
            listener_thread = threading.Thread(target=self._queue_listener, args=(response_queue,))
            listener_thread.daemon = True
            listener_thread.start()
            
            # 4. Вызываем метод чата сервиса, который запустит CLI в своем потоке
            history = metadata.get('chat_history', []) if metadata else []
            current_message = {'role': 'user', 'content': message}
            full_chat_history = history + [current_message]
            
            model = metadata.get('model_id', 'gemini-pro') if metadata else 'gemini-pro'
            
            cli_service.chat(messages=full_chat_history, model=model)
            
            return True
            
        except Exception as e:
            logger.error(f"[ChatAsyncHandler] Ошибка отправки сообщения: {e}", exc_info=True)
            self.message_error.emit(str(e))
            return False

    def _queue_listener(self, response_queue: queue.Queue):
        """
        Слушает очередь в отдельном потоке и испускает сигналы для UI.
        """
        logger.info("[Listener] Поток-слушатель очереди запущен.")
        while True:
            try:
                item = response_queue.get() # Блокирующий вызов
                
                item_type = item.get('type')
                logger.debug(f"[Listener] Получен элемент из очереди: {item_type}")
                
                if item_type == 'oauth_url':
                    self.oauth_url_received.emit(item['url'])
                elif item_type == 'response':
                    self.response_ready.emit({'response': item.get('data', '')})
                elif item_type == 'error':
                    self.message_error.emit(item.get('message', 'Неизвестная ошибка'))
                elif item_type == 'done':
                    logger.info("[Listener] Получен сигнал 'done', поток завершается.")
                    break
                else:
                    # Игнорируем другие типы сообщений, например, 'raw_output'
                    pass

            except Exception as e:
                logger.error(f"[Listener] Ошибка в потоке-слушателе: {e}", exc_info=True)
                self.message_error.emit(str(e))
                break

# --- КОНЕЦ ФАЙЛА chat_async_handler.py ---
