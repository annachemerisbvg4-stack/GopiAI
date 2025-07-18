"""
Скрипт для автоматического применения патча для исправления проблемы с кратковременной памятью ИИ.
"""

import os
import re
import shutil
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_file(file_path):
    """Создает резервную копию файла"""
    backup_path = f"{file_path}.bak"
    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Создана резервная копия файла: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании резервной копии: {e}")
        return False

def apply_patch(file_path):
    """Применяет патч к файлу"""
    try:
        # Читаем содержимое файла
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем место для вставки патча
        pattern = r"(# Перемещаем system_prompt в metadata вместо корня запроса.*?logger\.debug\(\"\[REQUEST\] Добавлен стандартный системный промпт в metadata\"\))\s+logger\.debug\(f\"\[REQUEST\] Подготовка к отправке запроса в CrewAI API\"\)"
        
        # Код для вставки
        patch_code = """
        # Получаем историю сообщений для текущей сессии
        try:
            # Импортируем менеджер памяти
            from ..memory import get_memory_manager
            memory_manager = get_memory_manager()
            
            # Получаем ID сессии из метаданных сообщения
            session_id = message.get('metadata', {}).get('session_id', 'default_session')
            logger.debug(f"[REQUEST] Получение истории сообщений для сессии: {session_id}")
            
            # Получаем историю сообщений (последние 20 сообщений)
            chat_history = memory_manager.get_chat_history(session_id)
            if chat_history:
                # Берем последние 20 сообщений
                chat_history = chat_history[-20:]
                logger.info(f"[REQUEST] Получено {len(chat_history)} сообщений из истории для сессии {session_id}")
                
                # Добавляем историю сообщений в метаданные запроса
                message['metadata']['chat_history'] = chat_history
                logger.debug(f"[REQUEST] История сообщений добавлена в запрос")
            else:
                logger.debug(f"[REQUEST] История сообщений для сессии {session_id} не найдена")
        except Exception as e:
            logger.error(f"[REQUEST-ERROR] Ошибка при получении истории сообщений: {e}")
            
        logger.debug(f"[REQUEST] Подготовка к отправке запроса в CrewAI API")"""
        
        # Заменяем найденный текст
        new_content = re.sub(pattern, r"\1" + patch_code, content, flags=re.DOTALL)
        
        # Проверяем, что замена произошла
        if new_content == content:
            logger.error("Не удалось найти место для вставки патча. Возможно, файл уже был изменен или имеет другую структуру.")
            return False
        
        # Записываем изменения в файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Патч успешно применен к файлу: {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Ошибка при применении патча: {e}")
        return False

def main():
    """Основная функция скрипта"""
    # Путь к файлу crewai_client.py
    file_path = Path("GopiAI-UI/gopiai/ui/components/crewai_client.py")
    
    # Проверяем существование файла
    if not file_path.exists():
        logger.error(f"Файл не найден: {file_path}")
        return False
    
    # Создаем резервную копию
    if not backup_file(file_path):
        logger.error("Не удалось создать резервную копию. Отмена применения патча.")
        return False
    
    # Применяем патч
    if apply_patch(file_path):
        logger.info("Патч успешно применен!")
        logger.info("Для проверки работоспособности перезапустите приложение и проверьте, что ИИ корректно использует контекст из предыдущих сообщений.")
        return True
    else:
        logger.error("Не удалось применить патч. Восстанавливаем оригинальный файл.")
        # Восстанавливаем оригинальный файл
        shutil.copy2(f"{file_path}.bak", file_path)
        logger.info(f"Оригинальный файл восстановлен из резервной копии.")
        return False

if __name__ == "__main__":
    print("=== Применение патча для исправления проблемы с кратковременной памятью ИИ ===")
    result = main()
    if result:
        print("✅ Патч успешно применен!")
    else:
        print("❌ Не удалось применить патч. Смотрите логи для подробностей.")