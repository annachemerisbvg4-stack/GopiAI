"""
Improved AsyncChatHandler - улучшенный асинхронный обработчик чата
Решает проблемы с обрыванием сообщений и интегрируется с ResponseFormatter
"""

import logging
import time
import json
from typing import Dict, Any, Optional, Callable
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class ImprovedAsyncChatHandler(QThread):
    """Улучшенный асинхронный обработчик чата с оптимизированным polling"""
    
    # Сигналы для взаимодействия с UI
    message_chunk_received = Signal(str, str)  # (chunk, message_type)
    message_completed = Signal(dict)  # Полный ответ
    message_error = Signal(str)  # Ошибка
    status_updated = Signal(str)  # Обновление статуса
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.current_task_id = None
        self.polling_active = False
        self.last_response_length = 0
        
        # Настройки polling
        self.initial_delay = 0.3  # Начальная задержка
        self.max_delay = 3.0      # Максимальная задержка
        self.delay_multiplier = 1.2  # Множитель для экспоненциальной задержки
        
        logger.info("[ImprovedAsyncChatHandler] Инициализирован улучшенный обработчик чата")
        
    def send_message(self, message: str, metadata: Optional[Dict] = None) -> bool:
        """
        Отправка сообщения и начало асинхронной обработки
        
        Args:
            message: Текст сообщения
            metadata: Дополнительные метаданные
            
        Returns:
            True если сообщение отправлено успешно
        """
        try:
            logger.info(f"[ImprovedAsyncChatHandler] Отправляем сообщение: {message[:100]}...")
            
            # Отправляем сообщение в backend
            response = self.api_client.send_message(message, metadata or {})
            
            if not response:
                self.message_error.emit("Не удалось отправить сообщение")
                return False
                
            # Получаем task_id для polling
            self.current_task_id = response.get('task_id')
            
            if not self.current_task_id:
                self.message_error.emit("Не получен task_id от сервера")
                return False
                
            logger.info(f"[ImprovedAsyncChatHandler] Получен task_id: {self.current_task_id}")
            
            # Сбрасываем состояние
            self.last_response_length = 0
            self.polling_active = True
            
            # Запускаем поток для polling
            if not self.isRunning():
                self.start()
            else:
                logger.warning("[ImprovedAsyncChatHandler] Поток уже запущен")
                
            return True
            
        except Exception as e:
            logger.error(f"[ImprovedAsyncChatHandler] Ошибка отправки сообщения: {e}")
            self.message_error.emit(f"Ошибка отправки: {str(e)}")
            return False
            
    def run(self):
        """Основной цикл polling с оптимизированными задержками"""
        logger.info("[ImprovedAsyncChatHandler] Запущен цикл polling")
        
        delay = self.initial_delay
        attempt = 0
        
        while self.polling_active and self.current_task_id:
            try:
                attempt += 1
                logger.debug(f"[ImprovedAsyncChatHandler] Polling попытка #{attempt}")
                
                # Получаем статус задачи
                status_response = self.api_client.get_task_status(self.current_task_id)
                
                if not status_response:
                    logger.warning("[ImprovedAsyncChatHandler] Пустой ответ статуса")
                    time.sleep(delay)
                    continue
                    
                task_status = status_response.get('status', 'unknown')
                logger.debug(f"[ImprovedAsyncChatHandler] Статус задачи: {task_status}")
                
                # Обновляем UI статусом
                self.status_updated.emit(f"Обработка... ({task_status})")
                
                if task_status == 'completed':
                    self.handle_completion(status_response)
                    break
                elif task_status == 'processing':
                    # Обрабатываем частичные результаты если есть
                    self.handle_partial_result(status_response)
                    # Сбрасываем задержку при активности
                    delay = self.initial_delay
                elif task_status == 'error':
                    error_msg = status_response.get('error', 'Неизвестная ошибка')
                    self.message_error.emit(f"Ошибка обработки: {error_msg}")
                    break
                else:
                    # Увеличиваем задержку для неактивных состояний
                    delay = min(delay * self.delay_multiplier, self.max_delay)
                
                # Пауза перед следующей попыткой
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"[ImprovedAsyncChatHandler] Ошибка в цикле polling: {e}")
                time.sleep(1)  # Короткая пауза при ошибке
                
        logger.info("[ImprovedAsyncChatHandler] Цикл polling завершен")
        self.polling_active = False
        
    def handle_partial_result(self, status_response: Dict[str, Any]):
        """
        Обработка частичных результатов для streaming эффекта
        
        Args:
            status_response: Ответ с частичными данными
        """
        try:
            # Проверяем наличие частичного ответа
            partial_response = status_response.get('partial_response')
            if not partial_response:
                return
                
            # Фильтруем и отправляем только новые части
            current_length = len(str(partial_response))
            if current_length > self.last_response_length:
                # Извлекаем новую часть
                new_chunk = str(partial_response)[self.last_response_length:]
                
                # Фильтруем служебную информацию
                clean_chunk = self.filter_response_chunk(new_chunk)
                
                if clean_chunk:
                    self.message_chunk_received.emit(clean_chunk, "ai")
                    
                self.last_response_length = current_length
                
        except Exception as e:
            logger.error(f"[ImprovedAsyncChatHandler] Ошибка обработки частичного результата: {e}")
            
    def handle_completion(self, status_response: Dict[str, Any]):
        """
        Обработка завершенного ответа
        
        Args:
            status_response: Полный ответ от сервера
        """
        try:
            logger.info("[ImprovedAsyncChatHandler] Обрабатываем завершенный ответ")
            
            self.polling_active = False
            
            # Извлекаем результат
            result = status_response.get('result', {})
            if not result:
                self.message_error.emit("Пустой результат от сервера")
                return
                
            # Фильтруем ответ для чистого отображения
            filtered_response = self.filter_complete_response(result)
            
            # Отправляем в UI
            self.message_completed.emit(filtered_response)
            self.status_updated.emit("Готово")
            
            logger.info("[ImprovedAsyncChatHandler] Ответ успешно обработан и отправлен в UI")
            
        except Exception as e:
            logger.error(f"[ImprovedAsyncChatHandler] Ошибка обработки завершения: {e}")
            self.message_error.emit(f"Ошибка обработки ответа: {str(e)}")
            
    def filter_response_chunk(self, chunk: str) -> str:
        """
        Фильтрация части ответа от служебной информации
        
        Args:
            chunk: Часть ответа
            
        Returns:
            Очищенная часть ответа
        """
        try:
            if not chunk:
                return ""
                
            # Простая фильтрация JSON блоков в streaming режиме
            import re
            
            # Удаляем JSON блоки с командами
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            clean_chunk = re.sub(json_pattern, '', chunk)
            
            # Удаляем лишние пробелы
            clean_chunk = clean_chunk.strip()
            
            return clean_chunk
            
        except Exception as e:
            logger.error(f"[ImprovedAsyncChatHandler] Ошибка фильтрации chunk: {e}")
            return str(chunk)
            
    def filter_complete_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Фильтрация полного ответа
        
        Args:
            response_data: Данные ответа
            
        Returns:
            Отфильтрованный ответ
        """
        try:
            # Если backend уже отформатировал ответ, используем его
            if response_data.get('formatted', False):
                logger.debug("[ImprovedAsyncChatHandler] Ответ уже отформатирован backend")
                return {
                    'content': response_data.get('response', ''),
                    'has_commands': response_data.get('has_commands', False),
                    'metadata': response_data.get('analysis', {}),
                    'formatted': True
                }
            
            # Иначе применяем базовую фильтрацию
            raw_content = response_data.get('response', '')
            
            # Простая очистка от JSON блоков
            import re
            json_pattern = r'```json\s*\{.*?\}\s*```'
            clean_content = re.sub(json_pattern, '', raw_content, flags=re.DOTALL | re.IGNORECASE)
            
            return {
                'content': clean_content.strip(),
                'has_commands': False,
                'metadata': response_data.get('analysis', {}),
                'formatted': False
            }
            
        except Exception as e:
            logger.error(f"[ImprovedAsyncChatHandler] Ошибка фильтрации полного ответа: {e}")
            return {
                'content': str(response_data.get('response', 'Ошибка обработки ответа')),
                'has_commands': False,
                'metadata': {},
                'formatted': False
            }
            
    def stop_polling(self):
        """Остановка polling"""
        logger.info("[ImprovedAsyncChatHandler] Остановка polling")
        self.polling_active = False
        self.current_task_id = None
        
        if self.isRunning():
            self.quit()
            self.wait(3000)  # Ждем до 3 секунд
            
    def is_busy(self) -> bool:
        """Проверка, занят ли обработчик"""
        return self.polling_active and self.isRunning()
        
    def get_current_task_id(self) -> Optional[str]:
        """Получение текущего task_id"""
        return self.current_task_id
        
    def set_polling_delays(self, initial: float, maximum: float, multiplier: float):
        """
        Настройка задержек polling
        
        Args:
            initial: Начальная задержка в секундах
            maximum: Максимальная задержка в секундах  
            multiplier: Множитель для экспоненциального роста
        """
        self.initial_delay = max(0.1, initial)
        self.max_delay = max(initial, maximum)
        self.delay_multiplier = max(1.0, multiplier)
        
        logger.debug(f"[ImprovedAsyncChatHandler] Настройки polling обновлены: "
                    f"initial={self.initial_delay}, max={self.max_delay}, mult={self.delay_multiplier}")

class ChatIntegrationHelper:
    """Вспомогательный класс для интеграции с существующим UI"""
    
    @staticmethod
    def create_improved_handler(api_client, chat_widget) -> ImprovedAsyncChatHandler:
        """
        Создание улучшенного обработчика с подключением к виджету чата
        
        Args:
            api_client: Клиент для API
            chat_widget: Виджет чата (OptimizedChatWidget)
            
        Returns:
            Настроенный ImprovedAsyncChatHandler
        """
        handler = ImprovedAsyncChatHandler(api_client)
        
        # Подключаем сигналы к виджету чата
        handler.message_chunk_received.connect(
            lambda chunk, msg_type: chat_widget.append_text_chunk(chunk, msg_type)
        )
        
        handler.message_completed.connect(
            lambda response: chat_widget.append_message(
                response.get('content', ''), 
                'ai'
            )
        )
        
        handler.message_error.connect(
            lambda error: chat_widget.append_message(error, 'error')
        )
        
        handler.status_updated.connect(
            lambda status: logger.debug(f"Статус: {status}")
        )
        
        logger.info("[ChatIntegrationHelper] Улучшенный обработчик создан и подключен")
        return handler
