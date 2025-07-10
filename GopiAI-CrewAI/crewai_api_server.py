import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#!/usr/bin/env python3
"""
🌐 CrewAI API Server
Микросервис для доступа к CrewAI из основного окружения через REST API
"""

from flask import Flask, request, jsonify
import os
import sys
import json
import time
import traceback
import uuid
import threading
from pathlib import Path
from functools import wraps
import hashlib
import secrets
from datetime import datetime, timedelta

# Настройки сервера
HOST = "127.0.0.1"
PORT = 5050
DEBUG = False

# Настройки таймаутов
REQUEST_TIMEOUT = 300  # 5 минут таймаут для обработки запросов
CONNECTION_TIMEOUT = 60  # 1 минута для установки соединения
TASK_TIMEOUT = 300  # 5 минут на выполнение задачи
TASK_CLEANUP_INTERVAL = 300  # 5 минут между очистками старых задач

# Базовая безопасность - API токен (в реальном проекте использовать переменные окружения)
API_TOKEN = os.environ.get('CREWAI_API_TOKEN', 'gopi-ai-default-token-2025')
RATE_LIMIT_REQUESTS = 100  # Максимум запросов в минуту
RATE_LIMIT_WINDOW = {}     # Счетчик запросов по IP

# Глобальное хранилище задач
TASKS = {}
TASKS_LOCK = threading.Lock()

class TaskStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class Task:
    def __init__(self, task_id, message):
        self.task_id = task_id
        self.message = message
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.lock = threading.Lock()

    def start_processing(self):
        with self.lock:
            self.status = TaskStatus.PROCESSING
            self.started_at = datetime.now()

    def complete(self, result):
        with self.lock:
            self.status = TaskStatus.COMPLETED
            self.result = result
            self.completed_at = datetime.now()

    def fail(self, error):
        with self.lock:
            self.status = TaskStatus.FAILED
            self.error = str(error)
            self.completed_at = datetime.now()

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "status": self.status,
            "message": self.message,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

def cleanup_old_tasks():
    """Фоновая задача для очистки старых завершенных задач"""
    while True:
        time.sleep(TASK_CLEANUP_INTERVAL)
        now = datetime.now()
        with TASKS_LOCK:
            # Удаляем задачи, завершенные более часа назад
            for task_id in list(TASKS.keys()):
                task = TASKS[task_id]
                if task.completed_at and (now - task.completed_at) > timedelta(hours=1):
                    del TASKS[task_id]

# Запускаем фоновую задачу для очистки старых задач
cleanup_thread = threading.Thread(target=cleanup_old_tasks, daemon=True)
cleanup_thread.start()

app = Flask(__name__)

# Настройка путей для импорта модулей
# Добавляем корень проекта (GopiAI-CrewAI) в sys.path для корректных импортов
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# --- Diagnostic: Check llm_rotation_config.py content ---
try:
    llm_config_path = current_dir / "llm_rotation_config.py"
    if llm_config_path.exists():
        with open(llm_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"DEBUG: Content of llm_rotation_config.py at {llm_config_path}:\n{content[:500]}...") # Print first 500 chars
    else:
        print(f"DEBUG: llm_rotation_config.py not found at {llm_config_path}")
except Exception as e:
    print(f"DEBUG: Error reading llm_rotation_config.py: {e}")
# --- End Diagnostic ---

# Добавляем путь к site-packages виртуального окружения
venv_site_packages = current_dir / "crewai_env" / "Lib" / "site-packages"
if venv_site_packages.exists():
    sys.path.insert(0, str(venv_site_packages))

# Определяем глобальные переменные для состояния сервера
API_STATUS = {
    "status": "initializing",
    "timestamp": time.time(),
    "crewai_available": False,
    "txtai_available": False
}

# Импорт Smart Delegator (должен быть доступен в окружении CrewAI)
try:
    from tools.gopiai_integration.smart_delegator import smart_delegator
    from tools.gopiai_integration.smart_delegator import crewai_available
    
    API_STATUS["status"] = "online"
    API_STATUS["crewai_available"] = crewai_available
    API_STATUS["txtai_available"] = hasattr(smart_delegator, 'rag_available') and smart_delegator.rag_available
    print("Smart Delegator успешно импортирован")
except ImportError as e:
    print(f"Ошибка импорта Smart Delegator: {e}")
    print("API сервер запущен в ограниченном режиме")
    API_STATUS["status"] = "limited"
    smart_delegator = None

