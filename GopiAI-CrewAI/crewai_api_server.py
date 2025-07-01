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
from pathlib import Path
from functools import wraps
import hashlib
import secrets

# Настройки сервера
HOST = "127.0.0.1"
PORT = 5050
DEBUG = False

# Настройки таймаутов
REQUEST_TIMEOUT = 300  # 5 минут таймаут для обработки запросов
CONNECTION_TIMEOUT = 60  # 1 минута для установки соединения

# Базовая безопасность - API токен (в реальном проекте использовать переменные окружения)
API_TOKEN = os.environ.get('CREWAI_API_TOKEN', 'gopi-ai-default-token-2025')
RATE_LIMIT_REQUESTS = 100  # Максимум запросов в минуту
RATE_LIMIT_WINDOW = {}     # Счетчик запросов по IP

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
    from tools.gopiai_integration.smart_delegator import crewai_available, is_rag_service_available
    API_STATUS["status"] = "online"
    API_STATUS["crewai_available"] = crewai_available
    API_STATUS["txtai_available"] = is_rag_service_available() # Проверяем доступность RAG-сервиса
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
    API_STATUS["txtai_available"] = is_rag_service_available() if 'is_rag_service_available' in globals() else False
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
        # Параметр force_crewai игнорируется, т.к. система сама определяет
        # необходимость использования CrewAI на основе анализа запроса
        # force_crewai = data.get('force_crewai', False)
        
        # Безопасная обработка запроса с перехватом всех исключений
        try:
            # Анализируем запрос
            analysis = smart_delegator.analyze_request(message)
            print(f"📊 Анализ запроса: сложность={analysis.get('complexity', 0)}, тип={analysis.get('type', 'unknown')}, CrewAI={analysis.get('requires_crewai', False)}")
            
            # Обрабатываем запрос через стандартный метод,
            # который автоматически выберет способ обработки
            # Smart Delegator уже интегрирует RAG контекст внутри себя
            response = smart_delegator.process_request(message)
            
            print(f"✅ Ответ получен, длина: {len(response)} символов")
                
            return jsonify({
                "response": response,
                "processed_with_crewai": analysis.get("requires_crewai", False),
                "analysis": analysis  # Добавляем детали анализа для отладки
            })
        except Exception as inner_e:
            # В случае любой ошибки возвращаем fallback ответ
            traceback.print_exc()
            return jsonify({
                "error_message": f"[ОШИБКА ОБРАБОТКИ] Извините, произошла ошибка при обработке вашего запроса: {str(inner_e)}",
                "processed_with_crewai": False,
                "error": str(inner_e)
            })
            
    except Exception as e:
        traceback.print_exc()
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
