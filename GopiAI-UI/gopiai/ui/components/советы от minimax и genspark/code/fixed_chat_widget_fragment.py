"""
ИСПРАВЛЕННЫЙ ФРАГМЕНТ CHAT_WIDGET.PY
Только методы, которые нужно изменить
"""

import logging
import time
import threading
from PySide6.QtCore import QTimer

logger = logging.getLogger(__name__)

# Этот код нужно заменить в вашем chat_widget.py

def send_message(self):
    """Отправляет сообщение и обрабатывает его через CrewAI API (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
    text = self.input.toPlainText().strip()
    if text:
        # Отображаем сообщение пользователя
        self.append_message("Вы", text)
        self.input.clear()
        
        # Показываем индикатор ожидания
        self.send_btn.setEnabled(False)
        
        # Создаем уникальный ID для сообщения ожидания
        waiting_id = f"waiting_{int(time.time())}"
        waiting_message_html = f"<span id='{waiting_id}'>⏳ Обрабатываю запрос...</span>"
        self.append_message("Ассистент", waiting_message_html)
        
        # Функция обработки в фоновом потоке
        def process_in_background():
            response = "Извините, я не смог обработать запрос из-за технической проблемы."
            error_occurred = False
            
            try:
                # Используем CrewAI API клиент
                process_result = self.crew_ai_client.process_request(text)
                logger.info(f"Получен результат от CrewAI API: {process_result}")
                
                # ИСПРАВЛЕНИЕ: Теперь обрабатываем структурированный ответ правильно
                if isinstance(process_result, dict):
                    if "response" in process_result:
                        response = process_result["response"]
                        if "error" in process_result:
                            logger.warning(f"Получена ошибка от API: {process_result['error']}")
                            error_occurred = True
                    else:
                        response = "Неизвестный формат ответа от CrewAI API."
                        error_occurred = True
                        logger.error(f"Неожиданный формат ответа: {process_result}")
                elif isinstance(process_result, str):
                    # Обратная совместимость на случай, если клиент вернул строку
                    response = process_result
                    logger.info("Получен ответ в виде строки (обратная совместимость)")
                else:
                    response = "Неизвестный тип ответа от CrewAI API."
                    error_occurred = True
                    logger.error(f"Неожиданный тип ответа: {type(process_result)}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка при обработке запроса: {e}", exc_info=True)
                response = f"Произошла ошибка при обработке запроса: {str(e)}"
                error_occurred = True
            
            # Обновляем UI в основном потоке
            def update_ui():
                self._update_assistant_response(waiting_id, response, error_occurred)
            
            QTimer.singleShot(0, update_ui)
        
        # Запускаем обработку в отдельном потоке
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()

def _update_assistant_response(self, waiting_id, response, error_occurred=False):
    """
    Обновляет ответ ассистента в истории чата (ИСПРАВЛЕННАЯ ВЕРСИЯ)
    
    Args:
        waiting_id: ID сообщения ожидания для замены
        response: Текст ответа
        error_occurred: Флаг ошибки для стилизации
    """
    logger.info(f"_update_assistant_response: waiting_id={waiting_id}, response_len={len(response)}, error={error_occurred}")
    
    # ИСПРАВЛЕНИЕ: Заменяем сообщение ожидания вместо добавления нового
    try:
        # Получаем текущий HTML
        current_html = self.history.toHtml()
        
        # Ищем и заменяем сообщение ожидания
        waiting_span = f"<span id='{waiting_id}'>⏳ Обрабатываю запрос...</span>"
        
        if waiting_span in current_html:
            # Стилизируем ответ в зависимости от наличия ошибки
            if error_occurred:
                new_response = f"<span style='color: #d73027;'>{response}</span>"
            else:
                new_response = response
                
            # Заменяем сообщение ожидания на реальный ответ
            updated_html = current_html.replace(waiting_span, new_response)
            self.history.setHtml(updated_html)
            logger.info("✅ Сообщение ожидания успешно заменено на ответ")
        else:
            # Fallback: если не удалось найти сообщение ожидания, добавляем новое
            logger.warning("⚠️ Не удалось найти сообщение ожидания, добавляем новое сообщение")
            self.append_message("Ассистент", response)
    
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении ответа: {e}")
        # Fallback: просто добавляем новое сообщение
        self.append_message("Ассистент", response)
    
    # Включаем кнопки и прокручиваем вниз
    self.send_btn.setEnabled(True)
    self._scroll_history_to_end()

def append_message(self, author, text):
    """Добавляет сообщение в историю чата (УЛУЧШЕННАЯ ВЕРСИЯ)"""
    logger.info(f"append_message: author={author}, text_len={len(text)}")
    
    # Добавляем timestamp для отладки
    timestamp = time.strftime("%H:%M:%S")
    
    # Форматируем сообщение с улучшенной стилизацией
    if author == "Система":
        formatted_message = f"<p><em style='color: #666;'>[{timestamp}] <b>{author}:</b> {text}</em></p>"
    elif author == "Вы":
        formatted_message = f"<p><span style='color: #1976d2;'>[{timestamp}] <b>{author}:</b></span> {text}</p>"
    else:  # Ассистент
        formatted_message = f"<p><span style='color: #388e3c;'>[{timestamp}] <b>{author}:</b></span> {text}</p>"
    
    self.history.append(formatted_message)
    self.history.repaint()

def _scroll_history_to_end(self):
    """Прокручивает историю чата в конец"""
    scrollbar = self.history.verticalScrollBar()
    scrollbar.setValue(scrollbar.maximum())

# ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ДЛЯ ОТЛАДКИ

def get_debug_info(self):
    """Возвращает отладочную информацию о состоянии чата"""
    return {
        "crewai_client_available": self.crew_ai_client is not None,
        "crewai_server_available": self.crew_ai_client.is_available() if self.crew_ai_client else False,
        "send_button_enabled": self.send_btn.isEnabled(),
        "input_text_length": len(self.input.toPlainText()),
        "history_length": len(self.history.toPlainText())
    }

def test_crewai_connection(self):
    """Тестирует соединение с CrewAI API"""
    if not self.crew_ai_client:
        self.append_message("Система", "❌ CrewAI клиент не инициализирован")
        return False
        
    if not self.crew_ai_client.is_available():
        self.append_message("Система", "❌ CrewAI API сервер недоступен")
        return False
        
    # Отправляем тестовый запрос
    try:
        test_result = self.crew_ai_client.process_request("Тест соединения")
        if isinstance(test_result, dict) and "response" in test_result:
            self.append_message("Система", "✅ CrewAI API работает корректно")
            return True
        else:
            self.append_message("Система", f"⚠️ Неожиданный ответ от API: {test_result}")
            return False
    except Exception as e:
        self.append_message("Система", f"❌ Ошибка тестирования API: {str(e)}")
        return False
