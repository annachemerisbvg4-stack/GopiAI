#!/usr/bin/env python3
"""
Минимальный тестовый сервер для диагностики
"""

import logging
import threading
import time
import uuid
from flask import Flask, request, jsonify

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Простое хранилище задач
TASKS = {}

class SimpleTask:
    def __init__(self, task_id, message):
        self.task_id = task_id
        self.message = message
        self.status = "pending"
        self.result = None
        self.error = None
        
    def process(self):
        """Простая обработка задачи"""
        self.status = "processing"
        time.sleep(2)  # Имитация работы
        self.result = f"Обработано: {self.message}"
        self.status = "completed"
        
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "message": self.message,
            "status": self.status,
            "result": self.result,
            "error": self.error
        }

def process_task(task_id):
    """Обработка задачи в отдельном потоке"""
    logger.info(f"[TASK] Начинаем обработку задачи {task_id}")
    
    task = TASKS.get(task_id)
    if not task:
        logger.error(f"[TASK] Задача {task_id} не найдена")
        return
    
    try:
        task.process()
        logger.info(f"[TASK] Задача {task_id} обработана успешно")
    except Exception as e:
        logger.error(f"[TASK] Ошибка при обработке задачи {task_id}: {e}")
        task.status = "failed"
        task.error = str(e)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "tasks": len(TASKS)})

@app.route('/api/process', methods=['POST'])
def process_request():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Missing 'message' field"}), 400
    
    message = data.get('message')
    task_id = str(uuid.uuid4())
    
    logger.info(f"[API] Создаем задачу {task_id} для сообщения: {message}")
    
    task = SimpleTask(task_id, message)
    TASKS[task_id] = task
    
    # Запускаем обработку в отдельном потоке
    thread = threading.Thread(target=process_task, args=(task_id,), daemon=True)
    thread.start()
    
    return jsonify({
        "task_id": task_id,
        "status": "pending",
        "message": "Task queued for processing"
    })

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())

if __name__ == '__main__':
    print("=== Минимальный тестовый сервер ===")
    print("Запуск на http://127.0.0.1:5052")
    app.run(host='127.0.0.1', port=5052, debug=False, threaded=True)
