import sys
import os
import time

# Добавляем путь к UI модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'GopiAI-UI'))

from gopiai.ui.components.crewai_client import CrewAIClient
from gopiai.ui.components.chat_async_handler import ChatAsyncHandler

# Создаем экземпляр клиента CrewAI
client = CrewAIClient(base_url="http://127.0.0.1:5052")

# Создаем обработчик асинхронных запросов
handler = ChatAsyncHandler(client)

# Функция для обработки ответа
def handle_response(response, is_error):
    print(f"Получен ответ (ошибка: {is_error}):")
    print(response)
    print("-" * 50)

# Функция для обработки обновления статуса
def handle_status(status):
    print(f"Статус: {status}")

# Подключаем сигналы
handler.response_ready.connect(handle_response)
handler.status_update.connect(handle_status)

# Отправляем тестовый запрос
print("Отправка тестового запроса...")
handler.process_message({"message": "Привет, это тестовое сообщение для проверки логирования!"})

# Ждем некоторое время для получения ответа
print("Ожидание ответа...")
time.sleep(10)

print("Тест завершен. Проверьте файлы логов.")