@app.route('/', methods=['GET'])
def index():
    """Главная страница с информацией о API"""
    API_STATUS["timestamp"] = time.time()
    
    # Формируем HTML страницу
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CrewAI API Server</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #333; }}
            .status {{ padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
            .online {{ background-color: #d4edda; color: #155724; }}
            .limited {{ background-color: #fff3cd; color: #856404; }}
            .offline {{ background-color: #f8d7da; color: #721c24; }}
            .endpoint {{ background-color: #f8f9fa; padding: 15px; margin-bottom: 10px; border-radius: 5px; }}
            .method {{ display: inline-block; padding: 3px 6px; border-radius: 3px; font-size: 12px; margin-right: 10px; }}
            .get {{ background-color: #61affe; color: white; }}
            .post {{ background-color: #49cc90; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CrewAI API Server</h1>
            
            <div class="status {API_STATUS['status']}">
                <strong>Статус:</strong> {API_STATUS['status'].upper()}<br>
                <strong>CrewAI доступен:</strong> {'Да' if API_STATUS['crewai_available'] else 'Нет'}<br>
                <strong>RAG-сервис (txtai) доступен:</strong> {'Да' if API_STATUS['txtai_available'] else 'Нет'}<br>
                <strong>Время последнего обновления:</strong> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(API_STATUS['timestamp']))}
            </div>
            
            <h2>Доступные эндпоинты</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span> <strong>/api/health</strong>
                <p>Проверка работоспособности API. Возвращает текущий статус сервера.</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span> <strong>/api/analyze</strong>
                <p>Анализ запроса пользователя. Определяет сложность и требуемый тип обработки.</p>
                <p><em>Параметры:</em> {{ "message": "текст запроса" }}</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span> <strong>/api/process</strong>
                <p>Обработка запроса пользователя через AI Router или CrewAI. Система автоматически определит необходимость использования команды агентов на основе сложности запроса.</p>
                <p><em>Параметры:</em> {{ "message": "текст запроса" }}</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span> <strong>/api/index_docs</strong>
                <p>Запуск индексации документации CrewAI для RAG.</p>
            </div>
            
            <hr>
            <p><small>Время запуска сервера: {time.strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности API"""
    if 'smart_delegator' in globals() and hasattr(smart_delegator, 'rag_available'):
        API_STATUS["txtai_available"] = smart_delegator.rag_available
    else:
        API_STATUS["txtai_available"] = False
    API_STATUS["timestamp"] = time.time()
    return jsonify(API_STATUS)

@app.route('/api/analyze', methods=['POST'])
def analyze_request():
    """Анализ запроса пользователя"""
    if not smart_delegator:
        return jsonify({"error": "Smart Delegator недоступен"}), 503
        
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Отсутствует поле 'message'"}), 400
    
    try:
        message = data['message']
        analysis = smart_delegator.analyze_request(message)
        return jsonify(analysis)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def process_task(task_id):
    """Функция для выполнения задачи в отдельном потоке"""
    try:
        task = TASKS.get(task_id)
        if not task:
            return

        task.start_processing()
        
        # Анализируем запрос
        analysis = smart_delegator.analyze_request(task.message)
        print(f"📊 [Задача {task_id}] Анализ запроса: сложность={analysis.get('complexity', 0)}, тип={analysis.get('type', 'unknown')}")
        
        # Определяем, является ли запрос сложным (требует асинхронной обработки)
        is_complex = (
            analysis.get('complexity', 0) >= 3 or  # Высокая сложность
            analysis.get('type') in ['summary', 'memory', 'history'] or  # Запросы на подведение итогов или поиск в памяти
            'что ты помнишь' in task.message.lower() or  # Прямой запрос на поиск в памяти
            'наши беседы' in task.message.lower() or    # Запрос о прошлых беседах
            'наши разговоры' in task.message.lower()    # Запрос о прошлых разговорах
        )
        
        if is_complex and not task.message.lower().startswith('!'):
            # Для сложных запросов запускаем асинхронную обработку
            thread = threading.Thread(
                target=process_complex_task,
                args=(task_id, analysis),
                daemon=True
            )
            thread.start()
            return
            
        # Для простых запросов обрабатываем синхронно
        response = smart_delegator.process_request(task.message)
        print(f"✅ [Задача {task_id}] Ответ получен, длина: {len(response)} символов")
        task.complete({
            "response": response,
            "processed_with_crewai": analysis.get("requires_crewai", False),
            "analysis": analysis
        })
        
    except Exception as e:
        print(f"❌ [Задача {task_id}] Ошибка при обработке: {str(e)}")
        traceback.print_exc()
        task.fail(f"Ошибка при обработке запроса: {str(e)}")

def process_complex_task(task_id, analysis):
    """Обработка сложных запросов, требующих длительного времени"""
    task = TASKS.get(task_id)
    if not task:
        return
        
    try:
        print(f"🔍 [Задача {task_id}] Начало обработки сложного запроса")
        
        # Обрабатываем запрос
        response = smart_delegator.process_request(task.message)
        
        print(f"✅ [Задача {task_id}] Сложный запрос обработан, длина ответа: {len(response)} символов")
        
        task.complete({
            "response": response,
            "processed_with_crewai": analysis.get("requires_crewai", False),
            "analysis": analysis
        })
        
    except Exception as e:
        print(f"❌ [Задача {task_id}] Ошибка при обработке сложного запроса: {str(e)}")
        traceback.print_exc()
        task.fail(f"Ошибка при обработке сложного запроса: {str(e)}")

@app.route('/api/process', methods=['POST'])
def process_request():
    """Обработка запроса через CrewAI"""
    if not smart_delegator:
        return jsonify({"error": "Smart Delegator недоступен"}), 503
        
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Отсутствует поле 'message'"}), 400
    
    try:
        message = data['message']
        
        # Создаем новую задачу
        task_id = str(uuid.uuid4())
        task = Task(task_id, message)
        
        with TASKS_LOCK:
            TASKS[task_id] = task
        
        # Запускаем обработку задачи в отдельном потоке
        thread = threading.Thread(
            target=process_task,
            args=(task_id,),
            daemon=True
        )
        thread.start()
        
        # Возвращаем немедленный ответ с ID задачи
        return jsonify({
            "task_id": task_id,
            "status": task.status,
            "message": "Задача поставлена в очередь на обработку",
            "created_at": task.created_at.isoformat()
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": f"Ошибка при создании задачи: {str(e)}",
            "status": TaskStatus.FAILED
        }), 500

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Проверка статуса задачи"""
    task = TASKS.get(task_id)
    if not task:
        return jsonify({"error": "Задача не найдена"}), 404
    
    task_dict = task.to_dict()
    
    # Для завершенных задач возвращаем полный ответ
    if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TIMEOUT]:
        return jsonify(task_dict)
    
    # Для незавершенных задач возвращаем только статус
    return jsonify({
        "task_id": task_id,
        "status": task.status,
        "message": task.message,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None
    })

@app.route('/api/process/sync', methods=['POST'])
def process_request_sync():
    """Синхронная обработка запроса (для обратной совместимости)"""
    if not smart_delegator:
        return jsonify({"error": "Smart Delegator недоступен"}), 503
        
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Отсутствует поле 'message'"}), 400
    
    try:
        message = data['message']
        
        # Анализируем запрос
        analysis = smart_delegator.analyze_request(message)
        print(f"📊 [Синхронный запрос] Анализ: сложность={analysis.get('complexity', 0)}")
        
        # Обрабатываем запрос
        response = smart_delegator.process_request(message)
        
        print(f"✅ [Синхронный запрос] Ответ получен, длина: {len(response)} символов")
        
        return jsonify({
            "response": response,
            "processed_with_crewai": analysis.get("requires_crewai", False),
            "analysis": analysis,
            "status": TaskStatus.COMPLETED
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": f"Ошибка при обработке запроса: {str(e)}",
            "status": TaskStatus.FAILED
        }), 500
        return jsonify({"error": str(e)}), 500

@app.route('/api/index_docs', methods=['POST'])
def index_documentation():
    """Запуск индексации документации CrewAI"""
    if not smart_delegator:
        return jsonify({"error": "Smart Delegator недоступен"}), 503
        
    try:
        # Проверяем, доступна ли функция индексации
        if not hasattr(smart_delegator, "index_documentation"):
            return jsonify({
                "success": False,
                "error": "Функция индексации недоступна (отсутствует txtai)"
            })
            
        try:
            result = smart_delegator.index_documentation()
            return jsonify({"success": result})
        except Exception as inner_e:
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(inner_e)
            })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"Starting CrewAI API server at http://{HOST}:{PORT}")
    print("This server should be run from the CrewAI environment (crewai_env)")
    
    # Проверяем корректность окружения
    import sys
    print(f"Using Python: {sys.executable}")
    
    # Проверяем доступность основных модулей
    try:
        import crewai
        print("CrewAI module is available")
    except ImportError:
        print("CrewAI module is NOT available")
    
    try:
        import langchain
        print("Langchain module is available")
    except ImportError:
        print("Модуль langchain НЕ доступен")
    
    # Настраиваем сервер с увеличенными таймаутами
    from werkzeug.serving import WSGIRequestHandler
    WSGIRequestHandler.timeout = REQUEST_TIMEOUT
    
    print(f"Request timeout: {REQUEST_TIMEOUT} seconds")
    print(f"Connection timeout: {CONNECTION_TIMEOUT} seconds")
    
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True, request_handler=WSGIRequestHandler)
